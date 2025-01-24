from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
import hashlib
from doctron_app.upload.utils_upload import *
from doctron_app.upload.utils_pubmed import *
from doctron_app.utils import *
from doctron_app.upload.configure import *

from django.db import transaction
import json
import os
from doctron_app.models import *
from django.http import HttpResponse
import ir_datasets


def load_ir_url(ir_url, name_space, username, users, ir_preanno, collection):

    try:
        documents, topics, qrels = [],[],[]
        dataset = ir_datasets.load(ir_url)

        for doc in dataset.docs_iter():
            document = {}

            doc_id = getattr(doc, 'doc_id', None)
            to_enc_id = username + str(datetime.now())
            pid = hashlib.md5(to_enc_id.encode()).hexdigest()
            document['document_id'] = doc_id
            if doc_id is None:
                return False
            for field in doc._fields:
                value = getattr(doc, field)
                document[field] = value

            Document.objects.create(batch=1, collection_id=collection, provenance='user',
                                    document_id=pid, language='english',
                                    document_content=document, insertion_time=Now())

        for query in dataset.queries_iter():
            details = {}
            topic = {}

            query_id = getattr(query, 'query_id', None)
            topic['query_id'] = query_id

            if query_id is None:
                return False
            for field in query._fields:
                value = getattr(query, field)
                details[field] = value
            topic['details'] = details
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO topic (topic_id,collection_id,title,description,narrative,details) values (%s,%s,%s,%s,%s,%s)""",
                    [query_id, collection.collection_id, None, None, None, json.dumps(details)])
            # Topic.objects.create(topic_id=query_id,collection_id=collection,details=details)

        for qrel in dataset.qrels_iter():
            rel = {}
            details = {}
            query_id = getattr(qrel, 'query_id', None)
            rel['query_id'] = query_id
            doc_id = getattr(qrel, 'doc_id', None)
            relevance = getattr(qrel, 'relevance', None)
            rel['doc_id'] = doc_id
            rel['relevance'] = relevance

            if query_id is None or doc_id is None or relevance is None:
                return False
            for field in query._fields:
                value = getattr(query, field)
                rel[field] = value
                details[field] = value
            rel['details'] = details
            qrels.append(rel)

    except Exception as e:
        print(e)
        return False
