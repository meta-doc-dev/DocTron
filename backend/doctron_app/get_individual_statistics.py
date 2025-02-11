from decimal import Decimal
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from doctron_app.models import *


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError



ANNOTATION_MODELS = {
    'Graded labeling': AnnotateLabel,
    'Passages annotation': AnnotatePassage
}

@require_http_methods(["GET"])
def get_individual_statistics(request):
    try:
        collection_id = request.GET.get('collection_id')
        username = request.session.get('username')
        name_space = request.session.get('name_space', 'Human')
        annotation_type = request.GET.get('annotation_type', 'Grade Labeling')

        if not all([collection_id, username]):
            return JsonResponse({
                'error': 'Missing required parameters, collection_id and/or username'
            }, status=400)

        results = []
        topics = Topic.objects.filter(collection_id=collection_id)

        # Get all documents for this collection and user from Split table
        all_documents = Document.objects.filter(
            collection_id=collection_id,
            # username=username,
            # name_space=name_space
        ).values_list('document_id', 'language')

        collection_labels = CollectionHasLabel.objects.filter(
            collection_id=collection_id
        ).select_related('label')

        # Convert to set for faster lookup
        all_docs_set = set((doc_id, lang) for doc_id, lang in all_documents)

        AnnotateModel = ANNOTATION_MODELS[annotation_type]
        for topic in topics:
            # Get annotated documents for this topic
            annotated_docs = AnnotateModel.objects.filter(
                topic_id=topic.topic_id,
                username=username,
                name_space=name_space,
                document_id__in=all_documents.values('document_id')
            ).values_list('document_id', 'label', 'grade', 'comment').distinct()

            # Convert to set for faster lookup
            annotated_doc_ids = set(doc_id for doc_id, _, _, _ in annotated_docs)

            # Prepare document lists
            annotated_documents = []
            missing_documents = []

            # Process all documents
            for doc_id, language in all_docs_set:
                doc_info = {
                    'id': str(doc_id),
                    'title': f"Document {doc_id}",
                    'language': language
                }

                if doc_id in annotated_doc_ids:
                    annotated_documents.append(doc_info)
                else:
                    missing_documents.append(doc_info)

            # Get label statistics with document details
            labels_data = {}
            label_documents = {}

            for coll_label in collection_labels:
                label_name = coll_label.label.name

                # Get annotations with grades for this label
                annotations = AnnotateModel.objects.filter(
                    topic_id=topic.topic_id,
                    username=username,
                    name_space=name_space,
                    label=coll_label.label,
                    document_id__in=all_documents.values('document_id')
                ).values('document_id', 'grade', 'comment')

                # Group documents by grade
                grade_docs = defaultdict(list)
                grade_counts = defaultdict(int)

                for ann in annotations:
                    grade = int(ann['grade'])  # Convert Decimal to int
                    doc_id = ann['document_id']
                    doc_language = next((lang for did, lang in all_docs_set if did == doc_id), None)

                    doc_info = {
                        'id': str(doc_id),
                        'title': f"Document {doc_id}",
                        'language': doc_language,
                        'grade': grade,  # Now an int
                        'comment': ann['comment']
                    }
                    grade_docs[grade].append(doc_info)
                    grade_counts[grade] += 1

                if grade_counts:
                    # Convert default dict to regular dict with string keys
                    labels_data[label_name] = {str(k): v for k, v in dict(grade_counts).items()}
                    label_documents[label_name] = {str(k): v for k, v in dict(grade_docs).items()}

            topic_data = {
                'id': str(topic.id),
                'topic_id': str(topic.topic_id),
                'topic_title': f"{topic.details['text'][:13]}...",
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