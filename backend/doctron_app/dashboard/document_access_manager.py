from doctron_app.models import Split, SplitReviewer, SplitTopic


class DocumentAccessManager:
    """Manages document access based on splits and reviewer assignments"""

    def __init__(self, username, name_space, collection_id):
        self.username = username
        self.name_space = name_space
        self.collection_id = collection_id

    def get_accessible_documents(self, documents):
        """Get documents accessible to the user based on splits and reviewer status"""
        # Get user's split assignments
        split_docs = Split.objects.filter(
            username=self.username,
            name_space=self.name_space,
            collection_id=self.collection_id
        ).values_list('document_id', 'language')

        # Get reviewer assignments
        reviewer_docs = SplitReviewer.objects.filter(
            username=self.username,
            name_space=self.name_space,
            collection_id=self.collection_id
        ).values_list('document_id', 'language')

        # If user has no splits or reviewer assignments, they can access all documents
        if not split_docs.exists() and not reviewer_docs.exists():
            print("we are here")
            return documents

        # Combine split and reviewer document IDs
        accessible_docs = set(split_docs) | set(reviewer_docs)

        # Filter documents based on accessible docs
        return documents.filter(
            document_id__in=[doc_id for doc_id, _ in accessible_docs]
        )

    def get_accessible_topics(self, topics):
        """Get topics accessible to the user based on split assignments"""
        # Get user's split topic assignments
        split_topics = SplitTopic.objects.filter(
            username=self.username,
            name_space=self.name_space,
            collection_id=self.collection_id
        ).values_list('topic_id', flat=True)

        # If user has no topic splits, they can access all topics
        if not split_topics.exists():
            return topics

        # Filter topics based on split assignments
        return topics.filter(topic_id__in=split_topics)