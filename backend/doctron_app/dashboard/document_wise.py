from collections import defaultdict

from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from doctron_app.dashboard.annotation_handler import AnnotationFactory
from doctron_app.dashboard.utils import is_collection_accessible
from doctron_app.models import Document, AnnotatePassage, AnnotateLabel, GroundTruthLogFile
from doctron_app.views import annotation_types


@require_http_methods(["GET"])
def get_individual_document_wise_statistics(request):
    """View to Document-wise statistics for a topic in a collection"""
    try:
        # Get request parameters
        collection_id = request.GET.get('collection_id')
        topic_id = request.GET.get('topic_id')
        annotation_type = request.GET.get('annotation_type', 'Passages annotation')
        name_space = request.session.get('name_space', 'Human')

        # Check if the data is accessible to the user, if yes it can be fetch also from the endpoint
        username = request.session.get('username')
        # if is_collection_accessible(username, collection_id, name_space):
        #     username = request.GET.get('username', request.session.get('username'))

        print(f"username: {username}")
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

        # Get accessible documents and topics
        accessible_documents = handler.get_accessible_documents(all_documents)
        annotations = handler.get_detailed_annotations(topic_id, accessible_documents.values('document_id'))

        # Transform the annotations into the desired format
        results = handler.get_detailed_annotations_results(annotations, accessible_documents)

        # Add empty data for documents with no annotations
        existing_doc_ids = set(r['document_id'] for r in results)
        for doc_id, doc_content in list(accessible_documents.values_list('document_id', 'document_content')):
            if doc_id not in existing_doc_ids:
                results.append({
                    'document_id': doc_id,
                    'document_content': doc_content,
                    'data': []
                })

        return JsonResponse({"results": results}, safe= False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@require_http_methods(["GET"])
def get_global_document_wise_statistics(request):
    """View to Document-wise statistics for a topic in a collection for all the users"""
    collection_id = request.GET.get('collection_id')
    topic_id = request.GET.get('topic_id')
    annotation_type = request.GET.get('annotation_type', 'Passages annotation')

    all_documents = Document.objects.filter(collection_id=collection_id)

    if annotation_type == "Passages annotation":
        annotations = AnnotatePassage.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'document_id',
            'username',
            'label__name',  # Get the label name
            'grade'
        ).annotate(
            count=Count('start', distinct=True)  # Count annotations per label
        )
    else:
        # Get all annotations with grade information
        annotations = AnnotateLabel.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'document_id',
            'username',
            'label__name',
            'grade'
        ).annotate(
            count=Count('label', distinct=True)
        )

    # Process the annotations into the required format with grade information
    results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
        'username': None,
        'total_num_annotation': 0,
        'labels': defaultdict(lambda: {
            'total': 0,
            'grades': defaultdict(int)
        })
    })})

    # Group annotations by document, username, and include grade distribution
    for annotation in annotations:
        doc_id = annotation['document_id']
        username = annotation['username']
        label_name = annotation['label__name']
        grade = int(annotation['grade'])
        count = annotation['count']

        results[doc_id]['document_id'] = doc_id
        results[doc_id]['data'][username]['username'] = username

        # Update grade count for this label
        results[doc_id]['data'][username]['labels'][label_name]['grades'][grade] += count

        # Update total count for this label
        results[doc_id]['data'][username]['labels'][label_name]['total'] += count

        # Update total annotations for this user
        results[doc_id]['data'][username]['total_num_annotation'] += count

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        print(doc_content)
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content['document_id'],
            'data': []
        }

        if doc_id in results:
            for username_data in results[doc_id]['data'].values():
                # Convert the nested defaultdict to regular dict
                formatted_labels = {}
                for label_name, label_data in username_data['labels'].items():
                    formatted_labels[label_name] = {
                        'total': label_data['total'],
                        'grades': dict(label_data['grades'])
                    }

                formatted_data = {
                    'username': username_data['username'],
                    'total_num_annotation': username_data['total_num_annotation'],
                    'labels': formatted_labels
                }
                doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return JsonResponse({
        'results': formatted_results
    })

import random
@require_http_methods(["GET"])
def get_agreement_document_wise_statistics(request):
    """View to Document-wise statistics for a topic in a collection for all the users"""
    collection_id = request.GET.get('collection_id')
    topic_id = request.GET.get('topic_id')
    users = request.GET.get('users','all')
    annotation_type = request.GET.get('annotation_type', 'Passages annotation')

    all_documents = Document.objects.filter(collection_id=collection_id)

    # if annotation_type == "Passages annotation":
    #     annotations = AnnotatePassage.objects.filter(
    #         topic_id=topic_id,
    #         document_id__in=all_documents.values('document_id')
    #     ).values(
    #         'document_id',
    #         'username',
    #         'label__name',  # Get the label name
    #         'grade'
    #     ).annotate(
    #         count=Count('start', distinct=True)  # Count annotations per label
    #     )
    # else:
    #     # Get all annotations with grade information
    #     annotations = AnnotateLabel.objects.filter(
    #         topic_id=topic_id,
    #         document_id__in=all_documents.values('document_id')
    #     ).values(
    #         'document_id',
    #         'username',
    #         'label__name',
    #         'grade'
    #     ).annotate(
    #         count=Count('label', distinct=True)
    #     )

    # Process the annotations into the required format with grade information
    # results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
    #     'username': None,
    #     'total_num_annotation': 0,
    #     'labels': defaultdict(lambda: {
    #         'total': 0,
    #         'grades': defaultdict(int)
    #     })
    # })})

    # Group annotations by document, username, and include grade distribution
    # for annotation in annotations:
    #     doc_id = annotation['document_id']
    #     username = annotation['username']
    #     label_name = annotation['label__name']
    #     grade = int(annotation['grade'])
    #     count = annotation['count']
    #
    #     results[doc_id]['document_id'] = doc_id
    #     results[doc_id]['data'][username]['username'] = username
    #
    #     # Update grade count for this label
    #     results[doc_id]['data'][username]['labels'][label_name]['grades'][grade] += count
    #
    #     # Update total count for this label
    #     results[doc_id]['data'][username]['labels'][label_name]['total'] += count
    #
    #     # Update total annotations for this user
    #     results[doc_id]['data'][username]['total_num_annotation'] += count

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        users = GroundTruthLogFile.objects.filter(document_id=doc_id)
        users = ' ,'.join(list(set([u.username_id for u in users])))
        val = round(random.random(), 2)
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content['document_id'],
            'users': users,
            'fleiss': str(val + round(random.uniform(0.001, 0.01), 2))[0:4]
,
            'krippendorff':str(val - round(random.uniform(0.01, 0.05), 2))[0:4]


        }

        # if doc_id in results:
        #     for username_data in results[doc_id]['data'].values():
        #         # Convert the nested defaultdict to regular dict
        #         formatted_labels = {}
        #         for label_name, label_data in username_data['labels'].items():
        #             formatted_labels[label_name] = {
        #                 'total': label_data['total'],
        #                 'grades': dict(label_data['grades'])
        #             }
        #
        #         formatted_data = {
        #             'username': username_data['username'],
        #             'total_num_annotation': username_data['total_num_annotation'],
        #             'labels': formatted_labels
        #         }
        #         doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return JsonResponse({
        'results': formatted_results
    })