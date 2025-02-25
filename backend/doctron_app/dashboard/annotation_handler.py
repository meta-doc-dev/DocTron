import base64
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import groupby
from operator import itemgetter

from bs4.diagnose import profile
from django.db.models import F

from doctron_app.dashboard.document_access_manager import DocumentAccessManager
from doctron_app.models import AnnotateLabel, AnnotatePassage, Concept, Associate, AssociateTag, Link, Document, \
    CreateFact, AnnotateObject, AnnotateObjectLabel


class BaseAnnotationHandler(ABC):
    """Abstract base class for annotation handlers"""

    def __init__(self, username: str, name_space: str, collection_id: str):
        self.username = username
        self.name_space = name_space
        self.collection_id = collection_id
        self.access_manager = DocumentAccessManager(username, name_space, collection_id)

    @property
    @abstractmethod
    def model(self):
        """Return the Django model class for this annotation type"""
        pass

    def get_accessible_documents(self, documents):
        """Get documents the user has access to"""
        return self.access_manager.get_accessible_documents(documents)

    def get_accessible_topics(self, topics):
        """Get topics the user has access to"""
        return self.access_manager.get_accessible_topics(topics)

    @abstractmethod
    def get_annotations(self, topic_id, documents):
        """Get annotations for given topic and documents"""
        pass

    @abstractmethod
    def get_stats(self, topic_id, collection_labels, documents, all_docs_set):
        pass

    # @abstractmethod
    # def get(self, annotations, collection_labels):
    #     """Process statistics from annotations"""
    #     pass

    def validate_grade(self, grade, label_range):
        """Validate if grade is within allowed range"""
        try:
            lower, upper = map(int, label_range.split(','))
            return lower <= grade <= upper
        except ValueError:
            return False

class GradedLabelHandler(BaseAnnotationHandler):
    """Handler for graded label annotations"""

    @property
    def model(self):
        return AnnotateLabel

    def get_annotations(self, topic_id, documents):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list('document_id', 'label', 'grade', 'comment').distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            document_id__in=accessible_document_ids
        ).values(
            'document_id',
            'grade',
            'comment',
            label_name=F('label__name'),
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        # Transform the annotations into the desired format
        results = []

        # Group by document_id
        for document_id, doc_annotations in groupby(annotations, key=itemgetter('document_id')):
            doc_annotations_list = list(doc_annotations)

            # Group passages by passage_id (start position)
            graded = []
            for graded_id, graded_annotations in groupby(doc_annotations_list, key=itemgetter('document_id')):
                graded_annotations_list = list(graded_annotations)

                # Create labels dictionary
                labels = {
                    anno['label_name']: anno['grade']
                    for anno in graded_annotations_list
                }

                graded.append({
                    # 'graded_id': document_id,
                    'labels': labels
                })

            results.append({
                'document_id': document_id,
                'document_content': accessible_documents.get(document_id=document_id).document_content,
                'data': graded
            })

        return results

    def get_stats(self, topic_id, collection_labels, documents, all_docs_set):
        labels_data = {}
        label_documents = {}

        for coll_label in collection_labels:
            label_name = coll_label.label.name

            # Get annotations with grades for this label
            annotations = self.model.objects.filter(
                topic_id=topic_id,
                username=self.username,
                name_space=self.name_space,
                label=coll_label.label,
                document_id__in=documents.values('document_id')
            ).values('document_id', 'grade', 'comment')

            # Group documents by grade
            grade_docs = defaultdict(list)
            grade_counts = defaultdict(int)

            for ann in annotations:
                grade = int(ann['grade'])  # Convert Decimal to int
                doc_id = ann['document_id']
                # doc_language = next((lang for did, lang, _ in all_docs_set if did == doc_id), None)
                extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)

                doc_info = {
                    'id': str(doc_id),
                    'title': extra_details[1],
                    'language': extra_details[0],
                    'grade': grade,  # Now an int
                    'comment': ann['comment']
                }
                grade_docs[grade].append(doc_info)
                grade_counts[grade] += 1

            if grade_counts:
                # Convert default dict to regular dict with string keys
                labels_data[label_name] = {str(k): v for k, v in dict(grade_counts).items()}
                label_documents[label_name] = {str(k): v for k, v in dict(grade_docs).items()}

        return labels_data, label_documents

class PassageAnnotationHandler(BaseAnnotationHandler):
    """Handler for passage annotations"""

    @property
    def model(self):
        return AnnotatePassage

    def get_annotations(self, topic_id: str, documents):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list('document_id', 'label', 'grade', 'comment').distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        return (
            self.model.objects
            .filter(
                topic_id=topic_id,
                username=self.username,
                document_id__in=accessible_document_ids
            )
            .select_related('start')  # Join with Mention table
            .values(
                'document_id',
                'start',
                'stop',
                'grade',
                passage_id=F('start'),  # Using start as passage_id
                actual_passage_text=F('start__mention_text'),
                label_name=F('label__name')
            )
            .order_by('document_id', 'start')
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        # Transform the annotations into the desired format
        results = []

        # Group by document_id
        for document_id, doc_annotations in groupby(annotations, key=itemgetter('document_id')):
            doc_annotations_list = list(doc_annotations)

            # Group passages by passage_id (start position)
            passages = []
            for passage_id, passage_annotations in groupby(doc_annotations_list, key=itemgetter('passage_id')):
                passage_annotations_list = list(passage_annotations)

                # Create labels dictionary
                labels = {
                    anno['label_name']: anno['grade']
                    for anno in passage_annotations_list
                }

                passages.append({
                    'passage_id': passage_id,
                    'actual_passage_text': passage_annotations_list[0]['actual_passage_text'],
                    'labels': labels
                })

            results.append({
                'document_id': document_id,
                'document_content': accessible_documents.get(document_id=document_id).document_content,
                'data': passages
            })

        return results

    def get_stats(self, topic_id, collection_labels, documents, all_docs_set):
        labels_data = {}
        label_documents = {}

        for coll_label in collection_labels:
            label_name = coll_label.label.name

            # Get annotations with grades for this label
            annotations = self.model.objects.filter(
                topic_id=topic_id,
                username=self.username,
                name_space=self.name_space,
                label=coll_label.label,
                document_id__in=documents.values('document_id')
            ).values('document_id', 'grade', 'comment')

            # Group documents by grade
            grade_docs = defaultdict(list)
            grade_counts = defaultdict(int)

            for ann in annotations:
                grade = int(ann['grade'])  # Convert Decimal to int
                doc_id = ann['document_id']
                extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)

                doc_info = {
                    'id': str(doc_id),
                    'title': extra_details[1],
                    'language': extra_details[0],
                    'grade': grade,  # Now an int
                    'comment': ann['comment']
                }
                grade_docs[grade].append(doc_info)
                grade_counts[grade] += 1

            if grade_counts:
                # Convert default dict to regular dict with string keys
                labels_data[label_name] = {str(k): v for k, v in dict(grade_counts).items()}
                label_documents[label_name] = {str(k): v for k, v in dict(grade_docs).items()}
            return labels_data, label_documents

class EntityTaggingHandler(BaseAnnotationHandler):
    """Handler for entity tagging annotations"""

    @property
    def model(self):
        return AssociateTag

    def get_annotations(self, topic_id, documents):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list('document_id', 'name', 'start', 'comment').distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            document_id__in=accessible_document_ids
        ).select_related('name').values(
            'document_id',
            'start',
            'stop',
            'comment',
            tag_name=F('name__name'),
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        results = []

        # Group by document_id
        for document_id, doc_annotations in groupby(annotations, key=itemgetter('document_id')):
            doc_annotations_list = list(doc_annotations)

            # Group by start position (entity mentions)
            entities = []
            for start, entity_annotations in groupby(doc_annotations_list, key=itemgetter('start')):
                entity_annotations_list = list(entity_annotations)

                # Create tags dictionary
                tags = {
                    anno['tag_name']: 1  # Using 1 to indicate presence
                    for anno in entity_annotations_list
                }

                entities.append({
                    'entity_id': start,
                    'start': entity_annotations_list[0]['start'],
                    'stop': entity_annotations_list[0]['stop'],
                    'tags': tags
                })

            results.append({
                'document_id': document_id,
                'document_content': accessible_documents.get(document_id=document_id).document_content,
                'data': entities
            })

        return results

    def get_stats(self, topic_id, collection_tags, documents, all_docs_set):
        tags_data = {}
        tag_documents = {}

        for coll_tag in collection_tags:
            tag_name = coll_tag.name.name

            # Get annotations with this tag
            annotations = self.model.objects.filter(
                topic_id=topic_id,
                username=self.username,
                name_space=self.name_space,
                name=coll_tag.name,
                document_id__in=documents.values('document_id')
            ).values('document_id', 'comment')

            # Count documents with this tag
            doc_count = annotations.count()

            if doc_count > 0:
                # Store document details
                doc_info = []
                for ann in annotations:
                    doc_id = ann['document_id']
                    extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)

                    if extra_details:
                        doc_info.append({
                            'id': str(doc_id),
                            'title': extra_details[1],
                            'language': extra_details[0],
                            'comment': ann['comment'] if ann['comment'] else ""
                        })

                tags_data[tag_name] = {"1": doc_count}  # Using "1" to match existing format
                tag_documents[tag_name] = {"1": doc_info}

        return tags_data, tag_documents


class EntityLinkingHandler(BaseAnnotationHandler):
    """Handler for entity linking annotations"""

    @property
    def model(self):
        return Associate

    def get_annotations(self, topic_id, documents):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list('document_id', 'concept_url', 'start', 'comment').distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            document_id__in=accessible_document_ids
        ).select_related('concept_url').values(
            'document_id',
            'start',
            'stop',
            'comment',
            concept_name=F('concept_url__concept_name'),
            concept_url=F('concept_url__concept_url'),
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        results = []

        # Group by document_id
        for document_id, doc_annotations in groupby(annotations, key=itemgetter('document_id')):
            doc_annotations_list = list(doc_annotations)

            # Group by start position (entity mentions)
            entities = []
            for start, entity_annotations in groupby(doc_annotations_list, key=itemgetter('start')):
                entity_annotations_list = list(entity_annotations)

                # Create concepts dictionary
                concepts = {
                    anno['concept_name'] or anno['concept_url']: anno['concept_url']
                    for anno in entity_annotations_list
                }

                entities.append({
                    'entity_id': start,
                    'start': entity_annotations_list[0]['start'],
                    'stop': entity_annotations_list[0]['stop'],
                    'concepts': concepts
                })

            results.append({
                'document_id': document_id,
                'document_content': accessible_documents.get(document_id=document_id).document_content,
                'data': entities
            })

        return results

    def get_stats(self, topic_id, collection_items, documents, all_docs_set):
        concepts_data = {}
        concept_documents = {}

        # Get all concepts used in annotations for this topic
        concept_ids = self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list('concept_url', flat=True).distinct()

        for concept_id in concept_ids:
            try:
                concept = Concept.objects.get(concept_url=concept_id)
                concept_name = concept.concept_name or concept.concept_url

                # Get annotations with this concept
                annotations = self.model.objects.filter(
                    topic_id=topic_id,
                    username=self.username,
                    name_space=self.name_space,
                    concept_url=concept_id,
                    document_id__in=documents.values('document_id')
                ).values('document_id', 'comment')

                # Count documents with this concept
                doc_count = annotations.count()

                if doc_count > 0:
                    # Store document details
                    doc_info = []
                    for ann in annotations:
                        doc_id = ann['document_id']
                        extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)

                        if extra_details:
                            doc_info.append({
                                'id': str(doc_id),
                                'title': extra_details[1],
                                'language': extra_details[0],
                                'comment': ann['comment'] if ann['comment'] else ""
                            })

                    concepts_data[concept_name] = {"1": doc_count}  # Using "1" to match existing format
                    concept_documents[concept_name] = {"1": doc_info}
            except Concept.DoesNotExist:
                continue

        return concepts_data, concept_documents


class RelationshipsAnnotationHandler(BaseAnnotationHandler):
    """Handler for relationships annotations"""

    @property
    def model(self):
        return Link

    def get_annotations(self, topic_id, documents):
        """Get relationship annotations for given topic and documents"""
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            subject_document_id__in=documents.values_list('document_id', flat=True)
        ).values_list(
            'subject_document_id',
            'predicate_document_id',
            'object_document_id',
            'insertion_time'
        ).distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        """Get detailed relationship annotations for document-wise display"""
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            subject_document_id__in=accessible_document_ids
        ).values(
            'subject_document_id',
            'subject_start',
            'subject_stop',
            'subject_language',
            'predicate_document_id',
            'predicate_start',
            'predicate_stop',
            'predicate_language',
            'object_document_id',
            'object_start',
            'object_stop',
            'object_language',
            'insertion_time'
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        """Process relationship annotations for display"""
        # Transform the annotations into the desired format
        results = []

        # Group by document_id (using subject document as primary)
        doc_annotations = {}
        for annotation in annotations:
            doc_id = annotation['subject_document_id']
            if doc_id not in doc_annotations:
                doc_annotations[doc_id] = []
            doc_annotations[doc_id].append(annotation)

        # Format each document's annotations
        for doc_id, annotations_list in doc_annotations.items():
            try:
                document = accessible_documents.get(document_id=doc_id)

                # Process relationships for this document
                relationships = []
                for rel in annotations_list:
                    # Get mention texts if needed here

                    relationships.append({
                        'subject': {
                            'document_id': rel['subject_document_id'],
                            'start': rel['subject_start'],
                            'stop': rel['subject_stop'],
                            'language': rel['subject_language']
                        },
                        'predicate': {
                            'document_id': rel['predicate_document_id'],
                            'start': rel['predicate_start'],
                            'stop': rel['predicate_stop'],
                            'language': rel['predicate_language']
                        },
                        'object': {
                            'document_id': rel['object_document_id'],
                            'start': rel['object_start'],
                            'stop': rel['object_stop'],
                            'language': rel['object_language']
                        },
                        'insertion_time': rel['insertion_time'].isoformat() if rel['insertion_time'] else None
                    })

                results.append({
                    'document_id': doc_id,
                    'document_content': document.document_content,
                    'data': [{
                        'relationship_type': 'links',
                        'count': len(relationships),
                        'relationships': relationships
                    }]
                })
            except Document.DoesNotExist:
                continue

        return results

    def get_stats(self, topic_id, collection_items, documents, all_docs_set):
        """Get statistics for relationship annotations"""
        # Count relationships by document
        relationships_data = {}
        relationship_documents = {}

        # Get relationship annotations for this topic
        annotations = self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            subject_document_id__in=documents.values_list('document_id', flat=True)
        ).values('subject_document_id')

        # Count by document (using subject document as reference)
        doc_counts = {}
        doc_details = defaultdict(list)

        for annotation in annotations:
            doc_id = annotation['subject_document_id']
            if doc_id not in doc_counts:
                doc_counts[doc_id] = 0
            doc_counts[doc_id] += 1

            # Find document details in all_docs_set
            extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)
            if extra_details:
                doc_info = {
                    'id': str(doc_id),
                    'title': extra_details[1],
                    'language': extra_details[0]
                }
                doc_details[doc_id].append(doc_info)

        # Only include relationships data if we have annotations
        if doc_counts:
            # Count total relationships
            total_relationships = sum(doc_counts.values())
            relationships_data['relationships'] = {'1': total_relationships}  # Using '1' to follow existing pattern

            # Group documents by relationship count
            docs_by_count = defaultdict(list)
            for doc_id, count in doc_counts.items():
                for doc_info in doc_details[doc_id]:
                    docs_by_count[count].append(doc_info)

            # Convert to format expected by frontend
            relationship_documents['relationships'] = {'1': [doc for docs in docs_by_count.values() for doc in docs]}

        return relationships_data, relationship_documents

class FactsAnnotationHandler(BaseAnnotationHandler):
    """Handler for facts annotations"""

    @property
    def model(self):
        return CreateFact

    def get_annotations(self, topic_id, documents):
        """Get fact annotations for given topic and documents"""
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list(
            'document_id',
            'predicate_concept_url',
            'subject_concept_url',
            'object_concept_url',
            'comment'
        ).distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        """Get detailed fact annotations for document-wise display"""
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=accessible_document_ids
        ).values(
            'document_id',
            'subject_name',
            'subject_concept_url',
            'predicate_name',
            'predicate_concept_url',
            'object_name',
            'object_concept_url',
            'language',
            'comment',
            'insertion_time'
        )

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        """Process fact annotations for display"""
        # Transform the annotations into the desired format
        results = []

        # Group by document_id
        doc_annotations = {}
        for annotation in annotations:
            doc_id = annotation['document_id']
            if doc_id not in doc_annotations:
                doc_annotations[doc_id] = []
            doc_annotations[doc_id].append(annotation)

        # Format each document's annotations
        for doc_id, annotations_list in doc_annotations.items():
            try:
                document = accessible_documents.get(document_id=doc_id)

                # Process facts for this document
                facts = []
                for fact in annotations_list:
                    facts.append({
                        'subject': {
                            'name': fact['subject_name'],
                            'concept_url': fact['subject_concept_url']
                        },
                        'predicate': {
                            'name': fact['predicate_name'],
                            'concept_url': fact['predicate_concept_url']
                        },
                        'object': {
                            'name': fact['object_name'],
                            'concept_url': fact['object_concept_url']
                        },
                        'comment': fact['comment'],
                        'language': fact['language'],
                        'insertion_time': fact['insertion_time'].isoformat() if fact['insertion_time'] else None
                    })

                results.append({
                    'document_id': doc_id,
                    'document_content': document.document_content,
                    'data': [{
                        'fact_type': 'facts',
                        'count': len(facts),
                        'facts': facts
                    }]
                })
            except Document.DoesNotExist:
                continue

        return results

    def get_stats(self, topic_id, collection_items, documents, all_docs_set):
        """Get statistics for fact annotations"""
        # Count facts by document
        facts_data = {}
        fact_documents = {}

        # Get fact annotations for this topic
        annotations = self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values('document_id', 'comment', 'language')

        # Count by document
        doc_counts = {}
        doc_details = defaultdict(list)

        for annotation in annotations:
            doc_id = annotation['document_id']
            if doc_id not in doc_counts:
                doc_counts[doc_id] = 0
            doc_counts[doc_id] += 1

            # Find document details in all_docs_set
            extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)
            if extra_details:
                doc_info = {
                    'id': str(doc_id),
                    'title': extra_details[1],
                    'language': extra_details[0],
                    'comment': annotation['comment']
                }
                doc_details[doc_id].append(doc_info)

        # Only include facts data if we have annotations
        if doc_counts:
            # Count total facts
            total_facts = sum(doc_counts.values())
            facts_data['facts'] = {'1': total_facts}  # Using '1' to follow existing pattern

            # Group documents by fact count
            docs_by_count = defaultdict(list)
            for doc_id, count in doc_counts.items():
                for doc_info in doc_details[doc_id]:
                    docs_by_count[count].append(doc_info)

            # Convert to format expected by frontend
            fact_documents['facts'] = {'1': [doc for docs in docs_by_count.values() for doc in docs]}

        return facts_data, fact_documents

class ObjectDetectionHandler(BaseAnnotationHandler):
    """Handler for object detection annotations"""

    @property
    def model(self):
        return AnnotateObject  # Base model for object detection

    def get_annotations(self, topic_id, documents):
        """Get object detection annotations for given topic and documents"""
        return self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=documents.values('document_id')
        ).values_list(
            'document_id',
            'points',
            'comment'
        ).distinct()

    def get_detailed_annotations(self, topic_id, accessible_document_ids):
        """Get detailed object detection annotations for document-wise display"""
        # First get base object annotations
        base_annotations = self.model.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=accessible_document_ids
        ).values(
            'document_id',
            'points',
            'comment',
            'language',
            'insertion_time'
        )

        # Also fetch label annotations for these objects
        label_annotations = AnnotateObjectLabel.objects.filter(
            topic_id=topic_id,
            username=self.username,
            name_space=self.name_space,
            document_id__in=accessible_document_ids
        ).values(
            'document_id',
            'points',
            'grade',
            'comment',
            'label__name'
        )

        # Return both types of annotations for processing
        return {
            'objects': list(base_annotations),
            'labels': list(label_annotations)
        }

    def get_detailed_annotations_results(self, annotations, accessible_documents):
        """Process object detection annotations for display"""
        # Transform the annotations into the desired format
        results = []

        # Extract the two types of annotations
        base_annotations = annotations.get('objects', [])
        label_annotations = annotations.get('labels', [])

        # Build a mapping of document_id -> points -> labels
        label_mapping = defaultdict(lambda: defaultdict(list))
        for label_anno in label_annotations:
            doc_id = label_anno['document_id']
            points = label_anno['points']
            label_mapping[doc_id][points].append({
                'label': label_anno['label__name'],
                'grade': label_anno['grade'],
                'comment': label_anno['comment']
            })

        # Group base annotations by document_id
        doc_annotations = {}
        for annotation in base_annotations:
            doc_id = annotation['document_id']
            if doc_id not in doc_annotations:
                doc_annotations[doc_id] = []
            doc_annotations[doc_id].append(annotation)

        # Format each document's annotations
        for doc_id, annotations_list in doc_annotations.items():
            try:
                document = accessible_documents.get(document_id=doc_id)

                # Process objects for this document
                objects = []
                for obj in annotations_list:
                    points = obj['points']
                    # Get any labels associated with this object
                    object_labels = label_mapping[doc_id][points]

                    objects.append({
                        'points': points,  # Coordinates/points defining the object
                        'comment': obj['comment'],
                        'labels': object_labels,
                        'insertion_time': obj['insertion_time'].isoformat() if obj['insertion_time'] else None
                    })

                results.append({
                    'document_id': doc_id,
                    'document_content': {
                        **document.document_content,
                        'doc_image': base64.b64encode(document.image).decode('utf-8'),
                    },
                    'data': [{
                        'object_type': 'detected_objects',
                        'count': len(objects),
                        'objects': objects
                    }]
                })
            except Document.DoesNotExist:
                continue

        return results

    def get_stats(self, topic_id, collection_labels, documents, all_docs_set):
        """Get statistics for object detection annotations"""
        objects_data = {}
        object_documents = {}

        # Count objects and their labels
        for coll_label in collection_labels:
            label_name = coll_label.label.name

            # Get annotations with this label
            label_annotations = AnnotateObjectLabel.objects.filter(
                topic_id=topic_id,
                username=self.username,
                name_space=self.name_space,
                label=coll_label.label,
                document_id__in=documents.values('document_id')
            ).values('document_id', 'grade', 'comment')

            # Group documents by grade
            grade_docs = defaultdict(list)
            grade_counts = defaultdict(int)

            for ann in label_annotations:
                grade = int(ann['grade'])  # Convert Decimal to int
                doc_id = ann['document_id']
                extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)

                doc_info = {
                    'id': str(doc_id),
                    'title': extra_details[1] if extra_details else str(doc_id),
                    'language': extra_details[0] if extra_details else '',
                    'grade': grade,
                    'comment': ann['comment']
                }
                grade_docs[grade].append(doc_info)
                grade_counts[grade] += 1

            if grade_counts:
                # Convert default dict to regular dict with string keys
                objects_data[label_name] = {str(k): v for k, v in dict(grade_counts).items()}
                object_documents[label_name] = {str(k): v for k, v in dict(grade_docs).items()}

        # If no labels found, also count total objects
        if not objects_data:
            # Count total objects without labels
            all_objects = self.model.objects.filter(
                topic_id=topic_id,
                username=self.username,
                name_space=self.name_space,
                document_id__in=documents.values('document_id')
            ).values('document_id', 'comment')

            doc_counts = {}
            doc_details = defaultdict(list)

            for obj in all_objects:
                doc_id = obj['document_id']
                if doc_id not in doc_counts:
                    doc_counts[doc_id] = 0
                doc_counts[doc_id] += 1

                extra_details = next(((lang, document_id) for did, lang, document_id in all_docs_set if did == doc_id), None)
                if extra_details:
                    doc_info = {
                        'id': str(doc_id),
                        'title': extra_details[1],
                        'language': extra_details[0],
                        'comment': obj['comment']
                    }
                    doc_details[doc_id].append(doc_info)

            if doc_counts:
                total_objects = sum(doc_counts.values())
                objects_data['objects'] = {'1': total_objects}
                object_documents['objects'] = {'1': [doc for docs in doc_details.values() for doc in docs]}

        return objects_data, object_documents


class AnnotationFactory:
    """Factory class for creating annotation handlers"""

    _handlers = {
        'Graded labeling': GradedLabelHandler,
        'Passages annotation': PassageAnnotationHandler,
        'Entity tagging': EntityTaggingHandler,
        'Entity linking': EntityLinkingHandler,
        'Relationships annotation': RelationshipsAnnotationHandler,
        'Facts annotation': FactsAnnotationHandler,
        'Object detection': ObjectDetectionHandler
    }

    @classmethod
    def get_handler(cls, annotation_type, username, name_space, collection_id):
        """Get appropriate handler for annotation type"""
        handler_class = cls._handlers.get(annotation_type)
        if not handler_class:
            raise ValueError(f"Unsupported annotation type: {annotation_type}")
        return handler_class(username, name_space, collection_id)

    @classmethod
    def register_handler(cls, annotation_type, handler_class):
        """Register a new handler type"""
        if not issubclass(handler_class, BaseAnnotationHandler):
            raise ValueError("Handler must inherit from BaseAnnotationHandler")
        cls._handlers[annotation_type] = handler_class


