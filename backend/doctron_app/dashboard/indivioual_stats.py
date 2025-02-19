from collections import defaultdict
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from doctron_app.dashboard.annotation_handler import AnnotationFactory
from doctron_app.models import Document, Topic, CollectionHasLabel


def decimal_default(obj) -> float:
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_document_info(doc_id, language, comment = None):
    """Helper function to create document info dictionary"""
    info = {
        'id': str(doc_id),
        'title': f"Document {doc_id}",
        'language': language
    }
    if comment:
        info['comment'] = comment
    return info

def get_label_ranges(collection_labels):
    """Get valid grade ranges for each label"""
    label_ranges = {}
    for coll_label in collection_labels:
        try:
            lower, upper = map(int, coll_label.values.split(','))
            label_ranges[coll_label.label.name] = list(range(lower, upper + 1))
        except (ValueError, AttributeError):
            continue
    return label_ranges

@require_http_methods(["GET"])
def get_individual_statistics(request):
    """View to get individual annotation statistics with split support"""
    try:
        # Get request parameters
        collection_id = request.GET.get('collection_id')

        # TODO:
        #  CHECK THE USER ACCESS AND IF ALLOWED, PERMIT THE USER TO ACCESS OTHER USERS' DATA,
        #  OTHERWISE, ONLY ALLOW THE USER TO ACCESS HIS/HER DATA
        username = request.GET.get('username', request.session.get('username'))

        name_space = request.session.get('name_space', 'Human')
        annotation_type = request.GET.get('annotation_type', 'Graded labeling')

        # Validate required parameters
        if not all([collection_id, username]):
            return JsonResponse({
                'error': 'Missing required parameters: collection_id and/or username'
            }, status=400)

        # Get handler for annotation type
        try:
            handler = AnnotationFactory.get_handler(
                annotation_type,
                username,
                name_space,
                collection_id
            )
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Get collection data
        all_documents = Document.objects.filter(collection_id=collection_id)
        all_topics = Topic.objects.filter(collection_id=collection_id)
        collection_labels = CollectionHasLabel.objects.filter(
            collection_id=collection_id
        ).select_related('label')

        # Get accessible documents and topics
        accessible_documents = handler.get_accessible_documents(all_documents)
        accessible_topics = handler.get_accessible_topics(all_topics)

        # Convert to set for faster lookup
        all_docs_set = set((doc.document_id, doc.language, doc.document_content['document_id']) for doc in accessible_documents)

        results = []
        for topic in accessible_topics:
            annotations = handler.get_annotations(topic.id, accessible_documents)
            annotated_doc_ids = set(doc_id for doc_id, _, _, _ in annotations)

            annotated_documents = []
            missing_documents = []

            # Process all documents
            for doc_id, language, real_document_id in all_docs_set:
                doc_info = {
                    'id': str(doc_id),
                    'title': real_document_id,
                    'language': language
                }

                if doc_id in annotated_doc_ids:
                    annotated_documents.append(doc_info)
                else:
                    missing_documents.append(doc_info)

            # Get label statistics with document details
            labels_data, label_documents = handler.get_stats(
                topic.id,
                collection_labels,
                accessible_documents,
                all_docs_set
            )

            topic_data = {
                'id': str(topic.id),
                'topic_id': str(topic.topic_id),
                'topic_title': topic.details['text'],
                'topic_info': topic.details,
                'number_of_annotated_documents': len(annotated_documents),
                'number_of_missing_documents': len(missing_documents),
                'labels': labels_data,
                'annotated_documents': annotated_documents,
                'missing_documents': missing_documents,
                'label_documents': label_documents
            }

            if annotation_type == "Passages annotation":
                topic_data['number_of_passages'] = sum(
                    sum(values.values()) for values in topic_data.get('labels', {}).values()
                )

            results.append(topic_data)

        response = {'status': 'success','data': results}

        if annotation_type in ['Graded labeling', 'Passages annotation']:
            labels_range = defaultdict()
            for coll_label in collection_labels:
                label_range = coll_label.values
                labels_range[coll_label.label.name] = list(range(int(label_range.lower), int(label_range.upper) + 1))
            response['label_range'] = labels_range

        return JsonResponse(response, json_dumps_params={'default': decimal_default})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)