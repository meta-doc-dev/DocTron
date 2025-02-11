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
    Collection
)

def decimal_default(obj) -> float:
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

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
        ).values('document_id', 'grade').annotate(
            # count=Count('username', distinct=True),
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
                'title': f"Document {doc_id}",
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
        ).values('document_id', 'grade').annotate(
            # count=Count('username', distinct=True),
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
                'title': f"Document {doc_id}",
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
        collection_labels = CollectionHasLabel.objects.filter(
            collection_id=collection_id
        ).select_related('label')

        # Get all users with access to collection
        collection_users = handler.get_collection_users()
        user_count = len(collection_users)

        results = []
        for topic in all_topics:
            topic_data = {
                'id': str(topic.id),
                'topic_id': str(topic.topic_id),
                'topic_title': f"{topic.details['text'][:13]}...",
                'total_annotators': user_count,
                'labels': {},
                'label_documents': {}
            }

            # Get document statistics
            if annotation_type == 'Graded labeling':
                annotated_docs = AnnotateLabel.objects.filter(
                    topic_id=topic.topic_id
                ).values('document_id').distinct().count()
            else:
                annotated_docs = AnnotatePassage.objects.filter(
                    topic_id=topic.topic_id
                ).values('document_id').distinct().count()

            topic_data['number_of_annotated_documents'] = annotated_docs
            topic_data['number_of_missing_documents'] = all_documents.count() - annotated_docs

            # Get label statistics
            for coll_label in collection_labels:
                label_name = coll_label.label.name

                if annotation_type == 'Graded labeling':
                    grade_stats, doc_stats = handler.get_label_stats(
                        topic.topic_id,
                        coll_label.label,
                        all_documents
                    )
                else:
                    grade_stats, doc_stats = handler.get_passage_stats(
                        topic.topic_id,
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

            if annotation_type == "Passages annotation":
                topic_data['number_of_passages'] = sum(
                    sum(values.values()) for values in topic_data.get('labels', {}).values()
                )

            results.append(topic_data)

        response = {
            'status': 'success',
            'data': results,
            'total_annotators': user_count
        }

        # Add label ranges if applicable
        if annotation_type in ['Graded labeling', 'Passages annotation']:
            labels_range = defaultdict()
            for coll_label in collection_labels:
                label_range = coll_label.values
                labels_range[coll_label.label.name] = list(range(
                    int(label_range.lower),
                    int(label_range.upper) + 1
                ))
            response['label_range'] = labels_range

        return JsonResponse(response, json_dumps_params={'default': decimal_default})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)