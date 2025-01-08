
from doctron_app.models import *
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
import hashlib
from django.contrib.postgres.aggregates import ArrayAgg
from itertools import chain
from doctron_app.upload.utils_pubmed import *
from doctron_app.upload.configure import *
from collections import Counter
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, timezone
from django.db import connection
import json
import os
from doctron_app.models import *
from django.http import HttpResponse

def compute_relationship_area_global(distinct_areas,documents,docs,name_space,users):

    json_doc = {}
    json_doc['subject'] = {}
    json_doc['predicate'] = {}
    json_doc['object'] = {}
    json_doc['global'] = {}
    for area in distinct_areas:



        global_list = []
        subject_list = []
        object_list = []
        predicate_list = []


        json_doc['global'][area] = {}
        json_doc['subject'][area] = {}
        json_doc['predicate'][area] = {}
        json_doc['object'][area] = {}
        json_doc['global'][area]['count'] = 0
        json_doc['subject'][area]['count'] = 0
        json_doc['predicate'][area]['count'] = 0
        json_doc['object'][area]['count'] = 0
        area_obj = SemanticArea.objects.get(name=area)

        # links = Link.objects.filter(subject_document_id__in=docs, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += links.count()
        # #
        # facts = CreateFact.objects.filter(document_id__in=documents, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += facts.count()
        # #
        # rels1 = RelationshipSubjMention.objects.filter(document_id__in=documents, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels1.count()
        # #
        # rels2 = RelationshipObjMention.objects.filter(document_id__in=documents, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels2.count()
        # #
        # rels3 = RelationshipPredMention.objects.filter(document_id__in=documents, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels3.count()
        #
        # rels4 = RelationshipSubjConcept.objects.filter(object_document_id__in=docs, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels4.count()
        #
        # rels5 = RelationshipObjConcept.objects.filter(subject_document_id__in=docs, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels5.count()
        #
        # rels6 = RelationshipPredConcept.objects.filter(subject_document_id__in=docs, name_space=name_space,username__in = users)
        # json_doc['global'][area]['count'] += rels6.count()

        # link e simili

        links_00 = Link.objects.filter(subject_document_id__in=docs,username__in = users).values('subject_start','subject_stop','predicate_start','predicate_stop',
                                                                         'object_start','object_stop','username')
        links_0 = RelationshipPredConcept.objects.filter(subject_document_id__in=docs,username__in = users).values('subject_start', 'subject_stop',

                                                                         'object_start', 'object_stop', 'username')
        links_1 = RelationshipObjConcept.objects.filter(subject_document_id__in=docs,username__in = users).values('subject_start', 'subject_stop',
                                                                         'predicate_start', 'predicate_stop',
                                                                          'username')
        links_2 = RelationshipSubjConcept.objects.filter(object_document_id__in=docs,username__in = users).values(
                                                                         'predicate_start', 'predicate_stop',
                                                                         'object_start', 'object_stop', 'username')
        links_3 = RelationshipPredMention.objects.filter(document_id__in=documents,username__in = users).values('start','stop', 'username')
        links_4 = RelationshipObjMention.objects.filter(document_id__in=documents,username__in = users).values('start','stop', 'username')
        links_5 = RelationshipSubjMention.objects.filter(document_id__in=documents,username__in = users).values('start','stop', 'username')

        links = list(chain(links_00,links_0,links_1,links_2,links_3,links_4,links_5))

        links_sub = list(chain(links_00,links_0,links_1))
        links_ob = list(chain(links_00,links_0,links_2))
        links_pred = list(chain(links_00,links_1,links_2))

        users_0 = [e['username'] for e in links]
        users_0 = User.objects.filter(username__in = users_0)

        links_subject = [(e['subject_start'],e['subject_stop']) for e in links_sub]
        links_subject += [(e['start'],e['stop']) for e in links_5]
        links_object = [(e['object_start'],e['object_stop']) for e in links_ob]
        links_object += [(e['start'],e['stop']) for e in links_4]
        links_predicate = [(e['predicate_start'],e['predicate_stop']) for e in links_pred]
        links_predicate += [(e['start'], e['stop']) for e in links_3]

        ass_list_area = Associate.objects.filter(document_id__in = documents,name = area_obj,username__in = users_0).values(
            'start','stop').annotate(agg_name=ArrayAgg('concept_url')).order_by('start','stop')

        for el in links_subject:
            for concepts_list in ass_list_area:
                if (concepts_list['start'], concepts_list['stop']) == el:
                    subject_list += concepts_list['agg_name']
                    break

        for el in links_object:
            for concepts_list in ass_list_area:
                if (concepts_list['start'], concepts_list['stop']) == el:
                    object_list += concepts_list['agg_name']
                    break

        for el in links_predicate:
            for concepts_list in ass_list_area:
                if (concepts_list['start'], concepts_list['stop']) == el:
                    predicate_list += concepts_list['agg_name']
                    break

        global_list += subject_list
        global_list += object_list
        global_list += predicate_list

        # # create fact
        facts_subject = CreateFact.objects.filter(document_id__in=documents,username__in = users).values(
            'subject_name').annotate(agg_name=ArrayAgg('subject_concept_url')).order_by('subject_name')

        links_subject_concepts = [item for concepts_list in facts_subject for item in concepts_list['agg_name']]
        global_list += links_subject_concepts
        subject_list += links_subject_concepts

        facts_object = CreateFact.objects.filter(document_id__in=documents,username__in = users).values(
            'object_name').annotate(agg_name=ArrayAgg('object_concept_url')).order_by('object_name')

        links_object_concepts = [item for concepts_list in facts_object for item in concepts_list['agg_name']]
        global_list += links_object_concepts
        object_list += links_object_concepts

        facts_predicate = CreateFact.objects.filter(document_id__in=documents,username__in = users).values(
            'predicate_name').annotate(agg_name=ArrayAgg('predicate_concept_url')).order_by('predicate_name')

        links_predicate_concepts = [item for concepts_list in facts_predicate for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        predicate_list += links_predicate_concepts


        # pred concept
        pred_con_subj = RelationshipPredConcept.objects.filter(subject_document_id__in=docs,username__in = users).values(
            'name').annotate(agg_name=ArrayAgg('concept_url')).order_by('name')
        links_predicate_concepts = [item for concepts_list in pred_con_subj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        predicate_list += links_predicate_concepts

        # subj concept
        subj_con_subj = RelationshipSubjConcept.objects.filter(object_document_id__in=docs,username__in = users).values(
            'name').annotate(agg_name=ArrayAgg('concept_url')).order_by('name')
        links_subject_concepts = [item for concepts_list in subj_con_subj for item in concepts_list['agg_name']]
        global_list += links_subject_concepts
        subject_list += links_subject_concepts

        # obj concept
        obj_con_subj = RelationshipObjConcept.objects.filter(subject_document_id__in=docs,username__in = users).values(
            'name').annotate(agg_name=ArrayAgg('concept_url')).order_by('name')
        links_object_concepts = [item for concepts_list in obj_con_subj for item in concepts_list['agg_name']]
        global_list += links_object_concepts
        object_list += links_object_concepts


        # pred concept
        subj = RelationshipPredMention.objects.filter(document_id__in=documents,username__in = users).values(
            'subject_name').annotate(agg_name=ArrayAgg('subject_concept_url')).order_by('subject_name')
        links_predicate_concepts = [item for concepts_list in subj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        subject_list += links_predicate_concepts

        obj = RelationshipPredMention.objects.filter(document_id__in=documents,username__in = users).values(
            'object_name').annotate(agg_name=ArrayAgg('object_concept_url')).order_by('object_name')
        links_predicate_concepts = [item for concepts_list in obj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        object_list += links_predicate_concepts

        # subj concept
        subj = RelationshipSubjMention.objects.filter(document_id__in=documents,username__in = users).values(
            'predicate_name').annotate(agg_name=ArrayAgg('predicate_concept_url')).order_by('predicate_name')
        links_predicate_concepts = [item for concepts_list in subj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        predicate_list += links_predicate_concepts

        obj = RelationshipSubjMention.objects.filter(document_id__in=documents,username__in = users).values(
            'object_name').annotate(agg_name=ArrayAgg('object_concept_url')).order_by('object_name')
        links_predicate_concepts = [item for concepts_list in obj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        object_list += links_predicate_concepts

        # obj concept
        subj = RelationshipObjMention.objects.filter(document_id__in=documents,username__in = users).values(
            'predicate_name').annotate(agg_name=ArrayAgg('predicate_concept_url')).order_by('predicate_name')
        links_predicate_concepts = [item for concepts_list in subj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        predicate_list += links_predicate_concepts

        obj = RelationshipObjMention.objects.filter(document_id__in=documents,username__in = users).values(
            'subject_name').annotate(agg_name=ArrayAgg('subject_concept_url')).order_by('subject_name')
        links_predicate_concepts = [item for concepts_list in obj for item in concepts_list['agg_name']]
        global_list += links_predicate_concepts
        subject_list += links_predicate_concepts

        global_list = Counter(global_list)
        subject_list = Counter(subject_list)
        predicate_list = Counter(predicate_list)
        object_list = Counter(object_list)

        json_doc['global'][area] = {map_keys(str(key)): value for key, value in global_list.items()}
        json_doc['subject'][area] = {map_keys(str(key)): value for key, value in subject_list.items()}
        json_doc['predicate'][area] ={map_keys(str(key)): value for key, value in predicate_list.items()}
        json_doc['object'][area] ={map_keys(str(key)): value for key, value in object_list.items()}


        json_doc['global'][area]['count'] = len(global_list)
        json_doc['subject'][area]['count'] = len(subject_list)
        json_doc['predicate'][area]['count'] = len(predicate_list)
        json_doc['object'][area]['count'] = len(subject_list)
    return json_doc



def map_keys(key):

    concept = Concept.objects.filter(concept_url = key)
    if concept.exists():
        return concept.first().concept_name
    return 'unknown_key'

def compute_relationship_area_global_old(distinct_areas,documents,docs,name_space):

    json_doc = {}
    json_doc['subject'] = {}
    json_doc['predicate'] = {}
    json_doc['object'] = {}
    json_doc['global'] = {}
    for area in distinct_areas:

        global_list = []
        subject_list = []
        object_list = []
        predicate_list = []


        json_doc['global'][area] = {}
        json_doc['subject'][area] = {}
        json_doc['predicate'][area] = {}
        json_doc['object'][area] = {}
        json_doc['global'][area]['count'] = 0
        json_doc['subject'][area]['count'] = 0
        json_doc['predicate'][area]['count'] = 0
        json_doc['object'][area]['count'] = 0
        area_obj = SemanticArea.objects.get(name=area)

        # links = Link.objects.filter(subject_document_id__in=docs, name_space=name_space)
        # json_doc['global'][area]['count'] += links.count()
        # #
        # facts = CreateFact.objects.filter(document_id__in=documents, name_space=name_space)
        # json_doc['global'][area]['count'] += facts.count()
        # #
        # rels1 = RelationshipSubjMention.objects.filter(document_id__in=documents, name_space=name_space)
        # json_doc['global'][area]['count'] += rels1.count()
        # #
        # rels2 = RelationshipObjMention.objects.filter(document_id__in=documents, name_space=name_space)
        # json_doc['global'][area]['count'] += rels2.count()
        # #
        # rels3 = RelationshipPredMention.objects.filter(document_id__in=documents, name_space=name_space)
        # json_doc['global'][area]['count'] += rels3.count()
        #
        # rels4 = RelationshipSubjConcept.objects.filter(object_document_id__in=docs, name_space=name_space)
        # json_doc['global'][area]['count'] += rels4.count()
        #
        # rels5 = RelationshipObjConcept.objects.filter(subject_document_id__in=docs, name_space=name_space)
        # json_doc['global'][area]['count'] += rels5.count()
        #
        # rels6 = RelationshipPredConcept.objects.filter(subject_document_id__in=docs, name_space=name_space)
        # json_doc['global'][area]['count'] += rels6.count()
        # #
        # links_subject = Link.objects.filter(subject_document_id__in=docs).values(
        #     'subject_name').annotate(agg_name=ArrayAgg('subject_concept_url')).order_by('subject_name')
        # #
        # links_subject_concepts = [item for concepts_list in links_subject for item in concepts_list.agg_name]
        # global_list += links_subject_concepts
        # subject_list += links_subject_concepts
        # #
        # links_object = Link.objects.filter(subject_document_id__in=docs).values(
        #     'object_name').annotate(agg_name=ArrayAgg('object_concept_url')).order_by('object_name')
        # #
        # links_object_concepts = [item for concepts_list in links_object for item in concepts_list.agg_name]
        # global_list += links_object_concepts
        # object_list += links_object_concepts
        # #
        # links_predicate = Link.objects.filter(subject_document_id__in=docs).values(
        #     'predicate_name').annotate(agg_name=ArrayAgg('predicate_concept_url')).order_by('predicate_name')
        #
        # links_predicate_concepts = [item for concepts_list in links_predicate for item in concepts_list.agg_name]
        # global_list += links_predicate_concepts
        # predicate_list += links_predicate_concepts
        # #
        # # # create fact
        # facts_subject = CreateFact.objects.filter(document_id__in=documents).values(
        #     'subject_name').annotate(agg_name=ArrayAgg('subject_concept_url')).order_by('subject_name')
        #
        # links_subject_concepts = [item for concepts_list in links_subject for item in concepts_list.agg_name]
        # global_list += links_subject_concepts
        # subject_list += links_subject_concepts
        #
        # facts_object = CreateFact.objects.filter(document_id__in=documents).values(
        #     'object_name').annotate(agg_name=ArrayAgg('object_concept_url')).order_by('object_name')
        #
        # links_object_concepts = [item for concepts_list in links_object for item in concepts_list.agg_name]
        # global_list += links_object_concepts
        # object_list += links_object_concepts
        #
        # facts_predicate = CreateFact.objects.filter(document_id__in=documents).values(
        #     'predicate_name').annotate(agg_name=ArrayAgg('predicate_concept_url')).order_by('predicate_name')
        #
        # links_predicate_concepts = [item for concepts_list in links_predicate for item in concepts_list.agg_name]
        # global_list += links_predicate_concepts
        # predicate_list += links_predicate_concepts




        links = Link.objects.filter(subject_document_id__in=docs, name_space=name_space)
        rels1 = RelationshipSubjMention.objects.filter(document_id__in=documents, name_space=name_space)
        rels2 = RelationshipPredMention.objects.filter(document_id__in=documents, name_space=name_space)
        rels3 = RelationshipObjMention.objects.filter(document_id__in=documents, name_space=name_space)
        rels4 = RelationshipSubjConcept.objects.filter(object_document_id__in=docs, name_space=name_space)
        rels5 = RelationshipPredConcept.objects.filter(subject_document_id__in=docs, name_space=name_space)
        rels6 = RelationshipObjConcept.objects.filter(subject_document_id__in=docs, name_space=name_space)
        rels7= CreateFact.objects.filter(document_id__in=documents, name_space=name_space)
        for link in rels7:
            concept_s = Concept.objects.get(concept_url = link.subject_concept_url)
            concept_o = Concept.objects.get(concept_url = link.object_concept_url)
            concept_p = Concept.objects.get(concept_url = link.predicate_concept_url)
            if HasArea.objects.filter(concept_url = concept_p, name= area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1
                if concept_p.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['object'][area]['count'] += 1
                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_s, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['subject'][area]['count'] += 1
                if concept_s.concept_name in json_doc['subject'][area].keys() :
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1

        for link in rels6:
            d = Document.objects.get(document_id=link.subject_document_id)
            mp = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            ms = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            concept = link.concept_url
            ass_s = Associate.objects.filter(document_id=d, start=ms, stop=ms.stop, name=area_obj,username = link.username)
            ass_p = Associate.objects.filter(document_id=d, start=mp, stop=mp.stop, name=area_obj,username = link.username)
            json_doc['predicate'][area]['count'] += ass_p.count()
            json_doc['subject'][area]['count'] += ass_s.count()
            for a in ass_p:
                concepto = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concepto.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concepto.concept_name] += 1
                else:
                    json_doc['predicate'][area][concepto.concept_name] = 1
            for a in ass_s:
                concepts = a.concept_url
                json_doc['global'][area]['count'] += 1
                if concepts.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concepts.concept_name] += 1
                else:
                    json_doc['subject'][area][concepts.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['object'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1
                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1

        for link in rels5:
            d = Document.objects.get(document_id=link.object_document_id)
            mo = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            ms = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            concept = link.concept_url
            ass_s = Associate.objects.filter(document_id=d, start=ms, stop=ms.stop, name=area_obj,username = link.username)
            ass_o = Associate.objects.filter(document_id=d, start=mo, stop=mo.stop, name=area_obj,username = link.username)
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['subject'][area]['count'] += ass_s.count()
            for a in ass_o:
                concepto = a.concept_url
                json_doc['global'][area]['count'] += 1
                if concepto.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concepto.concept_name] += 1
                else:
                    json_doc['object'][area][concepto.concept_name] = 1
            for a in ass_s:
                concepts = a.concept_url
                json_doc['global'][area]['count'] += 1
                if concepts.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concepts.concept_name] += 1
                else:
                    json_doc['subject'][area][concepts.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1
                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
        for link in rels4:
            d = Document.objects.get(document_id=link.object_document_id)
            mo = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            mp = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            concept = link.concept_url
            ass_p = Associate.objects.filter(document_id=d, start=mp, stop=mp.stop, name=area_obj,username = link.username)
            ass_o = Associate.objects.filter(document_id=d, start=mo, stop=mo.stop, name=area_obj,username = link.username)
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['predicate'][area]['count'] += ass_p.count()
            for a in ass_o:
                concepto = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concepto.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concepto.concept_name] += 1
                else:
                    json_doc['object'][area][concepto.concept_name] = 1
            for a in ass_p:
                conceptp = a.concept_url
                json_doc['global'][area]['count'] += 1
                if conceptp.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][conceptp.concept_name] += 1
                else:
                    json_doc['predicate'][area][conceptp.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['subject'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1

        for link in rels3:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_s = Concept.objects.get(concept_url=link.subject_concept_url)
            concept_p = Concept.objects.get(concept_url=link.predicate_concept_url)
            ass = Associate.objects.filter(document_id=d, start=m, stop=m.stop, name=area_obj,username = link.username)
            json_doc['object'][area]['count'] += ass.count()
            for a in ass:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1
                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1
            if HasArea.objects.filter(concept_url=concept_p, name=area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['subject'][area]['count'] += 1
                if concept_s.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_p, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['predicate'][area]['count'] += 1
                if concept_p.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
        for link in rels2:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_s = Concept.objects.get(concept_url=link.subject_concept_url)
            concept_o = Concept.objects.get(concept_url=link.object_concept_url)
            ass = Associate.objects.filter(document_id=d, start=m, stop=m.stop, name=area_obj,username = link.username)
            json_doc['predicate'][area]['count'] += ass.count()
            for a in ass:
                json_doc['global'][area]['count'] += 1
                concept = a.concept_url
                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_s, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1

                json_doc['subject'][area]['count'] += 1
                if concept_s.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1

                json_doc['object'][area]['count'] += 1
                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1
        for link in rels1:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_p = Concept.objects.get(concept_url=link.predicate_concept_url)
            concept_o = Concept.objects.get(concept_url=link.object_concept_url)
            ass = Associate.objects.filter(document_id=d, start=m, stop=m.stop, name=area_obj,username = link.username)
            json_doc['subject'][area]['count'] += ass.count()
            for a in ass:
                json_doc['global'][area]['count'] += 1

                concept = a.concept_url
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_p, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['predicate'][area]['count'] += 1
                if concept_p.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['global'][area]['count'] += 1
                json_doc['object'][area]['count'] += 1
                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1

        for link in links:
            d = Document.objects.get(document_id=link.subject_document_id)
            sm = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            pm = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            om = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            ass_s = Associate.objects.filter(document_id=d, start=sm, stop=sm.stop, name=area_obj,username = link.username)
            ass_o = Associate.objects.filter(document_id=d, start=om, stop=om.stop, name=area_obj,username = link.username)
            ass_p = Associate.objects.filter(document_id=d, start=pm, stop=pm.stop, name=area_obj,username = link.username)
            json_doc['subject'][area]['count'] += ass_s.count()
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['predicate'][area]['count'] += ass_p.count()

            for a in ass_s:
                json_doc['global'][area]['count'] += 1
                concept = a.concept_url
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1
            for a in ass_p:
                json_doc['global'][area]['count'] += 1
                concept = a.concept_url
                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
            for a in ass_o:
                json_doc['global'][area]['count'] += 1
                concept = a.concept_url
                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1
    return json_doc



def compute_relationship_area_personal(distinct_areas,documents,docs,user,name_space):
    json_doc = {}
    json_doc['subject'] = {}
    json_doc['global'] = {}
    json_doc['predicate'] = {}
    json_doc['object'] = {}
    for area in distinct_areas:
        json_doc['global'][area] = {}
        json_doc['subject'][area] = {}
        json_doc['predicate'][area] = {}
        json_doc['object'][area] = {}
        json_doc['global'][area]['count'] = 0
        json_doc['subject'][area]['count'] = 0
        json_doc['predicate'][area]['count'] = 0
        json_doc['object'][area]['count'] = 0
        area_obj = SemanticArea.objects.get(name=area)
        links = Link.objects.filter(subject_document_id__in=docs, name_space=name_space, username=user,
                                    )
        rels1 = RelationshipSubjMention.objects.filter(document_id__in=documents, name_space=name_space,
                                                       username=user)
        rels2 = RelationshipPredMention.objects.filter(document_id__in=documents, name_space=name_space,
                                                       username=user)
        rels3 = RelationshipObjMention.objects.filter(document_id__in=documents, name_space=name_space,
                                                      username=user)
        rels4 = RelationshipSubjConcept.objects.filter(object_document_id__in=docs, name_space=name_space,
                                                       username=user)
        rels5 = RelationshipPredConcept.objects.filter(subject_document_id__in=docs, name_space=name_space,
                                                       username=user)
        rels6 = RelationshipObjConcept.objects.filter(subject_document_id__in=docs, name_space=name_space,
                                                      username=user)
        rels7 = CreateFact.objects.filter(document_id__in=documents, name_space=name_space,username=user)
        for link in rels7:
            concept_s = Concept.objects.get(concept_url=link.subject_concept_url)
            concept_o = Concept.objects.get(concept_url=link.object_concept_url)
            concept_p = Concept.objects.get(concept_url=link.predicate_concept_url)

            if HasArea.objects.filter(concept_url=concept_p, name=area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_p.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['object'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_s, name= area_obj).exists():
                json_doc['subject'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_s.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1

        for link in rels6:
            d = Document.objects.get(document_id=link.subject_document_id)
            mp = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            ms = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            concept = link.concept_url
            ass_s = Associate.objects.filter(document_id=d, start=ms, stop=ms.stop, name=area_obj,username = link.username)
            ass_p = Associate.objects.filter(document_id=d, start=mp, stop=mp.stop, name=area_obj,username = link.username)
            json_doc['subject'][area]['count'] += ass_s.count()
            json_doc['predicate'][area]['count'] += ass_p.count()

            for a in ass_p:
                concepto = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concepto.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concepto.concept_name] += 1
                else:
                    json_doc['predicate'][area][concepto.concept_name] = 1
            for a in ass_s:
                json_doc['global'][area]['count'] += 1

                concepts = a.concept_url
                if concepts.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concepts.concept_name] += 1
                else:
                    json_doc['subject'][area][concepts.concept_name] = 1

            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['object'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1

        for link in rels5:
            d = Document.objects.get(document_id=link.object_document_id)
            mo = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            ms = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            concept = link.concept_url
            ass_s = Associate.objects.filter(document_id=d, start=ms, username=user, stop=ms.stop, name=area_obj)
            ass_o = Associate.objects.filter(document_id=d, start=mo, username=user, stop=mo.stop, name=area_obj)
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['subject'][area]['count'] += ass_s.count()
            for a in ass_o:
                json_doc['global'][area]['count'] += 1

                concepto = a.concept_url
                if concepto.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concepto.concept_name] += 1
                else:
                    json_doc['object'][area][concepto.concept_name] = 1
            for a in ass_s:
                concepts = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concepts.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concepts.concept_name] += 1
                else:
                    json_doc['subject'][area][concepts.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
        for link in rels4:
            d = Document.objects.get(document_id=link.object_document_id)
            mo = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            mp = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            concept = link.concept_url
            ass_p = Associate.objects.filter(document_id=d, start=mp, username=user, stop=mp.stop, name=area_obj)
            ass_o = Associate.objects.filter(document_id=d, start=mo, username=user, stop=mo.stop, name=area_obj)
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['predicate'][area]['count'] += ass_p.count()
            for a in ass_o:
                concepto = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concepto.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concepto.concept_name] += 1
                else:
                    json_doc['object'][area][concepto.concept_name] = 1
            for a in ass_p:
                conceptp = a.concept_url
                json_doc['global'][area]['count'] += 1

                if conceptp.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][conceptp.concept_name] += 1
                else:
                    json_doc['predicate'][area][conceptp.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept, name= area_obj).exists():
                json_doc['subject'][area]['count'] += 1
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1

        for link in rels3:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_s = Concept.objects.get(concept_url=link.subject_concept_url)
            concept_p = Concept.objects.get(concept_url=link.predicate_concept_url)
            ass = Associate.objects.filter(document_id=d, username=user, start=m, stop=m.stop, name=area_obj)
            json_doc['object'][area]['count'] += ass.count()
            for a in ass:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1

            if HasArea.objects.filter(concept_url = concept_s, name= area_obj).exists():
                json_doc['subject'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_s.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_p, name= area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_p.concept_name in json_doc['predicate'][area].keys() :
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
        for link in rels2:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_s = Concept.objects.get(concept_url=link.subject_concept_url)
            concept_o = Concept.objects.get(concept_url=link.object_concept_url)
            ass = Associate.objects.filter(document_id=d, username=user, start=m, stop=m.stop, name=area_obj)
            json_doc['predicate'][area]['count'] += ass.count()
            for a in ass:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_s, name= area_obj).exists():
                json_doc['subject'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_s.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept_s.concept_name] += 1
                else:
                    json_doc['subject'][area][concept_s.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['object'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1
        for link in rels1:
            d = Document.objects.get(document_id=link.document_id_id)
            m = Mention.objects.get(document_id=d, start=link.start_id, stop=link.stop)
            concept_p = Concept.objects.get(concept_url=link.predicate_concept_url)
            concept_o = Concept.objects.get(concept_url=link.object_concept_url)
            ass = Associate.objects.filter(document_id=d, username=user, start=m, stop=m.stop, name=area_obj)
            json_doc['subject'][area]['count'] += ass.count()
            for a in ass:
                json_doc['global'][area]['count'] += 1

                concept = a.concept_url
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_p, name= area_obj).exists():
                json_doc['predicate'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_p.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept_p.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept_p.concept_name] = 1
            if HasArea.objects.filter(concept_url = concept_o, name= area_obj).exists():
                json_doc['object'][area]['count'] += 1
                json_doc['global'][area]['count'] += 1

                if concept_o.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept_o.concept_name] += 1
                else:
                    json_doc['object'][area][concept_o.concept_name] = 1

        for link in links:
            d = Document.objects.get(document_id=link.subject_document_id)
            sm = Mention.objects.get(document_id=d, start=link.subject_start, stop=link.subject_stop)
            pm = Mention.objects.get(document_id=d, start=link.predicate_start, stop=link.predicate_stop)
            om = Mention.objects.get(document_id=d, start=link.object_start, stop=link.object_stop)
            ass_s = Associate.objects.filter(document_id=d, username=user, start=sm, stop=sm.stop, name=area_obj)
            ass_o = Associate.objects.filter(document_id=d, username=user, start=om, stop=om.stop, name=area_obj)
            ass_p = Associate.objects.filter(document_id=d, username=user, start=pm, stop=pm.stop, name=area_obj)
            json_doc['subject'][area]['count'] += ass_s.count()
            json_doc['object'][area]['count'] += ass_o.count()
            json_doc['predicate'][area]['count'] += ass_p.count()

            for a in ass_s:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1
                if concept.concept_name in json_doc['subject'][area].keys():
                    json_doc['subject'][area][concept.concept_name] += 1
                else:
                    json_doc['subject'][area][concept.concept_name] = 1
            for a in ass_p:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['predicate'][area].keys():
                    json_doc['predicate'][area][concept.concept_name] += 1
                else:
                    json_doc['predicate'][area][concept.concept_name] = 1
            for a in ass_o:
                concept = a.concept_url
                json_doc['global'][area]['count'] += 1

                if concept.concept_name in json_doc['object'][area].keys():
                    json_doc['object'][area][concept.concept_name] += 1
                else:
                    json_doc['object'][area][concept.concept_name] = 1
    return json_doc