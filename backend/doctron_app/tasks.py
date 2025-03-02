from celery import shared_task
import time

from django.db.backends.postgresql.psycopg_any import NumericRange
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
import hashlib

from doctron_app.utils import *
from doctron_app.upload.ir_datases import *
from doctron_app.utils_upload_documents import *
from doctron_app.upload.configure import *


from django.db import transaction
import json
import os
from doctron_app.models import *
from django.http import HttpResponse


@shared_task
def test_task1(request):
    # Task logic here
    print('task avviato')
    time.sleep(10)
    print('task completo')
    return 'ciao'

@shared_task
def try_task(param1, param2):
    return f"Task executed with {param1} and {param2}"




@shared_task
def compute_stats(document,topic):

    json_final = {}
    json_final['cohens'] = create_cohen(document,topic)
    json_final['fleiss'],json_final['kripp'] = create_fleiss_kripp(document,topic)
    return json_final



@shared_task
def get_json_fields(files):
    """This method returns the list of columns in a list of json files"""

    keys = []
    for file in files:
        data = json.load(file)
        keys = list(set(data.keys()))
        keys.extend([k for k in keys if k not in ['document_id', 'language']])
    return keys

from django.db import connection
def upload_preannotations(file,annotation,collection):

    def get_real_id(doc_id):

        docs = Document.objects.filter(collection_id = collection,doc_id_not_hashed=doc_id)
        docs1 = Document.objects.filter(collection_id = collection,document_id=doc_id)
        if docs.count() == 1:
            return docs.first().document_id
        elif docs1.count() == 1:
            return docs.first().document_id
        else: return None

    def compute_text(doc_id,start,stop,position):
        doc = Document.objects.get(document_id = doc_id).document_content
        text = doc[position][start:stop+1]
        start,stop = return_start_stop_for_backend(start,stop,position,doc)

        return start,stop,text


    if file is not None and file.name.endswith('.csv'):
        df_file = pd.read_csv(file)
        df = df_file.where(pd.notnull(df_file), None)


    elif file is not None and file.name.endswith('.json'):
        files = json.load(file)['annotations']
        df = pd.DataFrame(files)
        df = df.where(pd.notnull(df), None)


    df['doc_id'] = df['doc_id'].apply(get_real_id)

    docs = Document.objects.filter(collection_id=collection)
    users = ShareCollection.objects.filter(collection_id = collection)

    if annotation == 'Entity tagging':
        Mention.objects.filter(document_id__in=docs).delete()
        Annotate.objects.filter(document_id__in=docs).delete()
        AssociateTag.objects.filter(document_id__in=docs).delete()
        df["mention_text"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[2], axis=1)
        df["start"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[0], axis=1)
        df["stop"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[1], axis=1)

        tags = df['tag'].unique().tolist()
        tags_list = [tuple([tag]) for tag in tags]
        with connection.cursor() as cursor:
            cursor.executemany("""INSERT INTO tag (name)
                                               VALUES (%s) ON CONFLICT (name) DO NOTHING;
                                            """, [tags_list])
            tags = [tuple([collection.collection_id,tag]) for tag in tags]
            cursor.executemany("""INSERT INTO collection_has_tag (collection_id,name)
                                                VALUES (%s,%s) ON CONFLICT (name,collection_id) DO NOTHING;
                                             """, [tags])

    if annotation == 'Entity linking':
        Mention.objects.filter(document_id__in=docs).delete()
        Annotate.objects.filter(document_id__in=docs).delete()
        Associate.objects.filter(document_id__in=docs).delete()

        df["mention_text"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[2], axis=1)
        df["start"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[0], axis=1)
        df["stop"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[1], axis=1)

        urls = df['concept_url'].tolist()
        tups_co = []
        for url in urls:
            tups_co.append(tuple([url,url,'']))


        areas = df['area'].tolist()
        tups = []
        for url,area in zip(urls,areas):
            tups.append(tuple([url,area,collection.collection_id]))

        cursor.executemany("""INSERT INTO concept (concept_url,concpet_name,description)
                                                    VALUES (%s,%s,%s) ON CONFLICT (concept_url) DO NOTHING;
                                                 """, [tups_co])
        cursor.executemany("""INSERT INTO collection_has_concept (concept_url,name,collection_id)
                                            VALUES (%s,%s,%s) ON CONFLICT (concept_url,name,collection_id) DO NOTHING;
                                         """, [tups])




    if annotation == 'Relationships annotation':

        Mention.objects.filter(document_id__in=docs).delete()
        Annotate.objects.filter(document_id__in=docs).delete()
        Associate.objects.filter(document_id__in=docs).delete()
        AssociateTag.objects.filter(document_id__in=docs).delete()

        df["subject_mention_text"] = df.apply(lambda row: compute_text(row["subject_start"], row["subject_stop"],row['subject_position'])[2], axis=1)
        df["subject_start"] = df.apply(lambda row: compute_text(row["subject_start"], row["subject_stop"],row['subject_position'])[0], axis=1)
        df["subject_stop"] = df.apply(lambda row: compute_text(row["subject_start"], row["subject_stop"],row['subject_position'])[1], axis=1)

        df["predicate_mention_text"] = df.apply(lambda row: compute_text(row["predicate_start"], row["predicate_stop"],row['predicate_position'])[2], axis=1)
        df["predicate_start"] = df.apply(lambda row: compute_text(row["predicate_start"], row["predicate_stop"],row['predicate_position'])[0], axis=1)
        df["predicate_stop"] = df.apply(lambda row: compute_text(row["predicate_start"], row["predicate_stop"],row['predicate_position'])[1], axis=1)

        df["object_mention_text"] = df.apply(lambda row: compute_text(row["object_start"], row["object_stop"],row['object_position'])[2], axis=1)
        df["object_start"] = df.apply(lambda row: compute_text(row["object_start"], row["object_stop"],row['object_position'])[0], axis=1)
        df["object_stop"] = df.apply(lambda row: compute_text(row["object_start"], row["object_stop"],row['object_position'])[1], axis=1)

        urls = df['subject_concept_url'].tolist() + df['object_concept_url'].tolist() + df['predicate_concept_url'].tolist()
        tups_co = []
        for url in urls:
            tups_co.append(tuple([url,url,'']))


        areas = df['subject_area'].tolist() + df['object_area'].tolist() + df['predicate_area'].tolist()
        tups = []
        for url,area in zip(urls,areas):
            tups.append(tuple([url,area,collection.collection_id]))

        cursor.executemany("""INSERT INTO concept (concept_url,concpet_name,description)
                                                    VALUES (%s,%s,%s) ON CONFLICT (concept_url) DO NOTHING;
                                                 """, [tups_co])
        cursor.executemany("""INSERT INTO collection_has_concept (concept_url,name,collection_id)
                                            VALUES (%s,%s,%s) ON CONFLICT (concept_url,name,collection_id) DO NOTHING;
                                         """, [tups])

        tags = df['subject_tag'].unique().tolist() + df['object_tag'].unique().tolist() + df[
            'predicate_tag'].unique().tolist()
        tags_list = [tuple([tag]) for tag in tags]
        with connection.cursor() as cursor:
            cursor.executemany("""INSERT INTO tag (name)
                                               VALUES (%s) ON CONFLICT (name) DO NOTHING;
                                            """, [tags_list])

            tags = [tuple([collection.collection_id, tag]) for tag in tags]
            cursor.executemany("""INSERT INTO collection_has_tag (collection_id,name)
                                                VALUES (%s,%s) ON CONFLICT (name,collection_id) DO NOTHING;
                                             """, [tags])


    if annotation == 'Facts annotation':
        CreateFact.objects.filter(document_id__in=docs).delete()


        urls = df['subject_concept_url'].tolist() + df['oject_concept_url'].tolist() + df['predicate_concept_url'].tolist()
        tups_co = []
        for url in urls:
            tups_co.append(tuple([url,url,'']))


        areas = df['subject_area'].tolist() + df['object_area'].tolist() + df['predicate_area'].tolist()
        tups = []
        for url,area in zip(urls,areas):
            tups.append(tuple([url,area,collection.collection_id]))

        cursor.executemany("""INSERT INTO concept (concept_url,concpet_name,description)
                                                    VALUES (%s,%s,%s) ON CONFLICT (concept_url) DO NOTHING;
                                                 """, [tups_co])
        cursor.executemany("""INSERT INTO collection_has_concept (concept_url,name,collection_id)
                                            VALUES (%s,%s,%s) ON CONFLICT (concept_url,name,collection_id) DO NOTHING;
                                         """, [tups])

    elif annotation == 'Graded labeling':
        AnnotateLabel.objects.filter(document_id__in=docs).delete()

    if annotation == 'Passages annotation':
        Mention.objects.filter(document_id__in=docs).delete()
        Annotate.objects.filter(document_id__in=docs).delete()
        AnnotatePassage.objects.filter(document_id__in=docs).delete()
        df_mention = df[["doc_id", "language", "start", "stop", "mention_text"]]

        df["mention_text"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[2], axis=1)
        df["start"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[0], axis=1)
        df["stop"] = df.apply(lambda row: compute_text(row["start"], row["stop"],row['position'])[1], axis=1)
        data = list(df_mention.itertuples(index=False, name=None))

        with connection.cursor() as cursor:
            cursor.executemany("""INSERT INTO mention (document_id,language,start,stop,mention_text)
                                               VALUES (%s,%s,%s,%s,%s) ON CONFLICT (document_id,language,start,stop) DO NOTHING;
                                            """, [data])
    if annotation == 'Objects annotation':
        DocumentObject.objects.filter(document_id__in=docs).delete()
        AnnotateObject.objects.filter(document_id__in=docs).delete()
        AnnotateObjectLabel.objects.filter(document_id__in=docs).delete()
        df_obj = df[["doc_id", "language", "points"]]

        data = list(df_obj.itertuples(index=False, name=None))

        with connection.cursor() as cursor:
            cursor.executemany("""INSERT INTO document_object (document_id,language,points)
                                               VALUES (%s,%s,%s) ON CONFLICT (document_id,language,points) DO NOTHING;
                                            """, [data])




    for u in users:
        df['username'] = u.username
        df['name_space'] = u.username.name_space
        df['insertion_time'] = datetime.now()
        df['language'] = 'english'


        if annotation == 'Graded labeling':
            data = list(df.itertuples(index=False, name=None))
            with connection.cursor() as cursor:
                cursor.executemany("""INSERT INTO annotate_label (document_id, topic_id,label,score,username,name_space,insertion_time,language)
                                                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,label,score,username) DO NOTHING ;
                                                """, [data])

        elif annotation == 'Passages annotation':
            df_anno = df[["doc_id","topic_id", "start", "stop",'username','name_space','insertion_time','language']]
            df_label = df[["doc_id","topic_id", "start", "stop",'label','score','username','name_space','insertion_time','language']]


            with connection.cursor() as cursor:

                data = list(df_anno.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate (document_id, topic_id,start,stop,username,name_space,insertion_time,language)
                                                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,username) DO NOTHING;
                                                """, [data])
                data = list(df_label.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate_passage (document_id, topic_id,start,stop,label,grade,username,name_space,insertion_time,language)
                                                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,label,grade,username) DO NOTHING ;
                                                """, [data])
        elif annotation == 'Entity tagging':
            df_anno = df[["doc_id", "topic_id", "start", "stop", 'username', 'name_space', 'insertion_time', 'language']]
            df_label = df[["doc_id", "topic_id", "start", "stop", 'tag', 'username', 'name_space', 'insertion_time',
                           'language']]

            with connection.cursor() as cursor:

                data = list(df_anno.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate (document_id, topic_id,start,stop,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,username,name_space) DO NOTHING;
                                                       """, [data])
                data = list(df_label.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO associate_tag (document_id, topic_id,start,stop,name,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,name,username) DO NOTHING;
                                                       """, [data])

        elif annotation == 'Relationships annotation':

            df_link = df[["doc_id", "topic_id", "subject_start", "subject_stop","object_start", "object_stop","predicate_start", "predicate_stop", 'username', 'name_space', 'insertion_time', 'language']]
            df_link = df_link.dropna()
            # todo


        elif annotation == 'Entity linking' :
            df_anno = df[["doc_id", "topic_id", "start", "stop", 'username', 'name_space', 'insertion_time', 'language']]
            df_label = df[["doc_id", "topic_id", "start", "stop", 'url','area', 'username', 'name_space', 'insertion_time',
                           'language']]

            with connection.cursor() as cursor:

                data = list(df_anno.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate (document_id, topic_id,start,stop,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,username,name_space) DO NOTHING;
                                                       """, [data])

                data = list(df_label.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO associate_tag (document_id, topic_id,start,stop,concept_url,name,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,concept_url,name,username) DO NOTHING;
                                                       """, [data])
        elif annotation == 'Facts annotation':
            df_anno = df[["doc_id", "topic_id", "subject_concept_url", "object_concept_url", 'predicate_concept_url',"subject_area", "object_area", 'predicate_area','username', 'name_space', 'insertion_time', 'language']]


            with connection.cursor() as cursor:

                data = list(df_anno.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO create_fact (document_id, topic_id,subject_concept_url,object_concept_url,predicate_concept_url,subject_name,object_name,predicate_name,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,start,stop,username,name_space) DO NOTHING;
                                                       """, [data])
        elif annotation == 'Relationships annotation':
            #TODO: finish
            print()

        elif annotation == 'Objects annotation':
            df_anno = df[["doc_id", "topic_id", "points", 'username', 'name_space', 'insertion_time','language']]
            df_label = df[["doc_id", "topic_id", "points",'label','score', 'username', 'name_space', 'insertion_time',
                           'language']]

            with connection.cursor() as cursor:

                data = list(df_anno.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate_object (document_id, topic_id,points,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,points,username,name_space) DO NOTHING;
                                                       """, [data])

                data = list(df_label.itertuples(index=False, name=None))
                cursor.executemany("""INSERT INTO annotate_object_label (document_id, topic_id,points,label,grade,username,name_space,insertion_time,language)
                                                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (document_id, topic_id,points,label,grade,username) DO NOTHING;
                                                       """, [data])

@shared_task
def add_collection(session,type_collection,topic_type,tags,labels,name,min_labels,max_labels,labels_p,min_labels_p,max_labels_p,description,share_with,ir_url,ir_preanno,file_paths,pubmed_ids):
    # Task logic here
    print("task started")
    options = {}
    username = session['username']
    msg = 'The task has started, it will take some time. Please, be patient.'
    #name = data.get('name', None)
    #type_collection = data.get('type_collection', None)
    #topic_type = data.get('topic_type', None)
    #tags = data.getlist('tags[]', None)
    #labels = data.getlist('labels[]', None)
    # min_labels = [int(n) for n in data.getlist('min_labels[]', None)]
    # max_labels = [int(n) for n in data.getlist('max_labels[]', None)]
    # labels_p = data.getlist('labels_p[]', None)
    # min_labels_p = [int(n) for n in data.getlist('min_labels_p[]', None)]
    # max_labels_p = [int(n) for n in data.getlist('max_labels_p[]', None)]
    # description = data.get('description', None)
    # share_with = data.get('members', None)
    # ir_url = data.get('ir_dataset', None)
    # ir_preanno = data.get('ir_preanno', None)
    # files = request.FILES.items()
    # pubmed_ids = data.get('pubmed_ids', None)

    to_enc = name + session['username']
    collection_id = hashlib.md5(to_enc.encode()).hexdigest()

    if ir_url == '':
        ir_url = None
    if ir_preanno == 'false':
        ir_preanno = False
    else:
        ir_preanno = True
    if share_with == '' or share_with is None:
        share_with = []
    else:
        share_with = share_with.replace('\\n', '\n').split('\n')
        share_with = [x.replace('\r', '').strip() for x in share_with if x != '']
    with transaction.atomic():
        collection = Collection.objects.create(collection_id=collection_id, description=description,
                                               annotation_type=AnnotationType.objects.get(
                                                   name=session['annotation_type']),
                                               name=name, modality='Collaborative open', type=type_collection,
                                               topic_type=topic_type,
                                               insertion_time=Now())
        # task = Task.objects.get(name=task)
        # for type in annotation_types:
        #     type = AnnotationType.objects.get(name=type)
        #     CollectionHasTask.objects.create(collection_id=collection, task_id=task, annotation_type=type)

        name_space = NameSpace.objects.get(name_space=session['name_space'])
        creator = User.objects.filter(username=session['username'], name_space=name_space)
        for c in creator:  # gestisco i vari name space
            ShareCollection.objects.create(collection_id=collection, username=c,
                                           name_space=c.name_space,creator=True, admin=True, status='accepted')
        for user in share_with:
            print(user)
            if user != session['username']:
                us = User.objects.filter(username=user, name_space=name_space)
                print(us.exists())
                if us.exists():
                    us = us.first()
                    ShareCollection.objects.create(collection_id=collection, username=us,
                                                   name_space=us.name_space,
                                                   status='invited')

        for i, label in enumerate(labels):
            min_lab = min_labels[i]
            max_lab = max_labels[i]
            label = Label.objects.get_or_create(name=label)[0]
            # for field in CollectionHasLabel._meta.get_fields():
            #     print(field.name)
            if not CollectionHasLabel.objects.filter(collection_id=collection, label=label).exists():
                CollectionHasLabel.objects.create(collection_id=collection, labels_annotation=True,
                                                  passage_annotation=False, label=label,
                                                  values=str(NumericRange(int(min_lab), int(max_lab), bounds='[]')))

        for i, label in enumerate(labels_p):
            min_lab = min_labels_p[i]
            max_lab = max_labels_p[i]
            label = Label.objects.get_or_create(name=label)[0]

            if not CollectionHasLabel.objects.filter(collection_id=collection, label=label).exists():
                CollectionHasLabel.objects.create(collection_id=collection, labels_annotation=False,
                                                  passage_annotation=True, label=label,
                                                  values=str(NumericRange(int(min_lab), int(max_lab), bounds='[]')))

        for tag in tags:
            if not Tag.objects.filter(name=tag).exists():
                tag = Tag.objects.create(name=tag)
                options[tag] = 'rgba(65, 105, 225, 1)'

            else:
                tag = Tag.objects.get(name=tag)
            if not CollectionHasTag.objects.filter(collection_id=collection, name=tag).exists():
                CollectionHasTag.objects.create(collection_id=collection, name=tag)

        if ir_url is not None and ir_url != '':
            load_ir_url(ir_url, name_space.name_space, username, share_with, ir_preanno, collection)
        else:
            # files = request.FILES.items()
            #pubmed_ids = data.get('pubmed_ids', None)
            files = [(path, open(path, "rb")) for path in file_paths]
            for filename, file in files:
                filename = filename.solit('/')[-1]
                if filename.startswith('concept'):
                    if file.name.endswith('json'):
                        upload_json_concepts(file, name_space.name_space, username, collection)
                    elif file.name.endswith('csv'):
                        upload_csv_concepts(file, name_space.name_space, username, collection)

                elif filename.startswith('topic') and ir_url is None:
                    upload_topics(file, collection)

                elif filename.startswith('document') and ir_url is None:
                    json_contents = create_json_content_from_file(file)
                    for json_content in json_contents:
                        language = 'english'

                        to_enc_id = session['username'] + str(datetime.now())
                        pid = hashlib.md5(to_enc_id.encode()).hexdigest()
                        if 'language' in list(json_content.keys()) and not json_content[
                                                                               'language'].lower() == 'english':
                            language = json_content['language']

                        if not Document.objects.filter(document_id=pid).exists():
                            if (file.name.endswith('json') or file.name.endswith('csv') or file.name.endswith(
                                    'txt') or file.name.endswith('pdf')):
                                Document.objects.create(batch=1, collection_id=collection, provenance='user',
                                                        document_id=pid, language=language, honeypot=False,
                                                        doc_id_not_hashed=json_content['doc_id'],
                                                        document_content=json_content, insertion_time=Now())
                            elif (file.name.endswith('png') or file.name.endswith('jpg') or file.name.endswith('jpeg')):
                                Document.objects.create(batch=1, collection_id=collection, provenance='user',
                                                        document_id=pid, language=language, honeypot=False,
                                                        doc_id_not_hashed=json_content['doc_id'],
                                                        document_content=json_content, insertion_time=Now(),
                                                        image=file.read())

            #pubmed_ids = data.get('pubmed_ids', None)
            if pubmed_ids is not None and pubmed_ids != '' and ir_url is None:
                pubmed_ids = pubmed_ids.split()
                if len(pubmed_ids) > 10:
                    pubmed_ids = pubmed_ids[0:15]
                for pid in pubmed_ids:
                    print('elaborating pid: ', pid)
                    json_val = insert_articles_of_PUBMED(pid)
                    if json_val:
                        print(str(datetime.now()))
                        to_enc_id = session['username'] + str(datetime.now())

                        pid = hashlib.md5(to_enc_id.encode()).hexdigest()

                        if not Document.objects.filter(document_id=pid).exists():
                            Document.objects.create(batch=1, document_id=pid,
                                                    provenance='pubmed', language='english',
                                                    document_content=json_val, honeypot=False,
                                                    insertion_time=Now(), collection_id=collection)

        areas = get_areas_collection(collection_id)
        tags = get_tags_collection(collection_id)
        options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags)) if
                   k not in list(set(areas + tags))}
        collection.options = options
        collection.save()

    return msg