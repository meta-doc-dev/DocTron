# views.py
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
from itertools import combinations
from django.db.models import Count
from collections import defaultdict

from doctron_app.models import AnnotateLabel, AnnotatePassage, Associate, ShareCollection

# serializers.py
from rest_framework import serializers

class KappaResultSerializer(serializers.Serializer):
    annotators = serializers.ListField(
        child=serializers.CharField()
    )
    matrix = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        )
    )
    details = serializers.DictField(
        child=serializers.ListField(
            child=serializers.DictField()
        )
    )


class CohensKappaView(APIView):
    def calculate_kappa(self, annotations_1, annotations_2):
        """
        Calculate Cohen's Kappa for two sets of annotations

        Args:
            annotations_1: Set of annotations from first annotator
            annotations_2: Set of annotations from second annotator

        Returns:
            float: Cohen's Kappa score
        """
        if not annotations_1 or not annotations_2:
            return 0.0

        # Create sets of annotations
        items_1 = set((ann['document_id'], ann['start'], ann['stop'])
                      for ann in annotations_1)
        items_2 = set((ann['document_id'], ann['start'], ann['stop'])
                      for ann in annotations_2)

        # Calculate agreement metrics
        n_total = len(items_1.union(items_2))
        n_agree = len(items_1.intersection(items_2))

        # Handle edge cases
        if n_total == 0:
            return 0.0

        # Calculate observed agreement (po)
        po = n_agree / n_total

        # Calculate expected agreement (pe)
        pe = (len(items_1) * len(items_2)) / (n_total * n_total)

        # Calculate Cohen's Kappa
        if pe == 1:
            return 1.0 if po == 1 else 0.0

        kappa = (po - pe) / (1 - pe)
        return round(kappa, 3)

    def get_annotations_by_type(self, collection_id, username, annotation_type):
        """
        Get annotations based on annotation type
        """
        if annotation_type == 'label':
            return (AnnotateLabel.objects.filter(
                username=username,
                document_id__collection_id=collection_id
            ).values('document_id', 'label', 'grade'))

        elif annotation_type == 'passage':
            return (AnnotatePassage.objects.filter(
                username=username,
                document_id__collection_id=collection_id
            ).values('document_id', 'start', 'stop', 'label'))

        elif annotation_type == 'mention':
            return (Associate.objects.filter(
                username=username,
                document_id__collection_id=collection_id
            ).values('document_id', 'start', 'stop', 'concept_url'))

        return []

    def get(self, request):
        """
        Get Cohen's Kappa matrix for all annotators in a collection

        Query Parameters:
            collection_id: ID of the collection
            annotation_type: Type of annotation ('label', 'passage', 'mention')
        """
        # create_test_user_with_random_data()
        print("Calculating Kappa")
        collection_id = request.query_params.get('collection_id')
        annotation_type = request.query_params.get('annotation_type', 'label')

        if not collection_id:
            return Response(
                {"error": "collection_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all annotators for the collection
        annotators = (ShareCollection.objects
                      .filter(collection_id=collection_id)
                      .values_list('username', flat=True)
                      .distinct())

        # Initialize results matrix
        results = {
            'annotators': list(annotators),
            'matrix': [],
            'details': defaultdict(list)
        }

        # Calculate Kappa for each pair
        for ann1 in annotators:
            row = []
            annotations_1 = self.get_annotations_by_type(
                collection_id, ann1, annotation_type
            )

            for ann2 in annotators:
                if ann1 == ann2:
                    row.append(1.0)
                    continue

                annotations_2 = self.get_annotations_by_type(
                    collection_id, ann2, annotation_type
                )

                kappa = self.calculate_kappa(annotations_1, annotations_2)
                row.append(kappa)

                # Store agreement details
                if kappa < 1.0:
                    self.store_disagreements(
                        results['details'],
                        ann1,
                        ann2,
                        annotations_1,
                        annotations_2
                    )

            results['matrix'].append(row)

        return Response(results)

    def store_disagreements(self, details, ann1, ann2, anns1, anns2):
        """Store details about disagreements between annotators"""
        key = f"{ann1}-{ann2}"
        items_1 = set((a['document_id'], a.get('start'), a.get('stop'))
                      for a in anns1)
        items_2 = set((a['document_id'], a.get('start'), a.get('stop'))
                      for a in anns2)

        # Find items annotated by only one annotator
        only_ann1 = items_1 - items_2
        only_ann2 = items_2 - items_1

        if only_ann1 or only_ann2:
            details[key].append({
                'only_annotator1': list(only_ann1),
                'only_annotator2': list(only_ann2)
            })