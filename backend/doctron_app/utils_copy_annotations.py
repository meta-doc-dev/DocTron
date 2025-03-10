
from doctron_app.utils import *
from django.http import HttpResponse



def copy_labels(username,name_space,label,document,language):

    """This method copies a label in the logged in user"""

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    try:
        with transaction.atomic():
            label = Label.objects.get(name=label)
            label_anno = AnnotateLabel.objects.filter(document_id = document, language = language, username = user, name_space = name_space, name = label)
            if not label_anno.exists():
                AnnotateLabel.objects.create(document_id=document, language=language, username=user,
                                             name_space=name_space, name=label,insertion_time = Now())


                update_gt(user,name_space,document,language)
        json_resp = {'msg':'ok'}
    except Exception as e:
        print(e)
        json_resp = {'error':e}
    finally:
        return json_resp




def copy_assertion_aux(username,name_space,document,language,assertion):

    """This method copies an assertion in the logged in user"""


    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    assertion = assertion['assertion']
    source = assertion['subject']['concept']['concept_url']
    source_area = assertion['subject']['concept']['concept_area']
    predicate = assertion['predicate']['concept']['concept_url']
    predicate_area = assertion['predicate']['concept']['concept_area']
    target = assertion['object']['concept']['concept_url']
    target_area = assertion['object']['concept']['concept_area']

    assertion = CreateFact.objects.filter(document_id = document, language = language, username = user, name_space = name_space, subject_concept_url = source, subject_name = source_area,
                                          predicate_concept_url = predicate, predicate_name = predicate_area, object_concept_url = target, object_name = target_area)
    try:
        with transaction.atomic():

            if not assertion.exists():
                CreateFact.objects.create(document_id=document, language=language, username=user, name_space=name_space,
                                          subject_concept_url=source, subject_name=source_area,insertion_time = Now(),
                                          predicate_concept_url=predicate, predicate_name=predicate_area,
                                          object_concept_url=target, object_name=target_area)
                update_gt(user,name_space,document,language)
            return {'msg':'ok'}
    except Exception as e :
        print(e)
        return {'error':e}


def copy_mention_aux(user,name_space,document,language,mention,topic,username_source):
    start = mention['start']
    stop = mention['stop']

    position = mention.get('id',None)
    if position != None:
        position = '_'.join(position.split('_')[:-1])

    else:
        position = mention.get('position',None)

    # mentions = mention['mentions']

    start,stop = return_start_stop_for_backend(start,stop,position,document.document_content)
    # non controllo se tra le mentions c'è già in quanto la sto copiando
    json_resp = {'msg':'ok'}
    try:
        with transaction.atomic():
            topic_obj = Topic.objects.get(id=topic)
            mention = Mention.objects.get(start = start, stop = stop, document_id = document, language = language)
            # copy labels
            cursor = connection.cursor()
            cursor.execute("""
                                  INSERT INTO annotate (start, stop, document_id, language, username, name_space, insertion_time, topic_id)
                                      SELECT start, stop, document_id, language, %s, name_space, insertion_time, topic_id
                                      FROM annotate
                                      WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s;;
                                                   """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            cursor.execute("""
                                      INSERT INTO annotate_passage (username, name_space, document_id, language, start, stop, grade, insertion_time, topic_id, label)
                                          SELECT %s, name_space, document_id, language, start, stop, grade, insertion_time, topic_id, label
                                          FROM annotate_passage
                                          WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s ON CONFLICT DO NOTHING;
                                       """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            update_gt(user,name_space,document,language,topic_obj)
            return json_resp
    except Exception as e:
        json_resp = {'error': e}

        print(e)
        return json_resp

def copy_tags_aux(username,name_space,document,language,json_body,topic,username_source):
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    mention = json_body['mention']
    start = mention['start']
    stop = mention['stop']
    position = mention.get('id', None)
    if position != None:
        position = '_'.join(position.split('_')[:-1])

    else:
        position = mention.get('position', None)

    # position = '_'.join(position.split('_')[:-1])
    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)


    # non controllo se tra le mentions c'è già in quanto la sto copiando
    json_resp = {'msg': 'ok'}
    try:
        with transaction.atomic():
            topic_obj = Topic.objects.get(id=topic)
            mention = Mention.objects.get(start = start, stop = stop, document_id = document, language = language)
            # copy labels
            cursor = connection.cursor()
            cursor.execute("""
                                  INSERT INTO annotate (start, stop, document_id, language, username, name_space, insertion_time, topic_id)
                                      SELECT start, stop, document_id, language, %s, name_space, insertion_time, topic_id
                                      FROM annotate
                                      WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s ON CONFLICT DO NOTHING;
                                                   """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            cursor.execute("""
                                      INSERT INTO associate_tag (username, name_space, document_id, language, start, stop, name, insertion_time, topic_id)
                                          SELECT %s, name_space, document_id, language, start, stop, name, insertion_time, topic_id
                                          FROM associate_tag
                                          WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s ON CONFLICT DO NOTHING;
                                       """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            update_gt(user,name_space,document,language,topic_obj)
            return json_resp
    except Exception as e:
        json_resp = {'error': e}

        print(e)
        return json_resp
    
def copy_concepts_aux(username,name_space,document,language,json_body,topic,username_source):
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    mention = json_body['mention']
    start = mention['start']
    stop = mention['stop']
    position = mention.get('id', None)
    if position != None:
        position = '_'.join(position.split('_')[:-1])

    else:
        position = mention.get('position', None)

    # position = '_'.join(position.split('_')[:-1])
    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)


    # non controllo se tra le mentions c'è già in quanto la sto copiando
    json_resp = {'msg': 'ok'}
    try:
        with transaction.atomic():
            topic_obj = Topic.objects.get(id=topic)
            mention = Mention.objects.get(start = start, stop = stop, document_id = document, language = language)
            # copy labels
            cursor = connection.cursor()
            cursor.execute("""
                                  INSERT INTO annotate (start, stop, document_id, language, username, name_space, insertion_time, topic_id)
                                      SELECT start, stop, document_id, language, %s, name_space, insertion_time, topic_id
                                      FROM annotate
                                      WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s ON CONFLICT DO NOTHING;
                                                   """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            cursor.execute("""
                                      INSERT INTO associate (username, name_space, document_id, language, start, stop, name, insertion_time, topic_id, concept_url)
                                          SELECT %s, name_space, document_id, language, start, stop, name, insertion_time, topic_id, concept_url
                                          FROM associate
                                          WHERE document_id = %s and topic_id = %s and username = %s and start = %s and stop = %s ON CONFLICT DO NOTHING;
                                       """,
                           [user.username, document.document_id, topic_obj.id, username_source,mention.start,mention.stop])
            update_gt(user,name_space,document,language,topic_obj)
            return json_resp
    except Exception as e:
        json_resp = {'error': e}

        print(e)
        return json_resp

def copy_relation_aux(username, name_space,document, language, subject, predicate, object,user_source):

    # json_body = json.loads(request.body)

    subject_mention = subject['mention']
    subject_concept = subject['concept']
    predicate_mention = predicate['mention']
    predicate_concept = predicate['concept']
    object_mention = object['mention']
    object_concept = object['concept']


    if subject_mention != {}:
        mention = {}
        mention_obj = {}
        mention['start'] = subject_mention['start']
        mention['stop'] = subject_mention['stop']
        mention['position'] = subject_mention['position']
        mention_obj['user'] = user_source
        mention_obj['mention'] = mention
        copy_concepts_aux(username, name_space, document, language, mention_obj)
    if predicate_mention != {}:
        mention = {}
        mention_obj = {}
        mention['start'] = predicate_mention['start']
        mention['stop'] = predicate_mention['stop']
        mention['position'] = predicate_mention['position']
        mention_obj['user'] = user_source
        mention_obj['mention'] = mention
        copy_concepts_aux(username, name_space, document, language, mention_obj)
    if object_mention != {}:
        mention = {}
        mention_obj = {}
        mention['start'] = object_mention['start']
        mention['stop'] = object_mention['stop']
        mention['position'] = object_mention['position']
        mention_obj['user'] = user_source
        mention_obj['mention'] = mention
        copy_concepts_aux(username, name_space, document, language, mention_obj)

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)


    try:
        with transaction.atomic():
            if subject_mention != {} and predicate_mention != {} and object_mention != {}:
                subject_start, subject_stop = return_start_stop_for_backend(subject_mention['start'], subject_mention['stop'],
                                                                            subject_mention['position'],
                                                                            document.document_content)
                predicate_start, predicate_stop = return_start_stop_for_backend(predicate_mention['start'],
                                                                                predicate_mention['stop'],
                                                                                predicate_mention['position'],
                                                                                document.document_content)
                object_start, object_stop = return_start_stop_for_backend(object_mention['start'], object_mention['stop'],
                                                                          object_mention['position'], document.document_content)
                relations = Link.objects.filter(username=user, name_space=name_space, subject_document_id=document.document_id,
                                                subject_language=document.language,
                                                subject_start=subject_start, subject_stop=subject_stop,
                                                predicate_start=predicate_start, predicate_stop=predicate_stop,
                                                object_start=object_start, object_stop=object_stop)
                if not relations.exists():
                    Link.objects.create(username=user, name_space=name_space, subject_document_id=document.document_id,
                                        subject_language=document.language,object_document_id=document.document_id,
                                        object_language=document.language,predicate_document_id=document.document_id,
                                        predicate_language=document.language, insertion_time=Now(),
                                        subject_start=subject_start, subject_stop=subject_stop,
                                        predicate_start=predicate_start, predicate_stop=predicate_stop,
                                        object_start=object_start, object_stop=object_stop)


            elif subject_mention != {} and predicate_mention != {} and object_mention == {} and object_concept != {}:

                concept = Concept.objects.get(concept_url=object_concept['concept_url'])
                area = SemanticArea.objects.get(name=object_concept['concept_area'])
                subject_start, subject_stop = return_start_stop_for_backend(subject_mention['start'], subject_mention['stop'],
                                                                            subject_mention['position'],
                                                                            document.document_content)

                predicate_start, predicate_stop = return_start_stop_for_backend(predicate_mention['start'],
                                                                                predicate_mention['stop'],
                                                                                predicate_mention['position'],
                                                                                document.document_content)

                relations = RelationshipObjConcept.objects.filter(username=user, name_space=name_space,
                                                                  subject_document_id=document.document_id,
                                                                  subject_language=document.language,
                                                                  subject_start=subject_start, subject_stop=subject_stop,
                                                                  predicate_start=predicate_start,
                                                                  predicate_stop=predicate_stop,
                                                                  concept_url=concept, name=area)

                if not relations.exists():
                    RelationshipObjConcept.objects.create(username=user, name_space=name_space, insertion_time=Now(),
                                                          subject_document_id=document.document_id,predicate_document_id=document.document_id,predicate_language = language,
                                                          subject_language=document.language,
                                                          subject_start=subject_start, subject_stop=subject_stop,
                                                          predicate_start=predicate_start, predicate_stop=predicate_stop,
                                                          concept_url=concept, name=area)


            elif subject_mention == {} and predicate_mention != {} and object_mention != {} and subject_concept != {}:

                concept = Concept.objects.get(concept_url=subject_concept['concept']['concept_url'])
                area = SemanticArea.objects.get(name=subject_concept['concept']['concept_area'])
                object_start, object_stop = return_start_stop_for_backend(subject_mention['start'], subject_mention['stop'],
                                                                          subject_mention['position'],
                                                                          document.document_content)

                predicate_start, predicate_stop = return_start_stop_for_backend(predicate_mention['start'],
                                                                                predicate_mention['stop'],
                                                                                predicate_mention['position'],
                                                                                document.document_content)

                relations = RelationshipSubjConcept.objects.filter(username=user, name_space=name_space,
                                                                   object_document_id=document.document_id,predicate_document_id=document.document_id,
                                                                   object_language=document.language,predicate_language=document.language,
                                                                   object_start=object_start, object_stop=object_stop,
                                                                   predicate_start=predicate_start,
                                                                   predicate_stop=predicate_stop,
                                                                   concept_url=concept, name=area)

                if not relations.exists():
                    RelationshipSubjConcept.objects.create(username=user, name_space=name_space,
                                                           subject_document_id=document.document_id,
                                                           subject_language=document.language, insertion_time=Now(),
                                                           object_start=object_start, object_stop=object_stop,
                                                           predicate_start=predicate_start,
                                                           predicate_stop=predicate_stop,
                                                           concept_url=concept, name=area)

            elif subject_mention != {} and predicate_mention == {} and object_mention != {} and predicate_concept != {}:
                concept = Concept.objects.get(concept_url=predicate_concept['concept_url'])
                area = SemanticArea.objects.get(name=predicate_concept['concept_area'])

                object_start, object_stop = return_start_stop_for_backend(object_mention['start'], object_mention['stop'],
                                                                            object_mention['position'],
                                                                            document.document_content)
                subject_start, subject_stop = return_start_stop_for_backend(subject_mention['start'],
                                                                          subject_mention['stop'],
                                                                          subject_mention['position'],
                                                                          document.document_content)

                relations = RelationshipPredConcept.objects.filter(username=user, name_space=name_space,
                                                                  subject_document_id=document.document_id,
                                                                  subject_language=document.language,
                                                                  object_start=object_start, object_stop=object_stop,
                                                                  subject_start=subject_start,
                                                                  subject_stop=subject_stop,
                                                                  concept_url=concept, name=area)
                if not relations.exists():
                    RelationshipPredConcept.objects.create(username=user, name_space=name_space,insertion_time = Now(),
                                                                  subject_document_id=document.document_id,object_document_id=document.document_id,
                                                                  object_language=document.language,
                                                                  subject_language=document.language,
                                                                  object_start=object_start, object_stop=object_stop,
                                                                   subject_start=subject_start,
                                                                   subject_stop=subject_stop,
                                                                  concept_url=concept, name=area)


            elif subject_mention == {} and predicate_mention != {} and object_mention == {} and object_concept != {} and subject_concept != {} and predicate_concept == {}:

                predicate_start, predicate_stop = return_start_stop_for_backend(predicate_mention['start'],
                                                                                predicate_mention['stop'],
                                                                                predicate_mention['position'],
                                                                                document.document_content)

                mention = Mention.objects.get(document_id=document, language=document.language, start=predicate_start,
                                              stop=predicate_stop)

                relations = RelationshipPredMention.objects.filter(username=user, name_space=name_space,
                                                                   document_id=document, language=language,
                                                                   start=mention, stop=mention.stop,
                                                                   subject_concept_url=subject_concept['concept_url'],
                                                                   subject_name=subject_concept['concept_area'],
                                                                   object_concept_url=object_concept['concept_url'],
                                                                   object_name=object_concept['concept_area'])

                if not relations.exists():
                    RelationshipPredMention.objects.create(username=user, name_space=name_space,
                                                           document_id=document, language=language,
                                                           start=mention, stop=mention.stop, insertion_time=Now(),
                                                           subject_concept_url=subject_concept['concept_url'],
                                                           subject_name=subject_concept['concept_area'],
                                                           object_concept_url=object_concept['concept_url'],
                                                           object_name=object_concept['concept_area'])

            elif subject_mention != {} and predicate_mention == {} and object_mention == {} and object_concept != {} and subject_concept == {} and predicate_concept != {}:

                subject_start, subject_stop = return_start_stop_for_backend(subject_mention['start'],
                                                                                subject_mention['stop'],
                                                                                subject_mention['position'],
                                                                                document.document_content)

                mention = Mention.objects.get(document_id=document, language=document.language, start=subject_start,
                                              stop=subject_stop)

                relations = RelationshipSubjMention.objects.filter(username=user, name_space=name_space,
                                                                   document_id=document, language=language,
                                                                   start=mention, stop=mention.stop,
                                                                   predicate_concept_url=predicate_concept['concept_url'],
                                                                   predicate_name=predicate_concept['concept_area'],
                                                                   object_concept_url=object_concept['concept_url'],
                                                                   object_name=object_concept['concept_area'])
                if not relations.exists():
                    RelationshipSubjMention.objects.create(username=user, name_space=name_space,
                                                           document_id=document, language=language,
                                                           start=mention, stop=mention.stop,insertion_time = Now(),
                                                           predicate_concept_url=predicate_concept['concept_url'],
                                                           predicate_name=predicate_concept['concept_area'],
                                                           object_concept_url=object_concept['concept_url'],
                                                           object_name=object_concept['concept_area'])

            elif subject_mention == {} and predicate_mention == {} and object_mention != {} and object_concept == {} and subject_concept != {} and predicate_concept != {}:

                object_start, object_stop = return_start_stop_for_backend(object_mention['start'],
                                                                                object_mention['stop'],
                                                                                object_mention['position'],
                                                                                document.document_content)

                mention = Mention.objects.get(document_id=document, language=document.language, start=object_start,
                                              stop=object_stop)

                relations = RelationshipObjMention.objects.filter(username=user, name_space=name_space,
                                                                   document_id=document, language=language,
                                                                   start=mention, stop=mention.stop,
                                                                   predicate_concept_url=predicate_concept['concept_url'],
                                                                   predicate_name=predicate_concept['concept_area'],
                                                                   subject_concept_url=subject_concept['concept_url'],
                                                                   subject_name=subject_concept['concept_area'])
                if not relations.exists():
                    RelationshipObjMention.objects.create(username=user, name_space=name_space,
                                                           document_id=document, language=language,
                                                           start=mention, stop=mention.stop,insertion_time = Now(),
                                                           predicate_concept_url=predicate_concept['concept_url'],
                                                           predicate_name=predicate_concept['concept_area'],
                                                           subject_concept_url=subject_concept['concept_url'],
                                                           subject_name=subject_concept['concept_area'])
        update_gt(user, name_space, document, language)

        return {'msg':'ok'}
    except Exception as e:
        return {'error':e}
