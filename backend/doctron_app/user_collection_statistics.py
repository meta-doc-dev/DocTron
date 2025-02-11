#
# from django.db.models import Count, Avg, Q, F, FloatField, IntegerField
# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from django.db.models.functions import Coalesce, Cast
# from collections import defaultdict
#
from doctron_app.models import *
#
#
# @require_http_methods(["GET"])
# def get_user_collection_statistics(request):
#     try:
#         collection_id = request.GET.get('collection_id')
#         username = request.session.get('username')
#         name_space = request.GET.get('name_space', 'Human')
#
#         if not all([collection_id, username, name_space]):
#             return JsonResponse({
#                 'error': 'Missing required parameters: collection_id, username, and name_space are required'
#             }, status=400)
#
#         # Get total documents assigned to user
#         total_assigned_docs = Split.objects.filter(
#             collection_id=collection_id,
#             username=username,
#             name_space=name_space
#         ).count()
#
#         # Get annotation stats
#         annotation_stats = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).aggregate(
#             total_annotations=Count('document_id'),
#             avg_grade=Coalesce(Avg('grade', output_field=FloatField()), 0.0)
#         )
#
#         # Get label-wise statistics
#         label_stats = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).values('label__name').annotate(
#             count=Count('document_id'),
#             avg_grade=Coalesce(Avg('grade', output_field=FloatField()), 0.0)
#         )
#
#         # Get topic statistics
#         topic_stats = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).values('topic_id').annotate(
#             annotations=Count('document_id')
#         )
#
#         # Get time-based statistics
#         time_stats = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).order_by('insertion_time')
#
#         first_annotation = time_stats.first()
#         last_annotation = time_stats.last()
#
#         # Get unique documents annotated
#         unique_docs_annotated = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).values('document_id').distinct().count()
#
#         # Calculate completion percentage with proper casting
#         completion_percentage = 0.0
#         if total_assigned_docs > 0:
#             completion_percentage = (Cast(unique_docs_annotated, FloatField()) /
#                                      Cast(total_assigned_docs, FloatField()) *
#                                      100.0)
#
#         # Get grade distribution
#         grade_distribution = AnnotateLabel.objects.filter(
#             username=username,
#             name_space=name_space,
#             document_id__in=Split.objects.filter(
#                 collection_id=collection_id,
#                 username=username,
#                 name_space=name_space
#             ).values('document_id')
#         ).values('grade').annotate(
#             count=Count('document_id')
#         )
#
#         print(completion_percentage)
#         print(completion_percentage)
#         print(completion_percentage)
#         print(completion_percentage)
#         print(completion_percentage)
#
#
#         # Prepare response
#         response_data = {
#             'general_stats': {
#                 'total_assigned_documents': total_assigned_docs,
#                 'documents_annotated': unique_docs_annotated,
#                 # 'completion_percentage': float(round(completion_percentage, 2)),
#                 'total_annotations': annotation_stats['total_annotations'],
#                 'average_grade': float(round(annotation_stats['avg_grade'], 2)),
#             },
#             'time_stats': {
#                 'first_annotation': first_annotation.insertion_time.isoformat() if first_annotation else None,
#                 'last_annotation': last_annotation.insertion_time.isoformat() if last_annotation else None,
#             },
#             'label_stats': {
#                 stat['label__name']: {
#                     'count': stat['count'],
#                     'average_grade': float(round(stat['avg_grade'], 2))
#                 } for stat in label_stats
#             },
#             'topic_stats': {
#                 str(stat['topic_id']): {
#                     'total_annotations': stat['annotations']
#                 } for stat in topic_stats
#             },
#             'grade_distribution': {
#                 str(grade['grade']): grade['count']
#                 for grade in grade_distribution
#             }
#         }
#
#         return JsonResponse({
#             'status': 'success',
#             'data': response_data
#         })
#
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)


from django.db.models import Count, Avg, Q, F, FloatField, IntegerField, Value
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models.functions import Coalesce, Cast, Round
from collections import defaultdict

@require_http_methods(["GET"])
def get_user_collection_statistics(request):
    try:
        collection_id = request.GET.get('collection_id')
        username = request.session.get('username')
        name_space = request.GET.get('name_space', 'Human')

        if not all([collection_id, username]):
            return JsonResponse({
                'error': 'Missing required parameters: collection_id, username, and name_space are required'
            }, status=400)

        # Get total documents assigned to user
        total_assigned_docs = Split.objects.filter(
            collection_id=collection_id,
            username=username,
            name_space=name_space
        ).count()

        # Get unique documents annotated
        unique_docs_annotated = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).values('document_id').distinct().count()

        # Calculate completion percentage
        completion_percentage = round((unique_docs_annotated * 100) / total_assigned_docs, 2) if total_assigned_docs > 0 else 0

        # Get annotation stats
        annotation_stats = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).aggregate(
            total_annotations=Count('document_id'),
            avg_grade=Coalesce(Avg('grade', output_field=FloatField()), Value(0.0))
        )

        # Get label-wise statistics
        label_stats = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).values('label__name').annotate(
            count=Count('document_id'),
            avg_grade=Round(Coalesce(Avg('grade', output_field=FloatField()), Value(0.0)), 2)
        )

        # Get topic statistics
        topic_stats = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).values('topic_id').annotate(
            annotations=Count('document_id')
        )

        # Get time-based statistics
        time_stats = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).order_by('insertion_time')

        first_annotation = time_stats.first()
        last_annotation = time_stats.last()

        # Get grade distribution
        grade_distribution = AnnotateLabel.objects.filter(
            username=username,
            name_space=name_space,
            document_id__in=Split.objects.filter(
                collection_id=collection_id,
                username=username,
                name_space=name_space
            ).values('document_id')
        ).values('grade').annotate(
            count=Count('document_id')
        )

        # Prepare response
        response_data = {
            'general_stats': {
                'total_assigned_documents': total_assigned_docs,
                'documents_annotated': unique_docs_annotated,
                'completion_percentage': completion_percentage,
                'total_annotations': annotation_stats['total_annotations'],
                'average_grade': round(annotation_stats['avg_grade'], 2),
            },
            'time_stats': {
                'first_annotation': first_annotation.insertion_time.isoformat() if first_annotation else None,
                'last_annotation': last_annotation.insertion_time.isoformat() if last_annotation else None,
            },
            'label_stats': {
                stat['label__name']: {
                    'count': stat['count'],
                    'average_grade': stat['avg_grade']
                } for stat in label_stats
            },
            'topic_stats': {
                str(stat['topic_id']): {
                    'total_annotations': stat['annotations']
                } for stat in topic_stats
            },
            'grade_distribution': {
                str(grade['grade']): grade['count']
                for grade in grade_distribution
            }
        }

        return JsonResponse({
            'status': 'success',
            'data': response_data
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)