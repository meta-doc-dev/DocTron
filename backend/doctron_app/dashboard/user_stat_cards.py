from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .utils import is_collection_accessible
from doctron_app.models import ShareCollection, Collection, AnnotateLabel, Document, Topic

from django.db.models import Avg, Count, F, Q
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@require_http_methods(["GET"])
def get_user_statistic_cards(request):
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
            # if is_collection_accessible(username, collection_id, name_space):
            #     # can see general statistics also
            #     pass

            # Get all annotations for this collection
            annotations = AnnotateLabel.objects.filter(
                document_id__collection_id=collection_id
            ).select_related('document_id', 'label')

            # 1. Label Distribution Score
            label_distribution = annotations.values('label__name').annotate(
                avg_grade=Avg('grade'),
                total_annotations=Count('label')
            ).order_by('-total_annotations')

            # 2. Inter-annotator Agreement
            # Calculate cases where multiple annotators labeled same document-label pair
            agreement_query = """
            SELECT 
                COUNT(*) as total_pairs, SUM(CASE WHEN ABS(a1.grade - a2.grade) = 0 THEN 1 ELSE 0 END) as agreed_pairs
            FROM annotate_label a1
            JOIN 
                annotate_label a2 ON 	a1.document_id = a2.document_id AND
                                        a1.label = a2.label AND
                                        a1.topic_id = a2.topic_id AND
                                        a1.username < a2.username
            WHERE a1.document_id IN (
                SELECT document_id 
                FROM document 
                WHERE collection_id = %s
            )
            """
            with connection.cursor() as cursor:
                cursor.execute(agreement_query, [collection_id])
                agreement_result = cursor.fetchone()

            agreement_score = 0
            if agreement_result[0] > 0:  # if there are any pairs
                agreement_score = (agreement_result[1] / agreement_result[0]) * 100

            # 3. Annotation Coverage
            total_topics = Topic.objects.filter(collection_id=collection_id).count()
            total_docs = Document.objects.filter(collection_id=collection_id).count() * total_topics
            labeled_docs = annotations.values('document_id', 'topic_id').distinct().count()
            coverage = (labeled_docs / total_docs  * 100) if total_docs > 0 else 0

            # return JsonResponse({
            #     'label_distribution': {
            #         'labels': [item['label__name'] for item in label_distribution],
            #         'average_grades': [float(item['avg_grade']) for item in label_distribution],
            #         'annotation_counts': [item['total_annotations'] for item in label_distribution]
            #     },
            #     'inter_annotator_agreement': {
            #         'score': agreement_score,
            #         'total_pairs': agreement_result[0],
            #         'agreed_pairs': agreement_result[1]
            #     },
            #     'coverage': {
            #         'percentage': round(coverage, 2),
            #         'labeled_documents': labeled_docs,
            #         'total_documents': total_docs
            #     }
            # })


            return JsonResponse([
                {"title": "Total # Topics", "value": total_topics},
                {"title": "Avg Grades", "value": " | ".join(
                    f'{item["label__name"]} {round(item["avg_grade"], 2)}' for item in label_distribution
                )},
                {"title": "Total Agreement", "value": f'{agreement_result[0]} pairs, {agreement_result[1]} agreed'},
                {"title": "Total Coverage %", "value": f'{round(coverage, 2)} %'}
            ], safe=False)

        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)