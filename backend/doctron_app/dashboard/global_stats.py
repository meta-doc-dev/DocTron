from collections import defaultdict
from decimal import Decimal

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from doctron_app.models import (
    Document,
    Topic,
    CollectionHasLabel,
    AnnotateLabel,
    AnnotatePassage,
    ShareCollection,
    Collection,
    AssociateTag,
    Associate,
    CollectionHasTag,
    Concept,
    Tag
)

def decimal_default(obj) -> float:
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_document_statistics(topic_id, annotation_type, all_documents):
    """Calculate detailed document statistics for a topic"""
    if annotation_type == 'Graded labeling':
        base_query = AnnotateLabel.objects.filter(topic_id=topic_id)
    elif annotation_type == 'Passages annotation':
        base_query = AnnotatePassage.objects.filter(topic_id=topic_id)
    elif annotation_type == 'Entity tagging':
        base_query = AssociateTag.objects.filter(topic_id=topic_id)
    elif annotation_type == 'Entity linking':
        base_query = Associate.objects.filter(topic_id=topic_id)
    else:
        return {
            'total_annotated': 0,
            'total_missing': 0,
            'total_annotators': 0,
            'avg_annotators_per_doc': 0,
            'total_documents': 0,
            'document_coverage': {}
        }

    # Get unique annotated documents
    annotated_docs_query = base_query.values(
        'document_id',
        'language'
    ).distinct()

    # Total unique documents annotated (considering document_id and language)
    total_unique_docs = annotated_docs_query.count()

    # Total missing documents
    total_docs = all_documents.count()
    total_missing = total_docs - total_unique_docs

    # Get documents with annotator counts and calculate average annotators per document
    docs_with_annotators = base_query.values(
        'document_id',
        'language'
    ).annotate(
        annotator_count=Count('username', distinct=True),
        annotators=ArrayAgg('username', distinct=True)
    ).order_by('-annotator_count')

    # Calculate average annotators per document
    total_annotations = sum(doc['annotator_count'] for doc in docs_with_annotators)
    avg_annotators_per_doc = round(total_annotations / total_unique_docs if total_unique_docs > 0 else 0, 2)

    # Get total annotators
    total_annotators = base_query.values('username').distinct().count()

    # Calculate statistics for documents by annotator count
    doc_coverage = defaultdict(list)
    for doc in docs_with_annotators:
        doc_coverage[doc['annotator_count']].append({
            'id': str(doc['document_id']),
            'language': doc['language'],
            'annotators': doc['annotators']
        })

    return {
        'total_annotated': total_unique_docs,
        'total_missing': total_missing,
        'total_annotators': total_annotators,
        'avg_annotators_per_doc': avg_annotators_per_doc,
        'total_documents': total_annotations,
        'document_coverage': dict(doc_coverage)
    }

class GlobalAnnotationHandler:
    """Handler for global annotation statistics"""

    def __init__(self, collection_id: str):
        self.collection_id = collection_id

    def get_collection_users(self):
        """Get all users with access to the collection"""
        return ShareCollection.objects.filter(
            collection_id=self.collection_id
        ).values_list('username', 'name_space')

    def check_user_access(self, username, name_space):
        """Check if user has access to global statistics based on role and collection mode"""
        try:
            # Get collection mode (collaborative or not)
            collection = Collection.objects.get(collection_id=self.collection_id)

            # Regular users only have access in collaborative mode
            if collection.modality == "Collaborative open":
                return True

            # Get user's role in the collection
            user_role = ShareCollection.objects.get(
                collection_id=self.collection_id,
                username=username,
                name_space=name_space
            )

            # Admin always has access
            if user_role.admin:
                return True

            # Reviewer has access regardless of mode
            if user_role.reviewer:
                return True

            return False

        except (Collection.DoesNotExist, ShareCollection.DoesNotExist):
            return False

    def get_label_stats(self, topic_id, label, documents):
        """Get aggregated label statistics across all users"""
        # Get annotations for graded labels
        label_annotations = AnnotateLabel.objects.filter(
            topic_id=topic_id,
            label=label,
            document_id__in=documents.values('document_id')
        ).values('document_id', 'document_id__document_content', 'grade').annotate(
            usernames=ArrayAgg('username', distinct=True)
        )

        # Group by grade
        grade_stats = defaultdict(int)
        doc_stats = defaultdict(list)

        for ann in label_annotations:
            grade = int(ann['grade'])
            doc_id = ann['document_id']
            usernames = ann['usernames']
            count = len(ann['usernames'])

            grade_stats[grade] += count
            doc_stats[grade].append({
                'id': str(doc_id),
                'title': ann['document_id__document_content']['document_id'],
                'annotator_count': count,
                'annotators': usernames
            })

        return dict(grade_stats), dict(doc_stats)

    def get_passage_stats(self, topic_id, label, documents):
        """Get aggregated passage statistics across all users"""
        # Get annotations for passages
        passage_annotations = AnnotatePassage.objects.filter(
            topic_id=topic_id,
            label=label,
            document_id__in=documents.values('document_id')
        ).values('document_id', 'document_id__document_content', 'grade').annotate(
            usernames=ArrayAgg('username', distinct=True)
        )

        # Group by grade
        grade_stats = defaultdict(int)
        doc_stats = defaultdict(list)

        for ann in passage_annotations:
            grade = int(ann['grade'])
            doc_id = ann['document_id']
            usernames = ann['usernames']
            count = len(ann['usernames'])

            grade_stats[grade] += count
            doc_stats[grade].append({
                'id': str(doc_id),
                'title': ann['document_id__document_content']['document_id'],
                'annotator_count': count,
                'annotators': usernames
            })

        return dict(grade_stats), dict(doc_stats)

    def get_tag_stats(self, topic_id, tag, documents):
        """Get aggregated tag statistics across all users"""
        # Get annotations for tags
        tag_annotations = AssociateTag.objects.filter(
            topic_id=topic_id,
            name=tag,
            document_id__in=documents.values('document_id')
        ).values('document_id', 'document_id__document_content').annotate(
            usernames=ArrayAgg('username', distinct=True)
        )

        # We use a single grade (1) for tags, indicating presence
        grade_stats = defaultdict(int)
        doc_stats = defaultdict(list)

        for ann in tag_annotations:
            doc_id = ann['document_id']
            usernames = ann['usernames']
            count = len(ann['usernames'])

            # Use grade "1" to indicate presence
            grade_stats[1] += count
            doc_stats[1].append({
                'id': str(doc_id),
                'title': ann['document_id__document_content']['document_id'],
                'annotator_count': count,
                'annotators': usernames
            })

        return dict(grade_stats), dict(doc_stats)

    def get_concept_stats(self, topic_id, concept_url, documents):
        """Get aggregated concept statistics across all users"""
        # Get annotations for concepts
        concept_annotations = Associate.objects.filter(
            topic_id=topic_id,
            concept_url=concept_url,
            document_id__in=documents.values('document_id')
        ).values('document_id', 'document_id__document_content').annotate(
            usernames=ArrayAgg('username', distinct=True)
        )

        # We use a single grade (1) for concepts, indicating presence
        grade_stats = defaultdict(int)
        doc_stats = defaultdict(list)

        for ann in concept_annotations:
            doc_id = ann['document_id']
            usernames = ann['usernames']
            count = len(ann['usernames'])

            # Use grade "1" to indicate presence
            grade_stats[1] += count
            doc_stats[1].append({
                'id': str(doc_id),
                'title': ann['document_id__document_content']['document_id'],
                'annotator_count': count,
                'annotators': usernames
            })

        return dict(grade_stats), dict(doc_stats)

@require_http_methods(["GET"])
def get_global_statistics(request):
    """View to get global annotation statistics across all users"""
    try:
        # Get request parameters
        collection_id = request.GET.get('collection_id')
        username = request.session.get('username')
        name_space = request.session.get('name_space', 'Human')
        annotation_type = request.GET.get('annotation_type', 'Graded labeling')

        # Validate required parameters
        if not all([collection_id, username]):
            return JsonResponse({
                'error': 'Missing required parameters: collection_id and/or username'
            }, status=400)

        # Initialize global handler
        handler = GlobalAnnotationHandler(collection_id)

        # Check user access
        if not handler.check_user_access(username, name_space):
            return JsonResponse({
                'error': 'Access denied. Global statistics are only available to admins, reviewers, or in collaborative mode.'
            }, status=403)

        # Get collection data
        all_documents = Document.objects.filter(collection_id=collection_id)
        all_topics = Topic.objects.filter(collection_id=collection_id)

        # Get appropriate collection items based on annotation type
        if annotation_type in ['Graded labeling', 'Passages annotation']:
            collection_items = CollectionHasLabel.objects.filter(
                collection_id=collection_id
            ).select_related('label')
        elif annotation_type == 'Entity tagging':
            collection_items = CollectionHasTag.objects.filter(
                collection_id=collection_id
            ).select_related('name')
        elif annotation_type == 'Entity linking':
            # For entity linking, we'll get concept data directly from annotations
            collection_items = []
        else:
            collection_items = []

        results = []
        for topic in all_topics:
            topic_data = {
                'id': str(topic.id),
                'topic_id': str(topic.topic_id),
                'topic_title': topic.details['text'],
                'topic_info': topic.details,
                'labels': {},
                'label_documents': {}
            }

            # Get detailed document statistics with unique document count
            doc_stats = get_document_statistics(
                topic.id,
                annotation_type,
                all_documents,
            )

            # Update topic data with document statistics
            topic_data.update({
                'total_annotators': doc_stats['total_annotators'],
                'total_documents_unique': doc_stats['total_annotated'],
                'number_of_missing_documents': doc_stats['total_missing'],
                'total_documents': doc_stats['total_documents'],
                'avg_annotators_per_document': doc_stats['avg_annotators_per_doc'],
                'document_coverage': doc_stats['document_coverage']
            })

            # Get statistics based on annotation type
            if annotation_type in ['Graded labeling', 'Passages annotation']:
                # Handle label-based annotations
                for coll_label in collection_items:
                    label_name = coll_label.label.name

                    if annotation_type == 'Graded labeling':
                        grade_stats, doc_stats = handler.get_label_stats(
                            topic.id,
                            coll_label.label,
                            all_documents
                        )
                    else:
                        grade_stats, doc_stats = handler.get_passage_stats(
                            topic.id,
                            coll_label.label,
                            all_documents
                        )

                    if grade_stats:
                        topic_data['labels'][label_name] = {
                            str(k): v for k, v in grade_stats.items()
                        }
                        topic_data['label_documents'][label_name] = {
                            str(k): v for k, v in doc_stats.items()
                        }

            elif annotation_type == 'Entity tagging':
                # Handle tag-based annotations
                for coll_tag in collection_items:
                    tag_name = coll_tag.name.name

                    grade_stats, doc_stats = handler.get_tag_stats(
                        topic.id,
                        coll_tag.name,
                        all_documents
                    )

                    if grade_stats:
                        topic_data['labels'][tag_name] = {
                            str(k): v for k, v in grade_stats.items()
                        }
                        topic_data['label_documents'][tag_name] = {
                            str(k): v for k, v in doc_stats.items()
                        }

            elif annotation_type == 'Entity linking':
                # Handle concept-based annotations
                # First get all concept URLs used in this topic
                concept_urls = Associate.objects.filter(
                    topic_id=topic.id,
                    document_id__in=all_documents.values('document_id')
                ).values_list('concept_url', flat=True).distinct()

                for concept_url in concept_urls:
                    try:
                        # Get concept name
                        concept = Concept.objects.get(concept_url=concept_url)
                        concept_name = concept.concept_name or concept.concept_url

                        grade_stats, doc_stats = handler.get_concept_stats(
                            topic.id,
                            concept_url,
                            all_documents
                        )

                        if grade_stats:
                            topic_data['labels'][concept_name] = {
                                str(k): v for k, v in grade_stats.items()
                            }
                            topic_data['label_documents'][concept_name] = {
                                str(k): v for k, v in doc_stats.items()
                            }
                    except Concept.DoesNotExist:
                        continue

            if annotation_type == "Passages annotation":
                topic_data['number_of_passages'] = sum(
                    sum(values.values()) for values in topic_data.get('labels', {}).values()
                )

            results.append(topic_data)

        response = {
            'status': 'success',
            'data': results,
        }

        # Add label ranges based on annotation type
        if annotation_type in ['Graded labeling', 'Passages annotation']:
            labels_range = defaultdict()
            for coll_label in collection_items:
                label_range = coll_label.values
                labels_range[coll_label.label.name] = list(range(
                    int(label_range.lower),
                    int(label_range.upper) + 1
                ))
            response['label_range'] = labels_range

        elif annotation_type == 'Entity tagging':
            # For entity tagging, we use a single value (1) indicating presence
            tags_range = defaultdict(list)
            for coll_tag in collection_items:
                tags_range[coll_tag.name.name] = [1]
            response['label_range'] = tags_range

        elif annotation_type == 'Entity linking':
            # For entity linking, we use a single value (1) for each concept
            concepts_range = defaultdict(list)
            for topic in all_topics:
                concept_urls = Associate.objects.filter(
                    topic_id=topic.id,
                    document_id__in=all_documents.values('document_id')
                ).values_list('concept_url', flat=True).distinct()

                for concept_url in concept_urls:
                    try:
                        concept = Concept.objects.get(concept_url=concept_url)
                        concept_name = concept.concept_name or concept.concept_url
                        concepts_range[concept_name] = [1]
                    except Concept.DoesNotExist:
                        continue

            response['label_range'] = concepts_range

        return JsonResponse(response, json_dumps_params={'default': decimal_default})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)