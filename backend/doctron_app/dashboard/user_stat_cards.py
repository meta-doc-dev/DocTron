from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from doctron_app.models import ShareCollection, Collection, AnnotateLabel, Document, Topic, AnnotatePassage
from doctron_app.views import topic


@require_http_methods(["GET"])
def get_user_statistic_cards(request):
    try:
        # Get request parameters
        collection_id = request.GET.get('collection_id')
        username = request.session.get('username')
        active_tab = request.GET.get('active_tab', 'individual')
        selected_topic = request.GET.get('selected_topic', None)
        name_space = request.session.get('name_space', 'Human')

        print("+="*50)
        print(f"username: {username}")
        print(f"collection_id: {collection_id}")
        print(f"active_tab: {active_tab}")
        print(f"selected_topic: {selected_topic}")
        print("+="*50)


        all_documents = Document.objects.filter(collection_id=collection_id).count()
        annotation_type = Collection.objects.filter(collection_id=collection_id).values('annotation_type__name')[0]['annotation_type__name']

        if selected_topic:
            filters = {
                'topic_id': selected_topic,
                'document_id__in': Document.objects.filter(collection_id=collection_id)
            }

            if active_tab == 'individual':
                filters['username'] = username

            # Get annotated document count
            if annotation_type == 'Graded labeling':
                annotated_documents = AnnotateLabel.objects.filter(**filters).values('document_id').distinct().count()
            elif annotation_type == 'Passages annotation':
                annotated_documents = AnnotatePassage.objects.filter(**filters).values('document_id').distinct().count()
            else:
                annotated_documents = 0

            missing_documents = all_documents - annotated_documents

            if active_tab == 'individual':
                return JsonResponse([
                    {"title": "Documents with annotations", "value": annotated_documents},
                    {"title": "Documents without annotations", "value": missing_documents}
                ], safe=False)
            elif active_tab == 'global':
                total_documents = AnnotateLabel.objects.filter(**filters).values('document_id', 'username').distinct().count()
                return JsonResponse([
                    {"title": "Documents with annotations", "value": total_documents},
                    {"title": "Documents with annotations (Unique)", "value": annotated_documents},
                    {"title": "Documents without annotations", "value": missing_documents}
                ], safe=False)
            else:
                return JsonResponse({'error': 'Invalid active tab'}, status=400)

        total_topics = Topic.objects.filter(collection_id=collection_id).count()

        filters = {
            'document_id__collection_id': collection_id
        }

        if active_tab == 'individual':
            filters['username'] = username

        # Count all the topics with at least one annotation
        annotated_topics = 0
        if annotation_type == 'Graded labeling':
            annotated_topics = AnnotateLabel.objects.filter(**filters).values('topic_id').distinct().count()
        elif annotation_type == 'Passages annotation':
            annotated_topics = AnnotatePassage.objects.filter(**filters).values('topic_id', 'document_id').distinct().count()

        if active_tab == 'individual':
            return JsonResponse([
                {"title": "Total # Topics", "value": total_topics},
                {"title": "Total # Documents", "value": all_documents},
                {"title": "Topics with ≥1 annotated document ", "value": annotated_topics}
            ], safe=False)

        total_annotators = ShareCollection.objects.filter(collection_id=collection_id).count()
        if active_tab == 'global':
            return JsonResponse([
                {"title": "Total # Topics", "value": total_topics},
                {"title": "Total # Documents", "value": all_documents},
                {"title": "Total # Annotators", "value": total_annotators},
                {"title": "Topics with ≥1 annotated document ", "value": annotated_topics}
            ], safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
