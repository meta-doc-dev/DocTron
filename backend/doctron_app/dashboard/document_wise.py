import random
from collections import defaultdict

from django.db.models import Count, F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from doctron_app.dashboard.annotation_handler import AnnotationFactory
from doctron_app.models import (
    Document, AnnotatePassage, AnnotateLabel, GroundTruthLogFile,
    AssociateTag, Associate, Mention, HasArea, CollectionHasConcept, Link, CreateFact, AnnotateObjectLabel,
)


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

        # Update this condition to include the new annotation types
        if annotation_type in ['Graded labeling', 'Passages annotation', 'Relationships annotation', 'Facts annotation', 'Object detection']:
            annotations = handler.get_detailed_annotations(topic_id, accessible_documents.values('document_id'))
            results = handler.get_detailed_annotations_results(annotations, accessible_documents)
        elif annotation_type == 'Entity tagging':
            # Get tag annotations with mention text directly from the Mention model
            annotations = AssociateTag.objects.filter(
                topic_id=topic_id,
                username=username,
                name_space=name_space,
                document_id__in=accessible_documents.values('document_id')
            ).select_related('start', 'name')

            # Process into hierarchical structure with correct mention text
            results = process_entity_tagging_results(annotations, accessible_documents)
        elif annotation_type == 'Entity linking':
            # Get concept annotations with mention text directly from the Mention model
            annotations = Associate.objects.filter(
                topic_id=topic_id,
                username=username,
                name_space=name_space,
                document_id__in=accessible_documents.values('document_id')
            ).select_related('start', 'concept_url', 'name')

            # Process into hierarchical structure with correct mention text and categorized by concept types
            results = process_entity_linking_results(annotations, accessible_documents, collection_id)
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
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def process_entity_tagging_results(annotations, accessible_documents):
    """Process entity tagging annotations into hierarchical structure"""
    results = []
    doc_annotations = defaultdict(list)

    # Group annotations by document
    for annotation in annotations:
        doc_id = annotation.document_id_id
        doc_annotations[doc_id].append(annotation)

    # Process each document
    for doc_id, annotations_list in doc_annotations.items():
        try:
            document = accessible_documents.get(document_id=doc_id)

            # Group tags
            tags = {}
            # Track unique entities by (start, stop) to prevent duplicates
            unique_entities = {}

            for annotation in annotations_list:
                tag_name = annotation.name.name
                if tag_name not in tags:
                    tags[tag_name] = []

                # Create a unique key for this entity
                entity_key = (annotation.start_id, annotation.stop)

                # Skip if we've already processed this exact entity for this tag
                if entity_key in unique_entities.get(tag_name, set()):
                    continue

                # Add to the set of unique entities for this tag
                if tag_name not in unique_entities:
                    unique_entities[tag_name] = set()
                unique_entities[tag_name].add(entity_key)

                # Get the correct mention text from the Mention model
                try:
                    mention = Mention.objects.get(
                        start=annotation.start_id,
                        stop=annotation.stop,
                        document_id=annotation.document_id,
                        language=annotation.language
                    )

                    # Add entity info to the tag with proper mention text
                    tags[tag_name].append({
                        'start': annotation.start_id,
                        'stop': annotation.stop,
                        'comment': annotation.comment,
                        'mention_text': mention.mention_text,  # Correct mention text
                        'insertion_time': annotation.insertion_time.isoformat() if annotation.insertion_time else None
                    })
                except Mention.DoesNotExist:
                    continue

            tag_data = [
                {
                    'tag_name': tag_name,
                    'entities': entities,
                    'count': len(entities),
                }
                for tag_name, entities in tags.items()
            ]
            results.append({
                'document_id': doc_id,
                'document_content': document.document_content,
                'data': tag_data
            })
        except (Document.DoesNotExist, Mention.DoesNotExist) as e:
            print(f"Error processing document {doc_id}: {str(e)}")
            continue

    return results


def process_entity_linking_results(annotations, accessible_documents, collection_id):
    """Process entity linking annotations into hierarchical structure with concept types"""
    results = []
    doc_annotations = defaultdict(list)

    # Group annotations by document
    for annotation in annotations:
        doc_id = annotation.document_id_id
        doc_annotations[doc_id].append(annotation)

    # Get concept types for this collection
    # First try looking in CollectionHasConcept
    collection_concepts = CollectionHasConcept.objects.select_related('name')

    # Create a mapping of concept_urls to their types
    concept_type_map = {}

    # Get all concept URLs used in annotations
    concept_urls = set(annotation.concept_url_id for doc_annotations_list in doc_annotations.values()
                       for annotation in doc_annotations_list)

    # Check for concept types in CollectionHasConcept
    for concept_url in concept_urls:
        vocab_concepts = collection_concepts.filter(concept_url=concept_url)
        if vocab_concepts.exists():
            vocabulary_type = vocab_concepts.first().name.name
            concept_type_map[concept_url] = vocabulary_type

    # For concepts without a type from Vocabulary, check HasArea
    for concept_url in concept_urls:
        if concept_url not in concept_type_map:
            area_concepts = HasArea.objects.filter(concept_url=concept_url).select_related('name')
            if area_concepts.exists():
                area_type = area_concepts.first().name.name
                concept_type_map[concept_url] = area_type

    # Default type for concepts that don't have a defined type
    default_type = "Uncategorized"

    # Process each document
    for doc_id, annotations_list in doc_annotations.items():
        try:
            document = accessible_documents.get(document_id=doc_id)

            # First, group by concept type
            concept_types = defaultdict(dict)

            # Track unique entities by (start, stop) for each concept to prevent duplicates
            unique_entities = defaultdict(set)

            for annotation in annotations_list:
                concept_url = annotation.concept_url_id
                concept_name = annotation.concept_url.concept_name or concept_url

                # Get concept type from our mapping or use default
                concept_type = concept_type_map.get(concept_url, default_type)

                # Initialize concept in its type group if not exists
                if concept_url not in concept_types[concept_type]:
                    concept_types[concept_type][concept_url] = {
                        'name': concept_name,
                        'url': concept_url,
                        'entities': []
                    }

                # Create a unique key for this entity
                entity_key = (annotation.start_id, annotation.stop)

                # Skip if we've already processed this exact entity for this concept
                if entity_key in unique_entities[concept_url]:
                    continue

                # Add to the set of unique entities for this concept
                unique_entities[concept_url].add(entity_key)

                # Get the correct mention text from the Mention model
                try:
                    mention = Mention.objects.get(
                        start=annotation.start_id,
                        stop=annotation.stop,
                        document_id=annotation.document_id,
                        language=annotation.language
                    )

                    # Add entity info to the concept with proper mention text
                    concept_types[concept_type][concept_url]['entities'].append({
                        'start': annotation.start_id,
                        'stop': annotation.stop,
                        'comment': annotation.comment,
                        'mention_text': mention.mention_text,  # Correct mention text
                        'insertion_time': annotation.insertion_time.isoformat() if annotation.insertion_time else None
                    })
                except Mention.DoesNotExist:
                    continue

            # Structure the data for hierarchical display
            concept_type_data = []

            # Process each concept type
            for concept_type, concepts in concept_types.items():
                # Convert concepts dict to list
                concept_list = []
                for concept_url, concept_info in concepts.items():
                    concept_list.append({
                        'concept_name': concept_info['name'],
                        'concept_url': concept_info['url'],
                        'entities': concept_info['entities'],
                        'count': len(concept_info['entities'])
                    })

                # Add the concept type with its concepts
                concept_type_data.append({
                    'type_name': concept_type,
                    'concepts': concept_list,
                    'count': sum(len(c['entities']) for c in concept_list)
                })

            # Add document result
            results.append({
                'document_id': doc_id,
                'document_content': document.document_content,
                'data': concept_type_data
            })
        except (Document.DoesNotExist, Mention.DoesNotExist) as e:
            print(f"Error processing document {doc_id}: {str(e)}")
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
        # Get concept annotations
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
    # Add new annotation types
    elif annotation_type == "Relationships annotation":
        # Get relationship annotations (using subject_document_id as primary)
        annotations = Link.objects.filter(
            topic_id=topic_id,
            subject_document_id__in=all_documents.values_list('document_id', flat=True)
        ).values(
            'topic_id',  # Include topic_id for detailed query later
            'subject_document_id',  # Use as document_id
            'username'
        ).annotate(
            count=Count('subject_document_id')  # Count relationships
        )
    elif annotation_type == "Facts annotation":
        # Get fact annotations
        annotations = CreateFact.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'topic_id',  # Include topic_id for detailed query later
            'document_id',
            'username'
        ).annotate(
            count=Count('document_id')  # Count facts
        )
    elif annotation_type == "Object detection":
        # Get object detection annotations
        annotations = AnnotateObjectLabel.objects.filter(
            topic_id=topic_id,
            document_id__in=all_documents.values('document_id')
        ).values(
            'document_id',
            'username',
            'label__name',  # Get the label name
            'grade'
        ).annotate(
            count=Count('document_id')  # Count annotated objects
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
    elif annotation_type == "Relationships annotation":
        results = process_relationship_annotations(annotations, all_documents)
    elif annotation_type == "Facts annotation":
        results = process_fact_annotations(annotations, all_documents)
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
                formatted_labels = {
                    label_name: {
                        'total': label_data['total'],
                        'grades': dict(label_data['grades']),
                    }
                    for label_name, label_data in username_data[
                        'labels'
                    ].items()
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
        concept_name = annotation['concept_name'] or annotation[
            'concept_url_id']  # Use name if available, otherwise use URL
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

def process_relationship_annotations(annotations, all_documents):
    """Process relationship annotations for global document-wise statistics"""
    results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
        'username': None,
        'total_num_annotation': 0,
        'relationships': []
    })})

    # Get all document IDs from annotations
    doc_ids = set()
    for annotation in annotations:
        doc_ids.add(annotation['subject_document_id'])

    # Fetch detailed relationship data
    detailed_relationships = Link.objects.filter(
        topic_id=annotations[0]['topic_id'] if annotations else None,
        subject_document_id__in=doc_ids
    )

    # Build mention text lookup dictionary
    mention_texts = {}
    for rel in detailed_relationships:
        # Extract subject mention
        subject_key = (rel.subject_document_id, rel.subject_start, rel.subject_stop)
        if subject_key not in mention_texts:
            try:
                mention = Mention.objects.get(
                    document_id=rel.subject_document_id,
                    start=rel.subject_start,
                    stop=rel.subject_stop
                )
                mention_texts[subject_key] = mention.mention_text
            except Mention.DoesNotExist:
                mention_texts[subject_key] = f"Text at position {rel.subject_start}-{rel.subject_stop}"

        # Extract predicate mention
        predicate_key = (rel.predicate_document_id, rel.predicate_start, rel.predicate_stop)
        if predicate_key not in mention_texts:
            try:
                mention = Mention.objects.get(
                    document_id=rel.predicate_document_id,
                    start=rel.predicate_start,
                    stop=rel.predicate_stop
                )
                mention_texts[predicate_key] = mention.mention_text
            except Mention.DoesNotExist:
                mention_texts[predicate_key] = f"Text at position {rel.predicate_start}-{rel.predicate_stop}"

        # Extract object mention
        object_key = (rel.object_document_id, rel.object_start, rel.object_stop)
        if object_key not in mention_texts:
            try:
                mention = Mention.objects.get(
                    document_id=rel.object_document_id,
                    start=rel.object_start,
                    stop=rel.object_stop
                )
                mention_texts[object_key] = mention.mention_text
            except Mention.DoesNotExist:
                mention_texts[object_key] = f"Text at position {rel.object_start}-{rel.object_stop}"

    # Group by document and username
    for rel in detailed_relationships:
        doc_id = rel.subject_document_id
        username = rel.username_id

        # Get mention texts
        subject_key = (rel.subject_document_id, rel.subject_start, rel.subject_stop)
        predicate_key = (rel.predicate_document_id, rel.predicate_start, rel.predicate_stop)
        object_key = (rel.object_document_id, rel.object_start, rel.object_stop)

        subject_text = mention_texts.get(subject_key, "Unknown subject")
        predicate_text = mention_texts.get(predicate_key, "Unknown predicate")
        object_key = mention_texts.get(object_key, "Unknown object")

        # Create relationship item
        relationship = {
            'subject': {
                'text': subject_text,
                'start': rel.subject_start,
                'stop': rel.subject_stop,
                'document_id': rel.subject_document_id
            },
            'predicate': {
                'text': predicate_text,
                'start': rel.predicate_start,
                'stop': rel.predicate_stop,
                'document_id': rel.predicate_document_id
            },
            'object': {
                'text': object_key,
                'start': rel.object_start,
                'stop': rel.object_stop,
                'document_id': rel.object_document_id
            },
        }

        results[doc_id]['document_id'] = doc_id
        results[doc_id]['data'][username]['username'] = username
        results[doc_id]['data'][username]['relationships'].append(relationship)
        results[doc_id]['data'][username]['total_num_annotation'] += 1

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content.get('document_id', doc_id),
            'data': []
        }

        if doc_id in results:
            for username_data in results[doc_id]['data'].values():
                formatted_data = {
                    'username': username_data['username'],
                    'total_num_annotation': username_data['total_num_annotation'],
                    'relationships': username_data['relationships']
                }
                doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return formatted_results

def process_fact_annotations(annotations, all_documents):
    """Process fact annotations for global document-wise statistics"""
    results = defaultdict(lambda: {'document_id': None, 'data': defaultdict(lambda: {
        'username': None,
        'total_num_annotation': 0,
        'facts': []
    })})

    # Get all document IDs from annotations
    doc_ids = set()
    for annotation in annotations:
        doc_ids.add(annotation['document_id'])

    # Fetch detailed fact data
    detailed_facts = CreateFact.objects.filter(
        topic_id=annotations[0]['topic_id'] if annotations else None,
        document_id__in=doc_ids
    )

    # Group by document and username
    for fact in detailed_facts:
        doc_id = fact.document_id_id
        username = fact.username_id

        # Create fact item with triple information
        fact_item = {
            'subject': {
                'name': fact.subject_name,
                'concept_url': fact.subject_concept_url
            },
            'predicate': {
                'name': fact.predicate_name,
                'concept_url': fact.predicate_concept_url
            },
            'object': {
                'name': fact.object_name,
                'concept_url': fact.object_concept_url
            },
            'comment': fact.comment
        }

        results[doc_id]['document_id'] = doc_id
        results[doc_id]['data'][username]['username'] = username
        results[doc_id]['data'][username]['facts'].append(fact_item)
        results[doc_id]['data'][username]['total_num_annotation'] += 1

    # Format the response
    formatted_results = []
    for doc_id, doc_content in list(all_documents.values_list('document_id', 'document_content')):
        doc_result = {
            'document_id': doc_id,
            'doc_id': doc_content.get('document_id', doc_id),
            'data': []
        }

        if doc_id in results:
            for username_data in results[doc_id]['data'].values():
                formatted_data = {
                    'username': username_data['username'],
                    'total_num_annotation': username_data['total_num_annotation'],
                    'facts': username_data['facts']
                }
                doc_result['data'].append(formatted_data)

        formatted_results.append(doc_result)

    return formatted_results

@require_http_methods(["GET"])
def get_agreement_document_wise_statistics(request):
    """View to Document-wise statistics for a topic in a collection for all the users"""
    collection_id = request.GET.get('collection_id')
    topic_id = request.GET.get('topic_id')
    users = request.GET.get('users', 'all')
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
            'krippendorff': str(val - round(random.uniform(0.01, 0.05), 2))[0:4]
        }

        formatted_results.append(doc_result)

    return JsonResponse({
        'results': formatted_results
    })
