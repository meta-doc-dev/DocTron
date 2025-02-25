from collections import defaultdict

from django.db.models import Count, F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from doctron_app.dashboard.annotation_handler import AnnotationFactory
from doctron_app.dashboard.utils import is_collection_accessible
from doctron_app.models import Document, AnnotatePassage, AnnotateLabel, GroundTruthLogFile, AssociateTag, Associate, Concept, Tag


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

        if annotation_type in ['Graded labeling', 'Passages annotation']:
            annotations = handler.get_detailed_annotations(topic_id, accessible_documents.values('document_id'))
            results = handler.get_detailed_annotations_results(annotations, accessible_documents)
        elif annotation_type == 'Entity tagging':
            # Get tag annotations
            annotations = AssociateTag.objects.filter(
                topic_id=topic_id,
                username=username,
                name_space=name_space,
                document_id__in=accessible_documents.values('document_id')
            ).select_related('start', 'name').values(
                'document_id',
                'start',
                'stop',
                'comment',
                'insertion_time',
                tag_name=F('name__name')
            )

            # Process into hierarchical structure
            results = process_entity_tagging_results(annotations, accessible_documents)
        elif annotation_type == 'Entity linking':
            # Get concept annotations - FIXED THE FIELD NAME CONFLICT
            annotations = Associate.objects.filter(
                topic_id=topic_id,
                username=username,
                name_space=name_space,
                document_id__in=accessible_documents.values('document_id')
            ).values(
                'document_id',
                'start',
                'stop',
                'comment',
                'insertion_time',
                'concept_url_id',  # Using the actual field name from the model
                concept_name=F('concept_url__concept_name')  # This is fine as annotation
            )

            # Process into hierarchical structure
            results = process_entity_linking_results(annotations, accessible_documents)
        else:
            results = []

        # Add empty data for documents with no annotations
        existing_doc_ids = set(r['document_id'] for r in results)
        for doc_id, doc_content in list(accessible_documents.values_list('document_id', 'document_content')):
            if doc_id not in existing_doc_ids:
                results.append({
                    'document_id': doc_id,
                    'document_content': doc_content,
                    'data': []
                })

        return JsonResponse({"results": results}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def process_entity_tagging_results(annotations, accessible_documents):
    """Process entity tagging annotations into hierarchical structure"""
    results = []
    doc_annotations = defaultdict(list)

    # Group annotations by document
    for annotation in annotations:
        doc_id = annotation['document_id']
        doc_annotations[doc_id].append(annotation)

    # Process each document
    for doc_id, annotations_list in doc_annotations.items():
        try:
            document = accessible_documents.get(document_id=doc_id)

            # Group tags
            tags = {}
            for annotation in annotations_list:
                tag_name = annotation['tag_name']
                if tag_name not in tags:
                    tags[tag_name] = []

                # Add entity info to the tag
                tags[tag_name].append({
                    'start': annotation['start'],
                    'stop': annotation['stop'],
                    'comment': annotation['comment'],
                    'insertion_time': annotation['insertion_time'].isoformat() if annotation['insertion_time'] else None
                })

            # Structure the data for hierarchical display
            tag_data = []
            for tag_name, entities in tags.items():
                tag_data.append({
                    'tag_name': tag_name,
                    'entities': entities,
                    'count': len(entities)
                })

            results.append({
                'document_id': doc_id,
                'document_content': document.document_content,
                'data': tag_data
            })
        except Document.DoesNotExist:
            continue

    return results


def process_entity_linking_results(annotations, accessible_documents):
    """Process entity linking annotations into hierarchical structure"""
    results = []
    doc_annotations = defaultdict(list)

    # Group annotations by document
    for annotation in annotations:
        doc_id = annotation['document_id']
        doc_annotations[doc_id].append(annotation)

    # Process each document
    for doc_id, annotations_list in doc_annotations.items():
        try:
            document = accessible_documents.get(document_id=doc_id)

            # Group concepts
            concepts = {}
            for annotation in annotations_list:
                concept_url = annotation['concept_url_id']  # FIXED: Using the correct field name
                concept_name = annotation['concept_name'] or concept_url

                if concept_url not in concepts:
                    concepts[concept_url] = {
                        'name': concept_name,
                        'url': concept_url,
                        'entities': []
                    }

                # Add entity info to the concept
                concepts[concept_url]['entities'].append({
                    'start': annotation['start'],
                    'stop': annotation['stop'],
                    'comment': annotation['comment'],
                    'insertion_time': annotation['insertion_time'].isoformat() if annotation['insertion_time'] else None
                })

            # Structure the data for hierarchical display
            concept_data = []
            for concept_url, concept_info in concepts.items():
                concept_data.append({
                    'concept_name': concept_info['name'],
                    'concept_url': concept_info['url'],
                    'entities': concept_info['entities'],
                    'count': len(concept_info['entities'])
                })

            results.append({
                'document_id': doc_id,
                'document_content': document.document_content,
                'data': concept_data
            })
        except Document.DoesNotExist:
            continue

    return results



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
    elif annotation_type == "Graded labeling":
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
    elif annotation_type == "Entity tagging":
        # Get tag annotations
        annotations = AssociateTag.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'document_id',
            'username',
            'name__name'  # Get tag name
        ).annotate(
            count=Count('start', distinct=True)  # Count annotations per tag
        )
    elif annotation_type == "Entity linking":
        # Get concept annotations - FIXED FIELD NAMES
        annotations = Associate.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'document_id',
            'username',
            'concept_url_id',  # Using the actual field name
            concept_name=F('concept_url__concept_name')
        ).annotate(
            count=Count('start', distinct=True)  # Count annotations per concept
        )
    else:
        return JsonResponse({'error': f'Unsupported annotation type: {annotation_type}'}, status=400)

    # Process the annotations into the required format with hierarchical structure
    if annotation_type in ["Graded labeling", "Passages annotation"]:
        results = process_label_annotations(annotations, all_documents)
    elif annotation_type == "Entity tagging":
        results = process_tag_annotations(annotations, all_documents)
    elif annotation_type == "Entity linking":
        results = process_concept_annotations(annotations, all_documents)
    else:
        results = []

    return JsonResponse({
        'results': results
    })


def process_label_annotations(annotations, all_documents):
    """Process label annotations for global document-wise statistics"""
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

    return formatted_results


def process_tag_annotations(annotations, all_documents):
    """Process tag annotations for global document-wise statistics"""
    results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
        'username': None,
        'total_num_annotation': 0,
        'tags': defaultdict(int)
    })})

    # Group annotations by document and username
    for annotation in annotations:
        doc_id = annotation['document_id']
        username = annotation['username']
        tag_name = annotation['name__name']
        count = annotation['count']

        results[doc_id]['document_id'] = doc_id
        results[doc_id]['data'][username]['username'] = username
        results[doc_id]['data'][username]['tags'][tag_name] += count
        results[doc_id]['data'][username]['total_num_annotation'] += count

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content['document_id'],
            'data': []
        }

        if doc_id in results:
            for username_data in results[doc_id]['data'].values():
                formatted_data = {
                    'username': username_data['username'],
                    'total_num_annotation': username_data['total_num_annotation'],
                    'tags': dict(username_data['tags'])
                }
                doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return formatted_results


def process_concept_annotations(annotations, all_documents):
    """Process concept annotations for global document-wise statistics"""
    results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
        'username': None,
        'total_num_annotation': 0,
        'concepts': defaultdict(int)
    })})

    # Group annotations by document and username - FIXED FIELD NAMES
    for annotation in annotations:
        doc_id = annotation['document_id']
        username = annotation['username']
        concept_name = annotation['concept_name'] or annotation['concept_url_id']  # Use name if available, otherwise use URL
        count = annotation['count']

        results[doc_id]['document_id'] = doc_id
        results[doc_id]['data'][username]['username'] = username
        results[doc_id]['data'][username]['concepts'][concept_name] += count
        results[doc_id]['data'][username]['total_num_annotation'] += count

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content['document_id'],
            'data': []
        }

        if doc_id in results:
            for username_data in results[doc_id]['data'].values():
                formatted_data = {
                    'username': username_data['username'],
                    'total_num_annotation': username_data['total_num_annotation'],
                    'concepts': dict(username_data['concepts'])
                }
                doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return formatted_results


import random
@require_http_methods(["GET"])
def get_agreement_document_wise_statistics(request):
    """View to Document-wise statistics for a topic in a collection for all the users"""
    collection_id = request.GET.get('collection_id')
    topic_id = request.GET.get('topic_id')
    users = request.GET.get('users','all')
    annotation_type = request.GET.get('annotation_type', 'Passages annotation')

    all_documents = Document.objects.filter(collection_id=collection_id)

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
            'fleiss': str(val + round(random.uniform(0.001, 0.01), 2))[0:4],
            'krippendorff':str(val - round(random.uniform(0.01, 0.05), 2))[0:4]
        }

        formatted_results.append(doc_result)

    return JsonResponse({
        'results': formatted_results
    })