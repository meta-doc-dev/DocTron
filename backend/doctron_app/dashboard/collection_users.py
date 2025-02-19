
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .utils import is_collection_accessible
from doctron_app.models import ShareCollection, Collection


@require_http_methods(["GET"])
def get_collection_users(request):
    try:
        # Get request parameters
        collection_id = request.GET.get('collection_id')
        username = request.session.get('username')
        name_space = request.session.get('name_space', 'Human')

        # Validate required parameters
        if not all([collection_id, username]):
            return JsonResponse({
                'error': 'Missing required parameters: collection_id and/or username'
            }, status=400)

        try:
            if is_collection_accessible(username, collection_id, name_space):
                response = list(ShareCollection.objects.filter(
                    collection_id=collection_id
                ).values_list('username', flat=True))

                return JsonResponse(response, safe=False)

            return JsonResponse({
                'error': 'User does not have access to the collection'
            }, status=403)

        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
