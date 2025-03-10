from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
import hashlib

from numpy.ma.extras import hsplit

from doctron import settings
from doctron_app.upload.utils_upload import *
from doctron_app.upload.utils_pubmed import *

import json
import os
from doctron_app.models import *
from django.http import HttpResponse


def from_start_stop_foreach_key(document_content,start = None, stop = None):

    """This method returns a json where for each json key the start and stop is returned"""

    json_dict = {}
    json_dict['key'] = {}
    json_dict['value'] = {}

    # TO DO AGGIUNGO CHIAVI ANNOTABILI NEL JSON
    document_content_string = json.dumps(document_content)
    try:
        for key in list(document_content.keys()):
            # print(report_json[key])
            if (document_content.get(key) is not None and document_content.get(key) != ""):
                # cerco la chiave
                k = '"' + key + '":'
                if document_content_string.index(k) >= 0:
                    start_k = document_content_string.index(k) + 1
                    end_k = start_k + len(key) - 1
                    json_dict['key'][key] = {'text': key, 'start': start_k, 'stop': end_k,'position':str(key)+'_key'}

                element = document_content[key]
                element_1 = json.dumps(element)
                if element_1.startswith('"') and element_1.endswith('"'):
                    element_1 = element_1[1:-1]

                key_enriched = '"'+key+'":'
                before_element = document_content_string.split(key_enriched)[0]
                after_element = document_content_string.split(key_enriched)[1]
                #after_element = ''.join(document_content_string.split(key)[1:])
                until_element_value = len(before_element) + len(key_enriched) + len(after_element.split(str(element_1))[0])
                start_element = until_element_value
                end_element = start_element + len(str(element_1)) - 1
                element = {'text': element, 'start': start_element, 'stop': end_element,'position':str(key)+'_value'}
                json_dict['value'][key] = element


    except Exception as error:
        print(error)
        pass

    if start is not None and stop is not None:
        keys = list(json_dict['value'].keys())
        for k in keys:
            if start >= json_dict['value'][k]['start'] and stop <= json_dict['value'][k]['stop']:
                return json_dict['value'][k]
            elif start >= json_dict['key'][k]['start'] and stop <= json_dict['key'][k]['stop']:
                return json_dict['key'][k]
        return None

        # se non è qua è nelle keys!


    else:
        return json_dict


def get_fields_list(document_id,language):

    document = Document.objects.get(document_id = document_id,language = language)
    content_json = document.document_content
    keys = list(content_json.keys())
    return keys


def return_start_stop_for_frontend(start, stop, document_content):

    """This view takes the document content, the mention start and stop indices and returns the start, stop for js ranges selection"""

    # stringify the content
    # json_string = json.dumps(document_content)

    # get the json key where the mention is
    to_ret = {}
    json_val = from_start_stop_foreach_key(document_content,start,stop)
    try:
        to_ret['start'] = start - json_val['start']
    except Exception as e:
        print(start,stop)
    to_ret['stop'] = stop - json_val['start'] # quando individuo il range in js l'ultimo indice è escluso.
    to_ret['position'] = json_val['position']

    return to_ret


def return_start_stop_for_backend(start, stop, position, document_content):

    """This view takes the document content, the mention start and stop indices of the frontend and returns the start, stop for django"""

    json_start_stop = from_start_stop_foreach_key(document_content)
    mention_start, mention_stop = 0,0
    json_keys = {}
    if position.endswith('_value'):
        json_keys = json_start_stop['value']

    elif position.endswith('_key'):
        json_keys = json_start_stop['key']

    for k in list(json_keys.keys()):
        if json_keys[k]['position'] == position:
            mention_start = start + json_keys[k]['start']
            mention_stop = json_keys[k]['start'] + stop   # js mi ritorna sempre come finale il primo indice non incluso, lo devo togliere
            # print(json_keys[k]['text'][start:stop])
            # if mention_start > int(json_keys[k]['stop']):
                # print('\n\n')
                # print(json_keys[k]['text'])
                # breakpoint()

    return mention_start,mention_stop

def generate_objects_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    c = 0
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = AnnotateObject.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document, language=language).order_by('insertion_time')
    for annotation in annotations:
        obj = DocumentObject.objects.get(document_id=document, points=annotation.points, language=language)
        # mention = annotation.start

        json_m = {}


        # json_m['concepts'] = []
        json_m['object_id'] = 'object_'+str(c)
        c += 1
        json_m['object'] = obj.points

        json_m['labels'] = {}
        labels = CollectionHasLabel.objects.filter(collection_id = document.collection_id,passage_annotation = True)
        for label in labels:
            json_m['labels'][label.label_id] = None
        annotations = AnnotateObjectLabel.objects.filter(username = user,name_space = name_space,document_id=document,points = annotation.points)
        for a in annotations:
            json_m['labels'][a.label_id] = int(a.grade)


        json_m['time'] = str(annotation.insertion_time).split('.')[0:-1][0]

        json_mentions.append(json_m)
    return json_mentions

def generate_mentions_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    c = 0
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = Annotate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document, language=language).order_by('insertion_time')
    for annotation in annotations:
        mention = Mention.objects.get(document_id=document, start=annotation.start_id,stop=annotation.stop, language=language)
        # mention = annotation.start

        json_m = {}
        testo = mention.mention_text
        json_m['mention_text'] = testo
        start = mention.start
        stop = mention.stop
        json_mention = return_start_stop_for_frontend(start, stop, document.document_content)
        if gt == False:
            json_m['start'] = json_mention['start']
            json_m['stop'] = json_mention['stop']
        else:
            json_m['start'] =start
            json_m['stop'] = stop

        # json_m['concepts'] = []
        json_m['mentions'] = 'mention_'+str(c)
        c += 1
        json_m['position'] = json_mention['position']

        json_m['labels'] = {}
        labels = CollectionHasLabel.objects.filter(collection_id = document.collection_id,passage_annotation = True)
        for label in labels:
            json_m['labels'][label.label_id] = None
        annotations = AnnotatePassage.objects.filter(username = user,name_space = name_space,document_id=document,start = mention,stop = mention.stop)
        for a in annotations:
            json_m['labels'][a.label_id] = int(a.grade)


        json_m['time'] = str(annotation.insertion_time).split('.')[0:-1][0]

        json_mentions.append(json_m)
    return json_mentions

def generate_mentions_list_iaa(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    c = 0
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    document = Document.objects.get(document_id=document, language=language)
    users = AnnotatePassage.objects.filter(document_id=document,topic_id=topic)
    users = list(set([u.username_id for u in users]))

    annotations = AnnotatePassage.objects.filter(topic_id=topic, document_id=document, language=language).values("document_id","topic_id", "start", "stop").distinct()

    for annotation in annotations:
        mention = Mention.objects.get(document_id=document, start=annotation['start'],stop=annotation['stop'], language=language)
        json_m = {}
        testo = mention.mention_text
        json_m['mention_text'] = testo
        start = mention.start
        stop = mention.stop
        json_mention = return_start_stop_for_frontend(start, stop, document.document_content)
        if gt == False:
            json_m['start'] = json_mention['start']
            json_m['stop'] = json_mention['stop']
        else:
            json_m['start'] =start
            json_m['stop'] = stop

        # json_m['concepts'] = []
        json_m['mentions'] = 'mention_'+str(c)
        c += 1
        json_m['position'] = json_mention['position']

        json_m['labels'] = {}
        labels = CollectionHasLabel.objects.filter(collection_id = document.collection_id,passage_annotation = True)
        for label in labels:
            json_m['labels'][label.label_id] = None
            
        annotations = AnnotatePassage.objects.filter(document_id=document,topic_id=topic,start = mention,stop = mention.stop).distinct("document_id","topic_id","start","stop","label","grade")
        app = False
        for a in annotations:
            if AnnotatePassage.objects.filter(document_id=document,topic_id=topic,start = mention,stop = mention.stop,label=a.label,grade=a.grade).count() > len(users) / 2:
                json_m['labels'][a.label_id] = int(a.grade)
                json_m['time'] = str(a.insertion_time).split('.')[0:-1][0]
                app = True



        if app:
            json_mentions.append(json_m)
    return json_mentions




def generate_objects_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    c = 0
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = AnnotateObject.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document, language=language).order_by('insertion_time')
    for annotation in annotations:
        points = annotation.points

        json_m = {}
        json_m['points'] = points



        json_m['labels'] = {}
        labels = CollectionHasLabel.objects.filter(collection_id = document.collection_id,passage_annotation = True)
        for label in labels:
            json_m['labels'][label.label_id] = None

        annotations = AnnotateObjectLabel.objects.filter(document_id=document,username = user,name_space = name_space,points = points)
        for a in annotations:
            json_m['labels'][a.label_id] = int(a.grade)


        json_m['time'] = str(annotation.insertion_time).split('.')[0:-1][0]

        json_mentions.append(json_m)
    return json_mentions


# def generate_mentions_list_splitted(username,name_space,document,language,topic):
#
#     """This view returns the list of mentions spllited according to the textual content"""
#
#     json_mentions = []
#     c = 0
#
#     name_space = NameSpace.objects.get(name_space=name_space)
#     topic = Topic.objects.get(id=topic)
#     user = User.objects.get(username=username, name_space=name_space)
#     document = Document.objects.get(document_id=document, language=language)
#     final_mentions_list = find_overlapping_mentions(document, user,topic)
#
#     return final_mentions_list


def send_email(email,subject,message):
    try:
        # subject = f"Welcome {name} {surname}"
        # message = f"Welcome {name} {surname},\nYou have just registered in CRANE with the email: {email}.\n\nThe CRANE Team"
        if isinstance(email,str):
            email = [email]

        res = send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            email,
            fail_silently=False,
        )
        print('result',res)
        return True
    except Exception as e:
        print(e)
        return False

def validate_password(password):
    # Check length
    if len(password) < 8:
        return False

    # Check for at least one number
    if not re.search(r'\d', password):
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()-=_+[\]{};:,.<>/?]', password):
        return False

    return True

def generate_tag_list(username,name_space,document,language,topic,gt=False):
    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    topic = Topic.objects.get(id=topic)
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = Annotate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    c = 0
    for annotation_mention in annotations:

        mention = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                      stop=annotation_mention.stop, language=language)
        # mention = annotation.start
        if AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                    language=language, start=mention, stop=mention.stop).exists():
            annotations_concepts = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                            language=language, start=mention, stop=mention.stop)
            for annotation in annotations_concepts:
                json_m = {}

                testo = mention.mention_text
                json_m['mention_text'] = testo
                # print(mention.mention_text)
                start = mention.start
                stop = mention.stop
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                if gt == False:
                    json_m['start'] = json_mention['start']
                    json_m['stop'] = json_mention['stop']
                else:
                    json_m['start'] = start
                    json_m['stop'] = stop
                json_m['mentions'] = 'mention_' + str(c)

                json_m['position'] = json_mention['position']
                json_m['tag'] = {}
                json_m['tag']['area'] = annotation.name_id

                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1][0]
                json_mentions.append(json_m)
        c += 1
    return json_mentions

def generate_associations_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = Annotate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    c = 0
    for annotation_mention in annotations:

        mention = Mention.objects.get(document_id=document, start=annotation_mention.start_id,stop=annotation_mention.stop, language=language)
        # mention = annotation.start
        if Associate.objects.filter(username=user, topic_id=topic,name_space=name_space, document_id=document,
                                            language=language, start = mention, stop = mention.stop).exists():
            annotations_concepts = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                            language=language, start = mention, stop = mention.stop)
            for annotation in annotations_concepts:
                json_m = {}

                testo = mention.mention_text
                json_m['mention_text'] = testo
                # print(mention.mention_text)
                start = mention.start
                stop = mention.stop
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                if gt == False:
                    json_m['start'] = json_mention['start']
                    json_m['stop'] = json_mention['stop']
                else:
                    json_m['start'] = start
                    json_m['stop'] = stop
                json_m['mentions'] = 'mention_'+str(c)

                json_m['position'] = json_mention['position']
                concept = annotation.concept_url
                json_m['concept'] = {}
                json_m['concept']['concept_url'] = concept.concept_url
                json_m['concept']['concept_name'] = concept.concept_name
                json_m['concept']['concept_description'] = concept.description
                json_m['concept']['area'] = annotation.name_id



                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1][0]
            # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
                json_mentions.append(json_m)
        c += 1
    return json_mentions



def delete_old_relationship(source_mention,predicate_mention,target_mention,source,target,predicate,collection,document,language,user,name_space,topic):

    """This method removes a specific relationship"""

    if source_mention != {} and  source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention != {} and predicate_mention[
        'start'] is not None and predicate_mention['stop'] is not None and target_mention != {} and target_mention['start'] is not None and \
            target_mention['stop'] is not None:
        start_source, stop_source = return_start_stop_for_backend(source_mention['start'], source_mention['stop'],
                                                                  source_mention['position'], document.document_content)
        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        start_target, stop_target = return_start_stop_for_backend(target_mention['start'], target_mention['stop'],
                                                                  target_mention['position'], document.document_content)
        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate, stop=stop_predicate)
        target_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)

        rel = Link.objects.filter(username=user, name_space=name_space, subject_document_id=document.document_id,
                                  subject_language=language, predicate_document_id=document.document_id,
                                  predicate_language=language, object_document_id=document.document_id,
                                  object_language=language,topic_id=topic,
                                  subject_start=source_mention.start, subject_stop=source_mention.stop,
                                  predicate_start=predicate_mention.start, predicate_stop=predicate_mention.stop,
                                  object_start=target_mention.start, object_stop=target_mention.stop)
        if  rel.exists():
            rel.delete()
    # CASO 2: S: MENTION, P: MENTION, T: CONCEPT
    elif source_mention != {} and source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention != {}  and predicate_mention[
        'start'] is not None and predicate_mention['stop'] is not None and target_mention == {}:

        start_source, stop_source = return_start_stop_for_backend(source_mention['start'],
                                                                  source_mention['stop'],
                                                                  source_mention['position'],
                                                                  document.document_content)
        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)

        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate,
                                                stop=stop_predicate)

        target_concept = target['concept']
        target_area = target['concept']['concept_area']
        insert_if_missing(target_concept, target_area, user, collection)

        target_concept = Concept.objects.get(concept_url=target['concept']['concept_url'])
        target_area = SemanticArea.objects.get(name=target['concept']['concept_area'])

        rel = RelationshipObjConcept.objects.filter(username=user, name_space=name_space,
                                                    subject_document_id=document.document_id,
                                                    subject_language=language,topic_id=topic,
                                                    predicate_document_id=document.document_id,
                                                    predicate_language=language,
                                                    subject_start=source_mention.start,
                                                    subject_stop=source_mention.stop,
                                                    predicate_start=predicate_mention.start,
                                                    predicate_stop=predicate_mention.stop,
                                                    concept_url=target_concept, name=target_area)
        if  rel.exists():
            to_up = True

            rel.delete()
    # CASO 3: S: MENTION, P: CONCEPT, T: MENTION
    elif  source_mention != {} and source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention =={} and target_mention != {} and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_source, stop_source = return_start_stop_for_backend(source_mention['start'],
                                                                  source_mention['stop'],
                                                                  source_mention['position'],
                                                                  document.document_content)

        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)
        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)

        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)
        predicate_concept = predicate['concept']
        predicate_area = predicate['concept']['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        predicate_concept = Concept.objects.get(concept_url=predicate['concept']['concept_url'])
        predicate_area = SemanticArea.objects.get(name=predicate_area)

        rel = RelationshipPredConcept.objects.filter(username=user, name_space=name_space,
                                                     subject_document_id=document.document_id,
                                                     subject_language=language, object_language=language,
                                                     object_document_id=document.document_id,
                                                     subject_start=source_mention.start,topic_id=topic,
                                                     subject_stop=source_mention.stop,
                                                     object_start=object_mention.start, object_stop=object_mention.stop,
                                                     concept_url=predicate_concept, name=predicate_area)
        if  rel.exists():
            to_up = True

            rel.delete()

    # CASO 4: S: CONCEPT, P: MENTION, T: MENTION
    elif source_mention =={} and predicate_mention != {} and predicate_mention[
        'start'] is not None and predicate_mention[
        'stop'] is not None and target_mention != {} and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate,
                                                stop=stop_predicate)
        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)
        subject_concept = source['concept']
        subject_area = source['concept']['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)

        subject_concept = Concept.objects.get(concept_url=source['concept']['concept_url'])
        subject_area = SemanticArea.objects.get(name=source['concept']['concept_area'])

        rel = RelationshipSubjConcept.objects.filter(username=user, name_space=name_space,
                                                     predicate_document_id=document.document_id,
                                                     predicate_language=language, object_language=language,
                                                     object_document_id=document.document_id,topic_id=topic,
                                                     predicate_start=predicate_mention.start,
                                                     predicate_stop=predicate_mention.stop,
                                                     object_start=object_mention.start, object_stop=object_mention.stop,
                                                     concept_url=subject_concept, name=subject_area)
        if  rel.exists():
            to_up = True

            rel.delete()
    # CASO 5: S: CONCEPT, P: CONCEPT, T: MENTION
    elif source_mention == {} and predicate_mention == {} and target_mention != {} and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)

        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)

        subject_concept = source['concept']
        subject_area = source['concept']['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)
        predicate_concept = predicate['concept']
        predicate_area = predicate['concept']['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)

        rel = RelationshipObjMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                    language=language, start=object_mention, stop=object_mention.stop,
                                                    subject_concept_url=subject_concept['concept_url'],topic_id=topic,
                                                    predicate_concept_url=predicate_concept['concept_url'], subject_name=subject_area,
                                                    predicate_name=predicate_area)
        if  rel.exists():
            to_up = True

            rel.delete()
    # CASO 6: S: CONCEPT, P: MENTION, T: CONCEPT
    elif source_mention == {} and predicate_mention != {} and predicate_mention[
        'start'] is not None and predicate_mention[
        'stop'] is not None and target_mention == {}:

        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate, stop=stop_predicate)

        subject_concept = source['concept']
        subject_area = source['concept']['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)
        object_concept = target['concept']
        object_area = target['concept']['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = RelationshipPredMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                     language=language, start=predicate_mention,
                                                     stop=predicate_mention.stop,topic_id=topic,
                                                     subject_concept_url=subject_concept['concept_url'],
                                                     object_concept_url=object_concept['concept_url'],
                                                     subject_name=subject_area, object_name=object_area)
        if rel.exists():
            to_up = True

            rel.delete()
    # CASO 7: S: MENTION, P: CONCEPT, T: CONCEPT
    elif source_mention != {} and source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention == {} and target_mention == {}:
        start_source, stop_source = return_start_stop_for_backend(source_mention['start'], source_mention['stop'],
                                                                  source_mention['position'], document.document_content)
        subject_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)

        predicate_concept = predicate['concept']
        predicate_area = predicate['concept']['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        object_concept = target['concept']
        object_area = target['concept']['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = RelationshipSubjMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                     language=language, start=subject_mention,
                                                     stop=subject_mention.stop,topic_id=topic,
                                                     predicate_concept_url=predicate_concept['concept_url'],
                                                     object_concept_url=object_concept['concept_url'],
                                                     predicate_name=predicate_area, object_name=object_area)
        if rel.exists():
            to_up = True
            rel.delete()
    # CASO 8: S: CONCEPT, P: CONCEPT, T: CONCEPT
    elif source_mention == {} and predicate_mention == {} and target_mention == {}:

        source_concept = source['concept']
        source_area = source['concept']['concept_area']
        insert_if_missing(source_concept, source_area, user, collection)
        predicate_concept = predicate['concept']
        predicate_area = predicate['concept']['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        object_concept = target['concept']
        object_area = target['concept']['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = CreateFact.objects.filter(username=user, name_space=name_space, document_id=document,
                                        language=language,topic_id=topic,
                                        predicate_concept_url=predicate_concept['concept_url'],
                                        object_concept_url=object_concept['concept_url'],
                                        subject_concept_url=source_concept['concept_url'],
                                        predicate_name=predicate_area, subject_name=source_area,
                                        object_name=object_area)
        if  rel.exists():
            to_up = True

            rel.delete()



import copy



def transform_relationships_list(json_mentions,document_id,username,name_space):

    """This method receives in input a list of relationships and separates it basing on areas"""

    json_ment_areas = {}
    document = Document.objects.get(document_id=document_id)
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username = username,name_space = name_space)
    json_ment_areas['subject'] = {}
    json_ment_areas['predicate'] = {}
    json_ment_areas['object'] = {}


    for area_obj in SemanticArea.objects.all():
        area = area_obj.name
        json_ment_areas['subject'][area] = []
        json_ment_areas['predicate'][area] = []
        json_ment_areas['object'][area] = []
        json_ment_areas['all_mentions'] = []
        json_ment_areas['all_concepts'] = []
        for rel in json_mentions:

            source_con = rel['subject']['concept'].get('concept_area',None)
            pred_con = rel['predicate']['concept'].get('concept_area',None)
            tar_con = rel['object']['concept'].get('concept_area',None)

            source_men = rel['subject']['mention'].get('mention_text',None)
            pred_men = rel['predicate']['mention'].get('mention_text',None)
            tar_men = rel['object']['mention'].get('mention_text',None)

            if source_men is not None:
                source_start,source_stop = return_start_stop_for_backend(rel['subject']['mention']['start'],rel['subject']['mention']['stop'],rel['subject']['mention']['position'],document.document_content)
                source_ment = Mention.objects.get(document_id=document, start=source_start,
                                                  stop=source_stop)
                source_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = source_ment,stop = source_ment.stop)
                if source_anno.exists():
                    for s in source_anno:
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name

                        json_ment_areas['subject'][area_obj.name].append(new_rel)
            #
            if pred_men is not None:
                pred_start,pred_stop = return_start_stop_for_backend(rel['predicate']['mention']['start'],rel['predicate']['mention']['stop'],rel['predicate']['mention']['position'],document.document_content)

                pred_ment = Mention.objects.get(document_id=document, start=pred_start,
                                                  stop=pred_stop)
                pred_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = pred_ment,stop = pred_ment.stop)
                if pred_anno.exists():
                    # json_ment_areas['predicate'][area].append(rel)
                    for s in pred_anno:
                        # rel['anchor'] = s.concept_url.concept_name
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name
                        json_ment_areas['predicate'][area_obj.name].append(new_rel)
            #
            #
            if tar_men is not None:
                obj_start,obj_stop = return_start_stop_for_backend(rel['object']['mention']['start'],rel['object']['mention']['stop'],rel['object']['mention']['position'],document.document_content)

                target_ment = Mention.objects.get(document_id=document, start=obj_start,
                                                  stop=obj_stop)
                target_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = target_ment,stop = target_ment.stop)
                if target_anno.exists():
                    for s in target_anno:
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name
                        json_ment_areas['object'][area_obj.name].append(new_rel)

            if any(v is not None for v in [source_men,pred_men,tar_men]):
                # qui sono esclusivamente concetti
                if source_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['subject']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['subject']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['subject']['concept']['concept_area']
                    json_ment_areas['subject'][area].append(new_rel)

                if pred_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['predicate']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['predicate']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['predicate']['concept']['concept_area']
                    json_ment_areas['predicate'][area].append(new_rel)

                if  tar_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['object']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['object']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['object']['concept']['concept_area']
                    json_ment_areas['object'][area].append(new_rel)




                if tar_con == pred_con == source_con == None and None not in [source_men,tar_men,pred_men]:
                    source_ment = Mention.objects.get(document_id=document, start=source_start,
                                                      stop=source_stop)
                    pred_ment = Mention.objects.get(document_id=document, start=pred_start,
                                                  stop=pred_stop)
                    target_ment = Mention.objects.get(document_id=document, start=obj_start,
                                                      stop=obj_stop)

                    if not Associate.objects.filter(document_id = document, username = user, name_space = name_space, start = source_ment,stop = source_ment.stop).exists() and not Associate.objects.filter(document_id = document, username = user, name_space = name_space, start = pred_ment,stop = pred_ment.stop).exists() and not Associate.objects.filter(document_id=document, username=user, name_space=name_space, start=target_ment, stop=target_ment.stop).exists():
                        json_ment_areas['all_mentions'].append(rel)
            else:
                json_ment_areas['all_concepts'].append(rel)

    return json_ment_areas


def transform_relationships_list1(json_mentions,document_id,username,name_space):

    """This method receives in input a list of relationships and separates it basing on areas"""

    json_ment_areas = {}
    document = Document.objects.get(document_id=document_id)
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username = username,name_space = name_space)
    json_ment_areas['subject'] = {}
    json_ment_areas['predicate'] = {}
    json_ment_areas['object'] = {}


    for area_obj in SemanticArea.objects.all():
        area = area_obj.name
        json_ment_areas['subject'][area] = []
        json_ment_areas['predicate'][area] = []
        json_ment_areas['object'][area] = []
        json_ment_areas['all_mentions'] = []
        json_ment_areas['all_concepts'] = []
        for rel in json_mentions:

            source_con = rel['subject']['concept'].get('concept_area',None)
            pred_con = rel['predicate']['concept'].get('concept_area',None)
            tar_con = rel['object']['concept'].get('concept_area',None)

            source_men = rel['subject']['mention'].get('mention_text',None)
            pred_men = rel['predicate']['mention'].get('mention_text',None)
            tar_men = rel['object']['mention'].get('mention_text',None)

            if source_men is not None:
                source_start,source_stop = return_start_stop_for_backend(rel['subject']['mention']['start'],rel['subject']['mention']['stop'],rel['subject']['mention']['position'],document.document_content)
                source_ment = Mention.objects.get(document_id=document, start=source_start,
                                                  stop=source_stop)
                source_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = source_ment,stop = source_ment.stop)
                if source_anno.exists():
                    for s in source_anno:
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name

                        json_ment_areas['subject'][area_obj.name].append(new_rel)
            #
            if pred_men is not None:
                pred_start,pred_stop = return_start_stop_for_backend(rel['predicate']['mention']['start'],rel['predicate']['mention']['stop'],rel['predicate']['mention']['position'],document.document_content)

                pred_ment = Mention.objects.get(document_id=document, start=pred_start,
                                                  stop=pred_stop)
                pred_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = pred_ment,stop = pred_ment.stop)
                if pred_anno.exists():
                    # json_ment_areas['predicate'][area].append(rel)
                    for s in pred_anno:
                        # rel['anchor'] = s.concept_url.concept_name
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name
                        json_ment_areas['predicate'][area_obj.name].append(new_rel)
            #
            #
            if tar_men is not None:
                obj_start,obj_stop = return_start_stop_for_backend(rel['object']['mention']['start'],rel['object']['mention']['stop'],rel['object']['mention']['position'],document.document_content)

                target_ment = Mention.objects.get(document_id=document, start=obj_start,
                                                  stop=obj_stop)
                target_anno = Associate.objects.filter(name=area_obj,username = user, name_space = name_space, document_id = document, start = target_ment,stop = target_ment.stop)
                if target_anno.exists():
                    for s in target_anno:
                        new_rel = copy.deepcopy(rel)
                        new_rel['anchor'] = s.concept_url.concept_name
                        new_rel['anchor_url'] = s.concept_url.concept_url
                        new_rel['anchor_area'] = s.name.name
                        json_ment_areas['object'][area_obj.name].append(new_rel)

            if any(v is not None for v in [source_men,pred_men,tar_men]):
                # qui sono esclusivamente concetti
                if source_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['subject']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['subject']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['subject']['concept']['concept_area']
                    json_ment_areas['subject'][area].append(new_rel)

                if pred_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['predicate']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['predicate']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['predicate']['concept']['concept_area']
                    json_ment_areas['predicate'][area].append(new_rel)

                if  tar_con == area:
                    new_rel = copy.deepcopy(rel)

                    new_rel['anchor'] = rel['object']['concept']['concept_name']
                    new_rel['anchor_url'] = rel['object']['concept']['concept_url']
                    new_rel['anchor_area'] = rel['object']['concept']['concept_area']
                    json_ment_areas['object'][area].append(new_rel)




                if tar_con == pred_con == source_con == None and None not in [source_men,tar_men,pred_men]:
                    source_ment = Mention.objects.get(document_id=document, start=source_start,
                                                      stop=source_stop)
                    pred_ment = Mention.objects.get(document_id=document, start=pred_start,
                                                  stop=pred_stop)
                    target_ment = Mention.objects.get(document_id=document, start=obj_start,
                                                      stop=obj_stop)

                    if not Associate.objects.filter(document_id = document, username = user, name_space = name_space, start = source_ment,stop = source_ment.stop).exists() and not Associate.objects.filter(document_id = document, username = user, name_space = name_space, start = pred_ment,stop = pred_ment.stop).exists() and not Associate.objects.filter(document_id=document, username=user, name_space=name_space, start=target_ment, stop=target_ment.stop).exists():
                        json_ment_areas['all_mentions'].append(rel)
            else:
                json_ment_areas['all_concepts'].append(rel)

    return json_ment_areas



def insert_new_relationship_if_exists(source_mention,predicate_mention,target_mention,source,target,predicate,collection,document,language,user,name_space,topic):

    if source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention[
        'start'] is not None and predicate_mention['stop'] is not None and target_mention['start'] is not None and \
            target_mention['stop'] is not None:
        start_source, stop_source = return_start_stop_for_backend(source_mention['start'], source_mention['stop'],
                                                                  source_mention['position'], document.document_content)
        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        start_target, stop_target = return_start_stop_for_backend(target_mention['start'], target_mention['stop'],
                                                                  target_mention['position'], document.document_content)
        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate, stop=stop_predicate)
        target_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)

        rel = Link.objects.filter(username=user, name_space=name_space, subject_document_id=document.document_id,
                                  subject_language=language, predicate_document_id=document.document_id,
                                  predicate_language=language, object_document_id=document.document_id,
                                  object_language=language,topic_id=topic,
                                  subject_start=source_mention.start, subject_stop=source_mention.stop,
                                  predicate_start=predicate_mention.start, predicate_stop=predicate_mention.stop,
                                  object_start=target_mention.start, object_stop=target_mention.stop)
        if not rel.exists():
            to_up = True
            Link.objects.create(username=user, name_space=name_space, subject_document_id=document.document_id,
                                subject_language=language, object_document_id=document.document_id,
                                object_language=language, predicate_document_id=document.document_id,
                                predicate_language=language, insertion_time=Now(),topic_id=topic,
                                subject_start=source_mention.start, subject_stop=source_mention.stop,
                                predicate_start=predicate_mention.start, predicate_stop=predicate_mention.stop,
                                object_start=target_mention.start, object_stop=target_mention.stop)
    # CASO 2: S: MENTION, P: MENTION, T: CONCEPT
    elif source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention[
        'start'] is not None and predicate_mention[
        'stop'] is not None and target_mention['start'] is None and target_mention['stop'] is None:

        start_source, stop_source = return_start_stop_for_backend(source_mention['start'],
                                                                  source_mention['stop'],
                                                                  source_mention['position'],
                                                                  document.document_content)
        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)

        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate,
                                                stop=stop_predicate)

        target_concept = target['concepts'][0]
        target_area = target['concepts'][0]['concept_area']
        insert_if_missing(target_concept, target_area, user, collection)

        target_concept = Concept.objects.get(concept_url=target['concepts'][0]['concept_url'])
        target_area = SemanticArea.objects.get(name=target['concepts'][0]['concept_area'])

        rel = RelationshipObjConcept.objects.filter(username=user, name_space=name_space,
                                                    subject_document_id=document.document_id,
                                                    subject_language=language,
                                                    predicate_document_id=document.document_id,
                                                    predicate_language=language,topic_id=topic,
                                                    subject_start=source_mention.start,
                                                    subject_stop=source_mention.stop,
                                                    predicate_start=predicate_mention.start,
                                                    predicate_stop=predicate_mention.stop,
                                                    concept_url=target_concept, name=target_area)
        if not rel.exists():
            to_up = True

            RelationshipObjConcept.objects.create(username=user, name_space=name_space,
                                                  subject_document_id=document.document_id,
                                                  predicate_document_id=document.document_id,
                                                  predicate_language=document.language,
                                                  subject_language=language, insertion_time=Now(),
                                                  subject_start=source_mention.start,topic_id=topic,
                                                  subject_stop=source_mention.stop,
                                                  predicate_start=predicate_mention.start,
                                                  predicate_stop=predicate_mention.stop,
                                                  concept_url=target_concept, name=target_area)
    # CASO 3: S: MENTION, P: CONCEPT, T: MENTION
    elif source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention[
        'start'] is None and predicate_mention[
        'stop'] is None and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_source, stop_source = return_start_stop_for_backend(source_mention['start'],
                                                                  source_mention['stop'],
                                                                  source_mention['position'],
                                                                  document.document_content)

        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)
        source_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)

        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)
        predicate_concept = predicate['concepts'][0]
        predicate_area = predicate['concepts'][0]['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        predicate_concept = Concept.objects.get(concept_url=predicate['concepts'][0]['concept_url'])
        predicate_area = SemanticArea.objects.get(name=predicate_area)

        rel = RelationshipPredConcept.objects.filter(username=user, name_space=name_space,
                                                     subject_document_id=document.document_id,
                                                     subject_language=language, object_language=language,
                                                     object_document_id=document.document_id,topic_id=topic,
                                                     subject_start=source_mention.start,
                                                     subject_stop=source_mention.stop,
                                                     object_start=object_mention.start, object_stop=object_mention.stop,
                                                     concept_url=predicate_concept, name=predicate_area)
        if not rel.exists():
            to_up = True

            RelationshipPredConcept.objects.create(username=user, name_space=name_space,
                                                   subject_document_id=document.document_id,
                                                   subject_language=language, object_language=language,
                                                   object_document_id=document.document_id,topic_id=topic,
                                                   subject_start=source_mention.start, insertion_time=Now(),
                                                   subject_stop=source_mention.stop,
                                                   object_start=object_mention.start, object_stop=object_mention.stop,
                                                   concept_url=predicate_concept, name=predicate_area)

    # CASO 4: S: CONCEPT, P: MENTION, T: MENTION
    elif source_mention['start'] is None and source_mention['stop'] is None and predicate_mention[
        'start'] is not None and predicate_mention[
        'stop'] is not None and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate,
                                                stop=stop_predicate)
        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)
        subject_concept = source['concepts'][0]
        subject_area = source['concepts'][0]['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)

        subject_concept = Concept.objects.get(concept_url=source['concepts'][0]['concept_url'])
        subject_area = SemanticArea.objects.get(name=source['concepts'][0]['concept_area'])

        rel = RelationshipSubjConcept.objects.filter(username=user, name_space=name_space,
                                                     predicate_document_id=document.document_id,
                                                     predicate_language=language, object_language=language,
                                                     object_document_id=document.document_id,topic_id=topic,
                                                     predicate_start=predicate_mention.start,
                                                     predicate_stop=predicate_mention.stop,
                                                     object_start=object_mention.start, object_stop=object_mention.stop,
                                                     concept_url=subject_concept, name=subject_area)
        if not rel.exists():
            to_up = True

            RelationshipSubjConcept.objects.create(username=user, name_space=name_space,
                                                   predicate_document_id=document.document_id,
                                                   predicate_language=language, object_language=language,
                                                   object_document_id=document.document_id,topic_id=topic,
                                                   predicate_start=predicate_mention.start,
                                                   predicate_stop=predicate_mention.stop, insertion_time=Now(),
                                                   object_start=object_mention.start, object_stop=object_mention.stop,
                                                   concept_url=subject_concept, name=subject_area)
    # CASO 5: S: CONCEPT, P: CONCEPT, T: MENTION
    elif source_mention['start'] is None and source_mention['stop'] is None and predicate_mention['start'] is None and \
            predicate_mention[
                'stop'] is None and target_mention['start'] is not None and target_mention['stop'] is not None:

        start_target, stop_target = return_start_stop_for_backend(target_mention['start'],
                                                                  target_mention['stop'],
                                                                  target_mention['position'],
                                                                  document.document_content)

        object_mention = Mention.objects.get(document_id=document, start=start_target, stop=stop_target)

        subject_concept = source['concepts'][0]
        subject_area = source['concepts'][0]['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)
        predicate_concept = predicate['concepts'][0]
        predicate_area = predicate['concepts'][0]['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)

        rel = RelationshipObjMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                    language=language, start=object_mention, stop=object_mention.stop,
                                                    subject_concept_url=subject_concept,topic_id=topic,
                                                    predicate_concept_url=predicate_concept, subject_name=subject_area,
                                                    predicate_name=predicate_area)
        if not rel.exists():
            to_up = True

            RelationshipObjMention.objects.create(username=user, name_space=name_space, document_id=document,
                                                  language=language, start=object_mention,topic_id=topic,
                                                  stop=object_mention.stop, insertion_time=Now(),
                                                  subject_concept_url=subject_concept['concept_url'],
                                                  predicate_concept_url=predicate_concept['concept_url'],
                                                  subject_name=subject_area, predicate_name=predicate_area)
    # CASO 6: S: CONCEPT, P: MENTION, T: CONCEPT
    elif source_mention['start'] is None and source_mention['stop'] is None and predicate_mention[
        'start'] is not None and predicate_mention[
        'stop'] is not None and target_mention['start'] is None and target_mention['stop'] is None:

        start_predicate, stop_predicate = return_start_stop_for_backend(predicate_mention['start'],
                                                                        predicate_mention['stop'],
                                                                        predicate_mention['position'],
                                                                        document.document_content)
        predicate_mention = Mention.objects.get(document_id=document, start=start_predicate, stop=stop_predicate)

        subject_concept = source['concepts'][0]
        subject_area = source['concepts'][0]['concept_area']
        insert_if_missing(subject_concept, subject_area, user, collection)
        object_concept = target['concepts'][0]
        object_area = target['concepts'][0]['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = RelationshipPredMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                     language=language, start=predicate_mention,
                                                     stop=predicate_mention.stop,topic_id=topic,
                                                     subject_concept_url=subject_concept['concept_url'],
                                                     object_concept_url=object_concept['concept_url'],
                                                     subject_name=subject_area, object_name=object_area)
        if not rel.exists():
            to_up = True

            RelationshipPredMention.objects.create(username=user, name_space=name_space, document_id=document,
                                                   language=language, start=predicate_mention,topic_id=topic,
                                                   stop=predicate_mention.stop, insertion_time=Now(),
                                                   subject_concept_url=subject_concept['concept_url'],
                                                   object_concept_url=object_concept['concept_url'],
                                                   subject_name=subject_area, object_name=object_area)
    # CASO 7: S: MENTION, P: CONCEPT, T: CONCEPT
    elif source_mention['start'] is not None and source_mention['stop'] is not None and predicate_mention[
        'start'] is None and predicate_mention[
        'stop'] is None and target_mention['start'] is None and target_mention['stop'] is None:
        start_source, stop_source = return_start_stop_for_backend(source_mention['start'], source_mention['stop'],
                                                                  source_mention['position'], document.document_content)
        subject_mention = Mention.objects.get(document_id=document, start=start_source, stop=stop_source)

        predicate_concept = predicate['concepts'][0]
        predicate_area = predicate['concepts'][0]['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        object_concept = target['concepts'][0]
        object_area = target['concepts'][0]['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = RelationshipSubjMention.objects.filter(username=user, name_space=name_space, document_id=document,
                                                     language=language, start=subject_mention,
                                                     stop=subject_mention.stop,topic_id=topic,
                                                     predicate_concept_url=predicate_concept['concept_url'],
                                                     object_concept_url=object_concept['concept_url'],
                                                     predicate_name=predicate_area, object_name=object_area)
        if not rel.exists():
            to_up = True

            RelationshipSubjMention.objects.create(username=user, name_space=name_space, document_id=document,
                                                   language=language, start=subject_mention,topic_id=topic,
                                                   stop=subject_mention.stop, insertion_time=Now(),
                                                   predicate_concept_url=predicate_concept['concept_url'],
                                                   object_concept_url=object_concept['concept_url'],
                                                   predicate_name=predicate_area, object_name=object_area)
    # CASO 8: S: CONCEPT, P: CONCEPT, T: CONCEPT
    elif source_mention['start'] is None and source_mention['stop'] is None and predicate_mention['start'] is None and \
            predicate_mention[
                'stop'] is None and target_mention['start'] is None and target_mention['stop'] is None:

        source_concept = source['concepts'][0]
        source_area = source['concepts'][0]['concept_area']
        insert_if_missing(source_concept, source_area, user, collection)
        predicate_concept = predicate['concepts'][0]
        predicate_area = predicate['concepts'][0]['concept_area']
        insert_if_missing(predicate_concept, predicate_area, user, collection)
        object_concept = target['concepts'][0]
        object_area = target['concepts'][0]['concept_area']
        insert_if_missing(object_concept, object_area, user, collection)

        rel = CreateFact.objects.filter(username=user, name_space=name_space, document_id=document,
                                        language=language,topic_id=topic,
                                        predicate_concept_url=predicate_concept['concept_url'],
                                        object_concept_url=object_concept['concept_url'],
                                        subject_concept_url=source_concept['concept_url'],
                                        predicate_name=predicate_area, subject_name=source_area,
                                        object_name=object_area)
        if not rel.exists():
            to_up = True

            CreateFact.objects.create(username=user, name_space=name_space, document_id=document,
                                      language=language, insertion_time=Now(),topic_id=topic,
                                      predicate_concept_url=predicate_concept['concept_url'],
                                      object_concept_url=object_concept['concept_url'],
                                      subject_concept_url=source_concept['concept_url'],
                                      predicate_name=predicate_area, subject_name=source_area, object_name=object_area)


def generate_relationships_list_iaa(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    #todo
    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)

    link_annotations = Link.objects.filter(username=user, name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')
    objment_annotations = RelationshipObjMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    subjment_annotations = RelationshipSubjMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    predment_annotations = RelationshipPredMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    predconc_annotations = RelationshipPredConcept.objects.filter(username=user,topic_id=topic, name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')
    subjcon_annotations = RelationshipSubjConcept.objects.filter(username=user,topic_id=topic, name_space=name_space, object_document_id=document.document_id,
                                          object_language=language).order_by('insertion_time')
    objcon_annotations = RelationshipObjConcept.objects.filter(username=user,topic_id=topic,name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')



    # TUTTO MENTION
    c = 0
    for annotation_mention in link_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}
        json_m['text'] = ''

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,stop=annotation_mention.subject_stop, language=language)
        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,stop=annotation_mention.predicate_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,stop=annotation_mention.object_stop, language=language)

        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start
        count_rel = Link.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        object_document_id=document.document_id, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop, predicate_language=language,
                                        name_space=name_space).count()


        testo_source = mention_source.mention_text
        testo_pred = mention_predicate.mention_text
        testo_target = mention_target.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['object']['mention']['start'] = mention_target.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        json_m['object']['mention']['stop'] = mention_target.stop
        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop, document.document_content)
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop, document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop, document.document_content)



        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']


        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['predicate']['mention']['position'] = json_mention_predicate['position']
        json_m['object']['mention']['position'] = json_mention_target['position']

        source_txt = json_m['subject']['mention']['mention_text']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = concepts_source.first().concept_name

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = concepts_target.first().concept_name

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']


        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

    # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1


    # MENTION MENTION CONCETTO
    c = 0
    for annotation_mention in objcon_annotations:

        json_m = {}
        json_m['start'] = -1
        # per ogni relazione o ho mention o concetto SINGOLO. questo prescinde dall'avere più concetti associati a una mention
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,
                                             stop=annotation_mention.subject_stop, language=language)
        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,
                                                stop=annotation_mention.predicate_stop, language=language)
        count_rel = RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop, predicate_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        # mention = annotation.start

        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)

        testo_source = mention_source.mention_text
        testo_pred = mention_predicate.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start

        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['predicate']['mention']['stop'] = mention_predicate.stop

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop,
                                                             document.document_content)
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                                document.document_content)

        source_txt = json_m['subject']['mention']['mention_text']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']



        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['predicate']['mention']['position'] = json_mention_predicate['position']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']
        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']


        concept = annotation_mention.concept_url
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept.concept_url
        json_m['object']['concept']['concept_name'] = concept.concept_name
        json_m['object']['concept']['concept_description'] = concept.description
        json_m['object']['concept']['concept_area'] = annotation_mention.name_id
        target_txt = json_m['object']['concept']['concept_name']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # MENTION CONCETTO MENTION
    c = 0
    for annotation_mention in predconc_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,stop=annotation_mention.subject_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,stop=annotation_mention.object_stop, language=language)
        # mention = annotation.start
        count_rel = RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        object_document_id=document.document_id, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        testo_source = mention_source.mention_text
        testo_target = mention_target.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start

        json_m['object']['mention']['start'] = mention_target.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['object']['mention']['stop'] = mention_target.stop

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop, document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop, document.document_content)

        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']


        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['object']['mention']['position'] = json_mention_target['position']
        source_txt = json_m['subject']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        concept = annotation_mention.concept_url
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept.concept_url
        json_m['predicate']['concept']['concept_name'] = concept.concept_name
        json_m['predicate']['concept']['concept_description'] = concept.description
        json_m['predicate']['concept']['concept_area'] = annotation_mention.name_id
        predicate_txt = json_m['predicate']['concept']['concept_name']


        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']
        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1



    # CONCETTO MENTION MENTION
    c = 0
    for annotation_mention in subjcon_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,
                                                stop=annotation_mention.predicate_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,
                                             stop=annotation_mention.object_stop, language=language)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start
        count_rel = RelationshipSubjConcept.objects.filter(predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop,predicate_language=language,
                                        object_document_id=document.document_id,topic_id=topic, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        testo_pred = mention_predicate.mention_text
        testo_target = mention_target.mention_text
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['object']['mention']['start'] = mention_target.start
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        json_m['object']['mention']['stop'] = mention_target.stop
        json_m['start'] = mention_predicate.start

        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                                document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop,
                                                             document.document_content)

        if gt == False:
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']

        json_m['predicate']['mention']['position'] = json_mention_predicate['position']
        json_m['object']['mention']['position'] = json_mention_target['position']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        concept = annotation_mention.concept_url
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept.concept_url
        json_m['subject']['concept']['concept_name'] = concept.concept_name
        json_m['subject']['concept']['concept_description'] = concept.description
        json_m['subject']['concept']['concept_area'] = annotation_mention.name_id
        source_txt = json_m['subject']['concept']['concept_name']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # CONCETTO CONCETTO MENTION
    c = 0
    for annotation_mention in objment_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)

        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start

        testo_target = mention_target.mention_text
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['object']['mention']['start'] = mention_target.start
        json_m['object']['mention']['stop'] = mention_target.stop
        json_m['start'] = mention_target.start
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop,
                                                             document.document_content)

        if gt == False:
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']

        json_m['object']['mention']['position'] = json_mention_target['position']
        target_txt = json_m['object']['mention']['mention_text']

        concept_subject = Concept.objects.get(concept_url = annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_predicate = Concept.objects.get(concept_url = annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)

        count_rel = RelationshipObjMention.objects.filter(document_id=document,topic_id=topic, start=mention_target,stop=mention_target.stop,language=language,
                                        name_space=name_space,subject_concept_url = annotation_mention.subject_concept_url,
                                                          subject_name = annotation_mention.subject_name,
                                                          predicate_concept_url = annotation_mention.predicate_concept_url,
                                                          predicate_name=annotation_mention.predicate_name).count()

        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        source_txt = json_m['subject']['concept']['concept_name']

        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']
        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt =  json_m['object']['tag']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # CONCETTO MENTION CONCETTO
    c = 0
    for annotation_mention in predment_annotations:

        json_m = {}
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}
        json_m['start'] = -1

        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        # mention = annotation.start
        json_m['start'] = mention_predicate.start
        testo_target = mention_predicate.mention_text
        json_m['predicate']['mention']['mention_text'] = testo_target
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        predicate_txt = json_m['predicate']['mention']['mention_text']
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                             document.document_content)

        if gt == False:
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']

        json_m['predicate']['mention']['position'] = json_mention_predicate['position']

        concept_subject = Concept.objects.get(concept_url=annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = RelationshipPredMention.objects.filter(document_id=document,topic_id=topic, start=mention_predicate,stop=mention_predicate.stop,language=language,
                                        name_space=name_space,subject_concept_url = annotation_mention.subject_concept_url,
                                                          subject_name = annotation_mention.subject_name,
                                                          object_concept_url = annotation_mention.object_concept_url,
                                                          object_name=annotation_mention.object_name).count()
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name
        target_txt = json_m['object']['concept']['concept_name']
        source_txt = json_m['subject']['concept']['concept_name']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

        # MENTION CONCETTO CONCETTO
    c = 0
    for annotation_mention in subjment_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)
        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)

        # mention = annotation.start

        testo_target = mention_source.mention_text
        json_m['subject']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['start'] = mention_source.start

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop,
                                                             document.document_content)

        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']

        json_m['subject']['mention']['position'] = json_mention_source['position']
        source_txt = json_m['subject']['mention']['mention_text']

        concept_predicate = Concept.objects.get(concept_url=annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = RelationshipSubjMention.objects.filter(document_id=document,topic_id=topic, start=mention_source,stop=mention_source.stop,language=language,
                                        name_space=name_space,predicate_concept_url = annotation_mention.predicate_concept_url,
                                                          predicate_name = annotation_mention.predicate_name,
                                                          object_concept_url = annotation_mention.object_concept_url,
                                                          object_name=annotation_mention.object_name).count()
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        predicate_txt = json_m['predicate']['concept']['concept_name']

        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name
        target_txt = json_m['object']['concept']['concept_name']

        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1][0]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        if count_rel == 0:
            print('')
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1
    json_mentions = sorted(json_mentions, key=lambda k: k['start'], reverse=False)

    return json_mentions


def generate_relationships_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    # associations = Associate.objects.filter(username=user, name_space=name_space, document_id=document,
    #                                         language=language)
    link_annotations = Link.objects.filter(username=user,topic_id=topic, name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')
    objment_annotations = RelationshipObjMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    subjment_annotations = RelationshipSubjMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    predment_annotations = RelationshipPredMention.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    predconc_annotations = RelationshipPredConcept.objects.filter(username=user,topic_id=topic, name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')
    subjcon_annotations = RelationshipSubjConcept.objects.filter(username=user,topic_id=topic, name_space=name_space, object_document_id=document.document_id,
                                          object_language=language).order_by('insertion_time')
    objcon_annotations = RelationshipObjConcept.objects.filter(username=user,topic_id=topic,name_space=name_space, subject_document_id=document.document_id,
                                          subject_language=language).order_by('insertion_time')



    # TUTTO MENTION
    c = 0
    for annotation_mention in link_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}
        json_m['text'] = ''

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,stop=annotation_mention.subject_stop, language=language)
        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,stop=annotation_mention.predicate_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,stop=annotation_mention.object_stop, language=language)

        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start
        count_rel = Link.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        object_document_id=document.document_id, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop, predicate_language=language,
                                        name_space=name_space).count()


        testo_source = mention_source.mention_text
        testo_pred = mention_predicate.mention_text
        testo_target = mention_target.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['object']['mention']['start'] = mention_target.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        json_m['object']['mention']['stop'] = mention_target.stop
        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop, document.document_content)
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop, document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop, document.document_content)



        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']


        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['predicate']['mention']['position'] = json_mention_predicate['position']
        json_m['object']['mention']['position'] = json_mention_target['position']

        source_txt = json_m['subject']['mention']['mention_text']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = concepts_source.first().concept_name

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = concepts_target.first().concept_name

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']


        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

    # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1


    # MENTION MENTION CONCETTO
    c = 0
    for annotation_mention in objcon_annotations:

        json_m = {}
        json_m['start'] = -1
        # per ogni relazione o ho mention o concetto SINGOLO. questo prescinde dall'avere più concetti associati a una mention
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,
                                             stop=annotation_mention.subject_stop, language=language)
        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,
                                                stop=annotation_mention.predicate_stop, language=language)
        count_rel = RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop, predicate_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        # mention = annotation.start

        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)

        testo_source = mention_source.mention_text
        testo_pred = mention_predicate.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start

        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['predicate']['mention']['stop'] = mention_predicate.stop

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop,
                                                             document.document_content)
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                                document.document_content)

        source_txt = json_m['subject']['mention']['mention_text']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']



        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['predicate']['mention']['position'] = json_mention_predicate['position']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']
        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']


        concept = annotation_mention.concept_url
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept.concept_url
        json_m['object']['concept']['concept_name'] = concept.concept_name
        json_m['object']['concept']['concept_description'] = concept.description
        json_m['object']['concept']['concept_area'] = annotation_mention.name_id
        target_txt = json_m['object']['concept']['concept_name']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # MENTION CONCETTO MENTION
    c = 0
    for annotation_mention in predconc_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.subject_start,stop=annotation_mention.subject_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,stop=annotation_mention.object_stop, language=language)
        # mention = annotation.start
        count_rel = RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,topic_id=topic, subject_start=annotation_mention.subject_start,subject_stop=annotation_mention.subject_stop, subject_language=language,
                                        object_document_id=document.document_id, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        testo_source = mention_source.mention_text
        testo_target = mention_target.mention_text
        json_m['subject']['mention']['mention_text'] = testo_source
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['start'] = mention_source.start

        json_m['object']['mention']['start'] = mention_target.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['object']['mention']['stop'] = mention_target.stop

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop, document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop, document.document_content)

        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']


        json_m['subject']['mention']['position'] = json_mention_source['position']
        json_m['object']['mention']['position'] = json_mention_target['position']
        source_txt = json_m['subject']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        concept = annotation_mention.concept_url
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept.concept_url
        json_m['predicate']['concept']['concept_name'] = concept.concept_name
        json_m['predicate']['concept']['concept_description'] = concept.description
        json_m['predicate']['concept']['concept_area'] = annotation_mention.name_id
        predicate_txt = json_m['predicate']['concept']['concept_name']


        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']
        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1



    # CONCETTO MENTION MENTION
    c = 0
    for annotation_mention in subjcon_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.predicate_start,
                                                stop=annotation_mention.predicate_stop, language=language)
        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.object_start,
                                             stop=annotation_mention.object_stop, language=language)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start
        count_rel = RelationshipSubjConcept.objects.filter(predicate_document_id=document.document_id, predicate_start=annotation_mention.predicate_start,predicate_stop=annotation_mention.predicate_stop,predicate_language=language,
                                        object_document_id=document.document_id,topic_id=topic, object_start=annotation_mention.object_start,object_stop=annotation_mention.object_stop, object_language=language,
                                        name_space=name_space,name=annotation_mention.name,concept_url = annotation_mention.concept_url).count()
        testo_pred = mention_predicate.mention_text
        testo_target = mention_target.mention_text
        json_m['predicate']['mention']['mention_text'] = testo_pred
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['object']['mention']['start'] = mention_target.start
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        json_m['object']['mention']['stop'] = mention_target.stop
        json_m['start'] = mention_predicate.start

        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                                document.document_content)
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop,
                                                             document.document_content)

        if gt == False:
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']

        json_m['predicate']['mention']['position'] = json_mention_predicate['position']
        json_m['object']['mention']['position'] = json_mention_target['position']
        predicate_txt = json_m['predicate']['mention']['mention_text']
        target_txt = json_m['object']['mention']['mention_text']

        concept = annotation_mention.concept_url
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept.concept_url
        json_m['subject']['concept']['concept_name'] = concept.concept_name
        json_m['subject']['concept']['concept_description'] = concept.description
        json_m['subject']['concept']['concept_area'] = annotation_mention.name_id
        source_txt = json_m['subject']['concept']['concept_name']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']

        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt = json_m['object']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # CONCETTO CONCETTO MENTION
    c = 0
    for annotation_mention in objment_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}


        mention_target = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)

        tags_target = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_target, stop=mention_target.stop)
        concepts_target = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_target, stop=mention_target.stop)
        # mention = annotation.start

        testo_target = mention_target.mention_text
        json_m['object']['mention']['mention_text'] = testo_target
        json_m['object']['mention']['start'] = mention_target.start
        json_m['object']['mention']['stop'] = mention_target.stop
        json_m['start'] = mention_target.start
        json_mention_target = return_start_stop_for_frontend(mention_target.start, mention_target.stop,
                                                             document.document_content)

        if gt == False:
            json_m['object']['mention']['start'] = json_mention_target['start']
            json_m['object']['mention']['stop'] = json_mention_target['stop']

        json_m['object']['mention']['position'] = json_mention_target['position']
        target_txt = json_m['object']['mention']['mention_text']

        concept_subject = Concept.objects.get(concept_url = annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_predicate = Concept.objects.get(concept_url = annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)

        count_rel = RelationshipObjMention.objects.filter(document_id=document,topic_id=topic, start=mention_target,stop=mention_target.stop,language=language,
                                        name_space=name_space,subject_concept_url = annotation_mention.subject_concept_url,
                                                          subject_name = annotation_mention.subject_name,
                                                          predicate_concept_url = annotation_mention.predicate_concept_url,
                                                          predicate_name=annotation_mention.predicate_name).count()

        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        source_txt = json_m['subject']['concept']['concept_name']

        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        predicate_txt = json_m['predicate']['concept']['concept_name']

        if concepts_target.exists():
            json_m['object']['concept']['concept_url'] = concepts_target.first().concept_url_id
            json_m['object']['concept']['concept_name'] = concepts_target.first().concept_name
            json_m['object']['concept']['concept_description'] = concepts_target.first().description
            json_m['object']['concept']['concept_area'] = concepts_target.first().name_id
            target_txt = json_m['object']['concept']['concept_name']
        if tags_target.exists():
            json_m['object']['tag'] = tags_target.first().name_id
            target_txt =  json_m['object']['tag']

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

    # CONCETTO MENTION CONCETTO
    c = 0
    for annotation_mention in predment_annotations:

        json_m = {}
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}
        json_m['start'] = -1

        mention_predicate = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)
        tags_predicate = AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                  start=mention_predicate, stop=mention_predicate.stop)
        concepts_predicate = Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                                   start=mention_predicate, stop=mention_predicate.stop)
        # mention = annotation.start
        json_m['start'] = mention_predicate.start
        testo_target = mention_predicate.mention_text
        json_m['predicate']['mention']['mention_text'] = testo_target
        json_m['predicate']['mention']['start'] = mention_predicate.start
        json_m['predicate']['mention']['stop'] = mention_predicate.stop
        predicate_txt = json_m['predicate']['mention']['mention_text']
        json_mention_predicate = return_start_stop_for_frontend(mention_predicate.start, mention_predicate.stop,
                                                             document.document_content)

        if gt == False:
            json_m['predicate']['mention']['start'] = json_mention_predicate['start']
            json_m['predicate']['mention']['stop'] = json_mention_predicate['stop']

        json_m['predicate']['mention']['position'] = json_mention_predicate['position']

        concept_subject = Concept.objects.get(concept_url=annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = RelationshipPredMention.objects.filter(document_id=document,topic_id=topic, start=mention_predicate,stop=mention_predicate.stop,language=language,
                                        name_space=name_space,subject_concept_url = annotation_mention.subject_concept_url,
                                                          subject_name = annotation_mention.subject_name,
                                                          object_concept_url = annotation_mention.object_concept_url,
                                                          object_name=annotation_mention.object_name).count()
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name
        target_txt = json_m['object']['concept']['concept_name']
        source_txt = json_m['subject']['concept']['concept_name']

        if concepts_predicate.exists():
            json_m['predicate']['concept']['concept_url'] = concepts_predicate.first().concept_url_id
            json_m['predicate']['concept']['concept_name'] = concepts_predicate.first().concept_name
            json_m['predicate']['concept']['concept_description'] = concepts_predicate.first().description
            json_m['predicate']['concept']['concept_area'] = concepts_predicate.first().name_id
            predicate_txt = json_m['predicate']['concept']['concept_name']

        if tags_predicate.exists():
            json_m['predicate']['tag'] = tags_predicate.first().name_id
            predicate_txt = json_m['predicate']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1

        # MENTION CONCETTO CONCETTO
    c = 0
    for annotation_mention in subjment_annotations:

        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        mention_source = Mention.objects.get(document_id=document, start=annotation_mention.start_id,
                                             stop=annotation_mention.stop, language=language)
        tags_source = AssociateTag.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)
        concepts_source = Associate.objects.filter(username=user,topic_id=topic,name_space=name_space,document_id=document,start=mention_source,stop=mention_source.stop)

        # mention = annotation.start

        testo_target = mention_source.mention_text
        json_m['subject']['mention']['mention_text'] = testo_target
        json_m['subject']['mention']['start'] = mention_source.start
        json_m['subject']['mention']['stop'] = mention_source.stop
        json_m['start'] = mention_source.start

        json_mention_source = return_start_stop_for_frontend(mention_source.start, mention_source.stop,
                                                             document.document_content)

        if gt == False:
            json_m['subject']['mention']['start'] = json_mention_source['start']
            json_m['subject']['mention']['stop'] = json_mention_source['stop']

        json_m['subject']['mention']['position'] = json_mention_source['position']
        source_txt = json_m['subject']['mention']['mention_text']

        concept_predicate = Concept.objects.get(concept_url=annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = RelationshipSubjMention.objects.filter(document_id=document,topic_id=topic, start=mention_source,stop=mention_source.stop,language=language,
                                        name_space=name_space,predicate_concept_url = annotation_mention.predicate_concept_url,
                                                          predicate_name = annotation_mention.predicate_name,
                                                          object_concept_url = annotation_mention.object_concept_url,
                                                          object_name=annotation_mention.object_name).count()
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        predicate_txt = json_m['predicate']['concept']['concept_name']

        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name
        target_txt = json_m['object']['concept']['concept_name']

        if concepts_source.exists():
            json_m['subject']['concept']['concept_url'] = concepts_source.first().concept_url_id
            json_m['subject']['concept']['concept_name'] = concepts_source.first().concept_name
            json_m['subject']['concept']['concept_description'] = concepts_source.first().description
            json_m['subject']['concept']['concept_area'] = concepts_source.first().name_id
            source_txt = json_m['subject']['concept']['concept_name']

        if tags_source.exists():
            json_m['subject']['tag'] = tags_source.first().name_id
            source_txt = json_m['subject']['tag']
        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1][0]
        json_m['count'] = count_rel
        json_m['text'] = f'{source_txt} - {predicate_txt} - {target_txt}'

        if count_rel == 0:
            print('')
        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)
        c += 1
    json_mentions = sorted(json_mentions, key=lambda k: k['start'], reverse=False)

    return json_mentions

def generate_assertions_list(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)

    facts_annotations = CreateFact.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')



    for annotation_mention in facts_annotations:
        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        concept_predicate = Concept.objects.get(concept_url=annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)
        concept_subject = Concept.objects.get(concept_url=annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = CreateFact.objects.filter(document_id=annotation_mention.document_id, language = annotation_mention.language,
                                              subject_concept_url = annotation_mention.subject_concept_url,predicate_concept_url = annotation_mention.predicate_concept_url,
                                              object_concept_url = annotation_mention.object_concept_url,subject_name=annotation_mention.subject_name,predicate_name = annotation_mention.predicate_name,
                                              object_name=annotation_mention.object_name).count()
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name

        json_m['text'] = f'{concept_subject.concept_name} - {concept_predicate.concept_name} - {concept_target.concept_name}'

        json_m['time'] = str(annotation_mention.insertion_time).split('.')[0:-1]
        json_m['count'] = count_rel

        # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
        json_mentions.append(json_m)



    json_mentions = sorted(json_mentions, key=lambda k: k['start'], reverse=False)



    return json_mentions

def generate_assertions_list_iaa(username,name_space,document,language,topic,gt=False):

    """This view returns the list of metnions annotated by a user for a document"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)

    users = CreateFact.objects.filter(topic_id=topic, document_id=document,
                                          language=language)
    users = list(set([u.username_id for u in users]))

    facts_annotations = CreateFact.objects.filter(topic_id=topic, document_id=document, language=language).values("document_id","topic_id", "subject_concept_url", "object_concept_url","predicate_concept_url", "subject_name", "object_name","predicate_name").distinct()


    for annotation_mention in facts_annotations:
        json_m = {}
        json_m['start'] = -1
        json_m['subject'] = {}
        json_m['subject']['mention'] = {}
        json_m['subject']['concept'] = {}
        json_m['subject']['tag'] = {}
        json_m['predicate'] = {}
        json_m['predicate']['mention'] = {}
        json_m['predicate']['concept'] = {}
        json_m['predicate']['tag'] = {}
        json_m['object'] = {}
        json_m['object']['mention'] = {}
        json_m['object']['concept'] = {}
        json_m['object']['tag'] = {}

        concept_predicate = Concept.objects.get(concept_url=annotation_mention.predicate_concept_url)
        predicate_area = SemanticArea.objects.get(name=annotation_mention.predicate_name)
        concept_subject = Concept.objects.get(concept_url=annotation_mention.subject_concept_url)
        subject_area = SemanticArea.objects.get(name=annotation_mention.subject_name)
        concept_target = Concept.objects.get(concept_url=annotation_mention.object_concept_url)
        target_area = SemanticArea.objects.get(name=annotation_mention.object_name)
        count_rel = CreateFact.objects.filter(document_id=annotation_mention.document_id, language = annotation_mention.language,
                                              subject_concept_url = annotation_mention.subject_concept_url,predicate_concept_url = annotation_mention.predicate_concept_url,
                                              object_concept_url = annotation_mention.object_concept_url,subject_name=annotation_mention.subject_name,predicate_name = annotation_mention.predicate_name,
                                              object_name=annotation_mention.object_name).count()
        json_m['subject']['concept'] = {}
        json_m['subject']['concept']['concept_url'] = concept_subject.concept_url
        json_m['subject']['concept']['concept_name'] = concept_subject.concept_name
        json_m['subject']['concept']['concept_description'] = concept_subject.description
        json_m['subject']['concept']['concept_area'] = subject_area.name
        json_m['predicate']['concept'] = {}
        json_m['predicate']['concept']['concept_url'] = concept_predicate.concept_url
        json_m['predicate']['concept']['concept_name'] = concept_predicate.concept_name
        json_m['predicate']['concept']['concept_description'] = concept_predicate.description
        json_m['predicate']['concept']['concept_area'] = predicate_area.name
        json_m['object']['concept'] = {}
        json_m['object']['concept']['concept_url'] = concept_target.concept_url
        json_m['object']['concept']['concept_name'] = concept_target.concept_name
        json_m['object']['concept']['concept_description'] = concept_target.description
        json_m['object']['concept']['concept_area'] = target_area.name

        json_m['text'] = f'{concept_subject.concept_name} - {concept_predicate.concept_name} - {concept_target.concept_name}'

        json_m['time'] = ''
        json_m['count'] = count_rel
        if count_rel >= len(users) / 2:
            json_mentions.append(json_m)



    json_mentions = sorted(json_mentions, key=lambda k: k['start'], reverse=False)



    return json_mentions


def generate_tag_list_splitted(username,name_space,document,language,topic):

    """This view returns the list of metnions annotated by a user for a document. Mentions are splitted as they are in the frontend (done for overlapping)"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = Annotate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                          language=language).order_by('insertion_time')
    c = 0

    final_mentions_list = find_overlapping_mentions(document,user,topic)

    for annotation_mention in annotations:

        mention = Mention.objects.get(document_id=document, start=annotation_mention.start_id,stop=annotation_mention.stop, language=language)
        # mention = annotation.start
        if AssociateTag.objects.filter(username=user, name_space=name_space, document_id=document,topic_id=topic,
                                            language=language, start = mention, stop = mention.stop).exists():
            annotations_concepts = AssociateTag.objects.filter(username=user, name_space=name_space, document_id=document,topic_id=topic,
                                            language=language, start = mention, stop = mention.stop)
            for annotation in annotations_concepts:
                json_m = {}


                json_m['mentions'] = 'mention_' + str(c)
                # json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                filtered_mention_splitted = [x for x in final_mentions_list if [json_m['mentions']] == x['overlap']] # deve esserci per forza
                if filtered_mention_splitted == []: # in questo caso è full overlapped
                    filtered_mention_splitted = [x for x in final_mentions_list if json_m['mentions'] in x['overlap']]
                filtered_mention_splitted = filtered_mention_splitted[0]

                start = filtered_mention_splitted['start']
                stop = filtered_mention_splitted['stop']
                json_m['mention_text'] = filtered_mention_splitted['mention_text']
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                json_m['start'] = json_mention['start']
                json_m['stop'] = json_mention['stop']


                json_m['position'] = json_mention['position']
                json_m['tag'] = {}
                json_m['tag']['area'] = annotation.name_id

                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1]
                json_mentions.append(json_m)
        c += 1
    return json_mentions

def generate_tag_list_splitted_iaa(username,name_space,document,language,topic):

    """This view returns the list of metnions annotated by a user for a document. Mentions are splitted as they are in the frontend (done for overlapping)"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    users = AssociateTag.objects.filter(topic_id=topic, document_id=document, language=language)
    users = list(set([u.username_id for u in users]))
    annotations = AssociateTag.objects.filter(topic_id=topic, document_id=document, language=language).values("document_id","topic_id", "start", "stop").distinct()

    c = 0

    final_mentions_list = find_overlapping_mentions(document,user,topic)

    for annotation_mention in annotations:

        mention = Mention.objects.get(document_id=document, start=annotation_mention['start'],stop=annotation_mention['stop'], language=language)
        if AssociateTag.objects.filter( document_id=document,topic_id=topic,
                                            language=language, start = mention, stop = mention.stop).exists():
            annotations_concepts = AssociateTag.objects.filter( document_id=document,topic_id=topic,
                                            language=language, start = mention, stop = mention.stop)
            for annotation in annotations_concepts:
                json_m = {}


                json_m['mentions'] = 'mention_' + str(c)
                # json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                filtered_mention_splitted = [x for x in final_mentions_list if [json_m['mentions']] == x['overlap']] # deve esserci per forza
                if filtered_mention_splitted == []: # in questo caso è full overlapped
                    filtered_mention_splitted = [x for x in final_mentions_list if json_m['mentions'] in x['overlap']]
                filtered_mention_splitted = filtered_mention_splitted[0]

                start = filtered_mention_splitted['start']
                stop = filtered_mention_splitted['stop']
                json_m['mention_text'] = filtered_mention_splitted['mention_text']
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                json_m['start'] = json_mention['start']
                json_m['stop'] = json_mention['stop']


                json_m['position'] = json_mention['position']
                json_m['tag'] = {}
                json_m['tag']['area'] = annotation.name_id
                

                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1]
                
                if AssociateTag.objects.filter( document_id=document,topic_id=topic,start=mention,name=annotation.name).count() > len(users) /2:
                    json_mentions.append(json_m)
        c += 1
    return json_mentions



def generate_associations_list_splitted(username,name_space,document,language,topic):

    """This view returns the list of metnions annotated by a user for a document. Mentions are splitted as they are in the frontend (done for overlapping)"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    annotations = Annotate.objects.filter(username=user, name_space=name_space, document_id=document,topic_id=topic,
                                          language=language).order_by('insertion_time')
    c = 0

    final_mentions_list = find_overlapping_mentions(document,user,topic)

    for annotation_mention in annotations:

        mention = Mention.objects.get(document_id=document, start=annotation_mention.start_id,stop=annotation_mention.stop, language=language)
        # mention = annotation.start
        if Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document,
                                            language=language, start = mention, stop = mention.stop).exists():
            annotations_concepts = Associate.objects.filter(username=user, name_space=name_space, document_id=document,
                                            language=language, topic_id=topic,start = mention, stop = mention.stop)
            for annotation in annotations_concepts:
                json_m = {}


                json_m['mentions'] = 'mention_' + str(c)
                # json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                filtered_mention_splitted = [x for x in final_mentions_list if [json_m['mentions']] == x['overlap']] # deve esserci per forza
                if filtered_mention_splitted == []: # in questo caso è full overlapped
                    filtered_mention_splitted = [x for x in final_mentions_list if json_m['mentions'] in x['overlap']]
                filtered_mention_splitted = filtered_mention_splitted[0]

                start = filtered_mention_splitted['start']
                stop = filtered_mention_splitted['stop']
                json_m['mention_text'] = filtered_mention_splitted['mention_text']
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                json_m['start'] = json_mention['start']
                json_m['stop'] = json_mention['stop']


                json_m['position'] = json_mention['position']
                concept = annotation.concept_url
                json_m['concept'] = {}
                json_m['concept']['concept_url'] = concept.concept_url
                json_m['concept']['concept_name'] = concept.concept_name
                json_m['concept']['concept_description'] = concept.description
                json_m['concept']['area'] = annotation.name_id
                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1]
                json_mentions.append(json_m)
        c += 1
    return json_mentions

def generate_associations_list_splitted_iaa(username,name_space,document,language,topic):

    """This view returns the list of metnions annotated by a user for a document. Mentions are splitted as they are in the frontend (done for overlapping)"""

    json_mentions = []
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    c = 0
    users = AssociateTag.objects.filter(topic_id=topic, document_id=document, language=language)
    users = list(set([u.username_id for u in users]))
    annotations = Associate.objects.filter(topic_id=topic, document_id=document, language=language).values("document_id","topic_id", "start", "stop").distinct()

    final_mentions_list = find_overlapping_mentions(document,user,topic)


    for annotation_mention in annotations:

            mention = Mention.objects.get(document_id=document, start=annotation_mention['start'],stop=annotation_mention['stop'], language=language)

            annotations_concepts = Associate.objects.filter( document_id=document,
                                            language=language, topic_id=topic,start = mention, stop = mention.stop).distinct('start','stop','document_id','topic_id')
            for annotation in annotations_concepts:
                json_m = {}


                json_m['mentions'] = 'mention_' + str(c)
                # json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                filtered_mention_splitted = [x for x in final_mentions_list if [json_m['mentions']] == x['overlap']] # deve esserci per forza
                if filtered_mention_splitted == []: # in questo caso è full overlapped
                    filtered_mention_splitted = [x for x in final_mentions_list if json_m['mentions'] in x['overlap']]
                filtered_mention_splitted = filtered_mention_splitted[0]

                start = filtered_mention_splitted['start']
                stop = filtered_mention_splitted['stop']
                json_m['mention_text'] = filtered_mention_splitted['mention_text']
                json_mention = return_start_stop_for_frontend(start, stop, document.document_content)

                json_m['start'] = json_mention['start']
                json_m['stop'] = json_mention['stop']


                json_m['position'] = json_mention['position']
                concept = annotation.concept_url
                json_m['concept'] = {}
                json_m['concept']['concept_url'] = concept.concept_url
                json_m['concept']['concept_name'] = concept.concept_name
                json_m['concept']['concept_description'] = concept.description
                json_m['concept']['area'] = annotation.name_id
                json_m['time'] = str(annotation.insertion_time).split('.')[0:-1]
                asso = Associate.objects.filter(document_id=document,concept_url = concept,name=annotation.name,
                                         language=language, topic_id=topic, start=mention, stop=mention.stop)
                if asso.count() > len(users) / 2:
                    json_mentions.append(json_m)
            c += 1
    return json_mentions
# def generate_mentions_list(username,name_space,document,language):
#
#     """This view returns the list of metnions annotated by a user for a document"""
#
#     json_mentions = []
#     name_space = NameSpace.objects.get(name_space=name_space)
#     user = User.objects.get(username=username, name_space=name_space)
#     document = Document.objects.get(document_id=document, language=language)
#     annotations = Annotate.objects.filter(username=user, name_space=name_space, document_id=document, language=language)
#     for annotation in annotations:
#         mention = Mention.objects.get(document_id=document, start=annotation.start_id, language=language)
#         # mention = annotation.start
#
#         json_m = {}
#         json_m['concepts'] = []
#         testo = mention.mention_text
#         json_m['mention_text'] = testo
#         # print(mention.mention_text)
#         start = mention.start
#         stop = mention.stop
#
#
#         json_mention = return_start_stop_for_frontend(start, stop, document.document_content)
#         json_m['start'] = json_mention['start']
#         json_m['stop'] = json_mention['stop']
#
#         json_m['position'] = json_mention['position']
#         associations = Associate.objects.filter(username=user, name_space=name_space, document_id=document,
#                                                 language=language, start=mention, stop=mention.stop)
#         if associations.count() > 0:
#             for association in associations:
#                 concept = association.concept_url
#                 area = association.name
#                 json_conc = {}
#                 json_conc['concept_url'] = concept.concept_url
#                 json_conc['concept_name'] = concept.concept_name
#                 json_conc['area'] = area.name
#                 json_conc['annotation_time'] = str(association.insertion_time).split('.')[0:-1]
#                 json_m['concepts'].append(json_conc)
#
#         json_m['time'] = str(annotation.insertion_time).split('.')[0:-1]
#         # json_mentions.append([testo,json_mention['start'],json_mention['stop'],json_mention['position']])
#         json_mentions.append(json_m)
#     return json_mentions


def generate_ground_truth(user,name_space,document,language,topic):

    """Groundtruth generation for user and document"""

    json_gt = {}
    json_gt['username'] = user.username
    json_gt['mode'] = name_space.name_space
    json_gt['document'] = document.document_id
    json_gt['language'] = document.language
    json_gt['topic'] = topic.id

    # name_space = NameSpace.objects.get(name_space = name_space)
    # user = User.objects.get(username = user, name_space = name_space)
    # document = Document.objects.get(document_id = document, language = language)

    # labels
    labels = AnnotateLabel.objects.filter(document_id = document,topic_id=topic,username = user,name_space = name_space)
    json_gt['labels'] = [{l.label.name:int(l.grade)} for l in labels]

    # mentions & concepts
    json_gt['objects'] = generate_objects_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)
    json_gt['passages'] = generate_mentions_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)
    json_gt['concepts'] = generate_associations_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)
    json_gt['tags'] = generate_tag_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)
    json_gt['relationships'] = generate_relationships_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)
    json_gt['facts'] = generate_assertions_list(user.username,name_space.name_space,document.document_id,document.language,topic.id)

    # associations

    return json_gt


def insert_if_missing(concept,area,username,collection):

    """This method adds a concept and an area if missing"""

    concept_url = str(concept['concept_url'].strip())
    concept_name = str(concept['concept_name'])
    if concept['concept_description'] is None:
        concept_description = ''
    else:
        concept_description = str(concept['concept_description'])
    concept = Concept.objects.filter(concept_url = concept_url)
    if not concept.exists():
        Concept.objects.create(concept_url = concept_url,concept_name = concept_name, description = concept_description)
    area = area.strip()
    if concept_url == '':
        concept_url = 'empty_concept_ID'



    area_obj = SemanticArea.objects.filter(name = area)
    if not area_obj.exists():
        SemanticArea.objects.create(name=area)
        areas = get_areas_collection(collection)
        tags = get_tags_collection(collection)
        collection_obj = Collection.objects.get(collection_id = collection)
        options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags))}
        collection_obj.options = json.dumps(options)
        collection_obj.save()

    area = SemanticArea.objects.get(name=area)
    concept = Concept.objects.get(concept_url = concept_url)

    #has_area = HasArea.objects.filter(name=area,concept_url = concept)
    #if not has_area.exists():
        #HasArea.objects.create(name=area, concept_url=concept)

    collection = Collection.objects.get(collection_id = collection)
    addconcept = CollectionHasConcept.objects.filter(collection_id = collection, concept_url = concept, name=area)
    if not addconcept.exists():
        CollectionHasConcept.objects.create(collection_id=collection,
                                  concept_url=concept, name=area)

def get_tags_collection(collection):
    if collection:
        collection = Collection.objects.get(collection_id=collection)
        areas = CollectionHasTag.objects.filter(collection_id=collection)
        areas = [area.name_id for area in areas]
    return areas

def get_areas_collection(collection):

    if collection is not None:
        collection = Collection.objects.get(collection_id = collection)
        tuples = CollectionHasConcept.objects.filter(collection_id = collection).values('name').distinct()
        areas = [concept['name'] for concept in tuples]
    return areas

from doctron_app.utils_iaa import *
def update_gt(user,name_space,document,language,topic):
    try:
        if GroundTruthLogFile.objects.filter(username=user, name_space=name_space, document_id=document,
                                                   language=language,topic_id=topic).exists():
            GroundTruthLogFile.objects.filter(username=user, name_space=name_space,topic_id=topic, document_id=document, language=language).delete()

        json_gt = generate_ground_truth(user, name_space, document, language,topic)
        if json_gt['labels'] != [] or json_gt['passages'] != [] or json_gt['concepts'] != [] or json_gt['concepts'] != []  or json_gt['relationships'] != []or json_gt['objects'] != []:
            GroundTruthLogFile.objects.create(username=user, name_space=name_space, insertion_time=Now(), gt_json=json_gt,topic_id=topic,
                                          document_id=document, language=language)



        # update_iaa_agreement(document.document_id)
        # user_iaa = User.objects.get(username = "IAA-Inter Annotator Agreement",name_space = name_space)
        # json_gt = generate_ground_truth(user_iaa, name_space, document, language)



    except Exception as e:
        print(e)


def get_baseurl():
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open((os.path.join(workpath, '../url.txt')), 'r', encoding='utf-8') as f:
        baseurl = f.read()
        if '0.0.0.0:' in baseurl:
            baseurl = 'http://localhost:8000'
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        return baseurl


def create_concepts_list(collection):

    """Return the list of concepts of a collection"""

    collection = Collection.objects.get(collection_id=collection)
    coll_conc = CollectionHasConcept.objects.filter(collection_id=collection)
    concepts = []
    for concept in coll_conc:
        json_l = {}
        c = concept.concept_url
        area = concept.name
        json_l['url'] = c.concept_url
        json_l['name'] = c.concept_name
        json_l['description'] = c.description
        area = area.name
        json_l['area'] = area
        concepts.append(json_l)
    return concepts




def find_overlapping_mentions(document, user,topic):

    mentions_list = Annotate.objects.filter(document_id=document, username=user, name_space=user.name_space,topic_id=topic,
                                            language=document.language).order_by('start')
    mentions_list_sorted = Annotate.objects.filter(document_id=document, username=user, name_space=user.name_space,topic_id=topic,
                                                   language=document.language).order_by('insertion_time')
    dict_mapping = {}
    ind = 0

    for m in mentions_list:
        ind_j = 0
        for mm in mentions_list_sorted:

            if m.start_id == mm.start_id and m.stop == mm.stop:
                chiave = 'mention_'+str(ind)
                valore = 'mention_'+str(ind_j)
                dict_mapping[chiave] = valore
            ind_j += 1
        ind += 1
    start_stop_sorted = []
    for m in mentions_list_sorted:
        start = m.start_id
        stop = m.stop
        start_stop_sorted.append([start, stop])
    items_mentions = []
    start_stops = []
    new_item_mentions = []
    content = document.document_content
    start_list, stop_list = [], []
    j = 0

    if mentions_list.count()>0:
        for mention in mentions_list:
            j +=1
            # print(j)
            mention_obj = Mention.objects.get(document_id=document, language=document.language, start=mention.start_id,
                                              stop=mention.stop)
            #print(mention_obj.start,mention_obj.stop,mention_obj.mention_text)

            range_sel = [i for i in range(mention_obj.start, mention_obj.stop + 1)]

            k = from_start_stop_foreach_key(document.document_content, mention.start_id, mention.stop)
            # if k == None:
            #     breakpoint()
            #print(mention_obj.mention_text)
            items_mentions.append({'start': mention_obj.start, 'stop': mention_obj.stop, 'mention_text': mention_obj.mention_text,
                 'position': k['position'], 'range': range_sel, 'overlap': []})


            start_stops.append([i for i in range(mention_obj.start, mention_obj.stop+1)])
            start_list.append(mention_obj.start)
            stop_list.append(mention_obj.stop)

        json_chars = {}
        for i in range(len(start_stops)):
            for k in start_stops[i]:
                if k not in list(json_chars.keys()):
                    json_chars[k] = ['mention_'+str(i)]
                    for j in range(i+1,len(start_stops)):
                        if k in start_stops[j]:
                            json_chars[k].append('mention_'+str(j))
                else:
                    if('mention_' + str(i) not in json_chars[k]):
                        json_chars[k].append('mention_' + str(i))

        first_key = list(json_chars.keys())[0]
        cur_val = '___'.join(json_chars[first_key])
        final_list = []
        cur_item = [cur_val]
        # json_reversed = {}
        # json_reversed[cur_val] = [list(json_chars.keys())[0]]
        for key,item in json_chars.items():
            if '___'.join(item) == cur_val:
                cur_item.append(key)
            else:
                final_list.append(cur_item)
                cur_val = '___'.join(item)
                cur_item = [cur_val,key]
        final_list.append(cur_item)
        #         json_reversed['___'.join(item)].append(key)
        #     else:
        #         cur_val = '___'.join(item)
        #         json_reversed[cur_val] = [key]

        for lista in final_list:
            start = lista[1]
            stop = lista[-1]
            overlap = lista[0].split('___')
            # qua prendo le overlapping mentions separate da ___ e per ogni elemento vedo le parti non overlapping
            # not_overlapping_chars = []
            # for x in overlap:
            #     if x in dict_mapping.keys():
            #         not_overlapping_chars.append(dict_mapping[x])
            #     else:


            overlap = [dict_mapping[x] for x in overlap]
            new_range = [p for p in range(start,stop+1)]
            k = from_start_stop_foreach_key(document.document_content, start,stop)
            if k is not None:
                cur_key_splitted = k['position'][:-6] if k['position'].endswith('_value') else k['position'][:-4]
                json_value = content[cur_key_splitted] if k['position'].endswith('_value') else k['position'][:-4]


                new_mention = ({'start': lista[1], 'stop': lista[-1],
                            'mention_text': json_value[start - k['start']:stop - k['start']+1],
                            'range': new_range,
                            'overlap': overlap, 'position': k['position']})
                new_item_mentions.append(new_mention)

    return new_item_mentions


def create_new_content(document,user,topic):
    new_doc = {}
    mentions = {}
    content = document.document_content
    mentions['mentions'] = []
    # current_key = list(document.document_content.keys())[0]
    current_index = 0
    index_mention = 0

    dict_keys = from_start_stop_foreach_key(document_content=document.document_content)
    dict_keys = [v for k,v in dict_keys['key'].items()] + [v for k,v in dict_keys['value'].items()]

    dict_keys = sorted(dict_keys,key=lambda x: x['start'])

    new_content_from_dict_keys = {}
    for item in dict_keys:
        new_content_from_dict_keys[item['position']] = [{'type': 'no_mention', 'text': item['text']}]

    new_item_mentions = find_overlapping_mentions(document,user,topic)


    distinct_keys_mention = [item['position'] for item in new_item_mentions]
    distinct_keys_mention = list(set(distinct_keys_mention))
    for k in distinct_keys_mention:
        new_content_from_dict_keys[k] = []
        # costruisco contenuto delle mentions

        forbidden_indices = []
        mentions_k = [item for item in new_item_mentions if item['position'] == k]
        key = from_start_stop_foreach_key(document_content=document.document_content, start=mentions_k[0]['start'],
                                          stop=mentions_k[0]['stop'])
        cur_key_splitted = key['position'][0:-6] if key['position'].endswith('_value') else key['position'][0:-4]
        json_value = content[cur_key_splitted] if key['position'].endswith('_value') else key['position'][0:-4]
        for mention in mentions_k:

            forbidden_indices.extend(mention['range'])
            new_content_from_dict_keys[k].append({'type':'mention',
                'text': mention['mention_text'],'start':mention['start']-key['start'],'stop':mention['stop']-key['start'],
                                                  'mentions': str(' '.join(mention['overlap']
                                                                           ))})


        # costruisco contenuto privo di mentions

        forbidden_lists = []
        forb_list = [forbidden_indices[0]]
        for i in range(len(forbidden_indices)-1):
            if forbidden_indices[i+1] == forbidden_indices[i]+1:
                forb_list.append(forbidden_indices[i+1])
            else:
                forbidden_lists.append(forb_list)
                forb_list = [forbidden_indices[i+1]]
        forbidden_lists.append(forb_list)
        # print(forbidden_lists)
        # print(len(json_value),json_value)

        no_mentions_indices = []
        if forbidden_indices[0] != 0:
            no_mentions_indices.append([j for j in range(0,forbidden_indices[0])])
            if forbidden_indices[0]-key['start']-1 != -1: # 09/01/25
                new_content_from_dict_keys[k].append({'type':'no_mention','text':json_value[0:forbidden_indices[0]-key['start']],'start':0,'stop':forbidden_indices[0]-key['start']-1})

        if forbidden_indices[-1] != key['stop']:
            no_mentions_indices.append([j for j in range(forbidden_indices[-1]+1,len(json_value))])
            new_content_from_dict_keys[k].append({'type':'no_mention','text':json_value[forbidden_indices[-1] + 1 -key['start'] : key['stop']-key['start']+1],'start':forbidden_indices[-1]-key['start'],'stop':key['stop']-key['start']})

        for ind in range(len(forbidden_lists)-1):
                if forbidden_lists[ind][-1] < forbidden_lists[ind+1][0]:
                    no_mentions_indices.append([j for j in range(forbidden_lists[ind][-1]+1, forbidden_lists[ind+1][0])])
                    new_content_from_dict_keys[k].append({'type':'no_mention','text':json_value[forbidden_lists[ind][-1]+1-key['start']:forbidden_lists[ind+1][0]-key['start']],'start':forbidden_lists[ind][-1]+1 -key['start'],'stop':forbidden_lists[ind+1][0]-key['start']-1})

        new_content_from_dict_keys[k] = sorted(new_content_from_dict_keys[k],key=lambda x:x['start'])


    for k,v in new_content_from_dict_keys.items():
        for element in v:
            if isinstance(element['text'],list):
                    element['text'] = ', '.join(element['text'])


    new_content = {}
    # for k in content.keys():
        # if k != 'sk_metatron':
        #     new_content[k] = new_content_from_dict_keys[k]
    # if "sk_metatron" in content.keys():
    #     for k in content['sk_metatron']:
    #         # new_empty[k] = content[k]
    #         new_content[k + '_key'] = new_content_from_dict_keys[k + '_key']
    #         new_content[k + '_value'] = new_content_from_dict_keys[k + '_value']
    if new_content != {}:
        return new_content
    return new_content_from_dict_keys

