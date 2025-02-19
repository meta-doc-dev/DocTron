#from bioc.bioc_writer import BioCJSONWriter, BioCXMLWriter

from doctron_app.utils import *
#from bioc import *
from datetime import date

from doctron_app.models import *
from django.http import HttpResponse



def create_bioc_to_download(annotation_key,annotators,document_number,batch,user,name_space,document,collection_start,form):
    return
    #try:
    #     collection_start = Collection.objects.get(collection_id = collection_start)
    #
    #     if annotators != 'all':
    #         # solo utente login
    #         users_list = User.objects.filter(username=user, name_space=name_space)
    #     else:
    #
    #
    #         users_list = ShareCollection.objects.filter(collection_id=collection_start, name_space=name_space)
    #         users_list = [u.username for u in users_list]
    #
    #     if document_number == '0':
    #         documents = Document.objects.filter(document_id=document)
    #     else:
    #         if batch == 'all':
    #
    #             documents = Document.objects.filter(collection_id=collection_start)
    #
    #         else:
    #             documents = Document.objects.filter(collection_id=collection_start, batch=batch)
    #
    #     writer = BioCXMLWriter()
    #     json_writer = BioCJSONWriter()
    #     writer.collection = BioCCollection()
    #     json_writer.collection = BioCCollection()
    #     collection = writer.collection
    #     collection1 = json_writer.collection
    #     today = str(date.today())
    #     collection.date = today
    #     collection1.date = today
    #     collection.source = collection_start.name
    #
    #     # collection1.source = collection
    #     for u in users_list:
    #         for d in documents:
    #
    #             document = BioCDocument()
    #
    #             document.id = str(d.document_id)  # pubmed id
    #             document.put_infon('provenance', d.provenance)
    #             document.put_infon('language', d.language)
    #             document.put_infon('username', u.username)
    #             document.put_infon('batch', str(d.batch))
    #             if(annotation_key == 'mentions'):
    #                 positions,bioc_annotations = mentions_bioc(d,u)
    #                 for position in list(set(positions)):
    #                     passage = BioCPassage()
    #                     passage.put_infon('section', position)
    #                     # passage.text = d.document_content[position]
    #
    #                     for bioc_annotation in bioc_annotations:
    #                         if bioc_annotation[1]['position'] == position:
    #                             passage.add_annotation(bioc_annotation[0])
    #                     document.add_passage(passage)
    #                 collection.add_document(document)
    #                 collection1.add_document(document)
    #                 print(writer)
    #
    #             elif annotation_key == 'concepts':
    #                     positions, bioc_annotations = concepts_bioc(d, u)
    #                     for position in list(set(positions)):
    #                         passage = BioCPassage()
    #                         passage.put_infon('section', position)
    #                         # passage.text = d.document_content[position]
    #                         for bioc_annotation in bioc_annotations:
    #                             if bioc_annotation[1]['position'] == position:
    #                                 passage.add_annotation(bioc_annotation[0])
    #                         document.add_passage(passage)
    #                     collection.add_document(document)
    #                     collection1.add_document(document)
    #                     print(writer)
    #             elif annotation_key == 'tags':
    #                     positions, bioc_annotations = tags_bioc(d, u)
    #                     for position in list(set(positions)):
    #                         passage = BioCPassage()
    #                         passage.put_infon('section', position)
    #                         # passage.text = d.document_content[position]
    #                         for bioc_annotation in bioc_annotations:
    #                             if bioc_annotation[1]['position'] == position:
    #                                 passage.add_annotation(bioc_annotation[0])
    #                         document.add_passage(passage)
    #                     collection.add_document(document)
    #                     collection1.add_document(document)
    #                     print(writer)
    #             elif annotation_key == 'relationships':
    #                 positions_concepts, bioc_annotations_concepts = concepts_bioc(d, u)
    #
    #                 positions_link, bioc_annotations_link = links_bioc(d, u)
    #                 positions_subjconcept, bioc_annotations_subjconcept = rels_subj_conc_bioc(d, u)
    #                 positions_objconcept, bioc_annotations_objconcept = rels_obj_conc_bioc(d, u)
    #                 positions_predconcept, bioc_annotations_predconcept = rels_pred_conc_bioc(d, u)
    #
    #                 # bioc_annotations_subjmention, positions_subjmention = links_bioc(d, u)
    #                 # positions_objmention, bioc_annotations_objmention = links_bioc(d, u)
    #                 # positions_predmention, bioc_annotations_predmention = links_bioc(d, u)
    #
    #                 for position in positions_concepts:
    #                     passage = BioCPassage()
    #                     passage.put_infon('section', position)
    #                     for bioc_annotation_c in bioc_annotations_concepts:
    #                         if bioc_annotation_c[1]['position'] == position:
    #                             passage.add_annotation(bioc_annotation_c[0])
    #                     for pos in positions_link:
    #                         for bioc_annotation_link in bioc_annotations_link:
    #                             if bioc_annotation_link[1]['position'] == pos:
    #                                 passage.add_relation(bioc_annotation_link[0])
    #
    #                     for pos in positions_objconcept:
    #                         for bioc_annotation_subj_concept in bioc_annotations_objconcept:
    #                             if bioc_annotation_subj_concept[1]['position'] == pos:
    #                                 passage.add_relation(bioc_annotation_subj_concept[0])
    #
    #                     for pos in positions_subjconcept:
    #                         for bioc_annotation_subj_concept in bioc_annotations_subjconcept:
    #                             if bioc_annotation_subj_concept[1]['position'] == pos:
    #                                 passage.add_relation(bioc_annotation_subj_concept[0])
    #                     #
    #
    #                     for pos in positions_predconcept:
    #                         for bioc_annotation_pred_concept in bioc_annotations_predconcept:
    #                             if bioc_annotation_pred_concept[1]['position'] == pos:
    #                                 passage.add_relation(bioc_annotation_pred_concept[0])
    #
    #                     # for pos in positions_subjmention:
    #                     #     for bioc_annotation_subj_mention in bioc_annotations_subjmention:
    #                     #         if bioc_annotation_subj_mention[1]['position'] == pos:
    #                     #             passage.add_relation(bioc_annotation_subj_mention[0])
    #                     #
    #                     # for pos in positions_objmention:
    #                     #     for bioc_annotation_obj_mention in bioc_annotations_objmention:
    #                     #         if bioc_annotation_obj_mention[1]['position'] == pos:
    #                     #             passage.add_relation(bioc_annotation_obj_mention[0])
    #                     #
    #                     # for pos in positions_predmention:
    #                     #     for bioc_annotation_pred_concept in bioc_annotations_predmention:
    #                     #         if bioc_annotation_pred_concept[1]['position'] == pos:
    #                     #             passage.add_relation(bioc_annotation_pred_concept[0])
    #
    #                     document.add_passage(passage)
    #                 collection.add_document(document)
    #                 collection1.add_document(document)
    #                 print(writer)



    # except Exception as e:
    #     print(e)
    #     return False
    #
    # else:
    #     print(writer)
    #     #
    #     # #os.remove(path1)
    #     if form == 'json':
    #         # os.remove(path1)
    #         return json_writer
    #     # # return True
    #     return writer


def mentions_bioc(d,u):
    count = 0
    bioc_annotations = []
    positions = []
    mentions = Mention.objects.filter(language = d.language,document_id=d)
    # for mention in mentions:
    #     annotations_objs = Annotate.objects.filter(username=u,start=mention, stop = mention.stop,name_space=u.name_space, document_id=d)
    #
    #     for annotation_single in annotations_objs:
    #         mention = Mention.objects.get(start=annotation_single.start_id, stop=annotation_single.stop, document_id=d,
    #                                       language=d.language)
    #         bioc_ann = BioCAnnotation()
    #         bioc_ann.id = 'mention_'+str(mention.start)+'_'+str(mention.stop)
    #         json_start_stop_pos = return_start_stop_for_frontend(mention.start, mention.stop, d.document_content)
    #         count = count + 1
    #         loc_ann = BioCLocation()
    #         loc_ann.offset = str(json_start_stop_pos['start'])
    #         loc_ann.length = str(json_start_stop_pos['stop'] - json_start_stop_pos['start'] + 1)
    #         positions.append(json_start_stop_pos['position'])
    #         bioc_ann.add_location(loc_ann)
    #         mention_text = mention.mention_text
    #         mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)
    #
    #         bioc_ann.text = mtext
    #         couple = (bioc_ann, json_start_stop_pos)
    #         bioc_annotations.append(couple)
    return positions,bioc_annotations


def concepts_bioc(d,u):
    count = 0
    bioc_annotations = []
    positions = []
    mentions = Mention.objects.filter(language = d.language,document_id=d)
    # for mention in mentions:
    #     annotations_objs = Annotate.objects.filter(username=u,start=mention, stop = mention.stop,name_space=u.name_space, document_id=d)
    #
    #     for annotation_single in annotations_objs:
    #         associations = Associate.objects.filter(username=u, start=mention, stop=mention.stop, name_space=u.name_space,
    #                                 document_id=d)
    #         mention = Mention.objects.get(start=annotation_single.start_id, stop=annotation_single.stop, document_id=d,
    #                                       language=d.language)
    #
    #         bioc_ann = BioCAnnotation()
    #         bioc_ann.id = 'mention_'+str(mention.start)+'_'+str(mention.stop)
    #         json_start_stop_pos = return_start_stop_for_frontend(mention.start, mention.stop, d.document_content)
    #
    #         loc_ann = BioCLocation()
    #         loc_ann.offset = str(json_start_stop_pos['start'])
    #         loc_ann.length = str(json_start_stop_pos['stop'] - json_start_stop_pos['start'] + 1)
    #         positions.append(json_start_stop_pos['position'])
    #         bioc_ann.add_location(loc_ann)
    #         mention_text = mention.mention_text
    #         mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)
    #         count = 0
    #         for association in associations:
    #             concept = association.concept_url
    #             area = association.name
    #             bioc_ann.put_infon('concpet_url_'+str(count),concept.concept_url)
    #             bioc_ann.put_infon('concpet_name_'+str(count),concept.concept_name)
    #             bioc_ann.put_infon('concpet_area_'+str(count),area.name)
    #
    #         bioc_ann.text = mtext
    #         couple = (bioc_ann, json_start_stop_pos)
    #         bioc_annotations.append(couple)
    return positions,bioc_annotations

def tags_bioc(d,u):
    count = 0
    bioc_annotations = []
    positions = []
    mentions = Mention.objects.filter(language = d.language,document_id=d)
    # for mention in mentions:
    #     annotations_objs = Annotate.objects.filter(username=u,start=mention, stop = mention.stop,name_space=u.name_space, document_id=d)
    #
    #     for annotation_single in annotations_objs:
    #         associations = AssociateTag.objects.filter(username=u, start=mention, stop=mention.stop, name_space=u.name_space,
    #                                 document_id=d)
    #         mention = Mention.objects.get(start=annotation_single.start_id, stop=annotation_single.stop, document_id=d,
    #                                       language=d.language)
    #
    #         bioc_ann = BioCAnnotation()
    #         bioc_ann.id = 'mention_'+str(mention.start)+'_'+str(mention.stop)
    #         json_start_stop_pos = return_start_stop_for_frontend(mention.start, mention.stop, d.document_content)
    #
    #         loc_ann = BioCLocation()
    #         loc_ann.offset = str(json_start_stop_pos['start'])
    #         loc_ann.length = str(json_start_stop_pos['stop'] - json_start_stop_pos['start'] + 1)
    #         positions.append(json_start_stop_pos['position'])
    #         bioc_ann.add_location(loc_ann)
    #         mention_text = mention.mention_text
    #         mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)
    #         count = 0
    #         for association in associations:
    #             area = association.name
    #             bioc_ann.put_infon('tag_'+str(count),area.name)
    #
    #         bioc_ann.text = mtext
    #         couple = (bioc_ann, json_start_stop_pos)
    #         bioc_annotations.append(couple)
    return positions,bioc_annotations

def links_bioc(d,u):

    # pos,bioc_concepts = concepts_bioc(d,u)
    annotations_objs = Link.objects.filter(username=u, name_space=u.name_space, subject_document_id=d.document_id)
    bioc_annotations = []
    count = 0
    positions = []
    # for annotation_single in annotations_objs:
    #     subject_mention = Mention.objects.get(start=annotation_single.subject_start, stop=annotation_single.subject_stop, document_id=d,
    #                                   language=d.language)
    #
    #     predicate_mention = Mention.objects.get(start=annotation_single.predicate_start,
    #                                             stop=annotation_single.predicate_stop, document_id=d,
    #                                             language=d.language)
    #     object_mention = Mention.objects.get(start=annotation_single.object_start,
    #                                             stop=annotation_single.object_stop, document_id=d,
    #                                             language=d.language)
    #     subject_json_start_stop_pos = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop, d.document_content)
    #     predicate_json_start_stop_pos = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop, d.document_content)
    #     object_json_start_stop_pos = return_start_stop_for_frontend(object_mention.start, object_mention.stop, d.document_content)
    #
    #     refid_subj = 'mention_'+str(subject_mention.start)+'_'+str(subject_mention.stop)
    #     refid_pred = 'mention_'+str(predicate_mention.start)+'_'+str(predicate_mention.stop)
    #     refid_obj = 'mention_'+str(object_mention.start)+'_'+str(object_mention.stop)
    #     positions.append(subject_json_start_stop_pos['position'])
    #     bioc_ann = BioCRelation()
    #     bioc_ann.id = 'rel_'+str(count)
    #     bioc_node_subj = BioCNode()
    #     bioc_node_subj.refid = refid_subj
    #     bioc_node_subj.role = 'subject'
    #     bioc_node_pred = BioCNode()
    #     bioc_node_pred.refid = refid_pred
    #     bioc_node_pred.role = 'predicate'
    #     bioc_node_obj = BioCNode()
    #     bioc_node_obj.refid = refid_obj
    #     bioc_node_obj.role = 'object'
    #     bioc_ann.add_node(node=bioc_node_subj)
    #     bioc_ann.add_node(node=bioc_node_pred)
    #     bioc_ann.add_node(node=bioc_node_obj)
    #     count += 1
    #     couple = (bioc_ann,subject_json_start_stop_pos)
    #     bioc_annotations.append(couple)
    return positions,bioc_annotations


def rels_subj_conc_bioc(d, u):
    # pos,bioc_concepts = concepts_bioc(d,u)
    # annotations_objs = RelationshipSubjConcept.objects.filter(username=u, name_space=u.name_space,
    #                                                           object_document_id=d.document_id)
    bioc_annotations = []
    count = 0
    positions = []
    # for annotation_single in annotations_objs:
    #     concept = annotation_single.concept_url
    #     area = annotation_single.name
    #
    #     predicate_mention = Mention.objects.get(start=annotation_single.predicate_start,
    #                                             stop=annotation_single.predicate_stop, document_id=d,
    #                                             language=d.language)
    #     object_mention = Mention.objects.get(start=annotation_single.object_start,
    #                                          stop=annotation_single.object_stop, document_id=d,
    #                                          language=d.language)
    #     predicate_json_start_stop_pos = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop,
    #                                                                    d.document_content)
    #
    #
    #     refid_pred = 'mention_' + str(predicate_mention.start) + '_' + str(predicate_mention.stop)
    #     refid_subj = 'mention_' + str(object_mention.start) + '_' + str(object_mention.stop)
    #     positions.append(predicate_json_start_stop_pos['position'])
    #     bioc_ann = BioCRelation()
    #     bioc_ann.id = 'rel_' + str(count)
    #     bioc_node_pred = BioCNode()
    #     bioc_node_pred.refid = refid_pred
    #     bioc_node_pred.role = 'predicate'
    #     bioc_node_obj = BioCNode()
    #     bioc_node_obj.refid = refid_subj
    #     bioc_node_obj.role = 'object'
    #
    #     bioc_ann.add_node(node=bioc_node_pred)
    #     bioc_ann.add_node(node=bioc_node_obj)
    #     bioc_ann.put_infon('subject_concept_url', concept.concept_url)
    #     bioc_ann.put_infon('subject_concept_name', concept.concept_name)
    #     bioc_ann.put_infon('subject_concept_area', area.name)
    #     count += 1
    #     couple = (bioc_ann, predicate_json_start_stop_pos)
    #     bioc_annotations.append(couple)
    return [], []



def rels_obj_conc_bioc(d, u):
    # pos,bioc_concepts = concepts_bioc(d,u)
    annotations_objs = RelationshipObjConcept.objects.filter(username=u, name_space=u.name_space,
                                                              subject_document_id=d.document_id)
    bioc_annotations = []
    count = 0
    positions = []
    # for annotation_single in annotations_objs:
    #     concept = annotation_single.concept_url
    #     area = annotation_single.name
    #
    #     predicate_mention = Mention.objects.get(start=annotation_single.predicate_start,
    #                                             stop=annotation_single.predicate_stop, document_id=d,
    #                                             language=d.language)
    #     subject_mention = Mention.objects.get(start=annotation_single.subject_start,
    #                                          stop=annotation_single.subject_stop, document_id=d,
    #                                          language=d.language)
    #     predicate_json_start_stop_pos = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop,
    #                                                                    d.document_content)
    #     subject_json_start_stop_pos = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop,
    #                                                                 d.document_content)
    #
    #     refid_pred = 'mention_' + str(predicate_mention.start) + '_' + str(predicate_mention.stop)
    #     refid_subj = 'mention_' + str(subject_mention.start) + '_' + str(subject_mention.stop)
    #     positions.append(predicate_json_start_stop_pos['position'])
    #     bioc_ann = BioCRelation()
    #     bioc_ann.id = 'rel_' + str(count)
    #     bioc_node_pred = BioCNode()
    #     bioc_node_pred.refid = refid_pred
    #     bioc_node_pred.role = 'predicate'
    #     bioc_node_obj = BioCNode()
    #     bioc_node_obj.refid = refid_subj
    #     bioc_node_obj.role = 'subject'
    #
    #     bioc_ann.add_node(node=bioc_node_pred)
    #     bioc_ann.add_node(node=bioc_node_obj)
    #     bioc_ann.put_infon('object_concept_url', concept.concept_url)
    #     bioc_ann.put_infon('object_concept_name', concept.concept_name)
    #     bioc_ann.put_infon('object_concept_area', area.name)
    #     count += 1
    #     couple = (bioc_ann, predicate_json_start_stop_pos)
    #     bioc_annotations.append(couple)
    return positions, bioc_annotations


def rels_pred_conc_bioc(d, u):
    # pos,bioc_concepts = concepts_bioc(d,u)
    annotations_objs = RelationshipPredConcept.objects.filter(username=u, name_space=u.name_space,
                                                              subject_document_id=d.document_id)
    bioc_annotations = []
    count = 0
    positions = []
    # for annotation_single in annotations_objs:
    #     concept = annotation_single.concept_url
    #     area = annotation_single.name
    #
    #     object_mention = Mention.objects.get(start=annotation_single.object_start,
    #                                             stop=annotation_single.object_stop, document_id=d,
    #                                             language=d.language)
    #     subject_mention = Mention.objects.get(start=annotation_single.subject_start,
    #                                          stop=annotation_single.subject_stop, document_id=d,
    #                                          language=d.language)
    #     object_json_start_stop_pos = return_start_stop_for_frontend(object_mention.start, object_mention.stop,
    #                                                                    d.document_content)
    #     subject_json_start_stop_pos = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop,
    #                                                                 d.document_content)
    #
    #     refid_object = 'mention_' + str(object_mention.start) + '_' + str(object_mention.stop)
    #     refid_subj = 'mention_' + str(subject_mention.start) + '_' + str(subject_mention.stop)
    #     positions.append(object_json_start_stop_pos['position'])
    #     bioc_ann = BioCRelation()
    #     bioc_ann.id = 'rel_' + str(count)
    #     bioc_node_pred = BioCNode()
    #     bioc_node_pred.refid = refid_object
    #     bioc_node_pred.role = 'object'
    #     bioc_node_obj = BioCNode()
    #     bioc_node_obj.refid = refid_subj
    #     bioc_node_obj.role = 'subject'
    #
    #     bioc_ann.add_node(node=bioc_node_pred)
    #     bioc_ann.add_node(node=bioc_node_obj)
    #     bioc_ann.put_infon('predicate_concept_url', concept.concept_url)
    #     bioc_ann.put_infon('predicate_concept_name', concept.concept_name)
    #     bioc_ann.put_infon('predicate_concept_area', area.name)
    #     count += 1
    #     couple = (bioc_ann, object_json_start_stop_pos)
    #     bioc_annotations.append(couple)
    return positions, bioc_annotations






def create_json_to_download(annotators,batch,name_space,document,collection,topic):

    json_to_download = {}
    # json_to_download['download_date'] = Now()

    name_space = NameSpace.objects.get(name_space=name_space)
    collection = Collection.objects.get(collection_id=collection)
    annotation_type = collection.annotation_type.name
    json_to_download['collection'] = collection.name
    user = annotators
    if annotators != 'all':
        users_list = User.objects.filter(username = user, name_space = name_space)
    else:
        users_list = ShareCollection.objects.filter(collection_id = collection,name_space = name_space)
        users_list = [u.username for u in users_list]
    if topic != 'all':
        topics = Topic.objects.filter(collection_id=collection,topic_id=topic)
    else:
        topics = Topic.objects.filter(collection_id=collection)

    if document != 'all':
        documents = Document.objects.filter(document_id = document)
    else:
        if batch == 'all':
            documents = Document.objects.filter(collection_id = collection)
            if Split.objects.filter(collection_id = collection,username=user).exists():
                documents = Split.objects.filter(collection_id = collection,username=user)
                documents = [d.document_id for d in documents]

        else:
            documents = Document.objects.filter(collection_id=collection,batch = batch)
            if Split.objects.filter(collection_id = collection,document_id__in=documents,username=user).exists():
                documents = Split.objects.filter(collection_id = collection,document_id__in=documents,username=user)
                documents = [d.document_id for d in documents]

    if annotation_type == 'Graded labeling':
        json_to_download['graded_labeling'] = []
        for u in users_list:
                annotations = AnnotateLabel.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    json_ann = {}
                    json_ann['username'] = u.username
                    json_ann['document_id'] = d.document_id_not_hashed
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    if 'document_id' in list(d.document_content.keys()) or d.document_id_not_hashed is None:
                        json_ann['document_id'] = d.document_content['document_id']
                    json_ann['batch'] = d.batch
                    json_ann['batch'] = d.batch
                    json_ann['insertion_time'] = annotation.insertion_time
                    json_ann['label'] = annotation.label.name
                    json_ann['score'] = annotation.grade
                    json_to_download['graded_labeling'].append(json_ann)

                    mention = Mention.objects.get(document_id = d, start = annotation.start_id, stop = annotation.stop)
                    json_ann['mention_text'] = mention.mention_text
                    js_ret = return_start_stop_for_frontend(mention.start,mention.stop,d.document_content)
                    json_ann['start'] = js_ret['start']
                    json_ann['stop'] = js_ret['stop']
                    json_ann['mention_location'] = js_ret['position']



    if annotation_type == 'Passages annotation':
        json_to_download['passages_annotation'] = []
        for u in users_list:
                annotations = AnnotatePassage.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    json_ann = {}
                    json_ann['username'] = u.username
                    json_ann['document_id'] = d.document_id_not_hashed
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    if 'document_id' in list(d.document_content.keys()) or d.document_id_not_hashed is None:
                        json_ann['document_id'] = d.document_content['document_id']
                    json_ann['batch'] = d.batch
                    mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
                    json_ann['mention_text'] = mention.mention_text
                    js_ret = return_start_stop_for_frontend(mention.start, mention.stop, d.document_content)
                    json_ann['start'] = js_ret['start']
                    json_ann['stop'] = js_ret['stop']
                    json_ann['mention_location'] = js_ret['position']
                    json_ann['insertion_time'] = annotation.insertion_time
                    json_ann['label'] = annotation.label.name
                    json_ann['score'] = annotation.grade
                    json_to_download['passages_annotation'].append(json_ann)



    if annotation_type == 'Entity linking':
        json_to_download['entity_linking'] = []
        for u in users_list:
                annotations = Associate.objects.filter(username=u, name_space=name_space, document_id__in = documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    json_ann = {}
                    json_ann['username'] = u.username
                    json_ann['document_id'] = d.document_id
                    json_ann['topic_id'] = a.topic_id.topic_id
                    if 'document_id' in list(d.document_content.keys()):
                        json_ann['document_id'] = d.document_content['document_id']
                    json_ann['batch'] = d.batch

                    json_ann['insertion_time'] = annotation.insertion_time
                    mention = Mention.objects.get(document_id = d, start = annotation.start_id, stop = annotation.stop)
                    concept = annotation.concept_url
                    json_ann['concept_url'] = concept.concept_url
                    json_ann['concept_name'] = concept.concept_name
                    json_ann['area'] = annotation.name_id
                    js_ret = return_start_stop_for_frontend(mention.start,mention.stop,d.document_content)
                    json_ann['start'] = js_ret['start']
                    json_ann['stop'] = js_ret['stop']
                    json_ann['mention_location'] = js_ret['position']
                    json_ann['mention_text'] = mention.mention_text
                    json_to_download['entity_linking'].append(json_ann)

    if annotation_type == 'Entity tagging':
        json_to_download['entity_tagging'] = []
        for u in users_list:
                annotations = AssociateTag.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    json_ann = {}
                    json_ann['username'] = u.username
                    json_ann['document_id'] = d.document_id
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    if 'document_id' in list(d.document_content.keys()):
                        json_ann['document_id'] = d.document_content['document_id']

                    json_ann['batch'] = d.batch
                    json_ann['insertion_time'] = annotation.insertion_time
                    mention = Mention.objects.get(document_id = d, start = annotation.start_id, stop = annotation.stop)
                    json_ann['tag'] = annotation.name_id
                    json_ann['mention_text'] = mention.mention_text
                    js_ret = return_start_stop_for_frontend(mention.start,mention.stop,d.document_content)
                    json_ann['start'] = js_ret['start']
                    json_ann['stop'] = js_ret['stop']
                    json_ann['mention_location'] = js_ret['position']

                    json_to_download['entity_tagging'].append(json_ann)

    if annotation_type == 'Objects annotation':
        json_to_download['objects_annotation'] = []
        for u in users_list:
                annotations = AnnotateObjectLabel.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    json_ann = {}
                    json_ann['username'] = u.username
                    json_ann['document_id'] = d.document_id
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    if 'document_id' in list(d.document_content.keys()):
                        json_ann['document_id'] = d.document_content['document_id']
                    json_ann['batch'] = d.batch
                    json_ann['insertion_time'] = annotation.insertion_time
                    label = annotation.name
                    object_ind = annotation.points.points
                    json_ann['object'] = object_ind
                    json_ann['label'] = label.name
                    json_ann['score'] = annotation.score
                    json_to_download['labels'].append(json_ann)

    if annotation_type == 'relationships annotation':
        json_to_download['relationships_annotation'] = []
        print('relationships',len(users_list),len(documents))
        document_ids = [d.document_id for d in documents]
        language = documents.first().language
        for u in users_list:

                annotations = Link.objects.filter(username=u, name_space=name_space, subject_document_id__in=document_ids,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.subject_document_id
                    row = relationshipsLinkAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipSubjConcept.objects.filter(username=u, name_space=name_space,object_document_id__in=document_ids,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.object_document_id
                    row = relationshipsSubjConceptAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipPredConcept.objects.filter(username=u, name_space=name_space,object_document_id__in=document_ids,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.object_document_id
                    row = relationshipsPredConceptAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipObjConcept.objects.filter(username=u, name_space=name_space,subject_document_id__in=document_ids,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.subject_document_id
                    row = relationshipsObjConceptAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipSubjMention.objects.filter(username=u, name_space=name_space,
                                                                     language=d.language, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    row = relationshipsSubjMentionAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipPredMention.objects.filter(username=u, name_space=name_space,
                                                                     language=d.language,
                                                                     document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    row = relationshipsPredMentionAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

                annotations = RelationshipObjMention.objects.filter(username=u, name_space=name_space,
                                                                    language=d.language, document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    row = relationshipsObjMentionAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['relationships_annotation'].append(json_ann)

    if annotation_type == 'Facts annotation':
        json_to_download['facts_annotation'] = []

        for u in users_list:
                annotations = CreateFact.objects.filter(username=u, name_space=name_space, language=d.language,
                                                  document_id__in=documents,topic_id__in=topics)
                for annotation in annotations:
                    d = annotation.document_id
                    row = relationshipsFactsAnnotations(annotation, d, collection)
                    json_ann = row_to_json(row)
                    json_ann['topic_id'] = annotation.topic_id.topic_id
                    json_to_download['facts_annotation'].append(json_ann)

    return json_to_download




import csv
def create_csv_to_download(annotation,annotators,batch,name_space,document,collection,topic,trec=False):

    try:
        response = HttpResponse(content_type='text/csv')
        collection = Collection.objects.get(collection_id=collection)
        name_space = NameSpace.objects.get(name_space=name_space)
        users_list = []
        user = annotators
        if annotators != 'all':
            users_list = User.objects.filter(username=user, name_space=name_space)
        else:
            users_list = ShareCollection.objects.filter(collection_id=collection, name_space=name_space)
            users_list = [u.username for u in users_list]
        if topic != 'all':
            topics = Topic.objects.filter(collection_id=collection, topic_id=topic)
        else:
            topics = Topic.objects.filter(collection_id=collection)


        if document != 'all':
            documents = Document.objects.filter(document_id=document)
        else:
            if batch == 'all':

                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection, username=user).exists():
                    documents = Split.objects.filter(collection_id=collection, username=user)
                    documents = [d.document_id for d in documents]

            else:
                documents = Document.objects.filter(collection_id=collection, batch=batch)
                if Split.objects.filter(collection_id=collection, document_id__in=documents,username=user).exists():
                    documents = Split.objects.filter(collection_id=collection, document_id__in=documents, username=user)
                    documents = [d.document_id for d in documents]


        row_list = []
        document_ids = [d.document_id for d in documents]

        if annotation == 'Graded labeling':
            row_list.append(['username','collection_name','topic_id','document_id','batch','label','score','insertion_time'])
            if trec:
                row_list.append(["query_id", "0", "doc_id", "relevance"])

            for u in users_list:
                    annotations = AnnotateLabel.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = []
                        row.append(annotation.username_id)
                        row.append(collection.name)
                        row.append(annotation.topic_id.topic_id)
                        if 'document_id' in list(d.document_content.keys()):
                            row.append(d.document_content['document_id'])
                        else:
                            row.append(d.document_id)

                        row.append(d.batch)
                        row.append(annotation.label.name)
                        row.append(annotation.gade)
                        row.append(annotation.insertion_time)
                        if trec == True:
                            row = []
                            row.append(annotation.topic_id.topic_id)
                            row.append(0)
                            d_id = d.document_id
                            if 'document_id' in list(d.document_content.keys()):
                                d_id = d.document_content['document_id']

                            row.append(d_id)
                            row.append(annotation.grade)


                        row_list.append(row)


        elif annotation == 'Passages annotation':
            row_list.append(['username','collection_name','topic_id','document_id','batch','start','stop','mention_location','mention_text','label','score','insertion_time'])
            if trec:
                row_list.append(["query_id","0","passage_id","relevance"])

            for u in users_list:
                    annotations = Annotate.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = []
                        row.append(annotation.username_id)
                        row.append(collection.name)
                        row.append(annotation.topic_id.topic_id)
                        if 'document_id' in list(d.document_content.keys()):
                            row.append(d.document_content['document_id'])
                        else:
                            row.append(d.document_id)


                        row.append(d.batch)
                        mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
                        js_ret = return_start_stop_for_frontend(mention.start, mention.stop,
                                                                d.document_content)
                        row.append(js_ret['start'])
                        row.append(js_ret['stop'])
                        row.append(js_ret['position'])
                        row.append(mention.mention_text)
                        row.append(annotation.label.name)
                        row.append(annotation.grade)
                        row.append(annotation.insertion_time)
                        if trec == True:
                            row = []
                            row.append(annotation.topic_id.topic_id)
                            row.append(0)
                            d_id = d.document_id
                            if 'document_id' in list(d.document_content.keys()):
                                d_id = d.document_content['document_id']

                            row.append(d_id + '_' + js_ret['start'] + js_ret['stop'])
                            row.append(annotation.grade)

                        row_list.append(row)

        elif annotation == 'Objects annotation':
            row_list.append(['username','collection_name','topic_id','document_id','batch','points','label','score','insertion_time'])
            for u in users_list:
                    annotations = AnnotateObjectLabel.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = []
                        row.append(annotation.username_id)
                        row.append(collection.name)
                        row.append(annotation.topic_id.topic_id)
                        if 'document_id' in list(d.document_content.keys()):
                            row.append(d.document_content['document_id'])
                        else:
                            row.append(d.document_id)

                        row.append(d.batch)
                        points = annotation.points.points
                        row.append(points)
                        row.append(annotation.label.name)
                        row.append(annotation.grade)
                        row.append(annotation.insertion_time)
                        row_list.append(row)

        elif annotation == 'Entity tagging':
            row_list.append(['username','collection_name','topic_id','document_id','batch','start','stop','mention_location','mention_text','tag','insertion_time'])
            for u in users_list:
                    annotations = AssociateTag.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = []
                        row.append(annotation.username_id)
                        row.append(collection.name)
                        row.append(annotation.topic_id.topic_id)
                        if 'document_id' in list(d.document_content.keys()):
                            row.append(d.document_content['document_id'])
                        else:
                            row.append(d.document_id)


                        row.append(d.batch)
                        mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
                        js_ret = return_start_stop_for_frontend(mention.start, mention.stop,
                                                                d.document_content)
                        row.append(js_ret['start'])
                        row.append(js_ret['stop'])
                        row.append(js_ret['position'])
                        row.append(mention.mention_text)
                        row.append(annotation.name_id)
                        row.append(annotation.insertion_time)
                        row_list.append(row)

        elif annotation == 'Entity linking':
            row_list.append(['username','collection_name','topic_id','document_id','batch','start','stop','mention_location','mention_text','concept_url','concept_name','area','insertion_time'])
            for u in users_list:
                for d in documents:
                    annotations = Associate.objects.filter(username=u, name_space=name_space, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        row = []
                        row.append(annotation.username_id)
                        row.append(collection.name)
                        row.append(annotation.topic_id.topic_id)
                        if 'document_id' in list(d.document_content.keys()):
                            row.append(d.document_content['document_id'])
                        else:
                            row.append(d.document_id)

                        row.append(d.batch)
                        mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
                        concept = annotation.concept_url
                        js_ret = return_start_stop_for_frontend(mention.start, mention.stop,
                                                                d.document_content)
                        row.append(js_ret['start'])
                        row.append(js_ret['stop'])
                        row.append(js_ret['position'])
                        row.append(mention.mention_text)
                        row.append(concept.concept_url)
                        row.append(concept.concept_name)
                        row.append(annotation.name_id)
                        row.append(annotation.insertion_time)
                        row_list.append(row)

        elif annotation == 'relationships':
            row_list.append(['username','collection_name','topic_id','document_id','batch',
                             'subject_start','subject_stop','subject_mention_text','subject_concepts_list','subject_tagss_list'
                             'predicate_start', 'predicate_stop', 'predicate_mention_text', 'predicate_concepts_list','predicate_tagss_list',
                             'object_start', 'object_stop', 'object_mention_text', 'object_concepts_list','object_tags_list'

                             'insertion_time'])
            for u in users_list:
                    annotations = Link.objects.filter(username=u, name_space=name_space, subject_document_id__in=document_ids,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.subject_document_id
                        row = relationshipsLinkAnnotations(annotation,d,collection)
                        row.insert(2, annotation.topic_id.topic_id)
                        row_list.append(row)

                    annotations = RelationshipSubjConcept.objects.filter(username=u, name_space=name_space, object_document_id__in=document_ids,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.object_document_id
                        row = relationshipsSubjConceptAnnotations(annotation,d,collection)
                        row.insert(2, annotation.topic_id.topic_id)
                        row_list.append(row)
                    annotations = RelationshipPredConcept.objects.filter(username=u, name_space=name_space,object_document_id__in=document_ids,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.object_document_id
                        row = relationshipsPredConceptAnnotations(annotation, d, collection)
                        row.insert(2, annotation.topic_id.topic_id)

                        row_list.append(row)
                    annotations = RelationshipObjConcept.objects.filter(username=u, name_space=name_space,
                                                                         subject_language=d.language,
                                                                         subject_document_id__in=document_ids,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.subject_document_id
                        row = relationshipsObjConceptAnnotations(annotation, d, collection)
                        row.insert(2, annotation.topic_id.topic_id)



                        row_list.append(row)

                    annotations = RelationshipSubjMention.objects.filter(username=u, name_space=name_space,language = d.language, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = relationshipsSubjMentionAnnotations(annotation,d,collection)
                        row.insert(2, annotation.topic_id.topic_id)

                        row_list.append(row)
                    annotations = RelationshipPredMention.objects.filter(username=u, name_space=name_space,language=d.language,
                                                                         document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = relationshipsPredMentionAnnotations(annotation, d, collection)
                        row.insert(2, annotation.topic_id.topic_id)

                        row_list.append(row)
                    annotations = RelationshipObjMention.objects.filter(username=u, name_space=name_space,language=d.language,document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = relationshipsObjMentionAnnotations(annotation, d, collection)

                        row_list.append(row)
        elif annotation == 'Facts annotation':
            row_list.append(['username','collection_name','topic_id','document_id','batch',
                             'subject_start','subject_stop','subject_mention_location','subject_mention_text','subject_concepts_list'
                             'predicate_start', 'predicate_stop', 'predicate_mention_location','predicate_mention_text', 'predicate_concepts_list',
                             'object_start', 'object_stop','object_mention_location', 'object_mention_text', 'object_concepts_list',

                             'insertion_time'])
            for u in users_list:
                    annotations = CreateFact.objects.filter(username=u, name_space=name_space,language = d.language, document_id__in=documents,topic_id__in=topics)
                    for annotation in annotations:
                        d = annotation.document_id
                        row = relationshipsFactsAnnotations(annotation,d,collection)
                        row.insert(2, annotation.topic_id.topic_id)

                        row_list.append(row)

    except Exception as e:
        print(e)
        return False
    else:

        writer = csv.writer(response)
        writer.writerows(row_list)
        return response

def row_to_json(row):
    json_ann = {}
    json_ann['username'] = row[0]
    json_ann['document_id'] =row[2]
    json_ann['batch'] = row[3]
    json_ann['collection_name'] = row[1]

    json_ann['insertion_time'] = row[21]
    json_ann['subject_start'] = row[4]
    json_ann['subject_stop'] = row[5]
    json_ann['subject_mention_location'] = row[6]
    json_ann['subject_mention_text'] = row[7]
    # json_ann['subject_concept_url'] = row[7]
    # json_ann['subject_concept_name'] = row[8]
    # json_ann['subject_area'] = row[9]
    json_ann['subject_concepts'] = row[8]
    json_ann['subject_tags'] = row[9]
    json_ann['predicate_start'] = row[10]
    json_ann['predicate_stop'] = row[11]
    json_ann['predicate_mention_location'] = row[12]

    json_ann['predicate_mention_text'] = row[13]
    json_ann['predicate_concepts'] = row[14]
    json_ann['predicate_tags'] = row[14]

    # json_ann['predicate_concept_url'] = row[13]
    # json_ann['predicate_concept_name'] = row[14]
    # json_ann['predicate_area'] = row[15]

    json_ann['object_start'] = row[15]
    json_ann['object_stop'] = row[16]
    json_ann['object_mention_location'] = row[17]

    json_ann['object_mention_text'] = row[18]

    json_ann['object_concepts'] = row[19]
    json_ann['object_tags'] = row[20]
    # json_ann['object_concept_url'] = row[19]
    # json_ann['object_concept_name'] = row[20]
    # json_ann['object_area'] = row[21]

    return json_ann

def relationshipsSubjMentionAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)

    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)

    row.append(d.batch)
    subject_mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
    js_ret = return_start_stop_for_frontend(subject_mention.start,subject_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(subject_mention.mention_text)
    concepts = Associate.objects.filter(start=subject_mention,stop = subject_mention.stop,document_id = d,username = annotation.username)


    subject_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        subject_concepts_list.append(concept_json)
    if subject_concepts_list == []:
        subject_concepts_list = None

    row.append(subject_concepts_list)
    predicate_concept_url = Concept.objects.get(concept_url=annotation.predicate_concept_url)
    predicate_area = SemanticArea.objects.get(name=annotation.predicate_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    predicate_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = predicate_concept_url.concept_url
    json_pred['concept_name'] = predicate_concept_url.concept_name
    json_pred['concept_area'] = predicate_area.name
    predicate_concepts_list.append(json_pred)
    row.append(predicate_concepts_list)
    # row.append(predicate_concept_url.concept_url)
    # row.append(predicate_concept_url.concept_name)
    # row.append(predicate_area.name)

    object_concept_url = Concept.objects.get(concept_url=annotation.object_concept_url)
    object_area = SemanticArea.objects.get(name=annotation.object_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    object_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = object_concept_url.concept_url
    json_pred['concept_name'] = object_concept_url.concept_name
    json_pred['concept_area'] = object_area.name
    object_concepts_list.append(json_pred)
    row.append(object_concepts_list)
    # row.append(object_concept_url.concept_url)
    # row.append(object_concept_url.concept_name)
    # row.append(object_area.name)
    row.append(annotation.insertion_time)
    return row

def relationshipsPredMentionAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)
    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)
    row.append(d.batch)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    concept = Concept.objects.get(concept_url = annotation.subject_concept_url)
    area = SemanticArea.objects.get(name= annotation.subject_name)
    # row.append(concept.concept_url)
    # row.append(concept.concept_name)
    # row.append(area.name)
    subject_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = concept.concept_url
    json_pred['concept_name'] = concept.concept_name
    json_pred['concept_area'] = area.name
    subject_concepts_list.append(json_pred)
    row.append(subject_concepts_list)

    predicate_mention = Mention.objects.get(document_id=d, start=annotation.start_id,
                                            stop=annotation.stop)
    js_ret = return_start_stop_for_frontend(predicate_mention.start,predicate_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(predicate_mention.mention_text)
    concepts = Associate.objects.filter(start=predicate_mention,stop = predicate_mention.stop,document_id = d,username = annotation.username)

    predicate_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        predicate_concepts_list.append(concept_json)
    if predicate_concepts_list == []:
        predicate_concepts_list = None

    row.append(predicate_concepts_list)
    object_concept_url = Concept.objects.get(concept_url=annotation.object_concept_url)
    object_area = SemanticArea.objects.get(name=annotation.object_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    # row.append(object_concept_url.concept_url)
    # row.append(object_concept_url.concept_name)
    # row.append(object_area.name)
    object_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = object_concept_url.concept_url
    json_pred['concept_name'] = object_concept_url.concept_name
    json_pred['concept_area'] = object_area.name
    object_concepts_list.append(json_pred)
    row.append(object_concepts_list)
    row.append(annotation.insertion_time)
    return row

def relationshipsObjMentionAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)
    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)
    row.append(d.batch)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    concept = Concept.objects.get(concept_url = annotation.subject_concept_url)
    area = SemanticArea.objects.get(name= annotation.subject_name)
    # row.append(concept.concept_url)
    # row.append(concept.concept_name)
    # row.append(area.name)
    subject_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = concept.concept_url
    json_pred['concept_name'] = concept.concept_name
    json_pred['concept_area'] = area.name
    subject_concepts_list.append(json_pred)
    row.append(subject_concepts_list)


    predicate_concept_url = Concept.objects.get(concept_url=annotation.predicate_concept_url)
    predicate_area = SemanticArea.objects.get(name=annotation.predicate_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    predicate_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = predicate_concept_url.concept_url
    json_pred['concept_name'] = predicate_concept_url.concept_name
    json_pred['concept_area'] = predicate_area.name
    predicate_concepts_list.append(json_pred)
    row.append(predicate_concepts_list)
    # row.append(predicate_concept_url.concept_url)
    # row.append(predicate_concept_url.concept_name)
    # row.append(predicate_area.name)

    object_mention = Mention.objects.get(document_id=d, start=annotation.start_id, stop=annotation.stop)
    js_ret = return_start_stop_for_frontend(object_mention.start,object_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(object_mention.mention_text)
    concepts = Associate.objects.filter(start=object_mention,stop = object_mention.stop,document_id = d,username = annotation.username)

    object_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        object_concepts_list.append(concept_json)
    if object_concepts_list == []:
        object_concepts_list = None

    row.append(object_concepts_list)
    row.append(annotation.insertion_time)
    return row

def relationshipsSubjConceptAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)
    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)

    row.append(d.batch)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    concept = Concept.objects.get(concept_url = annotation.concept_url_id)
    area = SemanticArea.objects.get(name= annotation.name_id)
    # row.append(concept.concept_url)
    # row.append(concept.concept_name)
    # row.append(area.name)
    subject_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = concept.concept_url
    json_pred['concept_name'] = concept.concept_name
    json_pred['concept_area'] = area.name
    subject_concepts_list.append(json_pred)
    row.append(subject_concepts_list)
    row.append(None)
    predicate_mention = Mention.objects.get(document_id=d, start=annotation.predicate_start,
                                            stop=annotation.predicate_stop)
    js_ret = return_start_stop_for_frontend(predicate_mention.start,predicate_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(predicate_mention.mention_text)
    concepts = Associate.objects.filter(start=predicate_mention,stop = predicate_mention.stop,document_id = d,username = annotation.username)

    predicate_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        predicate_concepts_list.append(concept_json)
    if predicate_concepts_list == []:
        predicate_concepts_list = None

    row.append(predicate_concepts_list)
    tags = AssociateTag.objects.filter(start=predicate_mention, stop=predicate_mention.stop, document_id=d,
                                        username=annotation.username)

    predicate_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        predicate_tags_list.append(tag_json)
    if predicate_tags_list == []:
        predicate_tags_list = None
    row.append(predicate_tags_list)

    object_mention = Mention.objects.get(document_id=d, start=annotation.object_start, stop=annotation.object_stop)
    js_ret = return_start_stop_for_frontend(object_mention.start,object_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(object_mention.mention_text)
    concepts = Associate.objects.filter(start=object_mention,stop = object_mention.stop,document_id = d,username = annotation.username)

    object_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        object_concepts_list.append(concept_json)
    if object_concepts_list == []:
        object_concepts_list = None

    row.append(object_concepts_list)
    tags = AssociateTag.objects.filter(start=object_mention, stop=object_mention.stop, document_id=d,
                                        username=annotation.username)

    object_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        object_tags_list.append(tag_json)
    if object_tags_list == []:
        object_tags_list = None
    row.append(object_tags_list)
    row.append(annotation.insertion_time)
    return row




def relationshipsObjConceptAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)

    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)


    row.append(d.batch)
    subject_mention = Mention.objects.get(document_id=d, start=annotation.subject_start, stop=annotation.subject_stop)
    js_ret = return_start_stop_for_frontend(subject_mention.start,subject_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(subject_mention.mention_text)
    concepts = Associate.objects.filter(start=subject_mention,stop = subject_mention.stop,document_id = d,username = annotation.username)

    subject_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        subject_concepts_list.append(concept_json)
    if subject_concepts_list == []:
        subject_concepts_list = None

    row.append(subject_concepts_list)
    tags = AssociateTag.objects.filter(start=subject_mention, stop=subject_mention.stop, document_id=d,
                                        username=annotation.username)

    subject_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        subject_tags_list.append(tag_json)
    if subject_tags_list == []:
        subject_tags_list = None
    row.append(subject_tags_list)

    predicate_mention = Mention.objects.get(document_id=d, start=annotation.predicate_start,
                                            stop=annotation.predicate_stop)
    js_ret = return_start_stop_for_frontend(predicate_mention.start,predicate_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(predicate_mention.mention_text)
    concepts = Associate.objects.filter(start=predicate_mention,stop = predicate_mention.stop,document_id = d,username = annotation.username)
    predicate_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        concept_json['concept_area'] = concept.name_id
        predicate_concepts_list.append(concept_json)
    if predicate_concepts_list == []:
        predicate_concepts_list = None

    row.append(predicate_concepts_list)
    tags = AssociateTag.objects.filter(start=predicate_mention, stop=predicate_mention.stop, document_id=d,
                                        username=annotation.username)

    predicate_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        predicate_tags_list.append(tag_json)
    if predicate_tags_list == []:
        predicate_tags_list = None
    row.append(predicate_tags_list)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    concept = Concept.objects.get(concept_url=annotation.concept_url_id)
    area = SemanticArea.objects.get(name=annotation.name_id)
    # row.append(concept.concept_url)
    # row.append(concept.concept_name)
    # row.append(area.name)
    object_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = concept.concept_url
    json_pred['concept_name'] = concept.concept_name
    json_pred['concept_area'] = area.name
    object_concepts_list.append(json_pred)
    row.append(object_concepts_list)
    row.append(None)
    row.append(annotation.insertion_time)
    return row

def relationshipsPredConceptAnnotations(annotation, d, collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)
    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)

    row.append(d.batch)
    subject_mention = Mention.objects.get(document_id=d, start=annotation.subject_start, stop=annotation.subject_stop)
    js_ret = return_start_stop_for_frontend(subject_mention.start,subject_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(subject_mention.mention_text)
    concepts = Associate.objects.filter(start=subject_mention,stop = subject_mention.stop,document_id = d,username = annotation.username)

    subject_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        subject_concepts_list.append(concept_json)

    if subject_concepts_list == []:
        subject_concepts_list = None
    row.append(subject_concepts_list)

    tags = AssociateTag.objects.filter(start=subject_mention, stop=subject_mention.stop, document_id=d,
                                        username=annotation.username)

    subject_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        subject_tags_list.append(tag_json)
    if subject_tags_list == []:
        subject_tags_list = None
    row.append(subject_tags_list)


    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    concept = Concept.objects.get(concept_url = annotation.concept_url_id)
    area = SemanticArea.objects.get(name= annotation.name_id)
    # row.append(concept.concept_url)
    # row.append(concept.concept_name)
    # row.append(area.name)
    predicate_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = concept.concept_url
    json_pred['concept_name'] = concept.concept_name
    json_pred['concept_area'] = area.name
    predicate_concepts_list.append(json_pred)
    row.append(predicate_concepts_list)

    object_mention = Mention.objects.get(document_id=d, start=annotation.object_start, stop=annotation.object_stop)
    js_ret = return_start_stop_for_frontend(object_mention.start,object_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(object_mention.mention_text)
    concepts = Associate.objects.filter(start=object_mention,stop = object_mention.stop,document_id = d,username = annotation.username)

    object_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        object_concepts_list.append(concept_json)
    if object_concepts_list == []:
        object_concepts_list = None

    row.append(object_concepts_list)
    tags = AssociateTag.objects.filter(start=object_mention, stop=object_mention.stop, document_id=d,
                                        username=annotation.username)

    object_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        object_tags_list.append(tag_json)
    if object_tags_list == []:
        object_tags_list = None
    row.append(object_tags_list)

    row.append(annotation.insertion_time)
    return row


def relationshipsLinkAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)
    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)

    row.append(d.batch)
    subject_mention = Mention.objects.get(document_id=d, start=annotation.subject_start, stop=annotation.subject_stop)
    js_ret = return_start_stop_for_frontend(subject_mention.start,subject_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(subject_mention.mention_text)
    concepts = Associate.objects.filter(start=subject_mention, stop=subject_mention.stop, document_id=d,
                                        username=annotation.username)

    subject_concepts_list = []
    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        subject_concepts_list.append(concept_json)
    if subject_concepts_list == []:
        subject_concepts_list = None
    row.append(subject_concepts_list)


    tags = AssociateTag.objects.filter(start=subject_mention, stop=subject_mention.stop, document_id=d,
                                        username=annotation.username)

    subject_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        subject_tags_list.append(tag_json)
    if subject_tags_list == []:
        subject_tags_list = None
    row.append(subject_tags_list)

    predicate_mention = Mention.objects.get(document_id=d, start=annotation.predicate_start,
                                            stop=annotation.predicate_stop)
    js_ret = return_start_stop_for_frontend(predicate_mention.start,predicate_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(predicate_mention.mention_text)
    concepts = Associate.objects.filter(start=predicate_mention, stop=predicate_mention.stop, document_id=d,
                                        username=annotation.username)

    predicate_concepts_list = []
    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        predicate_concepts_list.append(concept_json)
    if predicate_concepts_list == []:
        predicate_concepts_list = None
    row.append(predicate_concepts_list)
    tags = AssociateTag.objects.filter(start=predicate_mention, stop=predicate_mention.stop, document_id=d,
                                        username=annotation.username)

    predicate_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        predicate_tags_list.append(tag_json)
    if predicate_tags_list == []:
        predicate_tags_list = None
    row.append(predicate_tags_list)


    object_mention = Mention.objects.get(document_id=d, start=annotation.object_start, stop=annotation.object_stop)
    js_ret = return_start_stop_for_frontend(object_mention.start,object_mention.stop,d.document_content)
    row.append(js_ret['start'])
    row.append(js_ret['stop'])
    row.append(js_ret['position'])
    row.append(object_mention.mention_text)
    concepts = Associate.objects.filter(start=object_mention, stop=object_mention.stop, document_id=d,
                                        username=annotation.username)

    object_concepts_list = []

    for concept in concepts:
        concept_json = {}
        concept_json['concept_url'] = concept.concept_url_id
        concept_json['concept_name'] = concept.concept_url.concept_name
        concept_json['concept_area'] = concept.name_id
        object_concepts_list.append(concept_json)
    if object_concepts_list == []:
        object_concepts_list = None

    row.append(object_concepts_list)
    tags = AssociateTag.objects.filter(start=object_mention, stop=object_mention.stop, document_id=d,
                                        username=annotation.username)

    object_tags_list = []
    for tag in tags:
        tag_json = {}
        tag_json['tag'] = tag.name_id
        object_tags_list.append(tag_json)
    if object_tags_list == []:
        object_tags_list = None
    row.append(object_tags_list)

    row.append(annotation.insertion_time)
    return row

def relationshipsFactsAnnotations(annotation,d,collection):
    row = []
    row.append(annotation.username_id)
    row.append(collection.name)

    if 'document_id' in list(d.document_content.keys()):
        row.append(d.document_content['document_id'])
    else:
        row.append(d.document_id)

    row.append(d.batch)
    subject_concept_url = Concept.objects.get(concept_url = annotation.subject_concept_url)
    subject_area = SemanticArea.objects.get(name = annotation.subject_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    subject_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = subject_concept_url.concept_url
    json_pred['concept_name'] = subject_concept_url.concept_name
    json_pred['concept_area'] = subject_area.name
    subject_concepts_list.append(json_pred)
    row.append(subject_concepts_list)
    # row.append(subject_concept_url.concept_url)
    # row.append(subject_concept_url.concept_name)
    # row.append(subject_area.name)


    predicate_concept_url = Concept.objects.get(concept_url = annotation.predicate_concept_url)
    predicate_area = SemanticArea.objects.get(name = annotation.predicate_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    predicate_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = predicate_concept_url.concept_url
    json_pred['concept_name'] = predicate_concept_url.concept_name
    json_pred['concept_area'] = predicate_area.name
    predicate_concepts_list.append(json_pred)
    row.append(predicate_concepts_list)
    # row.append(predicate_concept_url.concept_url)
    # row.append(predicate_concept_url.concept_name)
    # row.append(predicate_area.name)

    object_concept_url = Concept.objects.get(concept_url = annotation.object_concept_url)
    object_area = SemanticArea.objects.get(name = annotation.object_name)
    row.append(None)
    row.append(None)
    row.append(None)
    row.append(None)
    object_concepts_list = []
    json_pred = {}
    json_pred['concept_url'] = object_concept_url.concept_url
    json_pred['concept_name'] = object_concept_url.concept_name
    json_pred['concept_area'] = object_area.name
    object_concepts_list.append(json_pred)
    row.append(object_concepts_list)
    # row.append(object_concept_url.concept_url)
    # row.append(object_concept_url.concept_name)
    # row.append(object_area.name)

    row.append(annotation.insertion_time)
    return row

def decomp_rows_for_csv(row):
    subject_concepts = row[8]
    predicate_concepts = row[13]
    object_concepts = row[18]
    subject_concepts_url,subject_concepts_name,subject_concepts_area = ','.join([x['concept_url'] for x in subject_concepts]),','.join([x['concept_name'] for x in subject_concepts]),','.join([x['concept_area'] for x in subject_concepts])
    predicate_concepts_url,predicate_concepts_name,predicate_concepts_area = ','.join([x['concept_url'] for x in predicate_concepts]),','.join([x['concept_name'] for x in predicate_concepts]),','.join([x['concept_area'] for x in predicate_concepts])
    object_concepts_url,object_concepts_name,object_concepts_area = ','.join([x['concept_url'] for x in object_concepts]),','.join([x['concept_name'] for x in object_concepts]),','.join([x['concept_area'] for x in object_concepts])
    row = []
    row.append(subject_concepts_url)
    row.append(subject_concepts_name)
    row.append(subject_concepts_area)
    row.append(predicate_concepts_url)
    row.append(predicate_concepts_name)
    row.append(predicate_concepts_area)
    row.append(object_concepts_url)
    row.append(object_concepts_name)
    row.append(object_concepts_area)
    return row


