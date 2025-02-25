from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import groupby
from operator import itemgetter

from bs4.diagnose import profile
from django.db.models import F

from doctron_app.dashboard.document_access_manager import DocumentAccessManager
from doctron_app.models import AnnotateLabel, AnnotatePassage, Concept, Associate, AssociateTag


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

class AnnotationFactory:
    """Factory class for creating annotation handlers"""

    _handlers = {
        'Graded labeling': GradedLabelHandler,
        'Passages annotation': PassageAnnotationHandler,
        'Entity tagging': EntityTaggingHandler,
        'Entity linking': EntityLinkingHandler
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


