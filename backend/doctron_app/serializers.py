from rest_framework import serializers
from .models import Collection, ShareCollection

class CollectionSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()
    annotation_type_name = serializers.CharField(source='annotation_type.name', read_only=True)

    class Meta:
        model = Collection
        fields = [
            'collection_id',
            'name',
            'description',
            'type',
            'modality',
            'topic_type',
            'user_role',
            'annotation_type_name'
        ]

    def get_user_role(self, obj):
        # Get the ShareCollection instance from context
        share_info = self.context.get('share_info', {}).get(obj.collection_id)
        if share_info:
            return {
                'is_admin': share_info.admin,
                'is_creator': share_info.creator,
                'is_reviewer': share_info.reviewer,
                'status': share_info.status
            }
        return None