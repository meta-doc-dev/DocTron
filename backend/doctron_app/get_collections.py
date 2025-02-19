# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from .models import Collection, ShareCollection, User
from .serializers import CollectionSerializer


@api_view(['GET'])
def get_user_collections(request):
    try:
        # Get user from session
        username = request.session.get('username')
        name_space = request.session.get('name_space', "Human")

        if not username:
            return Response(
                {'error': 'User not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get user's shared collections
        # TODO: CONSIDER THE SPLIT AND OTHER ONES !
        shared_collections = ShareCollection.objects.filter(
            username=username,
            name_space=name_space
        ).select_related('collection_id')

        # Create a dictionary of share info for each collection
        share_info = {
            sc.collection_id_id: sc
            for sc in shared_collections
        }

        # Get the collections
        collections = Collection.objects.filter(
            collection_id__in=share_info.keys()
        ).order_by('name')

        # Serialize with share info context
        serializer = CollectionSerializer(
            collections,
            many=True,
            context={'share_info': share_info}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
