from abc import ABC, abstractmethod
from collections import defaultdict

from bs4.diagnose import profile

from doctron_app.dashboard.document_access_manager import DocumentAccessManager
from doctron_app.models import AnnotateLabel, AnnotatePassage


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
            return labels_data, label_documents


class AnnotationFactory:
    """Factory class for creating annotation handlers"""

    _handlers = {
        'Graded labeling': GradedLabelHandler,
        'Passages annotation': PassageAnnotationHandler
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