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
def test_task(request):
    # Task logic here
    print('task avviato')
    time.sleep(10)
    print('task completo')
    return 'ciao'

@shared_task
def add_collection(request):
    # Task logic here
    options = {}
    username = request.session['username']
    msg = 'The task has started, it will take some time. Please, be patient.'
    name = request.POST.get('name', None)
    task = request.POST.get('task', None)
    labels = request.POST.get('labels', None)
    tags = request.POST.get('tags', None)
    annotation_types = request.POST.get('annotation_types', None)
    description = request.POST.get('description', None)
    to_enc = name + request.session['username']
    collection_id = hashlib.md5(to_enc.encode()).hexdigest()
    share_with = request.POST.get('members', None)
    ir_url = request.POST.get('ir_dataset', None)
    ir_preanno = request.POST.get('ir_preanno', None)
    min_labels = request.POST.get('min_labels', None)
    max_labels = request.POST.get('max_labels', None)

    if share_with == '' or share_with is None:
        share_with = []
    else:
        share_with = share_with.replace('\\n', '\n').split('\n')
        share_with = [x.replace('\r', '').strip() for x in share_with if x != '']
    if labels == '' or labels is None:
        labels = []
    else:
        labels = labels.replace('\\n', '\n').split('\n')
        labels = [x.replace('\r', '').strip() for x in labels if x != '']
    if tags == '' or tags is None:
        tags = []
    else:
        tags = tags.replace('\\n', '\n').split('\n')
        tags = [x.replace('\r', '').strip() for x in tags if x != '']

    collection = Collection.objects.create(collection_id=collection_id, description=description,
                                           name=name, modality='Collaborative open',
                                           insertion_time=Now(), username=request.session['username'],
                                           name_space=request.session['name_space'])
    task = Task.objects.get(name=task)
    for type in annotation_types:
        type = AnnotationType.objects.get(name=type)
        CollectionHasTask.objects.create(collection_id=collection, task_id=task, annotation_type=type)

    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    creator = User.objects.filter(username=request.session['username'], name_space=name_space)
    for c in creator:  # gestisco i vari name space
        ShareCollection.objects.create(collection_id=collection, username=c,
                                       name_space=c.name_space, status='Creator')
    for user in share_with:
        print(user)
        if user != request.session['username']:
            us = User.objects.filter(username=user, name_space=name_space)
            print(us.exists())
            if us.exists():
                us = us.first()
                ShareCollection.objects.create(collection_id=collection, username=us,
                                               name_space=us.name_space,
                                               status='Invited')

    for i,label in enumerate(labels):
        min_lab = min_labels[i]
        max_lab = max_labels[i]
        label = Label.objects.get_or_create(name=label)
        if not CollectionHasLabel.objects.filter(collection_id=collection, label=label).exists():
            CollectionHasLabel.objects.create(collection_id=collection, label=label,values=NumericRange(int(min_lab), int(max_lab), bounds='[]'))

    for tag in tags:
        if not Tag.objects.filter(name=tag).exists():
            tag = Tag.objects.create(name=tag)
            options[tag] = 'rgba(65, 105, 225, 1)'

        else:
            tag = Tag.objects.get(name=tag)
        if not CollectionHasTag.objects.filter(collection_id=collection, name=tag).exists():
            CollectionHasTag.objects.create(collection_id=collection, name=tag)

    if ir_url is not None:
        load_ir_url(ir_url, name_space.name_space, username, share_with, ir_preanno, collection)
    else:
        files = request.FILES.items()
        for filename, file in files:
            if filename.startswith('concept'):

                if file.name.endswith('json'):
                    upload_json_concepts(file, name_space.name_space, username, collection)
                elif file.name.endswith('csv'):
                    upload_csv_concepts(file, name_space.name_space, username, collection)
            elif filename.startswith('topic') and ir_url is None:
                upload_topics(file, collection)
            elif filename.startswith('qrels') and ir_url is None:
                upload_qrels(file, name_space.name_space, share_with, collection)
            elif filename.startswith('document') and ir_url is None:
                json_contents = create_json_content_from_file(file)
                for json_content in json_contents:
                    language = 'english'

                    to_enc_id = request.session['username'] + str(datetime.now())
                    pid = hashlib.md5(to_enc_id.encode()).hexdigest()
                    if 'language' in list(json_content.keys()) and not json_content[
                                                                           'language'].lower() == 'english':
                        language = json_content['language']

                    if not Document.objects.filter(document_id=pid).exists():
                        Document.objects.create(batch=1, collection_id=collection, provenance='user',
                                                document_id=pid, language=language,
                                                document_content=json_content, insertion_time=Now())

        pubmed_ids = request.POST.get('pubmed_ids', None)
        if pubmed_ids is not None and pubmed_ids != '' and ir_url is None:
            pubmed_ids = pubmed_ids.split()
            if len(pubmed_ids) > 10:
                pubmed_ids = pubmed_ids[0:10]
            for pid in pubmed_ids:
                print('elaborating pid: ', pid)
                json_val = insert_articles_of_PUBMED(pid)
                if json_val:
                    print(str(datetime.now()))
                    to_enc_id = request.session['username'] + str(datetime.now())

                    pid = hashlib.md5(to_enc_id.encode()).hexdigest()

                    if not Document.objects.filter(document_id=pid).exists():
                        Document.objects.create(batch=1, document_id=pid,
                                                provenance='pubmed', language='english',
                                                document_content=json_val,
                                                insertion_time=Now(), collection_id=collection)

    areas = get_areas_collection(collection_id)
    tags = get_tags_collection(collection_id)
    options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags)) if
               k not in list(set(areas + tags))}
    collection.options = options
    collection.save()

    return msg