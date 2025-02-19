import datetime
from http.client import HTTPResponse

from doctron_app.utils_copy_annotations import *

import django.utils.timezone as timezone_1
from django.db.models import Max
from doctron_app.utils_download import *
from doctron_app.upload.ir_datases import *
from datetime import timedelta
import time
from doctron_app.utils_stats import *
from django.contrib.sessions.backends.db import SessionStore
import secrets
from django.conf import settings
from doctron_app.tasks import test_task, add_collection


# test
def link_orcid(request):
    # Save the user's session ID in the session store
    session_store = SessionStore()
    session_store['username'] = request.session['username']
    session_store['collection'] = request.session['collection']
    session_store['document'] = request.session['document']
    session_store['language'] = request.session['language']
    session_store['name_space'] = request.session['name_space']
    session_store['fields'] = request.session['fields']
    session_store['fields_to_ann'] = request.session['fields_to_ann']
    session_store['sessionid'] = request.session.session_key
    session_store.save()
    state = secrets.token_urlsafe(16)
    # Generate a random state parameter to prevent CSRF attacks
    orcid_url = f'https://orcid.org/oauth/authorize?client_id={settings.ORCID_CLIENT_ID}&response_type=code&scope=/authenticate&redirect_uri={settings.ORCID_REDIRECT_LINK_URI}&state={state}'
    return redirect(orcid_url)


def login_with_orcid(request):
    # redirect_uri = request.build_absolute_uri(reverse('orcid_callback'))
    orcid_url = f'https://orcid.org/oauth/authorize?client_id={settings.ORCID_CLIENT_ID}&response_type=code&scope=/authenticate&redirect_uri={settings.ORCID_REDIRECT_URI}'
    return redirect(orcid_url)

    # api = PublicAPI(settings.ORCID_CLIENT_ID,settings.ORCID_CLIENT_SECRET,sandbox=True)
    # url = api.get_login_url(scope=['/authenticate'],redirect_uri=settings.ORCID_REDIRECT_URI)
    # return redirect(url)


def signup_with_orcid(request):
    # redirect_uri = request.build_absolute_uri(reverse('orcid_callback'))
    final_url = settings.ORCID_REDIRECT_URI_REGISTER
    orcid_url = f'https://orcid.org/oauth/authorize?client_id={settings.ORCID_CLIENT_ID}&response_type=code&scope=/authenticate&redirect_uri={final_url}'
    return redirect(orcid_url)

    # api = PublicAPI(settings.ORCID_CLIENT_ID,settings.ORCID_CLIENT_SECRET,sandbox=True)
    # url = api.get_login_url(scope=['/authenticate'],redirect_uri=settings.ORCID_REDIRECT_URI)
    # return redirect(url)


def loginorcidcallback(request, type=False):
    code = request.GET.get('code')
    if type == 'link':
        session_id = request.COOKIES.get('sessionid')

        session = SessionStore(session_key=session_id)
        session_data = session.load()
        username = session_data['username']
        if not username:
            return redirect('doctron_app:index')
        session.update(session_data)
        session.save()

    token_url = 'https://orcid.org/oauth/token'
    if type == 'register':
        redir_url = settings.ORCID_REDIRECT_URI_REGISTER
    elif type == 'link':
        redir_url = settings.ORCID_REDIRECT_LINK_URI
    else:
        redir_url = settings.ORCID_REDIRECT_URI

    data = {
        'client_id': settings.ORCID_CLIENT_ID,
        'client_secret': settings.ORCID_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'scope': '/authenticate',
        'redirect_uri': redir_url
    }
    error = False
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        state = request.GET.get('state')
        print(state)

        resp = json.loads(response.text)
        name = resp['name']
        orcid = resp['orcid']
        orcid_token = resp['access_token']
        if orcid != 'null' and orcid is not None and orcid != '':
            params = {'orcid': orcid, 'orcid_token': orcid_token}
            url = get_baseurl() + 'login'
            if type == 'register':
                # search available usernames
                users = User.objects.all()
                usernames = [u.username for u in users]
                name = name.replace(' ','')
                while name in usernames:
                    sequence = [random.randint(0, 100) for _ in range(3)]
                    name = name + str(sequence)

                params = {'orcid': orcid, 'orcid_token': orcid_token, 'username': name}
                url = get_baseurl() + 'register'
            elif type == 'link':
                params = {'orcid': orcid, 'orcid_token': orcid_token, 'username': username}
                url = get_baseurl() + 'link'


            # Make the POST request to the other view
            response = requests.post(url, data=params)
            if response.status_code == 200:
                # return response
                print('tutto ok')
                resp = response.json()
                request.session['username'] = resp['username']
                request.session['name_space'] = 'Human'
                request.session['profile'] = resp['profile']
                if type == 'link':
                    return redirect('doctron_app:logout')
                return redirect('doctron_app:index')
            else:
                error = True

        else:
            error = True
    if error:
        return redirect('doctron_app:loginPage', orcid_error=True)


def link(request):
    """This view links an orcid to a user"""

    username = request.session.get('username', None)
    if username is None:
        username = request.POST.get('username')
    orcid_token = request.POST.get('orcid_token')
    orcid = request.POST.get('orcid')
    print(username, orcid, orcid_token)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE public.user SET orcid = %s, orcid_token = %s WHERE username = %s""",
                           [orcid, orcid_token, username])
        user = User.objects.filter(username=username, orcid_token=orcid_token, orcid=orcid)
        resp = {'username': user.first().username, 'profile': user.first().profile}
        response = JsonResponse(resp, status=200)
        return response
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def set_profile(request):
    profile = json.loads(request.body)
    profile = profile['profile']
    request.session['profile'] = profile
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("UPDATE public.user set profile = %s where username = %s",[profile,request.session['username']])
        return HttpResponse(status=200)

    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def login(request):

    """Login page for app """

    # print('login')
    try:
        if request.method == 'POST':
            md5_pwd = ''
            username = request.POST.get('username', False)
            annotation_type = request.POST.get('annotation_type', False)
            mode1 = 'Human'
            password = request.POST.get('password', False)
            orcid = request.POST.get("orcid",False)
            if username:
                username = username.replace("\"", "").replace("'", "")
            if password:
                password = password.replace("\"", "").replace("'", "")
                md5_pwd = hashlib.md5(password.encode()).hexdigest()

            if ((username != False and password != False and annotation_type != False) or orcid != False):
                if (username != False and password != False):
                    user = User.objects.filter(username = username,password = md5_pwd)
                else:
                    user = User.objects.filter(orcid = orcid)

                if user.exists():
                    request.session['username'] = user.first().username
                    request.session['profile'] = user.first().profile
                    user = user.first()
                    # with connection.cursor() as cursor:
                    #     cursor.execute("SELECT DISTINCT c.collection_id,c.annotation_type FROM share_collection as s "
                    #                    "INNER JOIN collection_has_task as c ON c.collection_id = s.collection_id "
                    #                    "WHERE s.username = %s",
                    #                    [request.session['username']])
                    #     results = cursor.fetchall()
                    #
                    # # Accedi ai valori usando i nomi delle colonne
                    # collections = []
                    # types = []
                    # for row in results:
                    #     collection_id = Collection.objects.get(collection_id=row[0])
                    #     t = AnnotationType.objects.get(id=int(row[1])).name
                    #     if collection_id not in collections:
                    #         collections.append(collection_id)
                    #     types.append(t)
                    annotation_type = AnnotationType.objects.get(name=annotation_type)
                    collections = Collection.objects.filter(annotation_type = annotation_type)
                    documents = Document.objects.filter(collection_id__in=collections)
                    if user.ncbi_key is not None:
                        os.environ['NCBI_API_KEY'] = user.first().ncbi_key
                    # prima recupero la sessione dall'ultima annotazione
                    if SessionDoc.objects.filter(username = user,collection_id__in=collections).exists():
                        sessions = SessionDoc.objects.filter(username = user,collection_id__in=collections).order_by('-last_view')
                        session = sessions.first()
                        document = session.document_id
                        role = session.role
                        request.session['language'] = document.language
                        request.session['name_space'] = user.name_space_id
                        request.session['collection'] = document.collection_id_id
                        # task = CollectionHasTask.objects.filter(collection_id = document.collection_id).first()
                        # task = task.task_id.name
                        # request.session['task'] = task
                        request.session['topic'] = session.topic_id_id
                        # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                        # types = [c.annotation_type.name for c in types]
                        request.session['annotation_type'] = document.collection_id.annotation_type.name
                        request.session['document'] = document.document_id
                        request.session['batch'] = document.batch
                        request.session['role'] = role
                        request.session['fields'] = request.session['fields_to_ann'] =  get_fields_list(request.session['document'],request.session['language'])

                    elif GroundTruthLogFile.objects.filter(username = user,document_id__in=documents).exists():
                        gts = GroundTruthLogFile.objects.filter(username = user,document_id__in=documents).order_by('-insertion_time')
                        last_gt = gts.first()
                        name_space = last_gt.name_space
                        document = last_gt.document_id
                        request.session['topic'] = last_gt.topic_id_id

                        request.session['language'] = document.language
                        request.session['name_space'] = name_space.name_space
                        request.session['collection'] = document.collection_id_id
                        # task = CollectionHasTask.objects.filter(collection_id = document.collection_id).first()
                        # task = task.task_id.name
                        # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                        # types = [c.annotation_type.name for c in types]
                        request.session['annotation_type'] = document.collection_id.annotation_type.name
                        # request.session['task'] = task
                        request.session['document'] = document.document_id
                        request.session['batch'] = document.batch
                        request.session['fields'] = request.session['fields_to_ann'] =  get_fields_list(request.session['document'],request.session['language'])

                    # se non ho ultima annotazione ma ho collezioni, allora setto la collezione all'ultima aggiunta e al primo doc della prima batch
                    elif ShareCollection.objects.filter(username = user,collection_id__in=collections).exclude(status = 'invited').exists(): # non importa il name space in questo caso
                        collections = ShareCollection.objects.filter(username = user,collection_id__in=collections).exclude(status = 'invited').values('collection_id').distinct()
                        collections_ids = [c['collection_id'] for c in collections]
                        collections = Collection.objects.filter(collection_id__in=collections_ids).order_by('-insertion_time')
                        collection = collections.first()
                        request.session['annotation_type'] = collection.annotation_type.name
                        t = Topic.objects.filter(collection_id=collection)
                        print(type(t))
                        print(type(collections))
                        if t.exists():
                            t = t.first()
                            request.session['topic'] = t.id
                        # request.session['task'] = task
                        request.session['collection'] = collection.collection_id
                        docs = Document.objects.filter(collection_id = collection)
                        if Split.objects.filter(username=user, collection_id=collection,
                                                document_id__in=docs).exists():
                            docs = Split.objects.filter(username=user, collection_id=collection,
                                                document_id__in=docs)
                            docs = sorted([d.document_id_id for d in docs])
                        else:
                            docs = sorted([d.document_id for d in docs])
                        document = Document.objects.get(document_id = docs[0])

                        request.session['document'] = document.document_id
                        request.session['language'] = document.language
                        request.session['batch'] = document.batch
                        request.session['name_space'] = mode1
                        request.session['role'] = request.session.get('role','Annotator')
                        request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                    request.session['language'])

                    else:
                        request.session['collection'] = None
                        request.session['document'] = None
                        request.session['topic'] = None
                        request.session['language'] = None
                        request.session['annotation_type'] = annotation_type.name

                        #request.session['task'] = task
                        request.session['types'] = []
                        request.session['name_space'] = 'Human'
                        request.session['fields'] = []
                        request.session['role'] = 'Annotator'
                        request.session['fields_to_ann'] = []

                    # return JsonResponse({'msg':'ok'})
                    if orcid:
                        resp = {'username': user.first().username, 'profile': user.first().profile}
                        response = JsonResponse(resp, status=200)
                        return response
                    return redirect('doctron_app:index')

            # return render(request, 'doctron_app/index.html',status=500)
            if orcid:
                response = HttpResponse(status=500)
                return response
            return JsonResponse({'error':'errore'},status=500)



        else:
            username = request.session.get('username', False)
            profile = request.session.get('profile', False)
            name_space = request.session.get('name_space', False)
            if username and profile and name_space:
                return redirect('doctron_app:index')

            # context = {'username': username, 'profile': user.profile}
            # return render(request, 'doctron_app/index.html')
            return redirect('doctron_app:loginPage')

    except Exception as e:
        print(e)
        return HttpResponse(status = 500)


def unlink_orcid(reuqest):
    """Unlink the orcid of the user"""

    username = reuqest.session.get('username', None)
    try:
        if username is not None:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE public.user SET orcid = NULL, orcid_token = NULL where username = %s",
                                   [username])
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


def password(request):
    """Get password of a user"""

    password = None
    if request.method == "GET":
        username = request.session.get('username', None)
        if username:
            user = User.objects.filter(username=username).first()
            password = user.password

        if password:
            return HttpResponse('ok', status=200)
        else:
            return HttpResponse('none', status=200)
    elif request.method == "POST":
        password = json.loads(request.body)['password']
        username = request.session.get('username', None)
        if username and password:

            password = hashlib.md5(password.encode()).hexdigest()
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE public.user SET password = %s where username = %s", [password, username])
                return HttpResponse('ok', status=200)
            except Exception as e:
                return HttpResponse('error', status=200)


def register(request):
    """This view handles the registration of new users: username, password and profile are inserted in the database"""

    if request.method == 'POST':
        username = request.POST.get('username', None)
        password1 = request.POST.get('password', None)
        password_check = request.POST.get('password_check', None)
        profile = request.POST.get('profile', 'Beginner')
        orcid = request.POST.get('orcid', None)
        email = request.POST.get('email', None)
        orcid_token = request.POST.get('orcid_token', None)
        ncbikey = request.POST.get('ncbikey', None)
        try:
            with transaction.atomic():
                ns_human = NameSpace.objects.get(name_space='Human')

                if not User.objects.filter(name_space=ns_human, username='IAA-Inter Annotator Agreement').exists():
                    User.objects.create(username='IAA-Inter Annotator Agreement', profile='Tech',
                                        password=hashlib.md5("iaa".encode()).hexdigest(), name_space=ns_human,
                                        orcid=None, ncbi_key=None)
                if not username or (not password1 and not orcid) or not profile or not email:
                    return JsonResponse({'error': 'missing credentials'}, status=500)

                if User.objects.filter(email=email).exists():
                    return JsonResponse({'message': 'There is an account registered with this email'}, status=500)

                if User.objects.filter(username=username).exists() or username == 'global':
                    if orcid:
                        if User.objects.filter(orcid=orcid).exists():
                            return JsonResponse({'message': 'The orcid is already assigned'})

                        i = 0
                        found = True
                        while found:
                            username = username + '_' + str(i)
                            i += 1
                            if not User.objects.filter(username=username).exists():
                                found = False
                    else:
                        return JsonResponse({'message': 'The username you chose already exists'}, status=500)

                if orcid:
                    User.objects.create(username=username, profile=profile, password=password1, name_space=ns_human,
                                        orcid=orcid, orcid_token=orcid_token, ncbi_key=ncbikey)

                if password1 == password_check and password1 is not None:
                    password = hashlib.md5(password1.encode()).hexdigest()
                    User.objects.create(username=username, email=email, profile=profile, password=password,
                                        name_space=ns_human, orcid=orcid, ncbi_key=ncbikey)



        except (Exception) as error:
            print(error)
            # context = {: "Something went wrong, probably you did not set any profile"}
            return JsonResponse({'error': 'This username already exists'}, status=500)
        else:
            request.session['username'] = username
            request.session['name_space'] = 'Human'
            request.session['profile'] = profile
            if orcid:
                print(request.session.get('username', None))
                resp = {'username': username, 'profile': profile}
                response = JsonResponse(resp, status=200)
                return response
            return redirect('doctron_app:index')
            # return JsonResponse({'response': 'ok'},status = 200)

    # return render(request, 'doctron_app/login.html')


def home(request):
    """Home page for app (and project)"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)

    baseurl = get_baseurl()
    if (username and baseurl != ''):
        orcid = User.objects.get(username=username)
        orcid = orcid.orcid
        if orcid == None:
            orcid = ''
        context = {'username': username, 'profile': profile, 'baseurl': baseurl, 'orcid': orcid}
        return render(request, 'doctron_app/index.html', context)
    else:
        context = {}
        return render(request, 'doctron_app/index.html', context)


def index(request):
    """Home page for app (and project)"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)

    baseurl = get_baseurl()
    if (username and baseurl != ''):
        orcid = User.objects.get(username=username)
        orcid = orcid.orcid
        if orcid == None:
            orcid = ''

        context = {'username': username, 'profile': profile, 'baseurl': baseurl, 'orcid': orcid}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def logout(request):
    """Logout: deletion of session's parameters"""

    try:
        for key in request.session.keys():
            del request.session[key]

        # return redirect('doctron_app:login')
    except KeyError:
        pass
    finally:
        request.session.flush()
        return redirect('doctron_app:login')


def registration(request):
    """This view handles the registration of new users: username, password and profile are inserted in the database"""

    if request.method == 'POST':
        username = request.POST.get('username', None)
        password1 = request.POST.get('password', None)
        profile = request.POST.get('profile', None)

        try:
            with transaction.atomic():

                password = hashlib.md5(password1.encode()).hexdigest()
                ns_robot = NameSpace.objects.get(ns_id='Robot')
                ns_human = NameSpace.objects.get(ns_id='Human')
                # User.objects.create(username = username,profile=profile,password = password,ns_id=ns_robot)
                User.objects.create(username=username, profile=profile, password=password, ns_id=ns_human)
                request.session['username'] = username
                request.session['name_space'] = 'Human'
                request.session['profile'] = profile

                # admin = User.objects.filter(profile='Admin')
                # admin = admin.first()
                #
                # admin_name = admin.username
                # request.session['team_member'] = admin_name

                return redirect('doctron_app:index')
        except (Exception) as error:
            print(error)
            return render(request, 'doctron_app/index.html')


def credits(request):
    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    baseurl = get_baseurl()
    if (username and baseurl != ''):
        context = {'username': username, 'profile': profile, 'baseurl': baseurl}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def demo(request):
    """Demo page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    baseurl = get_baseurl()
    context = {'username': username, 'profile': profile, 'baseurl': baseurl, 'orcid': None}
    return render(request, 'doctron_app/index.html', context)


def instructions(request):
    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    baseurl = get_baseurl()
    if (username and baseurl != ''):
        context = {'username': username, 'profile': profile, 'baseurl': baseurl}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def statistics(request, collection_id=None, type=None):
    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    baseurl = get_baseurl()
    # name_space = NameSpace.objects.get(name_space='Human')

    name_space = request.session['name_space']
    name_space = NameSpace.objects.get(name_space=name_space)
    user_iaa = User.objects.get(username="IAA-Inter Annotator Agreement", name_space=name_space)
    if request.method == 'GET':
        if (type is None and Collection.objects.filter(collection_id=collection_id).exists()) or (
                type is None and collection_id is None):
            # in questi due casi faccio un render
            if (username and baseurl != ''):
                context = {'username': username, 'profile': profile, 'baseurl': baseurl}
                return render(request, 'doctron_app/index.html', context)
            else:
                return redirect('doctron_app:login')

        elif type == 'general' and collection_id == 'personal':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            json_doc = {}
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)

            collection = Collection.objects.get(collection_id=collection)

            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
                json_doc['annotated_documents'] = GroundTruthLogFile.objects.filter(document_id__in=documents,
                                                                                    name_space=name_space,
                                                                                    username=user).count()
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)

            json_doc['mentions'] = Annotate.objects.filter(document_id__in=documents, name_space=name_space,
                                                           username=user).count()
            json_doc['concepts'] = Associate.objects.filter(document_id__in=documents, name_space=name_space,
                                                            username=user).count()
            json_doc['labels'] = AnnotateLabel.objects.filter(document_id__in=documents, name_space=name_space,
                                                              username=user).count()
            json_doc['assertions'] = CreateFact.objects.filter(document_id__in=documents, name_space=name_space,
                                                               username=user).count()
            documents_list_ids = [x.document_id for x in documents]
            json_doc['relationships'] = Link.objects.filter(subject_document_id__in=documents_list_ids,
                                                            name_space=name_space,
                                                            username=user).count() + \
                                        RelationshipPredConcept.objects.filter(
                                            subject_document_id__in=documents_list_ids, name_space=name_space,
                                            username=user).count() + \
                                        RelationshipObjConcept.objects.filter(
                                            subject_document_id__in=documents_list_ids, name_space=name_space,
                                            username=user).count() + \
                                        RelationshipSubjConcept.objects.filter(
                                            object_document_id__in=documents_list_ids, name_space=name_space,
                                            username=user).count() + \
                                        RelationshipSubjMention.objects.filter(document_id__in=documents,
                                                                               name_space=name_space,
                                                                               username=user).count() + \
                                        RelationshipObjMention.objects.filter(document_id__in=documents,
                                                                              name_space=name_space,
                                                                              username=user).count() + \
                                        RelationshipPredMention.objects.filter(document_id__in=documents,
                                                                               name_space=name_space,
                                                                               username=user).count()
            return JsonResponse(json_doc)

        elif type == 'general' and collection_id == 'global':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            json_doc = {}
            # name_space = NameSpace.objects.get(name_space = request.session.get('name_space'))
            # user = User.objects.get(username=username,name_space = name_space)
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            collection = Collection.objects.get(collection_id=collection)
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                json_doc['annotated_documents'] = GroundTruthLogFile.objects.filter(document_id__in=documents,
                                                                                    name_space=name_space).count()
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)

            json_doc['annotators_count'] = GroundTruthLogFile.objects.filter(document_id__in=documents,
                                                                             name_space=name_space).distinct(
                'username').count()
            json_doc['mentions'] = Annotate.objects.filter(document_id__in=documents, name_space=name_space).count()
            json_doc['concepts'] = Associate.objects.filter(document_id__in=documents, name_space=name_space).count()
            json_doc['labels'] = AnnotateLabel.objects.filter(document_id__in=documents, name_space=name_space).count()
            json_doc['assertions'] = CreateFact.objects.filter(document_id__in=documents, name_space=name_space).count()
            documents_list_ids = [x.document_id for x in documents]
            json_doc['relationships'] = Link.objects.filter(subject_document_id__in=documents_list_ids,
                                                            name_space=name_space).count() + \
                                        RelationshipPredConcept.objects.filter(
                                            subject_document_id__in=documents_list_ids, name_space=name_space).count() + \
                                        RelationshipObjConcept.objects.filter(
                                            subject_document_id__in=documents_list_ids, name_space=name_space).count() + \
                                        RelationshipSubjConcept.objects.filter(
                                            object_document_id__in=documents_list_ids, name_space=name_space).count() + \
                                        RelationshipSubjMention.objects.filter(document_id__in=documents,
                                                                               name_space=name_space).count() + \
                                        RelationshipObjMention.objects.filter(document_id__in=documents,
                                                                              name_space=name_space).count() + \
                                        RelationshipPredMention.objects.filter(document_id__in=documents,
                                                                               name_space=name_space).count()
            json_doc['iaa'] = {}
            st = time.time()
            mention_agreement = global_mentions_agreement(collection.collection_id, documents)
            print('mentions', str(time.time() - st))
            st = time.time()
            concepts_agreement = global_concepts_agreement(collection.collection_id, documents)
            print(time.time() - st)

            st = time.time()
            rels_agreement = global_relationships_agreement(collection.collection_id, documents)
            print(time.time() - st)

            st = time.time()
            ass_agreement = global_createfact_agreement(collection.collection_id, documents)
            print(time.time() - st)

            st = time.time()
            labels_agreement = global_labels_agreement(collection.collection_id, documents)
            print(time.time() - st)

            json_doc['iaa']['mentions'] = round(mention_agreement, 3) if mention_agreement != '' else ''
            json_doc['iaa']['concepts'] = round(concepts_agreement, 3) if concepts_agreement != '' else ''
            json_doc['iaa']['labels'] = round(labels_agreement, 3) if labels_agreement != '' else ''
            json_doc['iaa']['assertions'] = round(ass_agreement, 3) if ass_agreement != '' else ''
            json_doc['iaa']['relationships'] = round(rels_agreement, 3) if rels_agreement != '' else ''
            return JsonResponse(json_doc)

        elif type == 'relationship_area' and collection_id == 'personal':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            # name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))
            # user = User.objects.get(username=username, name_space=name_space)
            collection = Collection.objects.get(collection_id=collection)
            distinct_areas = AddConcept.objects.filter(collection_id=collection).distinct('name')
            distinct_areas = [x.name_id for x in distinct_areas]
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)
            docs = [x.document_id for x in documents]
            # json_doc = {}
            # json_doc['subject'] = {}
            # json_doc['predicate'] = {}
            # json_doc['object'] = {}
            users_all = ShareCollection.objects.filter(collection_id=collection)
            users_all = [a.username for a in users_all]
            json_doc = compute_relationship_area_global(distinct_areas, documents, docs, name_space,
                                                        users=[user.username])
            return JsonResponse(json_doc)

        elif type == 'relationship_area' and collection_id == 'global':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            # name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))
            # user = User.objects.get(username=username, name_space=name_space)
            collection = Collection.objects.get(collection_id=collection)
            distinct_areas = AddConcept.objects.filter(collection_id=collection).distinct('name')
            distinct_areas = [x.name_id for x in distinct_areas]
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)
            docs = [x.document_id for x in documents]
            # json_doc = {}
            # json_doc['subject'] = {}
            # json_doc['predicate'] = {}
            # json_doc['object'] = {}
            users_all = ShareCollection.objects.filter(collection_id=collection)
            users_all = [a.username for a in users_all]
            json_doc = compute_relationship_area_global(distinct_areas, documents, docs, name_space, users=users_all)
            return JsonResponse(json_doc)


        elif type == 'concept_area' and collection_id == 'personal':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            # name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))
            # user = User.objects.get(username=username, name_space=name_space)
            collection = Collection.objects.get(collection_id=collection)
            distinct_areas = AddConcept.objects.filter(collection_id=collection).distinct('name')
            distinct_areas = [x.name_id for x in distinct_areas]
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)
            json_doc = {}
            json_doc['concepts_per_area'] = {}
            json_doc['count_per_area'] = {}
            for area in distinct_areas:
                area_obj = SemanticArea.objects.get(name=area)
                json_doc['concepts_per_area'][area] = {}
                json_doc['count_per_area'][area] = Associate.objects.filter(document_id__in=documents,
                                                                            name_space=name_space, username=user,
                                                                            name=area_obj).count()
                concepts = Associate.objects.filter(document_id__in=documents, name_space=name_space, username=user,
                                                    name=area_obj).values('concept_url').order_by(
                    'concept_url').annotate(count=Count('concept_url'))
                for concept in concepts:
                    con = Concept.objects.get(concept_url=concept['concept_url'])
                    json_doc['concepts_per_area'][area][con.concept_name] = concept['count']

            return JsonResponse(json_doc)

        elif type == 'concept_area' and collection_id == 'global':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))
            collection = Collection.objects.get(collection_id=collection)
            distinct_areas = AddConcept.objects.filter(collection_id=collection).distinct('name')
            distinct_areas = [x.name_id for x in distinct_areas]
            user = User.objects.get(username=username, name_space=name_space)
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)
            json_doc = {}
            json_doc['concepts_per_area'] = {}
            json_doc['count_per_area'] = {}
            for area in distinct_areas:
                area_obj = SemanticArea.objects.get(name=area)
                json_doc['concepts_per_area'][area] = {}
                json_doc['count_per_area'][area] = Associate.objects.filter(document_id__in=documents,
                                                                            name_space=name_space,
                                                                            name=area_obj).count()
                concepts = Associate.objects.filter(document_id__in=documents, name_space=name_space,
                                                    name=area_obj).values('concept_url').order_by(
                    'concept_url').annotate(count=Count('concept_url'))

                for concept in concepts:
                    con = Concept.objects.get(concept_url=concept['concept_url'])
                    json_doc['concepts_per_area'][area][con.concept_name] = concept['count']
            return JsonResponse(json_doc)

        elif type == 'general' and collection_id == 'personal':
            document = request.GET.get('document')
            collection = request.GET.get('collection')
            json_doc = {}
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            # name_space = NameSpace.objects.get(name_space = request.session.get('name_space'))
            # user = User.objects.get(username=username,name_space = name_space)
            collection = Collection.objects.get(collection_id=collection)
            if document == '':
                documents = Document.objects.filter(collection_id=collection)
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(collection_id=collection,username=user,name_space=name_space).exists():
                    documents = Split.objects.filter(collection_id=collection,username=user,name_space=name_space)
                    documents = [d.document_id for d in documents]
                json_doc['annotated_documents'] = GroundTruthLogFile.objects.filter(document_id__in=documents,
                                                                                    name_space=name_space,
                                                                                    username=user).count()
            else:
                documents = Document.objects.filter(collection_id=collection, document_id=document)
            json_doc['mentions'] = Annotate.objects.filter(document_id__in=documents, name_space=name_space,
                                                           username=user).count()
            json_doc['concepts'] = Associate.objects.filter(document_id__in=documents, name_space=name_space,
                                                            username=user).count()
            json_doc['labels'] = AnnotateLabel.objects.filter(document_id__in=documents, name_space=name_space,
                                                              username=user).count()
            json_doc['assertions'] = CreateFact.objects.filter(document_id__in=documents, name_space=name_space,
                                                               username=user).count()
            documents_list_ids = [x.document_id for x in documents]
            json_doc['relationships'] = Link.objects.filter(subject_document_id__in=documents_list_ids,
                                                            name_space=name_space,
                                                            username=user).count() + RelationshipPredConcept.objects.filter(
                subject_document_id__in=documents_list_ids, name_space=name_space, username=user).count() + \
                                        RelationshipObjConcept.objects.filter(
                                            subject_document_id__in=documents_list_ids, name_space=name_space,
                                            username=user).count() + RelationshipSubjConcept.objects.filter(
                object_document_id__in=documents_list_ids, name_space=name_space,
                username=user).count() + RelationshipSubjMention.objects.filter(document_id__in=documents,
                                                                                name_space=name_space,
                                                                                username=user).count() + RelationshipObjMention.objects.filter(
                document_id__in=documents, name_space=name_space,
                username=user).count() + RelationshipPredMention.objects.filter(document_id__in=documents,
                                                                                name_space=name_space,
                                                                                username=user).count()
            return JsonResponse(json_doc)


        elif type == 'annotators_per_document' and collection_id is not None:
            collection = Collection.objects.get(collection_id=collection_id)
            documents = Document.objects.filter(collection_id=collection)
            documents = Document.objects.filter(collection_id=collection)

            user = User.objects.get(username=username, name_space=name_space)
            if Split.objects.filter(collection_id=collection, username=user, name_space=name_space).exists():
                documents = Split.objects.filter(collection_id=collection, username=user, name_space=name_space)
                documents = [d.document_id for d in documents]
            # documents = GroundTruthLogFile.objects.filter(document_id__in=documents).annotate(count=Count('document_id')).order_by('count')

            json_resp = {}
            dict_docs = []
            for document in documents:
                if 'doc_id' in list(document.document_content.keys()):
                    doc = document.document_content['doc_id']
                else:
                    doc = document.document_id

                json_resp[document.document_id] = {}
                json_resp[document.document_id]['count'] = GroundTruthLogFile.objects.filter(
                    document_id=document).exclude(username=user_iaa).count()
                annotators_list = GroundTruthLogFile.objects.filter(document_id=document).exclude(
                    username=user_iaa).distinct('username')
                json_resp[document.document_id]['annotators'] = [x.username_id for x in annotators_list]
            return JsonResponse(json_resp)


        elif type == 'annotation_per_document' and collection_id is not None:
            user = request.session['username']
            username_req = request.GET.get('user', None)
            name_space = NameSpace.objects.get(name_space=request.session.get('name_space'))

            if username_req is None:
                user = User.objects.get(username=username, name_space=name_space)
            else:
                user = User.objects.get(username=username_req, name_space=name_space)
            # user = User.objects.get(username=user, name_space = name_space)
            collection = Collection.objects.get(collection_id=collection_id)
            documents = Document.objects.filter(collection_id=collection)
            documents = Document.objects.filter(collection_id=collection)

            user = User.objects.get(username=username, name_space=name_space)
            if Split.objects.filter(collection_id=collection, username=user, name_space=name_space).exists():
                documents = Split.objects.filter(collection_id=collection, username=user, name_space=name_space)
                documents = [d.document_id for d in documents]

            json_resp = {}
            dict_docs = []

            for document in documents:
                json_resp[document.document_id] = {}
                json_resp[document.document_id]['count'] = 0
                json_resp[document.document_id]['mentions'] = Annotate.objects.filter(document_id=document,
                                                                                      username=user,
                                                                                      name_space=name_space).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['concepts'] = Associate.objects.filter(document_id=document,
                                                                                       username=user,
                                                                                       name_space=name_space).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['labels'] = AnnotateLabel.objects.filter(document_id=document,
                                                                                         username=user,
                                                                                         name_space=name_space).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['assertions'] = CreateFact.objects.filter(document_id=document,
                                                                                          username=user,
                                                                                          name_space=name_space).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['relationships'] = Link.objects.filter(
                    subject_document_id=document.document_id, username=user, name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipPredConcept.objects.filter(
                    subject_document_id=document.document_id, username=user, name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipSubjConcept.objects.filter(
                    object_document_id=document.document_id, username=user, name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipObjConcept.objects.filter(
                    subject_document_id=document.document_id, username=user, name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipPredMention.objects.filter(document_id=document,
                                                                                        username=user,
                                                                                        name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipSubjMention.objects.filter(document_id=document,
                                                                                        username=user,
                                                                                        name_space=name_space).exclude(
                    username=user_iaa).count() + RelationshipObjMention.objects.filter(document_id=document,
                                                                                       username=user,
                                                                                       name_space=name_space).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['mentions']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['concepts']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['relationships']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['assertions']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['labels']
                dict_docs.append([document.document_id, json_resp[document.document_id]['count']])
            # prima vedo quello con più annotazioni.
            json_to_ret = {}
            json_to_ret['mentions'] = []
            json_to_ret['concepts'] = []
            json_to_ret['relationships'] = []
            json_to_ret['assertions'] = []
            json_to_ret['documents'] = []
            json_to_ret['labels'] = []
            dict_docs = sorted(dict_docs, key=lambda x: x[1], reverse=True)
            for k in dict_docs:
                json_to_ret['documents'].append(k[0])
                json_to_ret['mentions'].append(json_resp[k[0]]['mentions'])
                json_to_ret['concepts'].append(json_resp[k[0]]['concepts'])
                json_to_ret['labels'].append(json_resp[k[0]]['labels'])
                json_to_ret['assertions'].append(json_resp[k[0]]['assertions'])
                json_to_ret['relationships'].append(json_resp[k[0]]['relationships'])

            return JsonResponse(json_to_ret)

        elif type == 'annotation_per_document_global' and collection_id is not None:
            st = time.time()
            user = request.session['username']
            name_space = request.session['name_space']
            name_space = NameSpace.objects.get(name_space=name_space)
            user = User.objects.get(username=user, name_space=name_space)
            collection = Collection.objects.get(collection_id=collection_id)
            documents = Document.objects.filter(collection_id=collection)
            documents = Document.objects.filter(collection_id=collection)

            user = User.objects.get(username=username, name_space=name_space)
            if Split.objects.filter(collection_id=collection, username=user, name_space=name_space).exists():
                documents = Split.objects.filter(collection_id=collection, username=user, name_space=name_space)
                documents = [d.document_id for d in documents]

            json_resp = {}
            dict_docs = []

            for document in documents:
                json_resp[document.document_id] = {}
                json_resp[document.document_id]['count'] = 0
                json_resp[document.document_id]['mentions'] = Annotate.objects.filter(document_id=document).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['concepts'] = Associate.objects.filter(document_id=document).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['labels'] = AnnotateLabel.objects.filter(document_id=document).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['assertions'] = CreateFact.objects.filter(document_id=document).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['relationships'] = Link.objects.filter(
                    subject_document_id=document.document_id).exclude(
                    username=user_iaa).count() + RelationshipPredConcept.objects.filter(
                    subject_document_id=document.document_id).exclude(
                    username=user_iaa).count() + RelationshipSubjConcept.objects.filter(
                    object_document_id=document.document_id).exclude(
                    username=user_iaa).count() + RelationshipObjConcept.objects.filter(
                    subject_document_id=document.document_id).exclude(
                    username=user_iaa).count() + RelationshipPredMention.objects.filter(document_id=document).exclude(
                    username=user_iaa).count() + RelationshipSubjMention.objects.filter(document_id=document).exclude(
                    username=user_iaa).count() + RelationshipObjMention.objects.filter(document_id=document).exclude(
                    username=user_iaa).count()
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['mentions']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['concepts']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['relationships']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['assertions']
                json_resp[document.document_id]['count'] += json_resp[document.document_id]['labels']
                dict_docs.append([document.document_id, json_resp[document.document_id]['count']])
            # prima vedo quello con più annotazioni.
            json_to_ret = {}

            json_to_ret['iaa'] = {}
            json_to_ret['mentions'] = []
            json_to_ret['concepts'] = []
            json_to_ret['relationships'] = []
            json_to_ret['assertions'] = []
            json_to_ret['documents'] = []
            json_to_ret['labels'] = []
            json_to_ret['iaa']['mentions'] = []
            json_to_ret['iaa']['concepts'] = []
            json_to_ret['iaa']['relationships'] = []
            json_to_ret['iaa']['assertions'] = []
            json_to_ret['iaa']['documents'] = []
            json_to_ret['iaa']['labels'] = []

            dict_docs = sorted(dict_docs, key=lambda x: x[1], reverse=True)
            for k in dict_docs:
                # print(k[0])
                json_to_ret['documents'].append(k[0])
                json_to_ret['mentions'].append(json_resp[k[0]]['mentions'])
                json_to_ret['concepts'].append(json_resp[k[0]]['concepts'])
                json_to_ret['labels'].append(json_resp[k[0]]['labels'])
                json_to_ret['assertions'].append(json_resp[k[0]]['assertions'])
                json_to_ret['relationships'].append(json_resp[k[0]]['relationships'])
                doc = Document.objects.filter(document_id=k[0])
                mention_agreement = global_mentions_agreement(collection.collection_id, doc)
                concepts_agreement = global_concepts_agreement(collection.collection_id, doc)
                rels_agreement = global_relationships_agreement(collection.collection_id, doc)
                ass_agreement = global_createfact_agreement(collection.collection_id, doc)
                labels_agreement = global_labels_agreement(collection.collection_id, doc)
                json_to_ret['iaa']['mentions'] = round(mention_agreement, 3) if mention_agreement != '' else ''
                json_to_ret['iaa']['concepts'] = round(concepts_agreement, 3) if concepts_agreement != '' else ''
                json_to_ret['iaa']['labels'] = round(labels_agreement, 3) if labels_agreement != '' else ''
                json_to_ret['iaa']['assertions'] = round(ass_agreement, 3) if ass_agreement != '' else ''
                json_to_ret['iaa']['relationships'] = round(rels_agreement, 3) if rels_agreement != '' else ''
            end = time.time()
            print(end - st)
            return JsonResponse(json_to_ret)


def annotate(request, type=None):
    username = request.session['username']
    if type is not None:
        name_space = NameSpace.objects.get(name_space=request.session['name_space'])
        user = User.objects.filter(username=request.session['username'], name_space=name_space)
        request.session['collection'] = type
        collection = Collection.objects.get(collection_id=type)
        documents = Document.objects.filter(collection_id=collection)
        gts = GroundTruthLogFile.objects.filter(document_id__in=documents, username=user).order_by('-insertion_time')
        if gts.exists():
            last_doc = gts.first().document_id
            request.session['document'] = last_doc.document_id
        else:
            request.session['document'] = documents.first().document_id

        if (not username):
            return redirect('doctron_app:login')

        baseurl = get_baseurl()
        if (username and baseurl != ''):
            profile = request.session.get('profile', False)

            context = {'username': username, 'profile': profile, 'baseurl': baseurl}
            return render(request, 'doctron_app/index.html', context)
        else:
            return redirect('doctron_app:login')

def update_last_doc(request):
    username = request.session.get('username', False)
    name_space = request.session.get('name_space', False)
    collection = request.session.get('collection', False)
    last_doc = json.loads(request.body).get('document',None)
    with transaction.atomic():
        if last_doc and username and name_space and collection:
            collection = Collection.objects.get(collection_id=collection)
            username = User.objects.get(username=username, name_space=name_space)
            document = Document.objects.get(collection_id=collection, document_id=last_doc)
            sc = ShareCollection.objects.get(collection_id=collection,username=username,name_space=username.name_space)

            return HttpResponse(status = 200)
    return HttpResponse(status = 500)



def collections(request, type=None):
    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    name_space = request.session.get('name_space', False)

    if (not username or not name_space):
        return redirect('doctron_app:login')

    name_space = NameSpace.objects.get(name_space=request.session['name_space'])

    baseurl = get_baseurl()
    if (username and baseurl != ''):
        context = {'username': username, 'profile': profile, 'baseurl': baseurl}

    if request.method == 'GET':
        user = User.objects.get(username=request.session['username'], name_space=name_space)
        collections = ShareCollection.objects.filter(username=user)

        if type is None:

            return render(request, 'doctron_app/index.html', context)
            # else:
            #     return redirect('doctron_app:login')
        elif type == 'name':
            collection = Collection.objects.get(collection_id=request.GET.get('collection', None))
            json_resp = {'name': collection.name}
            return JsonResponse(json_resp)
        elif type == 'modality':
            modality = 0
            collection = None
            if request.GET.get('collection', None) is not None:
                collection = Collection.objects.get(collection_id=request.GET.get('collection', None))
            elif request.session.get('collection', None) is not None:
                collection = Collection.objects.get(collection_id=request.session.get('collection', None))
            collection_type = "Textual"
            topic_type = "Textual"
            if collection:
                if collection.modality == 'Competitive':
                    modality = 1
                if collection.modality == 'Collaborative restricted':
                    modality = 2
                collection_type = collection.type
                topic_type = collection.topic_type
            print(modality, collection.collection_id)

            json_resp = {'modality': modality,"collection_type":collection_type,'topic_type':topic_type}

            return JsonResponse(json_resp)
        elif Collection.objects.filter(collection_id=type).exists() or type == 'list':
            collection_param = type
            name_space = NameSpace.objects.get(name_space=request.session['name_space'])

            annotation_type = request.GET.get('annotation_type', request.session['annotation_type'])
            request.session['annotation_type'] = annotation_type
            if annotation_type is not None:
                annotation_type = AnnotationType.objects.get(name=annotation_type)
                collections = Collection.objects.filter(annotation_type=annotation_type)

            user = User.objects.get(username=request.session['username'], name_space=name_space)
            collections = ShareCollection.objects.filter(username=user,collection_id__in=collections)
            json_collections = {}
            json_collections['collections'] = []
            for c in collections:
                cid = c.collection_id_id
                json_boj = {}
                json_boj['status'] = c.status

                c = Collection.objects.get(collection_id=cid)
                batches = Document.objects.filter(collection_id=c).values('batch').annotate(
                    total=Count('batch')).order_by('total')

                json_boj['batch'] = []
                for b in batches:
                    j_b = {}
                    batch = 'batch ' + str(b['batch'])
                    j_b[batch] = b['total']
                    json_boj['batch'].append(j_b)

                json_boj['name'] = c.name
                json_boj['id'] = cid
                #json_boj['task'] = CollectionHasTask.objects.filter(collection_id=c).first().task_id.name
                #types = CollectionHasTask.objects.filter(collection_id=c)
                creator = ShareCollection.objects.filter(collection_id = c, creator = True)
                json_boj['creator'] = creator.first().username_id
                json_boj['name_space'] = creator.first().username.name_space_id
                #types = [c.annotation_type.name for c in types]
                json_boj['annotation_type'] = c.annotation_type.name
                json_boj['collection_type'] = c.type
                json_boj['description'] = c.description
                json_boj['members'] = []
                time = str(c.insertion_time)
                before_p = time.split('+')
                first_split = before_p[0].split('.')[0]
                time = first_split + '+' + before_p[1]
                json_boj['insertion_time'] = time
                json_boj['date'] = time.split(' ')[0]
                json_boj['labels'] = []
                json_boj['documents_count'] = (Document.objects.filter(collection_id=cid).count())
                docs = Document.objects.filter(collection_id=cid)
                json_boj['annotations_count'] = (GroundTruthLogFile.objects.filter(document_id__in=docs).count())
                document_distinct_annotated = GroundTruthLogFile.objects.filter(document_id__in=docs).distinct('document_id').count()
                json_boj['annotated_documents'] = document_distinct_annotated
                json_boj['perc_annotations_all'] = float(
                    round((document_distinct_annotated / json_boj['documents_count']) * 100, 2))
                json_boj['user_annotations_count'] = (
                    GroundTruthLogFile.objects.filter(username=user, name_space=name_space,
                                                      document_id__in=docs).count())
                json_boj['perc_annotations_user'] = float(
                    round((json_boj['user_annotations_count'] / json_boj['documents_count']) * 100, 2))

                shared_with = ShareCollection.objects.filter(collection_id=c.collection_id)
                for el in shared_with:
                    us = User.objects.get(name_space=request.session['name_space'], username=el.username_id)
                    # if us.username != c.username:
                    json_boj['members'].append({'username': us.username, 'profile': us.profile,'reviewer':el.reviewer,'admin':el.admin, 'status': el.status})

                # controllo se sono tutti gli utenti appartengono a un profile esatto
                profiles = User.objects.all().values('profile')
                profiles = [p['profile'] for p in profiles]
                for p in profiles:
                    users = User.objects.filter(profile=p)
                    new_json_members = [j for j in json_boj['members'] if j['profile'] == p]

                    if len(users) == len(new_json_members):
                        json_boj['members'] = [j for j in json_boj['members'] if j['profile'] != p]
                        # json_boj['members'].append({'username': 'All' + p, 'profile': p})

                has_label = CollectionHasLabel.objects.filter(collection_id=c.collection_id)
                for el in has_label:
                    # label = Label.objects.get(name=el.name_id)
                    json_boj['labels'].append(el.label_id)
                json_boj['labels'] = list(set(json_boj['labels']))
                json_collections['collections'].append(json_boj)

                if collection_param is not None and collection_param == cid:  # in this case it was reqeusted a specific collection
                    # context = {'username': username, 'profile': profile}
                    return render(request, 'doctron_app/index.html', context)
                    # return redirect('doctron_app:documents')
            # return JsonResponse(json_boj)
            if type == 'list':
                json_collections['collections'] = sorted(json_collections['collections'],
                                                         key=lambda x: x['insertion_time'], reverse=True)
                return JsonResponse(json_collections)



        elif type == 'concepts':
            collection = request.session.get('collection', None)
            if collection is None:
                if len(collections) > 0:
                    collection = Collection.objects.get(collection_id=collections.first().collection_id)
                else:
                    return JsonResponse([], safe=False)
            else:
                collection = Collection.objects.get(collection_id=collection)

            concepts = create_concepts_list(collection=collection.collection_id)
            # print(concepts)
            return JsonResponse(concepts, safe=False)


        elif type == 'areas':
            collection = request.session.get('collection', None)
            if collection is not None:
                collection = Collection.objects.get(collection_id=collection)
                tuples = AddConcept.objects.filter(collection_id=collection).values('name').distinct()
                areas = [concept['name'] for concept in tuples]
                json_dict = {}
                json_dict['areas'] = areas
                return JsonResponse(json_dict)

        elif type == 'documents':
            collection = request.GET.get('collection', None)
            if collection is None and request.session.get('collection', None) is None:
                if len(collections) > 0:
                    collection = Collection.objects.get(collection_id=collections.first().collection_id)
                else:
                    return JsonResponse([], safe=False)
            elif collection is None and request.session.get('collection', None) is not None:
                collection = request.session.get('collection', None)
            collection = Collection.objects.get(collection_id = collection)
            name_space = NameSpace.objects.get(name_space=request.session['name_space'])
            user = User.objects.get(username=request.session['username'], name_space=name_space)
            docs = Document.objects.filter(collection_id=collection)
            if Split.objects.filter(collection_id=collection, username=user).exists():
                docs = Split.objects.filter(collection_id=collection, username=user)
                docs = [d.document_id for d in docs]
            gts = GroundTruthLogFile.objects.filter(document_id__in=docs, username=user,
                                                       name_space=name_space).order_by("-insertion_time")
            annotated_docs = [x.document_id for x in gts]
            annotated_docs_id = [x.document_id for x in annotated_docs]
            not_annotated_docs = [x for x in docs if x.document_id not in annotated_docs_id]
            docs_list = []
            seen_ids = []
            for document in annotated_docs:
                if document.document_id not in seen_ids:
                    seen_ids.append(document.document_id)
                    json_doc = {'id': document.document_content['doc_id'],'hashed_id':document.document_id, 'annotated': True,'batch':document.batch}


                    docs_list.append(json_doc)


            for document in not_annotated_docs:
                json_doc = {'id': document.document_content['doc_id'],'hashed_id':document.document_id, 'annotated': False,'batch':document.batch}

                docs_list.append(json_doc)




            docs_list = sorted(docs_list, key=lambda x: x['id'])
            return JsonResponse(docs_list, safe=False)

        elif type == 'labels':

            json_obj = {}
            json_obj['labels'] = []
            if request.GET.get('collection',None) is not None:
                collection = request.GET.get('collection',None)
            else:
                collection = request.session.get('collection', None)
            collection = Collection.objects.get(collection_id=collection)
            labels = CollectionHasLabel.objects.filter(collection_id=collection,labels_annotation=True)
            values = [l.values for l in labels]
            details = [l.details for l in labels]
            values = [
    [int(val.lower) if val.lower is not None else None,
    int(val.upper) if val.upper is not None else None] for val in values]
            labels_details = [l.label.name for l in labels]
            json_obj['labels'] = labels_details
            json_obj['values'] = values
            json_obj['details'] = details
            labels = CollectionHasLabel.objects.filter(collection_id=collection, passage_annotation=True)
            values = [l.values for l in labels]
            details = [l.details for l in labels]
            values = [
                [int(val.lower) if val.lower is not None else None,
                 int(val.upper) if val.upper is not None else None] for val in values]
            labels_details = [l.label.name for l in labels]
            json_obj['labels_passage'] = labels_details
            json_obj['values_passage'] = values
            json_obj['details_passage'] = details

            return JsonResponse(json_obj)

        elif type == 'users':
            collection = request.GET.get('collection', None)
            json_boj = {}
            json_boj['members'] = []
            if collection:
                collection = Collection.objects.get(collection_id=collection)
                shared = ShareCollection.objects.filter(collection_id=collection)
                for us in shared:
                    # print(us.username_id)
                    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                    us1 = User.objects.get(name_space=name_space, username=us.username_id)
                    # if us1.username != request.session['username']:
                    json_boj['members'].append({'username': us1.username,'reviewer':us.reviewer,'admin':us.admin, 'profile': us1.profile, 'status': us.status})

            # controllo se sono tutti gli utenti appartengono a un profile esatto
            return JsonResponse(json_boj)


    elif request.method == 'POST':
        if type == 'add_member':
            try:
                with transaction.atomic():
                    json_resp = {'msg': 'ok'}
                    # name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                    request_body_json = json.loads(request.body)
                    members = request_body_json['members']

                    collection = request_body_json['collection']
                    collection = Collection.objects.get(collection_id=collection)
                    # members = list(set(members))
                    members = members.replace('\\n', '\n').split('\n')
                    members = [m.strip() for m in members if m != '']
                    for member in members:
                        # if member not in ['All Professor','All Student','All Tech','All Beginner','All Expert','All Admin']:
                        name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                        users = User.objects.filter(username=member, name_space=name_space)
                        for user in users:
                            if not ShareCollection.objects.filter(collection_id=collection, username=user,
                                                                  name_space=user.name_space).exists():
                                ShareCollection.objects.create(collection_id=collection, username=user,
                                                               name_space=user.name_space, status='invited')
            except Exception as e:
                print(e)
                json_resp = {'error': e}
            finally:
                return JsonResponse(json_resp)
        elif type == 'add_labels':
            try:
                with transaction.atomic():
                    json_resp = {'msg': 'ok'}

                    request_body_json = json.loads(request.body)
                    label = request_body_json['label']
                    min_l = request_body_json['min']
                    max_l = request_body_json['max']
                    label = label.replace('\\n', '\n').strip()


                    collection = request_body_json['collection']
                    collection = Collection.objects.get(collection_id=collection)

                    if not Label.objects.filter(name=label).exists():
                        label_to_add = Label.objects.create(name=label)
                    else:
                        label_to_add = Label.objects.get(name=label)
                    if not CollectionHasLabel.objects.filter(collection_id=collection, label=label_to_add).exists():
                        if request.session['annotation_type'] == 'Graded labeling':
                            CollectionHasLabel.objects.create(collection_id=collection, label=label_to_add,labels_annotation=True,passage_annotation=False, values=str(NumericRange(int(min_l), int(max_l), bounds='[]')))
                        elif request.session['annotation_type'] == 'Passages annotation':
                            CollectionHasLabel.objects.create(collection_id=collection, label=label_to_add,labels_annotation=False,passage_annotation=True, values=str(NumericRange(int(min_l), int(max_l), bounds='[]')))


            except Exception as e:
                print(e)
                json_resp = {'error': e}
            finally:
                json_obj = {}
                json_obj['labels'] = []
                collection = request.session.get('collection', None)
                collection = Collection.objects.get(collection_id=collection)
                labels = CollectionHasLabel.objects.filter(collection_id=collection, labels_annotation=True)
                values = [l.values for l in labels]
                details = [l.details for l in labels]
                values = [
                    [int(val.lower) if val.lower is not None else None,
                     int(val.upper) if val.upper is not None else None] for val in values]
                labels_details = [l.label.name for l in labels]
                json_obj['labels'] = labels_details
                json_obj['values'] = values
                json_obj['details'] = details
                labels = CollectionHasLabel.objects.filter(collection_id=collection, passage_annotation=True)
                values = [l.values for l in labels]
                details = [l.details for l in labels]
                values = [
                    [int(val.lower) if val.lower is not None else None,
                     int(val.upper) if val.upper is not None else None] for val in values]
                labels_details = [l.label.name for l in labels]
                json_obj['labels_passage'] = labels_details
                json_obj['values_passage'] = values
                json_obj['details_passage'] = details
                return JsonResponse(json_obj)


        elif type == 'add_tags':
            try:
                with transaction.atomic():
                    json_resp = {'msg': 'ok'}

                    request_body_json = json.loads(request.body)
                    tags = []
                    if request_body_json['tags']:
                        print('adding tags')
                        tags = request_body_json['tags'].replace('\\n', '\n').split('\n')
                        tags = [l.strip() for l in tags if l != '']

                    collection = request_body_json['collection']
                    collection = Collection.objects.get(collection_id=collection)
                    for tag in tags:
                        if len(tag) > 0:
                            if not Tag.objects.filter(name=tag).exists():
                                tag_to_add = Tag.objects.create(name=tag)
                            else:
                                tag_to_add = Tag.objects.get(name=tag)
                            if not CollectionHasTag.objects.filter(collection_id=collection, name=tag_to_add).exists():
                                CollectionHasTag.objects.create(collection_id=collection, name=tag_to_add)
                    areas = get_areas_collection(collection.collection_id)
                    tags = get_tags_collection(collection.collection_id)
                    options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags)) if
                               k not in list(set(areas + tags))}
                    collection.options = options
                    collection.save()

            except Exception as e:
                print(e)
                json_resp = {'error': e}
            finally:
                return JsonResponse(json_resp)
        elif type == 'modality':
            try:
                request_body_json = json.loads(request.body)
                modality = request_body_json['modality']
                print(modality)
                collection = request_body_json['collection']
                collection = Collection.objects.get(collection_id=collection)
                collection.modality = modality
                collection.save()
                return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=500)
        elif type == 'add_type':
            try:
                # request_body_json = json.loads(request.body)
                # annotations = request_body_json['type']
                # collection = request_body_json['collection_id']
                # collection = Collection.objects.get(collection_id=collection)
                # annotations_types = CollectionHasTask.objects.filter(collection_id=collection)
                # task = annotations_types.first().task_id
                # types = [a.annotation_type.name for a in annotations_types]
                # if annotations not in types:
                #     t = AnnotationType.objects.get(name=annotations)
                #     CollectionHasTask.objects.create(collection_id=collection,task_id=task,annotation_type=t)

                return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=500)
        else:
            try:
                with transaction.atomic():
                    msg = new_collection(request)
                    #msg = add_collection.delay(request)
                    return JsonResponse({'status': msg})

            except Exception as e:
                print(e)
                json_resp = {'error': 'an error occurred'}

            else:
                json_resp = {'message': 'ok'}
            finally:
                json_resp = {'message': 'ok'}
                print(json_resp)
                return JsonResponse(json_resp)

    elif request.method == 'DELETE' and type == None:
        request_body_json = json.loads(request.body)
        try:

            with transaction.atomic():
                lista = []
                json_resp = {'msg': 'ok'}
                collection = request_body_json['collection']
                documents = Document.objects.filter(collection_id=collection)
                Annotate.objects.filter(document_id__in=documents).delete()
                Associate.objects.filter(document_id__in=documents).delete()
                AssociateTag.objects.filter(document_id__in=documents).delete()
                AnnotateLabel.objects.filter(document_id__in=documents).delete()
                CreateFact.objects.filter(document_id__in=documents).delete()
                AnnotatePassage.objects.filter(document_id__in=documents).delete()

                RelationshipObjMention.objects.filter(document_id__in=documents).delete()
                RelationshipPredMention.objects.filter(document_id__in=documents).delete()
                RelationshipSubjMention.objects.filter(document_id__in=documents).delete()

                documents_ids_list = [x.document_id for x in documents]
                RelationshipObjConcept.objects.filter(predicate_document_id__in=documents_ids_list).delete()
                RelationshipPredConcept.objects.filter(object_document_id__in=documents_ids_list).delete()
                RelationshipSubjConcept.objects.filter(object_document_id__in=documents_ids_list).delete()
                Link.objects.filter(predicate_document_id__in=documents_ids_list).delete()
                AnnotateObject.objects.filter(document_id__in=documents).delete()

                ShareCollection.objects.filter(collection_id=collection).delete()
                GroundTruthLogFile.objects.filter(document_id__in=documents).delete()
                Mention.objects.filter(document_id__in=documents).delete()
                DocumentObject.objects.filter(document_id__in=documents).delete()

                CollectionHasLabel.objects.filter(collection_id=collection).delete()
                AddConcept.objects.filter(collection_id=collection).delete()
                SessionDoc.objects.filter(collection_id=collection).delete()
                Document.objects.filter(collection_id=collection).delete()
                Topic.objects.filter(collection_id=collection).delete()
                Collection.objects.filter(collection_id=collection).delete()
                request.session['collection'] = None


        except Exception as e:
            json_resp = {'error': 'an error occurred'}
            return JsonResponse(json_resp)
        else:
            return JsonResponse(json_resp)

    elif request.method == 'DELETE' and type == 'delete_member':
        request_body_json = json.loads(request.body)
        try:
            with transaction.atomic():
                json_resp = {'msg': 'ok'}
                members = []
                member = request_body_json['member']
                collection = request_body_json['collection']
                members.append(member)
                # delete the annotation of that member for that collection first
                for member in members:
                    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                    users = User.objects.filter(username=member, name_space=name_space)

                    collection = Collection.objects.get(collection_id=collection)
                    for user in users:
                        documents = Document.objects.filter(collection_id=collection)
                        Annotate.objects.filter(document_id__in=documents, username=user,
                                                name_space=name_space).delete()
                        Associate.objects.filter(document_id__in=documents, username=user,
                                                 name_space=name_space).delete()
                        AssociateTag.objects.filter(document_id__in=documents, username=user,
                                                 name_space=name_space).delete()
                        AnnotateLabel.objects.filter(document_id__in=documents, username=user,
                                                     name_space=name_space).delete()
                        CreateFact.objects.filter(document_id__in=documents, username=user,
                                                  name_space=name_space).delete()

                        RelationshipObjMention.objects.filter(document_id__in=documents, username=user,
                                                              name_space=name_space).delete()
                        RelationshipPredMention.objects.filter(document_id__in=documents, username=user,
                                                               name_space=name_space).delete()
                        RelationshipSubjMention.objects.filter(document_id__in=documents, username=user,
                                                               name_space=name_space).delete()

                        documents_ids_list = [x.document_id for x in documents]
                        RelationshipObjConcept.objects.filter(predicate_document_id__in=documents_ids_list,
                                                              username=user, name_space=name_space).delete()
                        RelationshipPredConcept.objects.filter(object_document_id__in=documents_ids_list, username=user,
                                                               name_space=name_space).delete()
                        RelationshipSubjConcept.objects.filter(object_document_id__in=documents_ids_list, username=user,
                                                               name_space=name_space).delete()
                        Link.objects.filter(predicate_document_id__in=documents_ids_list, username=user,
                                            name_space=name_space).delete()

                        ShareCollection.objects.filter(collection_id=collection, username=user,
                                                       name_space=name_space).delete()
                        GroundTruthLogFile.objects.filter(document_id__in=documents, username=user,
                                                          name_space=name_space).delete()
                    # restore session
                    if GroundTruthLogFile.objects.filter(username__in=users).exists():
                        gts = GroundTruthLogFile.objects.filter(username__in=users).order_by('-insertion_time')
                        last_gt = gts.first()
                        name_space = last_gt.name_space
                        # collection = last_gt.collection_id
                        document = last_gt.document_id
                        request.session['language'] = document.language
                        request.session['name_space'] = name_space.name_space
                        request.session['collection'] = document.collection_id_id
                        request.session['document'] = document.document_id
                        request.session['batch'] = document.batch
                        request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                            request.session['document'], request.session['language'])

                    # se non ho ultima annotazione ma ho collezioni, allora setto la collezione all'ultima aggiunta e al primo doc della prima batch
                    elif ShareCollection.objects.filter(username=users.first()).exclude(
                            status='invited').exists():  # non importa il name space in questo caso
                        collections = ShareCollection.objects.filter(username=users.first()).values(
                            'collection_id').distinct()
                        collections_ids = [c['collection_id'] for c in collections]
                        collection = Collection.objects.filter(collection_id__in=collections_ids).order_by(
                            '-insertion_time').first()
                        request.session['collection'] = collection.collection_id
                        document = Document.objects.filter(collection_id=collection).order_by('insertion_time').first()
                        request.session['document'] = document.document_id
                        request.session['language'] = document.language
                        request.session['name_space'] = 'Human'
                        request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                            request.session['document'],
                            request.session['language'])
                    else:
                        request.session['collection'] = None
                        request.session['document'] = None
                        request.session['language'] = None
                        request.session['name_space'] = 'Human'
                        request.session['fields'] = []
                        request.session['fields_to_ann'] = []
                    # Collection.objects.filter(collection_id=collection).delete()
        except Exception as e:
            print(e)
            json_resp = {'error': e}
            return JsonResponse(json_resp)
        else:
            return JsonResponse(json_resp)


def uploadFile(request):
    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def configure(request):
    """Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


from django.urls import reverse


def password_reset(request, token=None):
    if request.method == 'GET':
        if token is None:
            context = {'email': None, 'user_type': None, 'username': None}
            return render(request, 'doctron_app/index.html', context)
        else:
            try:
                user = User.objects.get(psw_token=token)
                if user.username:
                    email = user.username
                    current_time = timezone_1.now()

                    if user.psw_token == token and current_time < user.psw_expired_time:
                        context = {'email': email, 'errorMessage': ''}
                    else:
                        context = {'email': email, 'errorMessage': 'The link is expired'}
                    return render(request, 'doctron_app/index.html', context)
            except Exception as e:
                print(e)
                return redirect('crane_app:login')

    if request.method == 'POST':
        email = request.POST.get('email', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        password_check = request.POST.get('password_check', None)

        if email is not None and password is None and password_check is None:
            try:
                if not User.objects.filter(email=email).exists():
                    return HTTPResponse(status=404)
                token = secrets.token_urlsafe(32)
                user = User.objects.filter(email=email).first()
                user.psw_token = token
                current_time = timezone_1.now()

                user.psw_expired_time = current_time + timedelta(minutes=60)
                user.save()
                # print(student.psw_expired_time)
                # print(current_time)
                reset_url = reverse('doctron_app:password_reset')  # Replace with your password reset URL name
                reset_link = request.build_absolute_uri(reset_url) + f'/{token}'
                subject = '[Metatron] Password Reset'
                message = f'Dear {user.username},\nPlease, click on the following link to reset your password: {reset_link}\n\nThe link will expire in 60 minutes.\nIf you have not requested to reset your password, please inform us at: ornella.irrera@unipd.it.\nBest regards,\nThe Metatron Team'
                print(message)
                send_email(email, subject, message)

                return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=500)
        elif password is not None and password_check is not None and token is not None:
            try:
                student = User.objects.filter(psw_token=token).first()

                if password == password_check and validate_password(password) and validate_password(password_check):
                    password_enc = hashlib.md5(password.encode()).hexdigest()
                    student.password = password_enc
                    student.save()
                    return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=500)


    else:
        return redirect('doctron_app:login')


def signup(request):
    """Configuration page for app """

    # username = request.session.get('username', False)
    # profile = request.session.get('profile', False)
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open((os.path.join(workpath, '../url.txt')), 'r', encoding='utf-8') as f:
        baseurl = f.read()
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
    # if (username and baseurl != ''):
    #     context = {'username': username, 'profile': profile, 'baseurl': baseurl}
    #
    #
    # else:
    context = {'baseurl': baseurl}
    # return render(request, 'doctron_app/index.html', context)
    return render(request, 'doctron_app/index.html', context)
    # return render(request, 'doctron_app/index.html')


# def register(request):
#
#     """This view handles the registration of new users: username, password and profile are inserted in the database"""
#
#     if request.method == 'POST':
#         username = request.POST.get('username',None)
#         password1 = request.POST.get('password',None)
#
#         profile = request.POST.get('profile',None)
#         orcid = request.POST.get('orcid',None)
#         email = request.POST.get('email',None)
#         ncbikey = request.POST.get('ncbikey',None)
#         # mode1 = request.POST.get('mode',None)
#         # mode = NameSpace.objects.get(ns_id=mode1)
#
#         try:
#             with transaction.atomic():
#
#                 password = hashlib.md5(password1.encode()).hexdigest()
#                 ns_robot = NameSpace.objects.get(name_space = 'Robot')
#                 ns_human = NameSpace.objects.get(name_space = 'Human')
#                 if User.objects.filter(username = username).exists() or username == 'global':
#                     return JsonResponse({'message': 'The username you chose already exists'})
#
#                 # User.objects.create(username = username,profile=profile,password = password,name_space=ns_robot,orcid=orcid,ncbikey=ncbikey)
#                 User.objects.create(username = username,profile=profile,password = password,name_space=ns_human,orcid=orcid,ncbi_key=ncbikey)
#
#                 if not User.objects.filter(name_space=ns_human,username='IAA-Inter Annotator Agreement').exists():
#                     User.objects.create(username='IAA-Inter Annotator Agreement', profile='Tech', password=hashlib.md5("iaa".encode()).hexdigest(), name_space=ns_human,
#                                         orcid=None, ncbi_key=None)
#                     # User.objects.create(username='IAA-Inter Annotator Agreement', profile='Tech', password=hashlib.md5("iaa".encode()).hexdigest(), name_space=ns_robot,
#                     #                     orcid=None, ncbikey=None)
#
#         except (Exception) as error:
#             print(error)
#             # context = {: "Something went wrong, probably you did not set any profile"}
#             return JsonResponse({'error': 'This username already exists'},status = 500)
#         else:
#             request.session['username'] = username
#             request.session['name_space'] = 'Human'
#             request.session['profile'] = profile
#             return JsonResponse({'response': 'ok'},status = 200)
#
#     return render(request, 'doctron_app/login.html')


def team_members_stats(request):
    """Team members' stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def updateConfiguration(request):
    """Update Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def loginPage(request, orcid_error=False):
    """Update Configuration page for app """

    # username = request.session.get('username', False)
    # profile = request.session.get('profile', False)
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open((os.path.join(workpath, '../url.txt')), 'r', encoding='utf-8') as f:
        baseurl = f.read()
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'

    if orcid_error:
        context = {'baseurl': baseurl, 'orcid_error': 'user not found'}
    else:
        context = {'baseurl': baseurl}
    # return render(request, 'doctron_app/index.html', context)
    return render(request, 'doctron_app/index.html', context)


def infoAboutConfiguration(request):
    """Information about Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def tutorial(request):
    """Tutorial page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


def my_stats(request):
    """User's reports stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')

    
def dashboard(request, subpath=None):
    """Serve React frontend for all `/dashboard/*` routes."""
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)

    if username:
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login') 


def documents(request):
    """Reports' stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'doctron_app/index.html', context)
    else:
        return redirect('doctron_app:login')


# def set_fields_params(request):
#     body_json = json.loads(request.body)
#     fields = body_json['fields']
#     request.session['fields'] = list(set(request.session['fields'] + fields))
#     return JsonResponse({'msg':'ok'})

def get_session_params(request):

    """This view returns the current session parameters """

    json_resp = {}
    # questo lo devo fare perché mi uccide la sessione l'autenticazione con oauth
    orcid = request.GET.get('orcid', '')

    if orcid != '':
        mode1 = 'Human'
        user = User.objects.filter(orcid=orcid)

        if user.exists():
            request.session['username'] = user.first().username
            request.session['profile'] = user.first().profile

            if user.first().ncbi_key is not None:
                os.environ['NCBI_API_KEY'] = user.first().ncbi_key
            # prima recupero la sessione dall'ultima annotazione
            user = user.first()
            if SessionDoc.objects.filter(username=user).exists():
                sessions = SessionDoc.objects.filter(username=user).order_by('-last_view')
                session = sessions.first()
                document = session.document_id
                role = session.role
                request.session['language'] = document.language
                request.session['name_space'] = user.name_space_id
                request.session['collection'] = document.collection_id_id
                request.session['topic'] = session.topic_id_id
                request.session['topic_type'] = session.topic_id.type
                #task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
                #task = task.task_id.name
                #request.session['task'] = task
                #types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                #types = [c.annotation_type.name for c in types]
                request.session['annotation_type'] = document.collection_id.annotation_type.name
                request.session['document'] = document.document_id
                request.session['batch'] = document.batch
                request.session['role'] = role
                request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                    request.session['document'], request.session['language'])


            elif GroundTruthLogFile.objects.filter(username=user).exists():
                gts = GroundTruthLogFile.objects.filter(username=user).order_by('-insertion_time')
                last_gt = gts.first()
                name_space = last_gt.name_space
                document = last_gt.document_id
                request.session['language'] = document.language
                request.session['name_space'] = name_space.name_space
                request.session['collection'] = document.collection_id_id
                request.session['topic'] = last_gt.topic_id_id
                request.session['topic_type'] = last_gt.topic_id.type

                # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
                # task = task.task_id.name
                # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                # types = [c.annotation_type.name for c in types]
                request.session['annotation_type'] = document.collection_id.annotation_type.name
                # request.session['task'] = task
                request.session['document'] = document.document_id
                request.session['batch'] = document.batch
                request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                    request.session['document'], request.session['language'])

            # se non ho ultima annotazione ma ho collezioni, allora setto la collezione all'ultima aggiunta e al primo doc della prima batch
            elif ShareCollection.objects.filter(username=user).exclude(
                    status='invited').exists():  # non importa il name space in questo caso
                collections = ShareCollection.objects.filter(username=user).exclude(status='invited').values(
                    'collection_id').distinct()
                collections_ids = [c['collection_id'] for c in collections]
                collection = Collection.objects.filter(collection_id__in=collections_ids).order_by(
                    '-insertion_time').first()
                # task = CollectionHasTask.objects.filter(collection_id=collection).first()
                # task = task.task_id.name
                # request.session['task'] = task
                request.session['topic'] = Topic.objects.filter(collection_id=collection).first().id

                # types = CollectionHasTask.objects.filter(collection_id=collection)
                # types = [c.annotation_type.name for c in types]
                request.session['types'] = collection.annotation_type.name
                request.session['collection'] = collection.collection_id
                documents = Document.objects.filter(collection_id=collection)
                if Split.objects.filter(username=user, collection_id=collection,
                                        document_id__in=documents).exists():
                    documents = Split.objects.filter(username=user, collection_id=collection,
                                                     document_id__in=documents)
                    documents = sorted([d.document_id_id for d in documents])
                else:
                    documents = sorted([d.document_id for d in documents])
                document = Document.objects.get(document_id=documents[0])

                request.session['document'] = document.document_id
                document = Document.objects.get(document_id = request.session['document'])
                request.session['language'] = document.language
                request.session['name_space'] = mode1
                request.session['role'] = request.session.get('role', "Annotator")
                request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                    request.session['document'],
                    request.session['language'])


            else:
                request.session['collection'] = None
                request.session['document'] = None
                request.session['topic'] = None
                request.session['language'] = None
                request.session['task'] = 'Default'
                request.session['name_space'] = 'Human'
                request.session['fields'] = []
                request.session['fields_to_ann'] = []

    username = request.session.get('username',None)
    annotation = request.session.get('name_space',None)

    if username is None or annotation is None:
        return redirect('doctron_app:login')


    name_space = NameSpace.objects.get(name_space = annotation)
    user = User.objects.get(username = username, name_space = name_space)

    collection = request.session.get('collection',None)
    topic = request.session.get('topic',None)
    annotation_type = request.session.get('annotation_type',"Graded labeling")
    document = request.session.get('document',None)
    language = request.session.get('language',None)
    fields_to_ann = request.session.get('fields_to_ann',[])
    fields = request.session.get('fields',[])
    json_resp['username'] = username
    json_resp['topic'] = topic
    json_resp['annotation_type'] = annotation_type


    json_resp['task'] = 'Default'
    json_resp['name_space'] = name_space.name_space
    if annotation is not None:
        if annotation == 'Human':
            json_resp['annotation'] = 'Manual'
        elif annotation == 'Robot':
            json_resp['annotation'] = 'Automatic'
    else:
        json_resp['annotation'] = 'Manual'

    if collection is not None:
        json_resp['collection'] = collection
        coll = Collection.objects.get(collection_id=collection)
        # task = CollectionHasTask.objects.filter(collection_id=coll).first()
        # task = task.task_id.name
        # request.session['task'] = task
        if document is not None:
            json_resp['document'] = document
            json_resp['language'] = language
            json_resp['role'] = "Annotator"
            if SessionDoc.objects.filter(username=user,document_id=Document.objects.get(document_id=document),collection_id=collection).exists():
                sessions = SessionDoc.objects.filter(username=user,document_id=Document.objects.get(document_id=document),collection_id=collection).order_by('-last_view')
                session = sessions.first()
                role = session.role
                request.session['role'] = json_resp['role'] = role
                request.session['topic'] = json_resp['topic'] = session.topic_id.topic_id

                # task = CollectionHasTask.objects.filter(collection_id=collection).first()
                # task = task.task_id.name
                # request.session['task'] = json_resp['task'] = task
                # types = CollectionHasTask.objects.filter(collection_id=collection)
                # types = [c.annotation_type.name for c in types]
                request.session['annotation_type'] = json_resp['annotation_type'] = coll.annotation_type.name
        else:
            collection = Collection.objects.get(collection_id = collection)
            # task = CollectionHasTask.objects.filter(collection_id=collection).first()
            # task = task.task_id.name
            # request.session['task'] = task
            request.session['topic'] = Topic.objects.filter(collection_id=collection).first().id
            docs_coll = Document.objects.filter(collection_id = collection)
            if SessionDoc.objects.filter(username=user,collection_id=collection).exists():
                sessions = SessionDoc.objects.filter(username=user,collection_id=collection).order_by('-last_view')
                session = sessions.first()
                document = session.document_id
                role = session.role
                request.session['topic'] = json_resp['topic'] = session.topic_id.topic_id
                request.session['language'] = json_resp['language'] = document.language
                request.session['name_space'] = json_resp['name_space'] = user.name_space_id
                request.session['collection'] = json_resp['collection'] = document.collection_id_id
                # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
                # task = task.task_id.name
                # request.session['task'] = json_resp['task'] = task
                # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                # types = [c.annotation_type.name for c in types]
                request.session['annotation_type'] = json_resp['annotation_type']= collection.annotation_type.name
                request.session['document'] = document.document_id
                request.session['batch'] = json_resp['batch'] =document.batch
                request.session['role'] =json_resp['role'] = role
                request.session['fields'] = json_resp['fields']= json_resp['fields_to_ann'] = request.session['fields_to_ann'] = get_fields_list(
                    request.session['document'], request.session['language'])


            elif GroundTruthLogFile.objects.filter(username=user,document_id__in=docs_coll).exists():
                gts = GroundTruthLogFile.objects.filter(username=user,document_id__in=docs_coll).order_by('-insertion_time')
                last_gt = gts.first()
                name_space = last_gt.name_space
                document = last_gt.document_id
                request.session['topic'] = json_resp['topic'] = last_gt.topic_id.topic_id

                request.session['language']  = json_resp['language'] = document.language
                request.session['name_space'] = json_resp['name_space'] =name_space.name_space
                request.session['collection'] = json_resp['collection'] = document.collection_id_id
                # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
                # task = task.task_id.name
                # request.session['task'] = json_resp['task'] = task
                # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
                # types = [c.annotation_type.name for c in types]
                request.session['annotation_type'] =json_resp['annotation_type'] = document.collection_id.annotation_type.name
                request.session['document'] = json_resp['document'] = document.document_id
                request.session['batch'] = json_resp['batch'] = document.batch
                request.session['fields'] = json_resp['fields'] = json_resp['fields_to_ann'] = request.session['fields_to_ann'] = get_fields_list(
                    request.session['document'], request.session['language'])

            elif Split.objects.filter(username=user, document_id__in=docs_coll).exists():

                docs = Split.objects.filter(collection_id=collection, username=user)
                docs = [d.document_id_id for d in docs]

                request.session['document'] = docs[0]
            else:
                document = Document.objects.filter(collection_id=collection).order_by('insertion_time').first()
                request.session['document'] = document.document_id

            document = Document.objects.get(document_id=request.session['document'])
            json_resp['document'] = request.session['document']
            topic = request.session.get('topic',None)
            if topic is not None:
                json_resp['topic'] = Topic.objects.get(id=topic).topic_id
            json_resp['task'] = request.session['task']
            # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
            # task = task.task_id.name
            # request.session['task'] = task
            # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
            # types = [c.annotation_type.name for c in types]
            request.session['annotation_type'] = collection.annotation_type.name
            json_resp['language'] = document.language
            json_resp['role'] = request.session.get('role',"Annotator")
            request.session['language'] = document.language
            if fields_to_ann == []:
                fields_to_ann = get_fields_list(document, language)
            json_resp['fields_to_ann'] = request.session['fields_to_ann'] = fields_to_ann
            json_resp['fields'] = request.session['fields'] = fields

    else:
        if SessionDoc.objects.filter(username=user).exists():
            sessions = SessionDoc.objects.filter(username=user).order_by('-last_view')
            session = sessions.first()
            document = session.document_id
            role = session.role
            request.session['topic'] = json_resp['topic'] = session.topic_id.topic_id
            request.session['language'] = json_resp['language'] = document.language
            request.session['name_space'] = json_resp['name_space'] = user.name_space_id
            request.session['collection'] = json_resp['collection'] = document.collection_id_id
            # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
            # task = task.task_id.name
            # request.session['task'] = json_resp['task'] = task
            # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
            # task = task.task_id.name
            # request.session['task'] = json_resp['task'] = task
            # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
            # types = [c.annotation_type.name for c in types]
            request.session['annotation_type'] = json_resp['annotation_type'] = document.collection_id.annotation_type.name
            request.session['document'] = json_resp['document'] = document.document_id
            request.session['batch'] = json_resp['batch'] = document.batch
            request.session['role'] = json_resp['tole'] = role
            request.session['fields'] = json_resp['fields'] = request.session['fields_to_ann'] = json_resp['fields_to_ann']= get_fields_list(request.session['document'],
                                                                                           request.session['language'])

        elif GroundTruthLogFile.objects.filter(username=user).exists():
            gts = GroundTruthLogFile.objects.filter(username=user).order_by('-insertion_time')
            last_gt = gts.first()
            name_space = last_gt.name_space
            document = last_gt.document_id
            request.session['topic'] = json_resp['topic'] = last_gt.topic_id.topic_id
            request.session['language'] = json_resp['language'] = document.language
            request.session['name_space'] = json_resp['name_space'] = name_space.name_space
            request.session['collection'] = json_resp['collection']= document.collection_id_id
            # task = CollectionHasTask.objects.filter(collection_id=document.collection_id).first()
            # task = task.task_id.name
            # request.session['task'] = json_resp['task'] = task
            #
            # types = CollectionHasTask.objects.filter(collection_id=document.collection_id)
            # types = [c.annotation_type.name for c in types]
            request.session['annotation_type'] = json_resp['annotation_type'] = document.collection_id.annotation_type.name
            request.session['document'] = json_resp['document']= document.document_id
            request.session['batch'] = json_resp['batch'] = document.batch
            request.session['fields'] = json_resp['fields']= request.session['fields_to_ann'] = json_resp['fields_to_ann']= get_fields_list(request.session['document'],
                                                                                           request.session['language'])

        # se non ho ultima annotazione ma ho collezioni, allora setto la collezione all'ultima aggiunta e al primo doc della prima batch
        elif ShareCollection.objects.filter(username=user).exclude(
                status='invited').exists():  # non importa il name space in questo caso
            collections = ShareCollection.objects.filter(username=user).exclude(status='invited').values(
                'collection_id').distinct()
            collections_ids = [c['collection_id'] for c in collections]
            collection = Collection.objects.filter(collection_id__in=collections_ids).order_by(
                '-insertion_time').first()
            # task = CollectionHasTask.objects.filter(collection_id=collection).first()
            # task = task.task_id.name
            # request.session['task'] = json_resp['task'] = task
            # request.session['topic'] = json_resp['topic'] = Topic.objects.filter(collection_id=collection).first().id
            #
            # types = CollectionHasTask.objects.filter(collection_id=collection)
            # types = [c.annotation_type.name for c in types]
            request.session['annotation_type'] = json_resp['annotation_type']= collection.annotation_type.name
            request.session['collection'] = json_resp['collection'] = collection.collection_id
            documents = Document.objects.filter(collection_id=collection)
            if ShareCollection.objects.filter(username=user,reviewer=True).exclude(status='invited').exists():
                documents = SplitReviewer.objects.filter(username=user, collection_id=collection,
                                                 document_id__in=documents)
            elif Split.objects.filter(username=user, collection_id=collection,
                                    document_id__in=documents).exists():
                documents = Split.objects.filter(username=user, collection_id=collection,
                                                 document_id__in=documents)
                documents = sorted([d.document_id_id for d in documents])
            else:
                documents = sorted([d.document_id for d in documents])
            document = Document.objects.get(document_id=documents[0])

            request.session['document'] = json_resp['document']= document.document_id
            request.session['language'] =json_resp['language']= document.language
            request.session['batch'] = json_resp['batch'] = document.batch
            request.session['name_space'] = json_resp['name_space'] = user.name_space_id
            request.session['role'] = json_resp['role'] =  'Annotator'
            request.session['fields'] = json_resp['fields'] = json_resp['fields_to_ann'] =  request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                                           request.session['language'])


        else:
            json_resp['collection'] = None
            json_resp['document'] = None
            json_resp['topic'] = None
            json_resp['task'] = 'Default'
            json_resp['annotation_type'] = annotation_type
            json_resp['role'] = "Annotator"
            json_resp['language'] = None
            json_resp['fields'] = None
            json_resp['fields_to_ann'] = None

    return JsonResponse(json_resp)

def annotation_types(request):

    types = AnnotationType.objects.all()
    types = [a.name for a in types]
    json_resp = {'types':types}
    return JsonResponse(json_resp)

def set_new_fields(request):
    """Set new fields to ann parameter session"""

    body = json.loads(request.body)
    fields_to_ann = body['fields_to_ann']
    request.session['fields_to_ann'] = fields_to_ann
    return JsonResponse({'msg': 'ok'})


def concepts(request, type=None):
    """Concepts requests"""

    username = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    collection = request.session['collection']
    topic = request.session['topic']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=request.session['document'])
    user = User.objects.get(username=username, name_space=name_space)

    if request.method == 'GET':

        if request.GET.get('user', None) is not None:
            username = request.GET.get('user', None)
        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)


        if type == 'comment':
            concept = request.GET.get('concept', None)
            concept = Concept.objects.get(concept_url = concept)
            topic = request.session.get('topic', None)
            topic = Topic.objects.get(id = topic)

            start = int(request.GET.get('mention[start]', None))
            stop = int(request.GET.get('mention[stop]', None))
            position = request.GET.get('mention[position]', None)
            start_recomp, stop_recomp = return_start_stop_for_backend(start, stop, position, document.document_content)
            mention =  Mention.objects.get(document_id=document, start=start_recomp, stop=stop_recomp)
            annotation = Associate.objects.filter(start = mention,stop=mention.stop,concept_url = concept,topic_id=topic,username = user,name_space=name_space)
            if annotation.exists():
                comment = annotation.first().comment
                if comment is None:
                    comment = ''
                return JsonResponse({'comment':comment})

        if type == 'full':
            json_mentions = generate_associations_list(username, name_space.name_space, document.document_id, language,topic)
        else:
            json_mentions = generate_associations_list_splitted(username, name_space.name_space, document.document_id,
                                                                language,topic)
        # print(json_mentions)
        return JsonResponse(json_mentions, safe=False)

    if request.method == 'POST' and type == 'copy':

        json_body = json.loads(request.body)
        json_resp = copy_concepts_aux(username, name_space.name_space, document.document_id, language, json_body)
        return JsonResponse(json_resp)

    elif request.method == 'POST' and type == 'comment':

        body_json = json.loads(request.body)
        concept = body_json.get('concept',None)

        mention = body_json.get('mention',None)
        comment = body_json.get('comment',None)
        try:
            name_space = NameSpace.objects.get(name_space=request.session['name_space'])
            document = Document.objects.get(document_id = request.session['document'])
            concept = Concept.objects.get(concept_url = concept)
            topic = Topic.objects.get(id = request.session['topic'])
            user = User.objects.get(username=username, name_space=name_space)
            start, stop = return_start_stop_for_backend(int(mention['start']),int(mention['stop']),mention['position'], document.document_content)
            mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                          stop=stop)
            ann = Associate.objects.filter(start=mention, stop=stop,concept_url=concept, username = user, document_id=document,topic_id=topic, language=language)
            if ann.exists() and comment is not None:
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE associate SET comment = %s WHERE concept_url=%s and username = %s AND document_id = %s AND start = %s AND stop = %s and topic_id=%s""",
                                   [comment, concept.concept_url,user.username,document.document_id,mention.start,mention.stop,topic.id])

            return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)

    elif request.method == 'POST' and type == 'insert':

        body_json = json.loads(request.body)
        area = body_json['area']
        user = request.session['username']
        name_space = request.session['name_space']
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)
        name_space = NameSpace.objects.get(name_space=name_space)
        document = Document.objects.get(document_id=request.session['document'])
        collection = request.session['collection']
        collection = Collection.objects.get(collection_id=collection)
        user = User.objects.get(username=user, name_space=name_space)
        url = body_json['url']
        name = body_json['name']
        description = body_json['description']
        mention = body_json['mention']
        start = mention['start']
        stop = mention['stop']
        position = mention['position']
        start_recomp, stop_recomp = return_start_stop_for_backend(start, stop, position, document.document_content)
        mention = Mention.objects.get(start=start_recomp, stop=stop_recomp, document_id=document)
        json_resp = {'msg': 'ok'}

        try:
            with transaction.atomic():
                if not SemanticArea.objects.filter(name=area).exists():
                    SemanticArea.objects.create(name=area)
                    areas = get_areas_collection(collection.collection_id)
                    tags = get_tags_collection(collection.collection_id)
                    options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags)) if
                               k not in list(set(areas + tags))}
                    collection.options = options
                    collection.save()

                area = SemanticArea.objects.get(name=area)
                if not Concept.objects.filter(concept_url=url).exists():
                    Concept.objects.create(concept_url=url, concept_name=name, description=description)

                concept = Concept.objects.get(concept_url=url)
                if not AddConcept.objects.filter(concept_url=concept, name=area,
                                                 collection_id=collection).exists():
                    AddConcept.objects.create(username=user, name_space=name_space, insertion_time=Now(),
                                              concept_url=concept, name=area, collection_id=collection)
                if not Associate.objects.filter(username=user, name_space=name_space, name=area, concept_url=concept,topic_id=topic,
                                                document_id=document, start=mention, stop=mention.stop).exists():
                    Associate.objects.create(username=user, name_space=name_space, language=request.session['language'],
                                             insertion_time=Now(), concept_url=concept, name=area, start=mention,topic_id=topic,
                                             stop=mention.stop, document_id=document)

                    update_gt(user, name_space, document, request.session['language'],request.session['topic'])
            json_resp['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                        request.session['name_space'],
                                                                        request.session['document'],
                                                                        request.session['language'],request.session['topic'])
            json_resp['tags'] = generate_tag_list_splitted(request.session['username'],
                                                           request.session['name_space'],
                                                           request.session['document'],
                                                           request.session['language'],request.session['topic'])
            json_mentions = generate_relationships_list(request.session['username'], request.session['name_space'],
                                                        request.session['document'], request.session['language'],request.session['topic'])

            json_resp['relationships'] = json_mentions
            json_resp['concepts_list'] = create_concepts_list(request.session['collection'])


        except Exception as e:
            print(e)
            json_resp = {'error': e}

        return JsonResponse(json_resp)

    elif request.method == 'DELETE':
        body_json = json.loads(request.body)
        json_resp = {'msg': 'ok'}

        mentions_list = generate_mentions_list(username, name_space.name_space, document.document_id,
                                               request.session['language'],request.session['topic'])

        # name_space = NameSpace.objects.get(name_space=name_space)
        # document = Document.objects.get(document_id=document, language=language)
        # user = User.objects.get(username=username, name_space=name_space)
        mention_js = body_json['mention']
        start = mention_js['start']
        stop = mention_js['stop']
        position = mention_js['id']
        position = '_'.join(position.split('_')[:-1])
        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
        language = document.language
        mentions_classes = mention_js['mentions'].split()

        start_stop_list = []
        found = False
        # questo pezzo è per l'overlapping: se ho una mention totalmente dentro un'altra, solo in questo caso avrò un concetto associato, se no è associato sempre alla parte non overlapping
        for m in mentions_list:
            pos = m['mentions']
            start = m['start']
            stop = m['stop']
            start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
            if pos in mentions_classes:
                start_stop_list.append([start, stop])

        start_stop_list = sorted(start_stop_list, key=lambda x: x[1] - x[0])
        for i in range(len(start_stop_list) - 1):
            item_i = start_stop_list[i]
            for j in range(i + 1, len(start_stop_list)):
                item_j = start_stop_list[j]
                if item_j[0] <= item_i[0] <= item_j[1] and item_j[0] <= item_i[1] <= item_j[1]:
                    start = item_i[0]
                    stop = item_i[1]
                    found = True
                    break
            if found:
                break
        if len(start_stop_list) == 1:
            start = start_stop_list[0][0]
            stop = start_stop_list[0][1]

        mention = Mention.objects.get(start=start, stop=stop, document_id=document)
        url = body_json['url']
        concept = Concept.objects.get(concept_url=url)
        topic = Topic.objects.get(id=request.session['topic'])
        name = SemanticArea.objects.get(name=body_json['area'])
        try:
            with transaction.atomic():

                Associate.objects.filter(concept_url=concept, start=mention, stop=mention.stop, username=user,
                                         name_space=name_space, name=name,topic_id=topic,
                                         document_id=document).delete()
                update_gt(user, name_space, document, language,topic)
                json_mentions = generate_relationships_list(request.session['username'], request.session['name_space'],
                                                            request.session['document'], request.session['language'],request.session['topic'])
                # suddivido per semantic areas

                json_resp['relationships'] = json_mentions
        except Exception as e:
            json_resp = {'error': e}

        return JsonResponse(json_resp)


import psycopg2
from psycopg2.extras import execute_values

def split_users(request):
    """This view splits equally the documents across the users of the collection"""

    if request.method == 'POST':
        body_json = json.loads(request.body)
        collection = body_json['collection']
        collection = Collection.objects.get(collection_id=collection)
        members = ShareCollection.objects.filter(collection_id=collection)
        members = [m.username_id for m in members if m.reviewer != True and m.admin != True]

        split_topic = body_json['topic']
        split_document = body_json['document']

        topics = Topic.objects.filter(collection_id=collection)
        topics = [t.id for t in topics]
        documents = Document.objects.filter(collection_id=collection, honeypot=False)
        # gts = GroundTruthLogFile.objects.filter(document_id__in=documents)
        already_splitted = Split.objects.filter(document_id__in=documents)
        documents = [document.document_id for document in documents]
        #gts_documents = [document.document_id for document in gts]
        already_splitted = [document.document_id for document in already_splitted]
        # documents = [d for d in documents if d not in gts_documents and d not in already_splitted]
        documents = [d for d in documents if d not in already_splitted]
        random.shuffle(topics)
        random.shuffle(documents)
        # Calculate the size of each partition
        total_length_topics = len(topics)
        total_length = len(documents)
        partition_size_topics = total_length_topics // len(members)
        partition_size = total_length // len(members)
        remainder_topics = total_length_topics % len(members)
        remainder = total_length % len(members)

        partitions = []
        partitions_topics = []
        start_index = 0
        start_index_topic = 0

        for i in range(len(members)):
            # Adjust the size of the last few partitions to handle the remainder
            end_index = start_index + partition_size + (1 if i < remainder else 0)
            partitions.append(documents[start_index:end_index])
            start_index = end_index

            end_index_topic = start_index_topic + partition_size_topics + (1 if i < remainder_topics else 0)
            partitions_topics.append(topics[start_index_topic:end_index_topic])
            start_index_topic = end_index_topic
        try:
            if split_document:
                with transaction.atomic():
                    for j, m in enumerate(members):
                        m = User.objects.get(username=m)
                        docs = partitions[j]
                        docs = [Document.objects.get(document_id=d) for d in docs]
                        tuples = [(collection.collection_id, d.document_id, m.username, m.name_space_id, d.language) for d
                                  in docs]
                        with connection.cursor() as cursor:
                            query = "INSERT INTO split (collection_id, document_id, username, name_space, language) VALUES %s"
                            execute_values(cursor, query, tuples)
            if split_topic:
                with transaction.atomic():
                    for j, m in enumerate(members):
                        m = User.objects.get(username=m)
                        topics = partitions_topics[j]
                        topics = [Topic.objects.get(id=d) for d in topics]
                        tuples = [(collection.collection_id, d.id, m.username, m.name_space_id) for
                                  d
                                  in topics]
                        with connection.cursor() as cursor:
                            query = "INSERT INTO split_topic (collection_id, topic_id, username, name_space) VALUES %s"
                            execute_values(cursor, query, tuples)

        except Exception as e:
            print(e)
            return HttpResponse(status=500)
        return HttpResponse(status=200)


def get_tags(request):
    """This view returns the list of tags associated to that collection"""

    collection = request.GET.get('collection', None)
    if not collection:
        collection = request.session.get('collection', None)
    areas = get_tags_collection(collection)
    return JsonResponse({'areas': areas})


def tag(request, type=None):
    """Tags requests"""

    username = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    topic = request.session['topic']
    collection = request.session['collection']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=request.session['document'])
    user = User.objects.get(username=username, name_space=name_space)
    if request.method == 'GET':

        if request.GET.get('user', None) is not None:
            username = request.GET.get('user', None)
        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)

        if type == 'comment':
            tag = request.GET.get('tag', None)
            tag = Tag.objects.get(name = tag)
            topic = request.session.get('topic', None)
            topic = Topic.objects.get(id = topic)

            start = int(request.GET.get('mention[start]', None))
            stop = int(request.GET.get('mention[stop]', None))
            position = request.GET.get('mention[position]', None)
            start_recomp, stop_recomp = return_start_stop_for_backend(start, stop, position, document.document_content)
            mention =  Mention.objects.get(document_id=document, start=start_recomp, stop=stop_recomp)
            annotation = AssociateTag.objects.filter(start = mention,stop=mention.stop,name = tag,topic_id=topic,username = user,name_space=name_space)
            if annotation.exists():
                comment = annotation.first().comment
                if comment is None:
                    comment = ''
                return JsonResponse({'comment':comment})

        if type == 'full':
            json_mentions = generate_tag_list(username, name_space.name_space, document.document_id, language,topic)
        else:
            json_mentions = generate_tag_list_splitted(username, name_space.name_space, document.document_id, language,topic)
        # print(json_mentions)
        return JsonResponse(json_mentions, safe=False)

    if request.method == 'POST' and type == 'copy':

        json_body = json.loads(request.body)
        json_resp = copy_tags_aux(username, name_space.name_space, document.document_id, language, json_body)
        return JsonResponse(json_resp)

    elif request.method == 'POST' and type == 'comment':

        body_json = json.loads(request.body)
        tag = body_json.get('tag',None)

        mention = body_json.get('mention',None)
        comment = body_json.get('comment',None)
        try:
            name_space = NameSpace.objects.get(name_space=request.session['name_space'])
            document = Document.objects.get(document_id = request.session['document'])
            tag = Tag.objects.get(name = tag)
            topic = Topic.objects.get(id = request.session['topic'])
            user = User.objects.get(username=username, name_space=name_space)
            start, stop = return_start_stop_for_backend(int(mention['start']),int(mention['stop']),mention['position'], document.document_content)
            mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                          stop=stop)
            ann = AssociateTag.objects.filter(start=mention, stop=stop,name=tag, username = user, document_id=document,topic_id=topic, language=language)
            if ann.exists() and comment is not None:
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE associate_tag SET comment = %s WHERE name=%s and username = %s AND document_id = %s AND start = %s AND stop = %s and topic_id=%s""",
                                   [comment, tag.name,user.username,document.document_id,mention.start,mention.stop,topic.id])

            return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)

    elif request.method == 'POST' and type == 'insert':

        body_json = json.loads(request.body)
        area = body_json['area']
        user = request.session['username']
        name_space = request.session['name_space']
        name_space = NameSpace.objects.get(name_space=name_space)
        document = Document.objects.get(document_id=request.session['document'])
        user = User.objects.get(username=user, name_space=name_space)
        collection_obj = Collection.objects.get(collection_id=request.session['collection'])
        topic = Topic.objects.get(id=request.session['topic'])
        mention = body_json['mention']
        start = mention['start']
        stop = mention['stop']
        position = mention['position']
        start_recomp, stop_recomp = return_start_stop_for_backend(start, stop, position, document.document_content)
        if not Mention.objects.filter(document_id=document, start=start_recomp, stop=stop_recomp).exists():
            mentions_list = Annotate.objects.filter(username=user, document_id=document)
            mentions = []
            for m in mentions_list:
                if m.start_id <= start_recomp and m.stop >= stop_recomp:
                    mention = Mention.objects.get(document_id=document, start=m.start_id, stop=m.stop)
                    mentions.append(mention)
            sorted(mentions, key=lambda x: x.stop - x.start)
            mention = mentions[0]
        else:
            mention = Mention.objects.get(document_id=document, start=start_recomp, stop=stop_recomp)
        json_resp = {'msg': 'ok'}

        try:
            with transaction.atomic():
                if not Tag.objects.filter(name=area).exists():
                    Tag.objects.create(name=area)

                if not CollectionHasTag.objects.filter(collection_id=collection_obj, name=area).exists():
                    tag = Tag.objects.get(name=area)
                    CollectionHasTag.objects.create(collection_id=collection_obj, name=tag)
                    options = collection_obj.options
                    if options is None:
                        options = {}
                    if tag.name not in list(options.keys()):
                        options[tag.name] = 'rgba(65, 105, 225, 1)'
                        collection_obj.options = options
                        collection_obj.save()

                area = Tag.objects.get(name=area)

                if not AssociateTag.objects.filter(username=user, name_space=name_space, name=area,topic_id=topic,
                                                   document_id=document, start=mention, stop=mention.stop).exists():
                    AssociateTag.objects.create(username=user, name_space=name_space,topic_id=topic,
                                                language=request.session['language'],
                                                insertion_time=Now(), name=area, start=mention,
                                                stop=mention.stop, document_id=document)

                    update_gt(user, name_space, document, request.session['language'],request.session['topic'])
            json_resp['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                        request.session['name_space'],
                                                                        request.session['document'],
                                                                        request.session['language'],request.session['topic'])
            json_resp['tags'] = generate_tag_list_splitted(request.session['username'],
                                                           request.session['name_space'],
                                                           request.session['document'],
                                                           request.session['language'],request.session['topic'])
            json_mentions = generate_relationships_list(request.session['username'], request.session['name_space'],
                                                        request.session['document'], request.session['language'],request.session['topic'])
            # suddivido per semantic areas

            json_resp['relationships'] = json_mentions
            json_resp['concepts_list'] = create_concepts_list(request.session['collection'])
            json_resp['tags_list'] = []
            collection = Collection.objects.get(collection_id=collection)
            areas = CollectionHasTag.objects.filter(collection_id=collection)
            areas = [area.name_id for area in areas]
            json_resp['tags_list'] = areas


        except Exception as e:
            print(e)
            json_resp = {'error': e}

        return JsonResponse(json_resp)

    elif request.method == 'DELETE':
        body_json = json.loads(request.body)
        json_resp = {'msg': 'ok'}

        mentions_list = generate_mentions_list(username, name_space.name_space, document.document_id,
                                               request.session['language'])

        # name_space = NameSpace.objects.get(name_space=name_space)
        # document = Document.objects.get(document_id=document, language=language)
        # user = User.objects.get(username=username, name_space=name_space)
        mention_js = body_json['mention']
        start = mention_js['start']
        stop = mention_js['stop']
        position = mention_js['id']
        position = '_'.join(position.split('_')[:-1])
        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
        language = document.language
        mentions_classes = mention_js['mentions'].split()

        start_stop_list = []
        found = False
        # questo pezzo è per l'overlapping: se ho una mention totalmente dentro un'altra, solo in questo caso avrò un concetto associato, se no è associato sempre alla parte non overlapping
        for m in mentions_list:
            pos = m['mentions']
            start = m['start']
            stop = m['stop']
            start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
            if pos in mentions_classes:
                start_stop_list.append([start, stop])

        start_stop_list = sorted(start_stop_list, key=lambda x: x[1] - x[0])
        for i in range(len(start_stop_list) - 1):
            item_i = start_stop_list[i]
            for j in range(i + 1, len(start_stop_list)):
                item_j = start_stop_list[j]
                if item_j[0] <= item_i[0] <= item_j[1] and item_j[0] <= item_i[1] <= item_j[1]:
                    start = item_i[0]
                    stop = item_i[1]
                    found = True
                    break
            if found:
                break
        if len(start_stop_list) == 1:
            start = start_stop_list[0][0]
            stop = start_stop_list[0][1]

        mention = Mention.objects.get(start=start, stop=stop, document_id=document)
        name = Tag.objects.get(name=body_json['area'])
        try:
            with transaction.atomic():

                AssociateTag.objects.filter(start=mention, stop=mention.stop, username=user, name_space=name_space,
                                            name=name,
                                            document_id=document).delete()
                update_gt(user, name_space, document, language,topic)
                json_mentions = generate_relationships_list(request.session['username'], request.session['name_space'],
                                                            request.session['document'], request.session['language'],request.session['topic'])

                json_resp['relationships'] = json_mentions
                json_resp['tags'] = generate_tag_list_splitted(request.session['username'],
                                                               request.session['name_space'],
                                                               request.session['document'],
                                                               request.session['language'],
                                                               request.session['topic'])
        except Exception as e:
            json_resp = {'error': e}

        return JsonResponse(json_resp)


def set_concept(request):
    """This view adds a new concept; rapid insertion from the modal"""

    body_json = json.loads(request.body)
    area = body_json['area']
    user = request.session['username']
    name_space = request.session['name_space']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=request.session['document'])
    collection = request.session['collection']
    collection = Collection.objects.get(collection_id=collection)
    user = User.objects.get(username=user, name_space=name_space)
    url = body_json['url']
    name = body_json['name']
    description = body_json['description']
    mention = body_json['mention']
    start = mention['start']
    stop = mention['stop']
    # dict_keys = from_start_stop_foreach_key(document_content=document.document_content)
    # keys = dict_keys['key']
    # for k in list(keys.keys()):
    #     if start >= k.start and stop <= k.stop:
    #         position = ''
    # val = dict_keys['value']
    # position = '_'.join(mention['id'].split('_')[:-1])
    position = mention['position']
    start_recomp, stop_recomp = return_start_stop_for_backend(start, stop, position, document.document_content)
    mention = Mention.objects.get(start=start_recomp, stop=stop_recomp, document_id=document)
    json_resp = {'msg': 'ok'}

    try:
        with transaction.atomic():
            if not SemanticArea.objects.filter(name=area).exists():
                SemanticArea.objects.create(name=area)
                areas = get_areas_collection(collection.collection_id)
                tags = get_tags_collection(collection.collection_id)
                options = {k: 'rgba(65, 105, 225, 1)' for k in list(set(areas + tags)) if
                           k not in list(set(areas + tags))}
                collection.options = options
                collection.save()
            area = SemanticArea.objects.get(name=area)
            if not Concept.objects.filter(concept_url=url).exists():
                Concept.objects.create(concept_url=url, concept_name=name, description=description)

            concept = Concept.objects.get(concept_url=url)
            if not AddConcept.objects.filter(concept_url=concept, name=area,
                                             collection_id=collection).exists():
                AddConcept.objects.create(username=user, name_space=name_space, insertion_time=Now(),
                                          concept_url=concept, name=area, collection_id=collection)
            if not Associate.objects.filter(username=user, name_space=name_space, name=area, concept_url=concept,
                                            document_id=document, start=mention, stop=mention.stop).exists():
                Associate.objects.create(username=user, name_space=name_space, language=request.session['language'],
                                         insertion_time=Now(), concept_url=concept, name=area, start=mention,
                                         stop=mention.stop, document_id=document)

                update_gt(user, name_space, document, request.session['language'])
        json_resp['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                    request.session['name_space'],
                                                                    request.session['document'],
                                                                    request.session['language'],request.session['topic'])
        json_resp['concepts_list'] = create_concepts_list(request.session['collection'])

    except Exception as e:
        print(e)
        json_resp = {'error': e}

    return JsonResponse(json_resp)


def honeypot(request):
    """create the honeypot: each member of the collection has the documents of the honeypot to be annotated"""

    if request.method == 'POST':
        body_json = json.loads(request.body)
        collection = body_json['collection']
        collection = Collection.objects.get(collection_id=collection)
        documents = body_json['documents']
        documents = [d['hashed_id'] for d in documents]
        documents = Document.objects.filter(document_id__in=documents)
        ids = [d.document_id for d in documents]
        with transaction.atomic():
            with connection.cursor() as cursor:
                for d in ids:
                    query = "UPDATE document SET honeypot = %s where document_id = %s"
                    cursor.execute(query, [True, d])

        members = ShareCollection.objects.filter(collection_id=collection)
        tuples = []
        try:
            with transaction.atomic():
                for m in members:
                    tuples.extend(
                        [(collection.collection_id, d.document_id, m.username_id, m.name_space_id, d.language) for
                         d in documents])
                with connection.cursor() as cursor:
                    query = "INSERT INTO split (collection_id, document_id, username, name_space, language) VALUES %s"
                    execute_values(cursor, query, tuples)

        except Exception as e:
            print(e)
            return HttpResponse(status=500)
        return HttpResponse(status=200)


def change_collection_id(request):
    """This view changes collection"""

    collection = request.GET.get('collection', None)
    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    user = User.objects.get(username=request.session['username'], name_space=name_space)
    request.session['role'] = "Annotator"

    if collection is not None:
        request.session['collection'] = collection
        documents = Document.objects.filter(collection_id=collection)
        request.session['document'] = documents.first().document_id
        if SessionDoc.objects.filter(username=user,document_id__in=documents).exists():
            sessions = SessionDoc.objects.filter(username=user,document_id__in=documents).order_by('-last_view')
            session = sessions.first()
            request.session['topic'] = session.topic_id_id
            document = session.document_id
            role = session.role
            request.session['language'] = document.language
            request.session['name_space'] = user.name_space_id
            request.session['collection'] = document.collection_id_id
            request.session['document'] = document.document_id
            request.session['batch'] = document.batch
            request.session['role'] = role
            request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                                           request.session['language'])
        elif GroundTruthLogFile.objects.filter(username=user,document_id__in=documents).exists():
            gts = GroundTruthLogFile.objects.filter(username=user, document_id__in=documents).order_by(
                '-insertion_time')
            last_gt = gts.first()
            name_space = last_gt.name_space
            document = last_gt.document_id
            request.session['topic'] = last_gt.topic_id_id
            request.session['language'] = document.language
            request.session['name_space'] = name_space.name_space
            request.session['collection'] = document.collection_id_id
            request.session['document'] = document.document_id
            request.session['batch'] = document.batch
            request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(
                request.session['document'], request.session['language'])


        elif Split.objects.filter(document_id__in=documents, username=user).exists():

            documents = Split.objects.filter(username=user,document_id__in=documents)
            documents = sorted([d.document_id_id for d in documents])

            document = Document.objects.get(document_id=documents[0])
            request.session['document'] = document.document_id

            # doc_sel = Document.objects.get(document_id=request.session['document'])
            request.session['language'] = document.language
            request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                                           request.session['language'])
            if SplitTopic.objects.filter(collection_id = document.collection_id, username=user).exists():
                topic = SplitTopic.objects.filter(collection_id = document.collection_id,username=user).first()
                request.session['topic'] = topic.topic_id_id
            else:
                topic = Topic.objects.filter(collection_id = collection).first()
                request.session['topic'] = topic.topic_id_id

            # print('session doc',request.session['document'])
            json_resp = {'document_id': request.session['document'],'topic': request.session['topic']}
            return JsonResponse(json_resp)

        elif SplitTopic.objects.filter(collection_id=collection, username=user).exists():
            documents = Split.objects.filter(username=user, document_id__in=documents)
            documents = sorted([d.document_id_id for d in documents])

            document = Document.objects.get(document_id=documents[0])
            request.session['language'] = document.language
            request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                                           request.session['language'])

            request.session['document'] = document.document_id
            topic = SplitTopic.objects.filter(collection_id=document.collection_id, username=user).first()
            request.session['topic'] = topic.topic_id_id


        request.session['fields'] = request.session['fields_to_ann'] = get_fields_list(request.session['document'],
                                                                                       request.session['language'])

        # print('session doc', request.session['document'])
        json_resp = {'document_id': request.session['document'],'topic': request.session['topic']}
        return JsonResponse(json_resp)


def get_batches(request):
    """This view returns the batches of a collection"""

    collection = Collection.objects.get(collection_id=request.session['collection'])
    batch = (Document.objects.filter(collection_id=collection).aggregate(Max('batch')))
    json_resp = {}
    json_resp['max_batch'] = batch["batch__max"]
    # print(batch["batch__max"])
    return JsonResponse(json_resp)


def get_collection_concepts(request):
    """ This view returns the list of concepts found for a collection"""

    collection = Collection.objects.get(collection_id=request.session['collection'])
    coll_conc = AddConcept.objects.filter(collection_id=collection)
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

    return JsonResponse(concepts, safe=False)


def get_collection_labels(request):
    """This view returns the labels of a collection"""

    collection = request.session.get('collection', None)
    collection = Collection.objects.get(collection_id=collection)
    labels = CollectionHasLabel.objects.filter(collection_id=collection)
    labels = [l.name_id for l in labels]
    print(labels)
    return JsonResponse(labels, safe=False)


def get_annotators(request):
    """This view returns the list of annotators of a document"""

    document = Document.objects.get(document_id=request.session['document'], language=request.session['language'])
    gts = GroundTruthLogFile.objects.filter(document_id=document)
    usernames = [g.username_id for g in gts]
    print(usernames)
    if gts.count() > 0:
        users = list(gts.order_by('username').values_list('username', flat=True).distinct())
    else:
        users = []
    print(users)
    if request.session['username'] in users:
        users.remove(request.session['username'])

    users.insert(0, request.session['username'])
    users.append("IAA-Inter Annotator Agreement")
    return JsonResponse(users, safe=False)


# ANNOTATIONS
def get_annotated_labels(request):
    """This view returns the labels annotated by the logged in user"""

    username = request.session['username']
    name_space = request.session['name_space']
    if request.GET.get('user', None) is not None:
        username = request.GET.get('user', None)
    if request.GET.get('name_space', None) is not None:
        name_space = request.GET.get('name_space', None)

    language = request.session['language']
    topic = request.session['topic']
    labels_obj = {}
    doc_id = request.session.get('document', None)
    json_error = {'error': 'an error occurred'}
    if name_space and username and doc_id and language:
        ns = NameSpace.objects.get(name_space=name_space)
        topic = Topic.objects.get(id=topic)
        user = User.objects.get(username=username, name_space=ns)
        document = Document.objects.get(document_id=doc_id, language=language)
        labels = AnnotateLabel.objects.filter(username=user, topic_id=topic,name_space=ns, document_id=document)
        labels = {l.label.name :int(l.grade) for l in labels}
        labels_obj['labels'] = labels
        return JsonResponse(labels_obj)
    else:
        return JsonResponse(json_error)


def labels(request, type=None):
    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    collection = request.session['collection']
    topic = request.session['topic']

    if request.method == 'GET':
        username = request.session['username']
        name_space = request.session['name_space']
        if request.GET.get('user', None) is not None:
            username = request.GET.get('user', None)
        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)
        if request.GET.get('topic', None) is not None:
            topic = request.GET.get('topic', None)

        language = request.session['language']

        doc_id = request.session.get('document', None)
        json_error = {'error': 'an error occurred'}
        if type == 'comment':
            label = request.GET.get('label',None)
            name_space = NameSpace.objects.get(name_space=name_space)
            topic = Topic.objects.get(id=topic)
            document = Document.objects.get(document_id=document, language=language)
            user = User.objects.get(username=username, name_space=name_space)
            label = Label.objects.get(name=label)
            comment = ''
            mention = request.GET.get('mention[start]',None)
            points = request.GET.get('points',None)
            if mention is None and points is None:
                comments = AnnotateLabel.objects.filter(username=user, document_id=document, language=language, label=label,
                                                topic_id=topic, name_space=name_space)
            elif mention is None and points is not None:
                points = DocumentObject.objects.get(document_id=document,points=points)
                comments = AnnotateObjectLabel.objects.filter(username=user, document_id=document, language=language, label=label,
                                                topic_id=topic, name_space=name_space,points=points)
            elif mention is not None:
                mention = {}
                mention['start'] = int(request.GET.get('mention[start]',None))
                mention['stop'] = int(request.GET.get('mention[stop]',None))
                mention['position'] = request.GET.get('mention[position]',None)

                start, stop = return_start_stop_for_backend(mention['start'], mention['stop'],
                                                            mention['position'],
                                                            document.document_content)
                mention = Mention.objects.get(document_id=document, language=request.session['language'],
                                              start=start,
                                              stop=stop)
                comments = AnnotatePassage.objects.filter(username=user, document_id=document, language=language,
                                                        label=label,start=mention,stop=mention.stop,
                                                        topic_id=topic, name_space=name_space)
            if comments.exists():
                comment = comments.first().comment
            json_resp = {'comment': comment}
            return JsonResponse(json_resp)


        else:
            if name_space and username and doc_id and language and topic:
                ns = NameSpace.objects.get(name_space=name_space)
                user = User.objects.get(username=username, name_space=ns)
                document = Document.objects.get(document_id=doc_id, language=language)
                topic = Topic.objects.get(id=topic)
                labels = AnnotateLabel.objects.filter(username=user, name_space=ns,topic_id=topic, document_id=document)
                labels = [l.label.name for l in labels]
                # labels = [l.name for l in labels]
                return JsonResponse(labels, safe=False)
            else:
                return JsonResponse(json_error)

    # elif request.method == 'POST' and collection.modality == 'Collaborative restricted':
    #     json_error = {'error':'TYou cannot annotate documents not assigned to you'}
    #     return JsonResponse(json_error,status=500)

    elif request.method == 'POST' and type == 'copy':
        json_body = json.loads(request.body)
        label = json_body['label']
        json_resp = copy_labels(username, name_space, label, document, language)
        return JsonResponse(json_resp)

    elif request.method == 'POST' and type == 'comment':
        json_body = json.loads(request.body)
        label = json_body['label']
        type = json_body['type']
        label = Label.objects.get(name=label)
        comment = json_body['comment']
        name_space = NameSpace.objects.get(name_space=name_space)
        topic = Topic.objects.get(id=topic)
        document = Document.objects.get(document_id=document, language=language)
        user = User.objects.get(username=username, name_space=name_space)
        if type == 'label':
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE annotate_label SET comment = %s WHERE label = %s and username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s """,
                    [comment, label.name, user.username, name_space.name_space, document.document_id, document.language,
                     topic.id])


                return HttpResponse(status = 200)
        elif type == 'passage':
            mention = json_body['mention']
            start, stop = return_start_stop_for_backend(mention['start'], mention['stop'],
                                                        mention['position'],
                                                        document.document_content)

            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE annotate_passage SET comment = %s WHERE label = %s and username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s and start = %s and stop = %s """,
                    [comment, label.name, user.username, name_space.name_space, document.document_id,
                     document.language,
                     topic.id,start,stop])

                return HttpResponse(status=200)
        elif type == 'object':
            points = json_body['points']
            points = DocumentObject.objects.get(document_id = document, points=points)

            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE annotate_object_label SET comment = %s WHERE label = %s and username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s and points = %s """,
                    [comment, label.name, user.username, name_space.name_space, document.document_id,
                     document.language,points.points])

                return HttpResponse(status=200)
        return HttpResponse(status = 500)

    elif request.method == 'POST' and type == 'insert':

        name_space = NameSpace.objects.get(name_space=name_space)
        topic = Topic.objects.get(id=topic)
        document = Document.objects.get(document_id=document, language=language)
        user = User.objects.get(username=username, name_space=name_space)
        body_json = json.loads(request.body)
        language = document.language
        label = body_json['label']
        mention = body_json.get('mention', None)
        points = body_json.get('points', None)

        score = body_json['score']
        label = Label.objects.get(name=label)
        try:
            if mention is None and points is None:
                with transaction.atomic():
                    if AnnotateLabel.objects.filter(username=user, document_id=document, language=language, label=label,
                                                 topic_id=topic,name_space=name_space).exists():
                        with connection.cursor() as cursor:
                            cursor.execute("""UPDATE annotate_label SET label = %s, grade = %s WHERE username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s """,[label.name,score,user.username,name_space.name_space,document.document_id,document.language, topic.id])

                    else:
                        AnnotateLabel.objects.create(username=user, document_id=document, language=language, label=label,
                                                 insertion_time=Now(), grade=score, topic_id=topic,name_space=name_space)
                    update_gt(user, name_space, document, language,topic)

                    return JsonResponse({'msg': 'ok'})
            elif points is not None:
                    dobj = DocumentObject.objects.get(document_id=document, points=points)
                    if AnnotateObjectLabel.objects.filter(username=user, document_id=document,points=dobj, language=language, label=label,
                                                 topic_id=topic,name_space=name_space).exists():
                        with connection.cursor() as cursor:
                            cursor.execute("""UPDATE annotate_object_label SET label = %s, grade = %s WHERE username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s and points = %s """,[label.name,score,user.username,name_space.name_space,document.document_id,document.language, topic.id,dobj.points])

                    else:
                        AnnotateObjectLabel.objects.create(username=user, document_id=document, language=language, label=label,points=dobj,
                                                 insertion_time=Now(), grade=score, topic_id=topic,name_space=name_space)
                    update_gt(user, name_space, document, language,topic)
                    return JsonResponse({'msg': 'ok'})
            else:
                with transaction.atomic():
                    start, stop = return_start_stop_for_backend(mention['start'], mention['stop'],
                                                                mention['position'],
                                                                document.document_content)
                    mention = Mention.objects.get(document_id=document, language=request.session['language'],
                                                  start=start,
                                                  stop=stop)
                    if AnnotatePassage.objects.filter(username=user, document_id=document,start = mention,stop = mention.stop, language=language, label=label,
                                                    topic_id=topic, name_space=name_space).exists():
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """UPDATE annotate_passage SET label = %s, grade = %s WHERE username = %s AND name_space = %s AND document_id = %s AND language = %s and topic_id = %s and start = %s and stop = %s""",
                                [label.name, score, user.username, name_space.name_space, document.document_id,
                                 document.language, topic.id, mention.start, mention.stop])
                    else:
                        AnnotatePassage.objects.create(username=user, document_id=document, language=language,
                                                     label=label,start = mention,stop = mention.stop,
                                                     insertion_time=Now(), grade=score, topic_id=topic,
                                                     name_space=name_space)
                    update_gt(user, name_space, document, language, topic)

                    return JsonResponse({'msg': 'ok'})

        except Exception as e:
            print(e)
            return JsonResponse({'error': e})

    elif request.method == 'DELETE':
        name_space = NameSpace.objects.get(name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        user = User.objects.get(username=username, name_space=name_space)
        topic = Topic.objects.get(id = topic)
        body_json = json.loads(request.body)
        language = document.language
        label = body_json['label']
        start = body_json.get('start',None)
        stop = body_json.get('stop',None)
        points = body_json.get('points',None)
        label = Label.objects.get(name=label)
        try:
            with transaction.atomic():
                if start and stop:
                    mention = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
                    AnnotatePassage.objects.filter(username=user, document_id=document,start=mention,stop=mention.stop, language=language, label=label,topic_id = topic)
                elif points:
                    points = DocumentObject.objects.get(document_id = document,language = document.language,points = points)
                    AnnotateObjectLabel.objects.filter(username=user, document_id=document, language=language, label=label,topic_id = topic,points=points)
                else:
                    AnnotateLabel.objects.filter(username=user, document_id=document, language=language,
                                                 label=label,topic_id = topic).delete()

                update_gt(user, name_space, document, language,topic)

                return JsonResponse({'msg': 'ok'})

        except Exception as e:
            print(e)
            return JsonResponse({'error': e})


def update_document_id(request):
    """This view updates the document id of the session"""

    body_json = json.loads(request.body)
    document = body_json['document']
    language = request.session['language']
    if Document.objects.filter(document_id=document, language=language).exists():
        request.session['document'] = body_json['document']

        username = request.session.get('username', False)
        name_space = request.session.get('name_space', False)
        collection = request.session.get('collection', False)
        topic = request.session.get('topic', False)
        role = request.session.get('role', False)
        last_doc = body_json['document']
        with transaction.atomic():
            if last_doc and username and name_space and collection and role and topic:
                document = Document.objects.get(document_id=last_doc)
                # with connection.cursor() as cursor:
                #     cursor.execute("""UPDATE share_collection SET last_document = %s, language_last_document = %s,last_view = %s
                #     WHERE username = %s AND collection_id = %s""",[document.document_id,document.language,datetime.now(),username,collection])
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO session_doc (document_id, language, username, name_space, role, last_view,collection_id,topic_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                    ON CONFLICT (username, name_space, collection_id, role,topic_id)
                    DO UPDATE SET
                        last_view = %s,document_id=%s,language=%s;""",[document.document_id,document.language,username,name_space,role,datetime.now(),document.collection_id_id,topic,datetime.now(),document.document_id,document.language])



        return JsonResponse({'msg': 'ok'})
    else:
        return HttpResponse(status=500)

def update_document_id_from_dashboard(request):
    """
    This view updates the document id of the session, basically use for moving to annotated or not annotated documents
    This views purpose is moving from Dashboard Page to actual indexing page of the cell that user selects inside the tables
    """
    body_json = json.loads(request.body)
    document_id = body_json['document']
    collection = body_json['collection']
    topic = body_json['topic']
    topic = int(topic)     # cast the topic to int

    language = request.session['language']

    name_space = request.session.get('name_space', 'Human')
    role = request.session.get('role')
    username = request.session.get('username')

    if Document.objects.filter(document_id=document_id, language=language).exists():
        request.session['document'] = document_id
        request.session['collection'] = collection
        with transaction.atomic():
            if username and name_space and collection and role and topic:
                document = Document.objects.get(document_id=document_id)
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO session_doc (document_id, language, username, name_space, role, last_view,collection_id,topic_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                    ON CONFLICT (username, name_space, collection_id, role,topic_id)
                    DO UPDATE SET
                        last_view = %s,document_id=%s,language=%s;""",[document.document_id,document.language,username,name_space,role,datetime.now(),document.collection_id_id,topic,datetime.now(),document.document_id,document.language])
        return JsonResponse({'msg': 'ok'})
    else:
        return HttpResponse(status=500)

def accept_invitation(request):
    """This view allows a user to accept the invitation to share a new collection"""

    username = request.session.get('username', None)
    name_space = request.session.get('name_space', None)
    doc_id = request.session.get('document', None)
    name_space = NameSpace.objects.get(name_space=name_space)
    username = User.objects.get(username=username, name_space=name_space)
    body_json = json.loads(request.body)
    collection = body_json['collection']
    collection = Collection.objects.get(collection_id=collection)
    sharecoll = ShareCollection.objects.filter(username=username, name_space=name_space, collection_id=collection)
    try:
        with transaction.atomic():
            if sharecoll.exists():
                # sharecoll.delete()
                sharecoll.update(status='accepted')
                # ShareCollection.objects.create(username = username,name_space = name_space, collection_id = collection,invitation= 'accepted')
        return JsonResponse({'msg': 'ok'})
    except Exception as e:
        return JsonResponse({'error': e})


def get_mention_info(request):
    """This view returns the information about the mention (or the mention + concept)"""

    json_to_ret = {}
    json_to_ret['concepts'] = []

    mention_requested = request.GET.get('mention', None)
    username = request.session.get('username', None)
    name_space = request.session.get('name_space', None)
    doc_id = request.session.get('document', None)
    document = Document.objects.get(document_id=doc_id, language=request.session['language'])
    language = request.session.get('language', None)
    name_space = NameSpace.objects.get(name_space=name_space)
    username = User.objects.get(username=username, name_space=name_space)
    if mention_requested:
        mention_requested = json.loads(mention_requested)
        start, stop = return_start_stop_for_backend(mention_requested['start'], mention_requested['stop'],
                                                    mention_requested['position'], document.document_content)
        mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                      stop=stop)
        json_to_ret['text'] = mention.mention_text
        annotation_all = Annotate.objects.filter(start=mention, stop=stop, document_id=document, language=language)
        json_to_ret['annotators_count'] = annotation_all.count()

        annotation_user = Annotate.objects.filter(username=username, name_space=name_space, start=mention, stop=stop,
                                                  document_id=document, language=language)
        json_to_ret['last_update'] = '.'.join(str(annotation_user.first().insertion_time).split('.')[:-1])

        association_user = Associate.objects.filter(start=mention, username=username, name_space=name_space,
                                                    stop=stop, document_id=document, language=language).order_by(
            '-insertion_time')
        for a in association_user:
            json_c = {}
            concept = a.concept_url
            json_c['concept_url'] = concept.concept_url
            area = a.name
            json_c['concept_area'] = area.name

            name = concept.concept_name
            json_c['concept_name'] = name
            json_c['last_update'] = '.'.join(str(a.insertion_time).split('.')[:-1])
            association_all = Associate.objects.filter(start=mention, stop=stop, document_id=document,
                                                       language=language, concept_url=concept)
            json_c['annotators_count'] = association_all.count()
            json_to_ret['concepts'].append(json_c)
        return JsonResponse(json_to_ret)


def get_assertions(request):
    """This view returns a list of assertions"""

    username = request.session['username']
    name_space = request.session['name_space']
    if request.GET.get('user', None) is not None:
        print('user assertions', request.GET.get('user', None))
        username = request.GET.get('user', None)
    if request.GET.get('name_space', None) is not None:
        name_space = request.GET.get('name_space', None)

    language = request.session['language']
    document = request.session['document']
    json_mentions = {}
    json_ment_areas = {}
    json_assertions = generate_assertions_list(username, name_space, document, language)
    return JsonResponse({'assertions': json_assertions}, safe=False)



import math

def object_detection(request,type=None):
    document = request.session.get('document', None)
    topic = request.session.get('topic', None)
    username = request.session.get('username', None)
    name_space = request.session.get('name_space', None)

    if None in [name_space, username, topic, document]:
        return HttpResponse(status=500)
    document = Document.objects.get(document_id=document)
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = Topic.objects.get(id=topic)
    labels = CollectionHasLabel.objects.filter(passage_annotation=True, collection_id=document.collection_id)

    if request.method == "GET":
        document = request.session.get('document',None)
        document = request.GET.get('document',document)
        username = request.session.get('username', None)
        username = request.GET.get('username',username)

        if None in [name_space, username, topic, document]:
            return HttpResponse(status = 500)
        document = Document.objects.get(document_id = document)
        username = User.objects.get(username = username,name_space = name_space)
        values = []

        if type == 'comment':
            points = request.GET.get('points',None)
            if points:
                points = DocumentObject.objects.get(points=points,document_id=document)
                comment = AnnotateObject.objects.get(points=points,document_id=document,username=username,topic_id=topic).comment
                if not comment:
                    comment = ''
                return JsonResponse({'comment':comment})



        ob = AnnotateObject.objects.filter(username = username, name_space = name_space, document_id = document, topic_id = topic).order_by('-insertion_time')
        if ob.exists():
            points = []
            for o in ob:
                points.append(o.points)
                val = {}
                for label in labels:
                    val[label.label_id] = None
                    annotations = AnnotateObjectLabel.objects.filter(username=username, name_space=name_space,
                                                                     points=o.points,
                                                                     document_id=document, label=label.label,
                                                                     topic_id=topic)
                    for a in annotations:
                        val[a.label_id] = int(a.grade)
                values.append(val)

            return JsonResponse({'points': points, 'values': values})
        return JsonResponse({'points': [], 'values': []})

    if request.method == 'POST' and type == 'comment':
        body = json.loads(request.body)
        username = User.objects.get(username = username,name_space = name_space)

        points = body['points']
        comment = body['comment']
        try:
            if points:
                points = DocumentObject.objects.get(points=points,document_id=document)

                cursor = connection.cursor()
                cursor.execute("UPDATE annotate_object SET comment = %s WHERE points=%s and username = %s and document_id = %s and topic_id = %s",
                               [comment, points.points,username.username,document.document_id,topic.id])
                return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)

    if request.method == 'POST' and type == 'insert':

        body = json.loads(request.body)
        points = body['points']
        username = User.objects.get(username = username,name_space = name_space)

        image = None

        try:
            with transaction.atomic():
                DocumentObject.objects.get_or_create(document_id=document, language=document.language, image=image,
                                                     points=points)
                obj = AnnotateObject.objects.filter(username=username, name_space=name_space, document_id=document,
                                                    topic_id=topic,
                                                    points=points)
                if not obj.exists():
                    # cursor.execute("""UPDATE annotate_object SET points = %s, insertion_time = %s WHERE
                    # username = %s and name_space = %s and document_id = %s and language = %s and topic_id = %s""",
                    #                [points,datetime.now(),username.username,name_space.name_space,document.document_id,document.language,topic.id])
                    AnnotateObject.objects.create(username=username, name_space=name_space, document_id=document,
                                                  topic_id=topic,insertion_time = Now(),language = document.language,
                                                  points=points)


        except Exception as e:
            print(e)
            return HttpResponse(status = 500)
        finally:
            ob = AnnotateObject.objects.filter(username=username, name_space=name_space, document_id=document,
                                               topic_id=topic).order_by('-insertion_time')
            if ob.exists():
                points = []
                values = []
                for o in ob:
                    points.append(o.points)
                    val = {}
                    for label in labels:
                        val[label.label_id] = None
                        annotations = AnnotateObjectLabel.objects.filter(username=username, name_space=name_space,points = o.points,
                                                                         document_id=document,label = label.label,
                                                                         topic_id=topic)
                        for a in annotations:
                            val[a.label_id] = int(a.grade)
                    values.append(val)

                return JsonResponse({'points': points,'values':values})
            return JsonResponse({'points': [],'values':[]})

    elif request.method == 'POST' and type == 'update':
        body = json.loads(request.body)
        points = body['points']
        points_prev = body['points_prev']
        print(points)
        document = request.session.get('document',None)
        topic = request.session.get('topic', None)
        username = request.session.get('username', None)
        name_space = request.session.get('name_space', None)

        if None in [name_space, username, topic, document]:
            return HttpResponse(status = 500)
        document = Document.objects.get(document_id = document)
        name_space = NameSpace.objects.get(name_space = name_space)
        username = User.objects.get(username = username,name_space = name_space)
        topic = Topic.objects.get(id=topic)
        image = None

        try:
            with transaction.atomic():
                DocumentObject.objects.get_or_create(document_id=document, language=document.language, image=image,
                                                     points=points)
                cursor = connection.cursor()

                cursor.execute("""UPDATE annotate_object SET points = %s, insertion_time = %s WHERE
                username = %s and name_space = %s and document_id = %s and language = %s and topic_id = %s and points = %s""",
                               [points,datetime.now(),username.username,name_space.name_space,document.document_id,document.language,topic.id,points_prev])



        except Exception as e:
            print(e)
            return JsonResponse({'points': []})

        finally:

            ob = AnnotateObject.objects.filter(username=username, name_space=name_space, document_id=document,
                                               topic_id=topic).order_by('-insertion_time')
            if ob.exists():
                points = []
                values = []
                for o in ob:
                    points.append(o.points)
                    val = {}
                    for label in labels:
                        val[label.label_id] = None
                        annotations = AnnotateObjectLabel.objects.filter(username=username, name_space=name_space,
                                                                         points=o.points,
                                                                         document_id=document, label=label.label,
                                                                         topic_id=topic)
                        for a in annotations:
                            val[a.label_id] = int(a.grade)
                    values.append(val)

                return JsonResponse({'points': points, 'values': values})
            return JsonResponse({'points': [], 'values': []})

    if request.method == 'DELETE':
        body_json = json.loads(request.body)
        path = body_json['points']
        document = request.session.get('document',None)
        topic = request.session.get('topic', None)
        username = request.session.get('username', None)
        name_space = request.session.get('name_space', None)

        if None in [name_space, username, topic, document]:
            return HttpResponse(status = 500)
        try:
            document = Document.objects.get(document_id = document)
            name_space = NameSpace.objects.get(name_space = name_space)
            username = User.objects.get(username = username,name_space = name_space)
            topic = Topic.objects.get(id=topic)
            obj = AnnotateObject.objects.filter(points=path,username = username, name_space = name_space, document_id = document, topic_id = topic)
            obj.delete()
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)
        finally:

            ob = AnnotateObject.objects.filter(username=username, name_space=name_space, document_id=document,
                                               topic_id=topic).order_by('-insertion_time')
            if ob.exists():
                points = []
                values = []
                for o in ob:
                    points.append(o.points)
                    val = {}
                    for label in labels:
                        val[label.label_id] = None
                        annotations = AnnotateObjectLabel.objects.filter(username=username, name_space=name_space,
                                                                         points=o.points,
                                                                         document_id=document, label=label.label,
                                                                         topic_id=topic)
                        for a in annotations:
                            val[a.label_id] = int(a.grade)
                    values.append(val)

                return JsonResponse({'points': points, 'values': values})
            return JsonResponse({'points': [], 'values': []})
    return HttpResponse(status = 200)
def mentions(request, type=None):
    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    topic = request.session['topic']
    if request.method == 'GET' and type == None:
        username = request.session['username']
        name_space = request.session['name_space']
        if request.GET.get('user', None) is not None:
            username = request.GET.get('user', None)
        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)

        language = request.session['language']
        document = request.session['document']
        json_mentions = {}

        json_mentions['mentions'] = generate_mentions_list(username, name_space, document, language,topic)
        #json_mentions['mentions_splitted'] = generate_mentions_list(username, name_space, document, language,topic)

        # print(json_mentions)
        return JsonResponse(json_mentions, safe=False)

    # elif request.method == 'GET' and type == 'label':
    #     collection = request.session['collection']
    #     collection = Collection.objects.get(collection_id=collection)
    #     start = request.GET.get('start',None)
    #     position = request.GET.get('position',None)
    #     comment = ''
    #     stop = request.GET.get('stop',None)
    #     name_space = NameSpace.objects.get(name_space=name_space)
    #     document = Document.objects.get(document_id = document)
    #     user = User.objects.get(username=username, name_space=name_space)
    #     start, stop = return_start_stop_for_backend(int(start),int(stop),position, document.document_content)
    #     mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
    #                                   stop=stop)
    #
    #     ann = AnnotatePassage.objects.filter(start=mention, stop=stop, username = user, document_id=document, language=language)
    #     json_resp = {}
    #     labels = CollectionHasLabel.objects.filter(passage_annotation = True,collection_id = collection)
    #     for l in labels:
    #         json_resp[l.name] = None
    #     for annotation in ann:
    #         json_resp[ann.label.name] = ann.grade
    #     return JsonResponse(json_resp)



    elif request.method == 'GET' and type == 'comment':
        start = request.GET.get('start',None)
        position = request.GET.get('position',None)
        comment = ''
        stop = request.GET.get('stop',None)
        name_space = NameSpace.objects.get(name_space=name_space)
        document = Document.objects.get(document_id = document)
        topic = Topic.objects.get(id = request.session['topic'])
        user = User.objects.get(username=username, name_space=name_space)
        start, stop = return_start_stop_for_backend(int(start),int(stop),position, document.document_content)
        mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                      stop=stop)
        ann = Annotate.objects.filter(start=mention, stop=stop,topic_id=topic, username = user, document_id=document, language=language)
        if ann.exists():
            ann = ann.first()
            if ann.comment is not None:
                comment = ann.comment


        json_resp = {'comment':comment}
        return JsonResponse(json_resp)


    elif request.method == 'GET' and type == 'info':
        json_to_ret = {}
        json_to_ret['concepts'] = []
        json_to_ret['tags'] = []

        mention_requested = request.GET.get('mention', None)
        username = request.session.get('username', None)
        name_space = request.session.get('name_space', None)
        doc_id = request.session.get('document', None)
        document = Document.objects.get(document_id=doc_id, language=request.session['language'])
        language = request.session.get('language', None)
        name_space = NameSpace.objects.get(name_space=name_space)
        username = User.objects.get(username=username, name_space=name_space)
        if mention_requested:
            mention_requested = json.loads(mention_requested)
            start, stop = return_start_stop_for_backend(mention_requested['start'], mention_requested['stop'],
                                                        mention_requested['position'], document.document_content)
            mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                          stop=stop)
            json_to_ret['text'] = mention.mention_text
            annotation_all = Annotate.objects.filter(start=mention, stop=stop, document_id=document, language=language)
            json_to_ret['annotators_count'] = annotation_all.count()

            annotation_user = Annotate.objects.filter(username=username, name_space=name_space, start=mention,
                                                      stop=stop,
                                                      document_id=document, language=language)
            json_to_ret['last_update'] = '.'.join(str(annotation_user.first().insertion_time).split('.')[:-1])

            association_user = Associate.objects.filter(start=mention, username=username, name_space=name_space,
                                                        stop=stop, document_id=document, language=language).order_by(
                '-insertion_time')
            association_tags_user = AssociateTag.objects.filter(start=mention, username=username, name_space=name_space,
                                                                stop=stop, document_id=document,
                                                                language=language).order_by(
                '-insertion_time')

            for a in association_user:
                json_c = {}
                concept = a.concept_url
                json_c['concept_url'] = concept.concept_url
                area = a.name
                json_c['concept_area'] = area.name

                name = concept.concept_name
                json_c['concept_name'] = name
                json_c['last_update'] = '.'.join(str(a.insertion_time).split('.')[:-1])
                association_all = Associate.objects.filter(start=mention, stop=stop, document_id=document,
                                                           language=language, concept_url=concept)
                json_c['annotators_count'] = association_all.count()
                json_to_ret['concepts'].append(json_c)

            for a in association_tags_user:
                json_c = {}
                area = a.name
                json_c['tag'] = {}
                json_c['tag']['area'] = area.name

                json_c['last_update'] = '.'.join(str(a.insertion_time).split('.')[:-1])
                association_all = AssociateTag.objects.filter(start=mention, stop=stop, document_id=document,
                                                              language=language, name=area)
                json_c['annotators_count'] = association_all.count()
                json_to_ret['tags'].append(json_c)

            return JsonResponse(json_to_ret)

    elif request.method == 'POST' and type == 'annotate_all':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        json_body = json.loads(request.body)
        start = json_body['start']
        stop = json_body['stop']
        position = json_body['position']
        mention_text = json_body['mention_text']
        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
        # print(start,stop)
        mention_s = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
        associate = Associate.objects.filter(start=mention_s, stop=stop,topic_id=topic, username=user, name_space=name_space,
                                             document_id=document)
        associate_tag = AssociateTag.objects.filter(start=mention_s, stop=stop,topic_id=topic, username=user, name_space=name_space,
                                                    document_id=document)
        with transaction.atomic():
            json_start_stop = from_start_stop_foreach_key(document.document_content)
            keys = json_start_stop['key']
            values = json_start_stop['value']
            keys = list(keys.values())
            values = list(values.values())
            lista_final = keys + values
            for k in lista_final:
                key_text = k['text']
                position = k['position']
                matches = re.finditer(re.escape(mention_text), key_text)
                indices = [match.start() for match in matches]
                for ind in indices:
                    start = ind
                    stop = start + len(mention_text) - 1
                    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                    if not Mention.objects.filter(start=start, stop=stop, document_id=document,topic_id=topic,
                                                  language=language).exists():
                        Mention.objects.create(start=start, stop=stop, document_id=document, mention_text=mention_text,
                                               language=language)
                    mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
                    if mention != mention_s:
                        if not Annotate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,topic_id=topic,
                                                       document_id=document, language=language).exists():
                            Annotate.objects.create(start=mention, stop=stop, username=user, name_space=name_space,
                                                    document_id=document,topic_id=topic,
                                                    language=language, insertion_time=Now())
                            update_gt(user, name_space, document, language,topic)
                        if Associate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,topic_id=topic,
                                                    document_id=document, language=language).exists():
                            Associate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,topic_id=topic,
                                                     document_id=document, language=language).delete()
                        for a in associate:
                            Associate.objects.create(start=mention, stop=stop, username=user, name_space=name_space,
                                                     document_id=document, concept_url=a.concept_url, name=a.name,topic_id=topic,
                                                     language=language, insertion_time=Now())
                            update_gt(user, name_space, document, language,topic)
                        if AssociateTag.objects.filter(start=mention, stop=stop, username=user, topic_id=topic,name_space=name_space,
                                                       document_id=document, language=language).exists():
                            AssociateTag.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                                        document_id=document,topic_id=topic, language=language).delete()
                        for a in associate_tag:
                            AssociateTag.objects.create(start=mention, stop=stop, username=user, name_space=name_space,
                                                        document_id=document, name=a.name,topic_id=topic,
                                                        language=language, insertion_time=Now())
                            update_gt(user, name_space, document, language,topic)
            json_to_return = {}
            json_to_return['document'] = create_new_content(document, user,topic)
            json_to_return['mentions'] = generate_mentions_list(username, name_space.name_space,
                                                                document.document_id, language,topic)
            json_to_return['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                             request.session['name_space'],
                                                                             request.session['document'],
                                                                             request.session['language'],request.session['topic'])
            json_to_return['tags'] = generate_tag_list_splitted(request.session['username'],
                                                                request.session['name_space'],
                                                                request.session['document'],
                                                                request.session['language'],request.session['topic'])
            # json_to_return['mentions_splitted'] = generate_mentions_list_splitted(username, name_space.name_space,
            #                                                                       document.document_id, language,topic)

        return JsonResponse(json_to_return)

    elif request.method == 'POST' and type == 'copy':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        json_body = json.loads(request.body)
        mention = json_body['mention']
        json_resp = copy_mention_aux(user, name_space, document, language, mention)
        return JsonResponse(json_resp)

    elif request.method == 'POST' and type == 'comment':
        body_json = json.loads(request.body)
        start = body_json.get('start',None)
        position = body_json.get('position',None)
        comment = body_json.get('comment',None)
        stop = body_json.get('stop',None)
        try:
            name_space = NameSpace.objects.get(name_space=name_space)
            document = Document.objects.get(document_id = document)
            topic = Topic.objects.get(id = request.session['topic'])
            user = User.objects.get(username=username, name_space=name_space)
            start, stop = return_start_stop_for_backend(int(start),int(stop),position, document.document_content)
            mention = Mention.objects.get(document_id=document, language=request.session['language'], start=start,
                                          stop=stop)
            ann = Annotate.objects.filter(start=mention,topic_id=topic, stop=stop, username = user, document_id=document, language=language)
            if ann.exists() and comment is not None:
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE annotate SET comment = %s WHERE username = %s AND document_id = %s AND start = %s AND stop = %s and topic_id = %s""",
                                   [comment, user.username,document.document_id,mention.start,mention.stop,topic.id])

        except Exception as e:
            print(e)
            return HttpResponse(status = 500)
        else:
            return HttpResponse(status = 200)

    elif request.method == 'POST' and type == 'insert':
        username = request.session['username']
        name_space = request.session['name_space']
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=request.session['username'], name_space=name_space)
        try:
            with transaction.atomic():
                document = Document.objects.get(document_id=request.session['document'],
                                                language=request.session['language'])
                json_start_stop = from_start_stop_foreach_key(document.document_content)
                body_json = json.loads(request.body)
                language = document.language
                start = body_json['start']
                mention_text = body_json['mention_text']
                position = body_json['position']
                chiave = 'value' if position.endswith('value') else 'key'
                portion = ''
                for k in json_start_stop[chiave].keys():
                    if k + "_" + chiave == position:
                        portion = json_start_stop[chiave][k]['text']
                        break

                # first: check if the start and the stops from the frontend are correct, otherwise recompute them
                # first check if in that part of text there are other portions with the same text

                occurrences = portion.count(mention_text)
                # se è 1 allora mi fermo
                if occurrences == 1:
                    start = portion.index(mention_text)
                    stop = start + len(mention_text) - 1
                else:
                    # qua gestisco eventuali errori di formattazione del testo
                    matches = re.finditer(re.escape(mention_text), portion)
                    indices = [match.start() for match in matches]
                    closest_number_start = None
                    closest_distance_from_start = None
                    for number in indices:
                        distance = math.fabs(number - start)
                        if closest_distance_from_start is None or distance < closest_distance_from_start:
                            closest_number_start = number
                            closest_distance_from_start = distance

                    start = closest_number_start
                    stop = start + len(mention_text) - 1

                start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)

                if not Mention.objects.filter(start=start, stop=stop, document_id=document, language=language).exists():
                    Mention.objects.create(start=start, stop=stop, document_id=document, mention_text=mention_text,
                                           language=language)

                mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)

                if not Annotate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                               document_id=document, topic_id=topic,language=language).exists():
                    Annotate.objects.create(start=mention, stop=stop, username=user, name_space=name_space,
                                            document_id=document,topic_id=topic,
                                            language=language, insertion_time=Now())
                    update_gt(user, name_space, document, language,topic)

                json_to_return = {}
                json_to_return['document'] = create_new_content(document, user,topic)
                json_to_return['mentions'] = generate_mentions_list(username, name_space.name_space,
                                                                    document.document_id, language,topic.id)
                json_to_return['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                                 request.session['name_space'],
                                                                                 request.session['document'],
                                                                                 request.session['language'],request.session['topic'])
                json_to_return['tags'] = generate_tag_list_splitted(request.session['username'],
                                                                    request.session['name_space'],
                                                                    request.session['document'],
                                                                    request.session['language'],request.session['topic'])
                # json_to_return['mentions_splitted'] = generate_mentions_list_splitted(username, name_space.name_space,
                #                                                                       document.document_id, language,topic.id)

            return JsonResponse(json_to_return)
        except Exception as e:
            print('add mention rollback', e)
            return JsonResponse({'error': e}, status=500)


    elif request.method == 'DELETE':

        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        try:
            with transaction.atomic():
                document = Document.objects.get(document_id=document, language=language)
                # json_start_stop = from_start_stop_foreach_key(document.document_content)
                body_json = json.loads(request.body)
                language = document.language
                topic = request.session['topic']
                topic = Topic.objects.get(id=topic)
                start = body_json['start']
                stop = body_json['stop']
                # print(start, stop)
                #mention_text = body_json['mention_text']
                position = body_json['position']
                start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                # print(start,stop)
                mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
                Annotate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                        document_id=document,topic_id=topic,
                                        language=language).delete()
                Associate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                         document_id=document,topic_id=topic,
                                         language=language).delete()
                AssociateTag.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                            document_id=document,topic_id=topic,
                                            language=language).delete()
                # relationships
                Link.objects.filter(subject_start=mention.start, subject_stop=mention.stop, username=user,
                                    name_space=name_space,topic_id=topic,
                                    subject_document_id=document.document_id,
                                    subject_language=language).delete()
                Link.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop, username=user,
                                    name_space=name_space,topic_id=topic,
                                    subject_document_id=document.document_id,
                                    subject_language=language).delete()
                Link.objects.filter(object_start=mention.start, object_stop=mention.stop, username=user,
                                    name_space=name_space,topic_id=topic,
                                    subject_document_id=document.document_id,
                                    subject_language=language).delete()

                RelationshipObjMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                      name_space=name_space,topic_id=topic,
                                                      document_id=document,
                                                      language=language).delete()

                RelationshipSubjMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                       name_space=name_space,
                                                       document_id=document,topic_id=topic,
                                                       language=language).delete()

                RelationshipPredMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                       name_space=name_space,topic_id=topic,
                                                       document_id=document,
                                                       language=language).delete()

                RelationshipPredConcept.objects.filter(object_start=mention.start, object_stop=mention.stop,
                                                       username=user, name_space=name_space,topic_id=topic,
                                                       subject_document_id=document.document_id,
                                                       subject_language=language).delete()
                RelationshipPredConcept.objects.filter(subject_start=mention.start, subject_stop=mention.stop,
                                                       username=user, name_space=name_space,topic_id=topic,
                                                       subject_document_id=document.document_id,
                                                       subject_language=language).delete()

                RelationshipSubjConcept.objects.filter(object_start=mention.start, object_stop=mention.stop,
                                                       username=user, name_space=name_space,
                                                       object_document_id=document.document_id,topic_id=topic,
                                                       object_language=language).delete()
                RelationshipSubjConcept.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop,
                                                       username=user, name_space=name_space,topic_id=topic,
                                                       object_document_id=document.document_id,
                                                       object_language=language).delete()

                RelationshipObjConcept.objects.filter(subject_start=mention.start, subject_stop=mention.stop,
                                                      username=user, name_space=name_space,topic_id=topic,
                                                      subject_document_id=document.document_id,
                                                      subject_language=language).delete()
                RelationshipObjConcept.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop,
                                                      username=user, name_space=name_space,topic_id=topic,
                                                      subject_document_id=document.document_id,
                                                      subject_language=language).delete()

                # if Annotate.objects.filter(start=mention, stop=stop,document_id=document,language=language).count() == 0:
                #     Mention.objects.filter(start=start, stop=stop, document_id=document,
                #                            language=language).delete()
                update_gt(user, name_space, document, language,topic)
                new_content = create_new_content(document, user,topic)
                json_resp = {}
                json_resp['document'] = new_content
                json_resp['mentions'] = generate_mentions_list(username, name_space.name_space, document.document_id,
                                                               language,topic.id)
                # json_resp['mentions_splitted'] = generate_mentions_list_splitted(username, name_space.name_space,
                #                                                                  document.document_id, language,topic.id)
                json_resp['concepts'] = generate_associations_list_splitted(username, name_space.name_space,
                                                                            document.document_id, language,topic.id)
                json_resp['tags'] = generate_tag_list_splitted(username, name_space.name_space,
                                                               document.document_id, language,topic.id)
                # print(new_content)
            return JsonResponse(json_resp)
        except Exception as e:
            print('add mention rollback', e)
            return JsonResponse({'error': e}, status=500)


def relationships(request, type=None):
    """This view returns the mentions a user annotated in a document"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    language = request.session['language']
    topic = request.session['topic']

    if request.method == 'GET' and type != 'comment':
        if request.GET.get('user', None) is not None:
            print('relationships user', request.GET.get('user', None))
            username = request.GET.get('user', None)

        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)

        language = request.session['language']
        document = request.session['document']
        json_mentions = {}
        if type is None:
            json_mentions = generate_relationships_list(username, name_space, document, language,topic)

            return JsonResponse(json_mentions, safe=False)



    elif type == 'comment':
        if request.method == "GET":
            index_rel = int(request.GET.get('relationship', None))

            if request.GET.get('user', None) is not None:
                username = request.GET.get('user', None)
            else:
                username = request.session.get('username', None)

            if request.GET.get('name_space', None) is not None:
                name_space = request.GET.get('name_space', None)
            else:
                name_space = request.session.get('name_space', None)
        elif request.method == 'POST':
            body_js = json.loads(request.body)
            index_rel = int(body_js.get('relationship', None))
            comment = body_js.get('comment', None)

        name_space = NameSpace.objects.get(name_space=name_space)
        username = User.objects.get(username=username,name_space=name_space)
        document = request.session['document']
        document = Document.objects.get(document_id=document)
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)
        relationship = generate_relationships_list(username.username, name_space.name_space, document.document_id, language,topic.id)
        relationship = relationship[index_rel]

        rel = None
        if relationship['subject']['mention'] != {}:
            start,stop = return_start_stop_for_backend(relationship['subject']['mention']['start'],relationship['subject']['mention']['stop'],relationship['subject']['mention']['position'],document.document_content)
            relationship['subject']['mention']['start'] = start
            relationship['subject']['mention']['stop'] = stop

        if relationship['object']['mention'] != {}:
            start,stop = return_start_stop_for_backend(relationship['object']['mention']['start'],relationship['object']['mention']['stop'],relationship['object']['mention']['position'],document.document_content)
            relationship['object']['mention']['start'] = start
            relationship['object']['mention']['stop'] = stop

        if relationship['predicate']['mention'] != {}:
            start,stop = return_start_stop_for_backend(relationship['predicate']['mention']['start'],relationship['predicate']['mention']['stop'],relationship['predicate']['mention']['position'],document.document_content)
            relationship['predicate']['mention']['start'] = start
            relationship['predicate']['mention']['stop'] = stop
        #mmm

        if relationship['subject']['mention'] != {} and relationship['predicate']['mention'] != {} and relationship['object']['mention'] != {}:
            subject_mention = Mention.objects.get(subject_document_id = document,start = int(relationship['subject']['mention']['start']), stop = int(relationship['subject']['mention']['stop']))
            object_mention = Mention.objects.get(document_id = document,start = relationship['object']['mention']['start'], stop = relationship['object']['mention']['stop'])
            predicate_mention = Mention.objects.get(document_id = document,start = relationship['predicate']['mention']['start'], stop = relationship['predicate']['mention']['stop'])
            rel = Link.objects.filter(subject_document_id = document.document_id,subject_start = subject_mention.start,subject_stop = subject_mention.stop,
                                      predicate_start = predicate_mention.start, predicate_stop = predicate_mention.stop, object_start = object_mention.start, object_stop = object_mention.stop,
                                      username = username, name_space = name_space, topic_id = topic)
        # mcc
        if relationship['subject']['mention'] != {} and relationship['predicate']['mention'] == {} and relationship['object']['mention'] == {}:
            subject_mention = Mention.objects.get(document_id = document,start = relationship['subject']['mention']['start'], stop = relationship['subject']['mention']['stop'])
            predicate_concept = Concept.objects.get(concept_url = relationship['subject']['concept']['concept_url'])
            predicate_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            object_concept = Concept.objects.get(concept_url=relationship['object']['concept']['concept_url'])
            object_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            rel = RelationshipSubjMention.objects.filter(document_id = document.document_id,start = subject_mention,stop = subject_mention.stop,
                                      predicate_concept_url = predicate_concept.concept_url, predicate_name = predicate_area.name, object_concept_url = object_concept.concept_url, object_name = object_area.name,
                                      username = username, name_space = name_space, topic_id = topic)
        # mcm
        if relationship['subject']['mention'] != {} and relationship['predicate']['mention'] == {} and relationship['object']['mention'] != {}:
            subject_mention = Mention.objects.get(document_id=document,
                                                  start=relationship['subject']['mention']['start'],
                                                  stop=relationship['subject']['mention']['stop'])
            object_mention = Mention.objects.get(document_id = document,start = relationship['obbject']['mention']['start'], stop = relationship['obbject']['mention']['stop'])
            predicate_concept = Concept.objects.get(concept_url = relationship['subject']['concept']['concept_url'])
            predicate_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            rel = RelationshipPredConcept.objects.filter(document_id = document.document_id,subject_start = subject_mention.start,subject_stop = subject_mention.stop,
                                      concept_url = predicate_concept, name = predicate_area, object_start = object_mention.start, object_stop = object_mention.stop,
                                      username = username, name_space = name_space, topic_id = topic)

            # mmc
        if relationship['subject']['mention'] != {} and relationship['predicate']['mention'] != {} and relationship['object']['mention'] == {}:
            mentions = Mention.objects.filter(document_id = document)
            subject_mention = Mention.objects.get(document_id=document,
                                                  start=int(relationship['subject']['mention']['start']),
                                                  stop=int(relationship['subject']['mention']['stop']))
            predicate_mention = Mention.objects.get(document_id = document,start = relationship['predicate']['mention']['start'], stop = relationship['predicate']['mention']['stop'])
            object_concept = Concept.objects.get(concept_url=relationship['object']['concept']['concept_url'])
            object_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            rel = RelationshipObjConcept.objects.filter(subject_document_id = document.document_id,subject_start = subject_mention.start,subject_stop = subject_mention.stop,
                                      concept_url = object_concept, name = object_area, predicate_start = predicate_mention.start, predicate_stop = predicate_mention.stop,
                                      username = username, name_space = name_space, topic_id = topic)
            # cmm
        if relationship['subject']['mention'] == {} and relationship['predicate']['mention'] != {} and relationship['object']['mention'] != {}:
            predicate_mention = Mention.objects.get(predicate_document_id=document,
                                                    start=relationship['predicate']['mention']['start'],
                                                    stop=relationship['predicate']['mention']['stop'])
            object_mention = Mention.objects.get(document_id = document,start = relationship['object']['mention']['start'], stop = relationship['object']['mention']['stop'])

            subject_concept = Concept.objects.get(concept_url=relationship['subject']['concept']['concept_url'])
            subject_area = SemanticArea.objects.get(name=relationship['subject']['concept']['concept_area'])
            rel = RelationshipSubjConcept.objects.filter(document_id=document.document_id,
                                                        object_start=object_mention.start,
                                                        object_stop=object_mention.stop,
                                                        concept_url=subject_concept, name=subject_area,
                                                        predicate_start=predicate_mention.start,
                                                        predicate_stop=predicate_mention.stop,
                                                        username=username, name_space=name_space, topic_id=topic)
            # ccm
        if relationship['subject']['mention'] == {} and relationship['predicate']['mention'] == {} and relationship['object']['mention'] != {}:
            object_mention = Mention.objects.get(document_id=document, start=relationship['object']['mention']['start'],
                                                 stop=relationship['object']['mention']['stop'])
            predicate_concept = Concept.objects.get(concept_url = relationship['subject']['concept']['concept_url'])
            predicate_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            subject_concept = Concept.objects.get(concept_url=relationship['subject']['concept']['concept_url'])
            subject_area = SemanticArea.objects.get(name=relationship['subject']['concept']['concept_area'])
            rel = RelationshipObjMention.objects.filter(document_id = document.document_id,start = object_mention,stop = object_mention.stop,
                                      predicate_concept_url = predicate_concept.concept_url, predicate_name = predicate_area.name, subject_concept_url = subject_concept.concept_url, subject_name = subject_area.name,
                                      username = username, name_space = name_space, topic_id = topic)

            # cmc
        if relationship['subject']['mention'] == {} and relationship['predicate']['mention'] != {} and relationship['object']['mention'] == {}:
            predicate_mention = Mention.objects.get(document_id=document, start=relationship['object']['mention']['start'],
                                                 stop=relationship['predicate']['mention']['stop'])
            subject_concept = Concept.objects.get(concept_url=relationship['subject']['concept']['concept_url'])
            subject_area = SemanticArea.objects.get(name=relationship['subject']['concept']['concept_area'])
            object_concept = Concept.objects.get(concept_url=relationship['object']['concept']['concept_url'])
            object_area = SemanticArea.objects.get(name=relationship['object']['concept']['concept_area'])
            rel = RelationshipPredMention.objects.filter(document_id = document.document_id,start = predicate_mention,stop = predicate_mention.stop,
                                      object_concept_url = object_concept.concept_url, object_name = object_area.name, subject_concept_url = subject_concept.concept_url, subject_name = subject_area.name,
                                      username = username, name_space = name_space, topic_id = topic)

        if request.method == 'GET':
            comment = ''
            if rel.exists():
                comment = rel.first().comment
                if comment is None:
                    comment = ''
            return JsonResponse({'comment': comment}, safe=False)

        elif request.method == 'POST':
            comment = body_js.get('comment', None)
            if rel.exists():
                rel = rel.first()
                rel.comment = comment
                rel.save()
                return HttpResponse(status = 200)

    elif request.method == 'POST' and type == 'copy':
        json_body = json.loads(request.body)
        relation = json_body

        subject = relation['subject']
        predicate = relation['predicate']
        object = relation['object']
        user_source = relation['user']

        json_resp = copy_relation_aux(username, name_space, document, language, subject, predicate, object, user_source)
        return JsonResponse(json_resp)

    if request.method == 'POST' and type == 'copy_assertion':
        json_body = json.loads(request.body)
        json_resp = copy_assertion_aux(username, name_space, document, language, json_body)
        return JsonResponse(json_resp)


    elif request.method == 'POST' and type == 'comment':
        username = request.session.get('username', None)
        name_space = request.session.get('name_space', None)

        name_space = NameSpace.objects.get(name_space=name_space)

        language = request.session['language']
        document = request.session['document']
        document = Document.objects.get(document_id=document)
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)
        username = User.objects.get(username=username,name_space=name_space)
        body_json = json.loads(request.body)
        relationship = body_json['relationship']
        comment = body_json['comment']
        try:


            fact = CreateFact.objects.filter(document_id = document,subject_name=relationship['subject_area'],object_name=relationship['object_area'],predicate_name=relationship['predicate_area'],username=username,topic_id=topic,subject_concept_url = relationship['subject_url'],object_concept_url = relationship['object_url'],predicate_concept_url = relationship['predicate_url'])


            if fact.exists() and comment is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE create_fact SET comment = %s WHERE subject_name=%s and object_name=%s and predicate_name = %s and subject_concept_url = %s and object_concept_url = %s and predicate_concept_url=%s and username = %s AND document_id = %s and topic_id=%s""",
                        [comment, relationship['subject_area'], relationship['object_area'], relationship['predicate_area'], relationship['subject_url'], relationship['object_url'], relationship['predicate_url'],  username.username, document.document_id, topic.id])

                return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)


    elif request.method == 'POST' and type == 'insert':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id=topic)
        json_body = json.loads(request.body)
        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']
        try:

            with transaction.atomic():
                insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                                  predicate, collection, document, language, user, name_space,topic)

                update_gt(user, name_space, document, language,topic)

            new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            # new_rel = transform_relationships_list(new_rel, document.document_id, username, name_space.name_space)
            return JsonResponse(new_rel, safe=False)

        except Exception as e:
            return JsonResponse({'error': e})

    elif request.method == 'POST' and type == 'update':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id=topic)
        json_body = json.loads(request.body)
        source_prev = json_body['prev_subject']
        source_mention_prev = source_prev['mention']
        predicate_prev = json_body['prev_predicate']
        predicate_mention_prev = predicate_prev['mention']
        target_prev = json_body['prev_object']
        target_mention_prev = target_prev['mention']

        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']

        try:
            with transaction.atomic():
                delete_old_relationship(source_mention_prev, predicate_mention_prev, target_mention_prev, source_prev,
                                        target_prev, predicate_prev, collection, document, language, user, name_space,topic)
                insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                                  predicate, collection, document, language, user, name_space,topic)

            update_gt(user, name_space, document, language,topic)

            new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            #new_rel = transform_relationships_list(new_rel, document.document_id, username, name_space.name_space)
            return JsonResponse(new_rel, safe=False)

        except Exception as e:
            print(e)
            return JsonResponse({'error': e})



    elif request.method == 'DELETE':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id = request.session['topic'])
        json_body = json.loads(request.body)
        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']
        try:
            with transaction.atomic():
                delete_old_relationship(source_mention, predicate_mention, target_mention, source, target, predicate,
                                        collection, document, language, user, name_space.name_space,topic)
            update_gt(user, name_space, document, language,topic)

            new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            #new_rel = transform_relationships_list(new_rel, document.document_id, username, name_space.name_space)
            return JsonResponse(new_rel, safe=False)
        except Exception as e:
            return JsonResponse({'error': e})



def facts(request, type=None):
    """This view returns the mentions a user annotated in a document"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    language = request.session['language']
    topic = request.session['topic']

    if request.method == 'GET':
        if request.GET.get('user', None) is not None:
            print('relationships user', request.GET.get('user', None))
            username = request.GET.get('user', None)

        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)

        language = request.session['language']
        document = request.session['document']
        json_mentions = {}
        if type is None:
            json_mentions = generate_assertions_list(username, name_space, document, language,topic)

            return JsonResponse(json_mentions, safe=False)


    if request.method == 'GET' and type == 'comment':
        if request.GET.get('user', None) is not None:
            username = request.GET.get('user', None)
        else:
            username = request.session.get('username', None)

        if request.GET.get('name_space', None) is not None:
            name_space = request.GET.get('name_space', None)
        else:
            name_space = request.session.get('name_space', None)

        name_space = NameSpace.objects.get(name_space=name_space)
        username = User.objects.get(username=username,name_space=name_space)
        document = request.session['document']
        document = Document.objects.get(document_id=document)
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)

        subj = request.GET.get('relationship[subject_concept_url]',None)
        obj = request.GET.get('relationship[object_concept_url]',None)
        pred = request.GET.get('relationship[predicate_concept_url]',None)
        subj_area = request.GET.get('relationship[subject_concept_area]',None)
        obj_area = request.GET.get('relationship[object_concept_area]',None)
        pred_area = request.GET.get('relationship[predicate_concept_area]',None)
        comment = ''
        fact = CreateFact.objects.filter(document_id = document,subject_name=subj_area,object_name=obj_area,predicate_name=pred_area,username=username,topic_id=topic,subject_concept_url = subj,object_concept_url = obj,predicate_concept_url = pred)
        if fact.exists():
            comment = fact.first().comment
            if comment is None:
                comment = ''
        return JsonResponse({'comment': comment}, safe=False)


    if request.method == 'POST' and type == 'copy':
        json_body = json.loads(request.body)
        json_resp = copy_assertion_aux(username, name_space, document, language, json_body)
        return JsonResponse(json_resp)


    elif request.method == 'POST' and type == 'comment':
        username = request.session.get('username', None)
        name_space = request.session.get('name_space', None)

        name_space = NameSpace.objects.get(name_space=name_space)

        language = request.session['language']
        document = request.session['document']
        document = Document.objects.get(document_id=document)
        topic = request.session['topic']
        topic = Topic.objects.get(id=topic)
        username = User.objects.get(username=username,name_space=name_space)
        body_json = json.loads(request.body)
        relationship = body_json['relationship']
        comment = body_json['comment']
        try:


            fact = CreateFact.objects.filter(document_id = document,subject_name=relationship['subject_area'],object_name=relationship['object_area'],predicate_name=relationship['predicate_area'],username=username,topic_id=topic,subject_concept_url = relationship['subject_url'],object_concept_url = relationship['object_url'],predicate_concept_url = relationship['predicate_url'])


            if fact.exists() and comment is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE create_fact SET comment = %s WHERE subject_name=%s and object_name=%s and predicate_name = %s and subject_concept_url = %s and object_concept_url = %s and predicate_concept_url=%s and username = %s AND document_id = %s and topic_id=%s""",
                        [comment, relationship['subject_area'], relationship['object_area'], relationship['predicate_area'], relationship['subject_url'], relationship['object_url'], relationship['predicate_url'],  username.username, document.document_id, topic.id])

                return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            return HttpResponse(status = 500)


    elif request.method == 'POST' and type == 'insert':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id=topic)
        json_body = json.loads(request.body)
        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']
        try:

            with transaction.atomic():
                insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                                  predicate, collection, document, language, user, name_space,topic)

                update_gt(user, name_space, document, language,topic)

            new_rel = generate_assertions_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            return JsonResponse(new_rel, safe=False)

        except Exception as e:
            return JsonResponse({'error': e})

    elif request.method == 'POST' and type == 'update':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id=topic)
        json_body = json.loads(request.body)
        source_prev = json_body['prev_subject']
        source_mention_prev = source_prev['mention']
        predicate_prev = json_body['prev_predicate']
        predicate_mention_prev = predicate_prev['mention']
        target_prev = json_body['prev_object']
        target_mention_prev = target_prev['mention']

        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']

        try:
            with transaction.atomic():
                delete_old_relationship(source_mention_prev, predicate_mention_prev, target_mention_prev, source_prev,
                                        target_prev, predicate_prev, collection, document, language, user, name_space,topic)
                insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                                  predicate, collection, document, language, user, name_space,topic)

            update_gt(user, name_space, document, language,topic)

            new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            return JsonResponse(new_rel, safe=False)

        except Exception as e:
            print(e)
            return JsonResponse({'error': e})



    elif request.method == 'DELETE':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        topic = Topic.objects.get(id = request.session['topic'])
        json_body = json.loads(request.body)
        source = json_body['source']
        source_mention = source['mention']
        predicate = json_body['predicate']
        predicate_mention = predicate['mention']
        target = json_body['target']
        target_mention = target['mention']
        try:
            with transaction.atomic():
                delete_old_relationship(source_mention, predicate_mention, target_mention, source, target, predicate,
                                        collection, document, language, user, name_space.name_space,topic)
            update_gt(user, name_space, document, language,topic)

            new_rel = generate_assertions_list(user.username, name_space.name_space, document.document_id,
                                                  document.language,topic.id)
            return JsonResponse(new_rel, safe=False)
        except Exception as e:
            return JsonResponse({'error': e})

def get_mentions(request):
    """This view returns the mentions a user annotated in a document"""

    username = request.session['username']
    name_space = request.session['name_space']
    if request.GET.get('user', None) is not None:
        username = request.GET.get('user', None)
    if request.GET.get('name_space', None) is not None:
        name_space = request.GET.get('name_space', None)

    language = request.session['language']
    document = request.session['document']
    json_mentions = {}

    json_mentions['mentions'] = generate_mentions_list(username, name_space, document, language,topic)
    # json_mentions['mentions_splitted'] = generate_mentions_list(username, name_space, document, language,topic)

    # print(json_mentions)
    return JsonResponse(json_mentions, safe=False)


def get_concepts(request):
    """This view returns the concepts a user annotated in a document"""

    username = request.session['username']
    name_space = request.session['name_space']
    if request.GET.get('user', None) is not None:
        username = request.GET.get('user', None)
    if request.GET.get('name_space', None) is not None:
        name_space = request.GET.get('name_space', None)

    language = request.session['language']
    document = request.session['document']
    topic = request.session['topic']

    json_mentions = generate_associations_list_splitted(username, name_space, document, language,topic)

    # print(json_mentions)
    return JsonResponse(json_mentions, safe=False)


def get_concepts_full(request):
    """This view returns the concepts a user annotated in a document. NOT SPLITTED"""

    username = request.session['username']
    name_space = request.session['name_space']
    if request.GET.get('user', None) is not None:
        username = request.GET.get('user', None)
    if request.GET.get('name_space', None) is not None:
        name_space = request.GET.get('name_space', None)

    language = request.session['language']
    document = request.session['document']
    topic = request.session['topic']

    json_mentions = generate_associations_list(username, name_space, document, language,topic)

    return JsonResponse(json_mentions, safe=False)


def pending_invitations(request):
    """This view returns the number of pending invitations of collections: those such that a user has not accepted yet"""

    username = request.session['username']
    name_space = request.session['name_space']
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)

    sharecollpending = ShareCollection.objects.filter(username=user, name_space=name_space, status='invited')
    json_r = {}
    json_r['count'] = sharecollpending.count()
    json_r['id'] = [x.collection_id_id for x in sharecollpending]
    return JsonResponse(json_r)


def delete_relationship(request):
    """This view deletes a single relationship"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    language = request.session['language']
    topic = request.session['topic']

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    topic = Topic.objects.get(id = topic)
    json_body = json.loads(request.body)
    to_up = False
    source = json_body['source']
    source_mention = source['mention']
    predicate = json_body['predicate']
    predicate_mention = predicate['mention']
    target = json_body['target']
    target_mention = target['mention']
    topic = request.session['topic']
    try:
        with transaction.atomic():
            delete_old_relationship(source_mention, predicate_mention, target_mention, source, target, predicate,
                                    collection, document, language, user, name_space)
        update_gt(user, name_space, document, language,topic)

        new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                              document.language,topic.id)
        #new_rel = transform_relationships_list(new_rel, document.document_id, username, name_space)
        return JsonResponse(new_rel, safe=False)
    except Exception as e:
        return JsonResponse({'error': e})


def update_relationship(request):
    """Update a relationship"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    language = request.session['language']

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    # collection = Collection.objects.get(collection_id = collection)
    json_body = json.loads(request.body)
    to_up = False
    source_prev = json_body['prev_subject']
    source_mention_prev = source_prev['mention']
    predicate_prev = json_body['prev_predicate']
    predicate_mention_prev = predicate_prev['mention']
    target_prev = json_body['prev_object']
    target_mention_prev = target_prev['mention']

    source = json_body['source']
    source_mention = source['mention']
    predicate = json_body['predicate']
    predicate_mention = predicate['mention']
    target = json_body['target']
    target_mention = target['mention']
    topic = request.session['topic']
    topic = Topic.objects.get(id=topic)

    try:
        with transaction.atomic():
            delete_old_relationship(source_mention_prev, predicate_mention_prev, target_mention_prev, source_prev,
                                    target_prev, predicate_prev, collection, document, language, user, name_space)
            insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                              predicate, collection, document, language, user, name_space,topic)

        update_gt(user, name_space, document, language,topic)

        new_rel = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                              document.language,topic.id)
        #new_rel = transform_relationships_list(new_rel, document.document_id, username, name_space)
        return JsonResponse(new_rel, safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({'error': e})


def add_relationship(request):
    """This view allows to add a relationship in the database"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    language = request.session['language']

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    # collection = Collection.objects.get(collection_id = collection)
    json_body = json.loads(request.body)
    to_up = False
    source = json_body['source']
    source_mention = source['mention']
    predicate = json_body['predicate']
    predicate_mention = predicate['mention']
    target = json_body['target']
    target_mention = target['mention']
    topic = request.session['topic']
    topic = Topic.objects.get(id=topic)

    try:
        with transaction.atomic():
            insert_new_relationship_if_exists(source_mention, predicate_mention, target_mention, source, target,
                                              predicate, collection, document, language, user, name_space,topic)

        if to_up:
            update_gt(user, name_space, document, language,topic)

        new_rel_list = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                   document.language,topic.id)
        #new_rel = transform_relationships_list(new_rel_list, document.document_id, username, name_space)
        return JsonResponse(new_rel_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': e})


def add_new_concepts_in_batch(request):
    """This view allows to upload a file with a set of new concepts"""

    username = request.session['username']
    name_space = request.session['name_space']
    collection = request.session['collection']

    files = request.FILES.items()
    json_resp = {'msg': 'ok'}
    try:
        for file, filename in files:
            if filename.endswith('json'):
                upload_json_concepts(file, name_space, username, collection)
            elif filename.endswith('csv'):
                upload_csv_concepts(file, name_space, username, collection)
        return JsonResponse(json_resp)
    except Exception as e:
        json_resp = {'error': e}
        JsonResponse(json_resp)


def add_mentions(request):
    """This view allows to add a mention in the database"""

    username = request.session['username']
    name_space = request.session['name_space']
    name_space = NameSpace.objects.get(name_space=name_space)
    topic = request.session['topic']
    topic = Topic.objects.get(id=topic)
    user = User.objects.get(username=request.session['username'], name_space=name_space)
    try:
        with transaction.atomic():
            document = Document.objects.get(document_id=request.session['document'],
                                            language=request.session['language'])
            body_json = json.loads(request.body)
            language = document.language
            start = body_json['start']
            stop = body_json['stop'] - 1  # il frontend mi ritorna un indice di troppo
            mention_text = body_json['mention_text']
            position = body_json['position']

            start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
            # print(start,stop)
            m = Mention.objects.filter(start=start, stop=stop, document_id=document, language=language).first()

            if not Mention.objects.filter(start=start, stop=stop, document_id=document, language=language).exists():
                Mention.objects.create(start=start, stop=stop, document_id=document, mention_text=mention_text,
                                       language=language)

            mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)

            if not Annotate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,topic_id=topic,
                                           document_id=document, language=language).exists():
                Annotate.objects.create(start=mention, stop=stop, username=user, name_space=name_space,
                                        document_id=document,topic_id=topic,
                                        language=language, insertion_time=Now())
                update_gt(user, name_space, document, language,topic)

            json_to_return = {}
            json_to_return['document'] = create_new_content(document, user,topic)
            json_to_return['mentions'] = generate_mentions_list(username, name_space.name_space, document.document_id,
                                                                language,topic.id)
            json_to_return['concepts'] = generate_associations_list_splitted(request.session['username'],
                                                                             request.session['name_space'],
                                                                             request.session['document'],
                                                                             request.session['language'],request.session['topic'])
            json_to_return['tags'] = generate_tag_list_splitted(request.session['username'],
                                                                request.session['name_space'],
                                                                request.session['document'],
                                                                request.session['language'],request.session['topic'])
            # json_to_return['mentions_splitted'] = generate_mentions_list_splitted(username, name_space.name_space,
            #                                                                       document.document_id, language,topic.id)

        return JsonResponse(json_to_return)
    except Exception as e:
        print('add mention rollback', e)
        return JsonResponse({'error': e}, status=500)


def delete_label(request):
    """This view removed a label"""

    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    user = User.objects.get(username=username, name_space=name_space)
    body_json = json.loads(request.body)
    language = document.language
    label = body_json['label']
    label = Label.objects.get(name=label)
    try:
        with transaction.atomic():
            AnnotateLabel.objects.filter(username=user, document_id=document, language=language, label=label).delete()

            update_gt(user, name_space, document, language,topic)

            return JsonResponse({'msg': 'ok'})

    except Exception as e:
        print(e)
        return JsonResponse({'error': e})


def delete_concept(request):
    """Delete a single concept associated to a mention"""

    body_json = json.loads(request.body)
    json_resp = {'msg': 'ok'}

    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    mentions_list = generate_mentions_list(username, name_space, document, request.session['language'])

    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    user = User.objects.get(username=username, name_space=name_space)
    mention_js = body_json['mention']
    start = mention_js['start']
    stop = mention_js['stop']
    position = mention_js['id']
    position = '_'.join(position.split('_')[:-1])
    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
    language = document.language
    mentions_classes = mention_js['mentions'].split()

    start_list = []
    stop_list = []
    start_stop_list = []
    found = False
    # questo pezzo è per l'overlapping: se ho una mention totalmente dentro un'altra, solo in questo caso avrò un concetto associato, se no è associato sempre alla parte non overlapping
    for m in mentions_list:
        pos = m['mentions']
        start = m['start']
        stop = m['stop']
        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
        if pos in mentions_classes:
            # for ss in start_stop_list:
            #     if ss[0] <= start <= ss[1] and ss[0] <= stop <= ss[1]:
            #         found = True
            #         break
            start_stop_list.append([start, stop])

        # if found:
        #     break
    start_stop_list = sorted(start_stop_list, key=lambda x: x[1] - x[0])
    start = start_stop_list[0][0]
    stop = start_stop_list[0][1]
    for i in range(len(start_stop_list) - 1):
        item_i = start_stop_list[i]
        for j in range(i + 1, len(start_stop_list)):
            item_j = start_stop_list[j]
            if item_j[0] <= item_i[0] <= item_j[1] and item_j[0] <= item_i[1] <= item_j[1]:
                start = item_i[0]
                stop = item_i[1]
                found = True
                break
        if found:
            break

    # start = min(start_list)
    # stop = max(stop_list)
    # start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)

    mention = Mention.objects.get(start=start, stop=stop, document_id=document)
    url = body_json['url']
    concept = Concept.objects.get(concept_url=url)
    try:
        with transaction.atomic():
            Associate.objects.filter(concept_url=concept, start=mention, username=user, name_space=name_space,
                                     document_id=document).delete()
            update_gt(user, name_space, document, language,topic)
    except Exception as e:
        json_resp = {'error': e}

    return JsonResponse(json_resp)


def annotate_label(request):
    """This view removed a label"""

    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    user = User.objects.get(username=username, name_space=name_space)
    body_json = json.loads(request.body)
    language = document.language
    label = body_json['label']
    label = Label.objects.get(name=label)
    try:
        with transaction.atomic():
            AnnotateLabel.objects.create(username=user, document_id=document, language=language, label=label,
                                         insertion_time=Now(), name_space=name_space)
            update_gt(user, name_space, document, language,topic)

            return JsonResponse({'msg': 'ok'})

    except Exception as e:
        print(e)
        return JsonResponse({'error': e})


def delete_single_mention(request):
    """This view allows to add a mention in the database"""

    name_space = request.session['name_space']
    username = request.session['username']
    document = request.session['document']
    language = request.session['language']
    topic = request.session['topic']
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    topic = Topic.objects.get(id=topic)
    try:
        with transaction.atomic():
            document = Document.objects.get(document_id=document, language=language)
            body_json = json.loads(request.body)
            language = document.language
            start = body_json['start']
            stop = body_json['stop']

            position = body_json['position']
            start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
            # print(start,stop)
            mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
            Annotate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                    document_id=document,topic_id=topic,
                                    language=language).delete()
            Associate.objects.filter(start=mention, stop=stop, username=user, name_space=name_space,
                                     document_id=document,topic_id=topic,
                                     language=language).delete()

            # relationships
            Link.objects.filter(subject_start=mention.start, subject_stop=mention.stop, username=user,
                                name_space=name_space,topic_id=topic,
                                subject_document_id=document.document_id,
                                subject_language=language).delete()
            Link.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop, username=user,
                                name_space=name_space,topic_id=topic,
                                subject_document_id=document.document_id,
                                subject_language=language).delete()
            Link.objects.filter(object_start=mention.start, object_stop=mention.stop, username=user,
                                name_space=name_space,topic_id=topic,
                                subject_document_id=document.document_id,
                                subject_language=language).delete()

            RelationshipObjMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                  name_space=name_space,topic_id=topic,
                                                  document_id=document,
                                                  language=language).delete()

            RelationshipSubjMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                   name_space=name_space,topic_id=topic,
                                                   document_id=document,
                                                   language=language).delete()

            RelationshipPredMention.objects.filter(start=mention.start, stop=mention.stop, username=user,
                                                   name_space=name_space,topic_id=topic,
                                                   document_id=document,
                                                   language=language).delete()

            RelationshipPredConcept.objects.filter(object_start=mention.start, object_stop=mention.stop, username=user,
                                                   name_space=name_space,topic_id=topic,
                                                   subject_document_id=document.document_id,
                                                   subject_language=language).delete()
            RelationshipPredConcept.objects.filter(subject_start=mention.start, subject_stop=mention.stop,
                                                   username=user, name_space=name_space,topic_id=topic,
                                                   subject_document_id=document.document_id,
                                                   subject_language=language).delete()

            RelationshipSubjConcept.objects.filter(object_start=mention.start, object_stop=mention.stop, username=user,
                                                   name_space=name_space,topic_id=topic,
                                                   object_document_id=document.document_id,
                                                   object_language=language).delete()
            RelationshipSubjConcept.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop,
                                                   username=user, name_space=name_space,topic_id=topic,
                                                   object_document_id=document.document_id,
                                                   object_language=language).delete()

            RelationshipObjConcept.objects.filter(subject_start=mention.start, subject_stop=mention.stop, username=user,
                                                  name_space=name_space,topic_id=topic,
                                                  subject_document_id=document.document_id,
                                                  subject_language=language).delete()
            RelationshipObjConcept.objects.filter(predicate_start=mention.start, predicate_stop=mention.stop,
                                                  username=user, name_space=name_space,topic_id=topic,
                                                  subject_document_id=document.document_id,
                                                  subject_language=language).delete()

            update_gt(user, name_space, document, language,topic)
            new_content = create_new_content(document, user,topic)
            json_resp = {}
            json_resp['document'] = new_content
            json_resp['mentions'] = generate_mentions_list(username, name_space.name_space, document.document_id,
                                                           language,topic)
            # json_resp['mentions_splitted'] = generate_mentions_list_splitted(username, name_space.name_space,
            #                                                                  document.document_id, language,topic)
            json_resp['concepts'] = generate_associations_list_splitted(username, name_space.name_space,
                                                                        document.document_id, language,topic)
            json_resp['tags'] = generate_tag_list_splitted(username, name_space.name_space, document.document_id,
                                                           language,topic)
            # print(new_content)
        return JsonResponse(json_resp)
    except Exception as e:
        print('add mention rollback', e)
        return JsonResponse({'error': e}, status=500)


# UTILITIES

def get_collection_languages(request):
    collection = request.GET.get('collection', None)
    if collection is not None:
        collection = Collection.objects.get(collection_id=collection)
        documents = Document.objects.filter(collection_id=collection).values('language').distinct()
        languages = [document['language'] for document in documents]
        json_dict = {}
        json_dict['languages'] = languages
        return JsonResponse(json_dict)


def add_reviewer(request):

    if request.method == 'POST':
        members = json.loads(request.body)['reviewers']
        collection = json.loads(request.body)['collection']
        collection = Collection.objects.filter(collection_id=collection)
        if collection.exists():
            collection = collection.first()
            documents = Document.objects.filter(collection_id=collection)
            doc_per_user = documents.count() // len(members)
            docs_per_user_resto = documents.count() % len(members)
            shared = ShareCollection.objects.filter(collection_id=collection)
            count_members = 0
            already_in_review = []
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        for member in shared:

                            if member.username_id in members:
                                count_members += 1
                                cursor.execute(
                                    """UPDATE share_collection SET reviewer = %s WHERE collection_id = %s AND username = %s""",
                                    [True, collection.collection_id, member.username_id])

                                # a ognuno assegno i suoi più quelli degli altri
                                gts_user = GroundTruthLogFile.objects.filter(document_id__in=documents,username=member.username)
                                already_splitted_user = Split.objects.filter(document_id__in=documents,username=member.username)


                                gts_user = [document.document_id for document in gts_user]
                                already_splitted_user = [document.document_id for document in already_splitted_user]
                                #already_in_review = [document.document_id for document in already_in_review]
                                documents_user = [d for d in documents if d in gts_user or d in already_splitted_user]
                                count_docs_member = doc_per_user if count_members != 1 else (doc_per_user) + docs_per_user_resto
                                documents_not_user = [d for d in documents if d not in documents_user and d not in already_in_review]
                                docs_totale = documents_user + documents_not_user
                                docs_totale = docs_totale[0:count_docs_member]
                                m = member.username
                                docs = docs_totale
                                already_in_review.extend(docs)
                                tuples = [
                                    (collection.collection_id, d.document_id, m.username, m.name_space_id, d.language)
                                    for d
                                    in docs]

                                query = "INSERT INTO split_reviewer (collection_id, document_id, username, name_space, language) VALUES %s"
                                execute_values(cursor, query, tuples)
                                docs = [d.document_id for d in docs]
                                docs_user = [d.document_id for d in documents_user]
                                docs = tuple([d for d in docs if d not in docs_user])
                                # labels
                                cursor.execute("""
                                    INSERT INTO annotate_label (document_id, name_space, username, name, language, insertion_time)
                                        SELECT document_id, name_space, %s, name, language, insertion_time
                                        FROM annotate_label
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])

                                # mentions
                                cursor.execute("""
                                    INSERT INTO annotate (start, stop, document_id, language, username, name_space, insertion_time)
                                        SELECT start, stop, document_id, language, %s, name_space, insertion_time
                                        FROM annotate
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # tags
                                cursor.execute("""
                                    INSERT INTO associate_tag (username, name_space, document_id, language, start, stop, insertion_time, name)
                                        SELECT %s, name_space, document_id, language, start, stop, insertion_time, name
                                        FROM associate_tag
                                        WHERE document_id in %s;
                                                                 """, [member.username_id, docs])
                                # concepts
                                cursor.execute("""
                                    INSERT INTO associate (username, name_space, document_id, language, start, stop, concept_url, insertion_time, name)
                                        SELECT %s, name_space, document_id, language, start, stop, concept_url, insertion_time, name
                                        FROM associate
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # assertions
                                cursor.execute("""
                                    INSERT INTO create_fact (username, name_space, document_id, language, subject_concept_url, object_concept_url, predicate_concept_url, subject_name, object_name, predicate_name, insertion_time)
                                        SELECT %s, name_space, document_id, language, subject_concept_url, object_concept_url, predicate_concept_url, subject_name, object_name, predicate_name, insertion_time
                                        FROM create_fact
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # rel obj concept
                                cursor.execute("""
                                    INSERT INTO relationship_obj_concept (username, name_space, subject_document_id, subject_language, predicate_document_id, predicate_language, subject_start, subject_stop, predicate_start, predicate_stop, concept_url, insertion_time, name)
                                        SELECT 	%s, name_space, subject_document_id, subject_language, predicate_document_id, predicate_language, subject_start, subject_stop, predicate_start, predicate_stop, concept_url, insertion_time, name
                                        FROM relationship_obj_concept
                                        WHERE subject_document_id in %s AND predicate_document_id in %s;
                                     """, [member.username_id, docs, docs])
                                # rel obj mention
                                cursor.execute("""
                                    INSERT INTO relationship_obj_mention (username, name_space, document_id, language, start, stop, predicate_concept_url, subject_concept_url, insertion_time, predicate_name, subject_name)
                                        SELECT %s, name_space, document_id, language, start, stop, predicate_concept_url, subject_concept_url, insertion_time, predicate_name, subject_name
                                        FROM relationship_obj_mention
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # rel sub concept
                                cursor.execute("""
                                    INSERT INTO relationship_subj_concept (	username, name_space, object_document_id, object_language, predicate_document_id, predicate_language, object_start, object_stop, predicate_start, predicate_stop, concept_url, insertion_time, name)
                                        SELECT 	%s, name_space, object_document_id, object_language, predicate_document_id, predicate_language, object_start, object_stop, predicate_start, predicate_stop, concept_url, insertion_time, name
                                        FROM relationship_subj_concept
                                        WHERE object_document_id in %s AND predicate_document_id in %s;
                                     """, [member.username_id, docs, docs])
                                # rel sub mention
                                cursor.execute("""
                                    INSERT INTO relationship_subj_mention (	username, name_space, document_id, language, start, stop, predicate_concept_url, object_concept_url, insertion_time, predicate_name, object_name)
                                    SELECT 	%s, name_space, document_id, language, start, stop, predicate_concept_url, object_concept_url, insertion_time, predicate_name, object_name
                                    FROM relationship_subj_mention
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # rel pred concept
                                cursor.execute("""
                                    INSERT INTO relationship_pred_concept (	username, name_space, subject_document_id, subject_language, object_document_id, object_language, subject_start, subject_stop, object_start, object_stop, concept_url, insertion_time, name)
                                        SELECT %s, name_space, subject_document_id, subject_language, object_document_id, object_language, subject_start, subject_stop, object_start, object_stop, concept_url, insertion_time, name
                                        FROM relationship_pred_concept
                                        WHERE object_document_id in %s AND subject_document_id in %s;
                                     """, [member.username_id, docs, docs])
                                # rel pred mention
                                cursor.execute("""
                                    INSERT INTO relationship_pred_mention (		username, name_space, document_id, language, start, stop, object_concept_url, subject_concept_url, insertion_time, object_name, subject_name)
                                    SELECT 	%s, name_space, document_id, language, start, stop, object_concept_url, subject_concept_url, insertion_time, object_name, subject_name
                                    FROM relationship_pred_mention
                                        WHERE document_id in %s;
                                     """, [member.username_id, docs])
                                # rel all mention
                                cursor.execute("""
                                    INSERT INTO link (username, name_space, subject_document_id, subject_language, subject_start, subject_stop, predicate_document_id, predicate_language, predicate_start, predicate_stop, object_document_id, object_language, object_start, object_stop, insertion_time)
                                        SELECT %s, name_space, subject_document_id, subject_language, subject_start, subject_stop, predicate_document_id, predicate_language, predicate_start, predicate_stop, object_document_id, object_language, object_start, object_stop, insertion_time
                                        FROM link
                                        WHERE subject_document_id in %s and object_document_id in %s and predicate_document_id in %s;
                                     """, [member.username_id, docs, docs, docs])

                    return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=500)
    return HttpResponse(status=500)


def add_admin(request):
    if request.method == 'POST':
        members = json.loads(request.body)['admin']
        collection = json.loads(request.body)['collection']
        collection = Collection.objects.filter(collection_id=collection)
        if collection.exists():
            collection = collection.first()
            shared = ShareCollection.objects.filter(collection_id=collection)
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for member in shared:
                        if member.username_id in members:
                            cursor.execute(
                                """UPDATE share_collection SET admin = %s WHERE collection_id = %s AND username = %s""",
                                [True, collection.collection_id, member.username_id])


            return HttpResponse(status=200)
    return HttpResponse(status=500)

def revise_collection(request):
    collection = json.loads(request.body).get('collection',None)


    if collection and Collection.objects.filter(collection_id=collection).exists() and Collection.objects.get(collection_id=collection).revisor == request.session['username']:
        with transaction.atomic():
            docs = Document.objects.filter(collection_id=collection).values('document_id')
            docs = [d['doc_id'] for d in docs]
            docs = tuple(docs)

            # with connection.cursor() as cursor:
            #     # labels
            #     cursor.execute("""
            #         INSERT INTO annotate_label (document_id, name_space, username, name, language, insertion_time)
            #             SELECT document_id, name_space, %s, name, language, insertion_time
            #             FROM annotate_label
            #             WHERE document_id in %s;
            #          """,[member,docs])
            #
            #     # mentions
            #     cursor.execute("""
            #         INSERT INTO annotate (start, stop, document_id, language, username, name_space, insertion_time)
            #             SELECT start, stop, document_id, language, %s, name_space, insertion_time
            #             FROM annotate
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # tags
            #     cursor.execute("""
            #         INSERT INTO associate_tag (username, name_space, document_id, language, start, stop, insertion_time, name)
            #             SELECT %s, name_space, document_id, language, start, stop, insertion_time, name
            #             FROM associate_tag
            #             WHERE document_id in %s;
            #                                      """, [member, docs])
            #     # concepts
            #     cursor.execute("""
            #         INSERT INTO associate (username, name_space, document_id, language, start, stop, concept_url, insertion_time, name)
            #             SELECT %s, name_space, document_id, language, start, stop, concept_url, insertion_time, name
            #             FROM associate
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # assertions
            #     cursor.execute("""
            #         INSERT INTO create_fact (username, name_space, document_id, language, subject_concept_url, object_concept_url, predicate_concept_url, subject_name, object_name, predicate_name, insertion_time)
            #             SELECT %s, name_space, document_id, language, subject_concept_url, object_concept_url, predicate_concept_url, subject_name, object_name, predicate_name, insertion_time
            #             FROM create_fact
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # rel obj concept
            #     cursor.execute("""
            #         INSERT INTO relationship_obj_concept (username, name_space, subject_document_id, subject_language, predicate_document_id, predicate_language, subject_start, subject_stop, predicate_start, predicate_stop, concept_url, insertion_time, name)
            #             SELECT 	%s, name_space, subject_document_id, subject_language, predicate_document_id, predicate_language, subject_start, subject_stop, predicate_start, predicate_stop, concept_url, insertion_time, name
            #             FROM relationship_obj_concept
            #             WHERE subject_document_id in %s AND predicate_document_id in %s;
            #          """, [member, docs, docs])
            #     # rel obj mention
            #     cursor.execute("""
            #         INSERT INTO relationship_obj_mention (username, name_space, document_id, language, start, stop, predicate_concept_url, subject_concept_url, insertion_time, predicate_name, subject_name)
            #             SELECT %s, name_space, document_id, language, start, stop, predicate_concept_url, subject_concept_url, insertion_time, predicate_name, subject_name
            #             FROM relationship_obj_mention
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # rel sub concept
            #     cursor.execute("""
            #         INSERT INTO relationship_subj_concept (	username, name_space, object_document_id, object_language, predicate_document_id, predicate_language, object_start, object_stop, predicate_start, predicate_stop, concept_url, insertion_time, name)
            #             SELECT 	%s, name_space, object_document_id, object_language, predicate_document_id, predicate_language, object_start, object_stop, predicate_start, predicate_stop, concept_url, insertion_time, name
            #             FROM relationship_subj_concept
            #             WHERE object_document_id in %s AND predicate_document_id in %s;
            #          """, [member, docs, docs])
            #     # rel sub mention
            #     cursor.execute("""
            #         INSERT INTO relationship_subj_mention (	username, name_space, document_id, language, start, stop, predicate_concept_url, object_concept_url, insertion_time, predicate_name, object_name)
            #         SELECT 	%s, name_space, document_id, language, start, stop, predicate_concept_url, object_concept_url, insertion_time, predicate_name, object_name
            #         FROM relationship_subj_mention
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # rel pred concept
            #     cursor.execute("""
            #         INSERT INTO relationship_pred_concept (	username, name_space, subject_document_id, subject_language, object_document_id, object_language, subject_start, subject_stop, object_start, object_stop, concept_url, insertion_time, name)
            #             SELECT %s, name_space, subject_document_id, subject_language, object_document_id, object_language, subject_start, subject_stop, object_start, object_stop, concept_url, insertion_time, name
            #             FROM relationship_pred_concept
            #             WHERE object_document_id in %s AND subject_document_id in %s;
            #          """, [member, docs, docs])
            #     # rel pred mention
            #     cursor.execute("""
            #         INSERT INTO relationship_pred_mention (		username, name_space, document_id, language, start, stop, object_concept_url, subject_concept_url, insertion_time, object_name, subject_name)
            #         SELECT 	%s, name_space, document_id, language, start, stop, object_concept_url, subject_concept_url, insertion_time, object_name, subject_name
            #         FROM relationship_pred_mention
            #             WHERE document_id in %s;
            #          """, [member, docs])
            #     # rel all mention
            #     cursor.execute("""
            #         INSERT INTO link (username, name_space, subject_document_id, subject_language, subject_start, subject_stop, predicate_document_id, predicate_language, predicate_start, predicate_stop, object_document_id, object_language, object_start, object_stop, insertion_time)
            #             SELECT %s, name_space, subject_document_id, subject_language, subject_start, subject_stop, predicate_document_id, predicate_language, predicate_start, predicate_stop, object_document_id, object_language, object_start, object_stop, insertion_time
            #             FROM link
            #             WHERE subject_document_id in %s and object_document_id in %s and predicate_document_id in %s;
            #          """, [member, docs,docs,docs])

        return HttpResponse(status = 200)

    return HttpResponse(status = 500)

def collection_options(request):
    if request.method == 'GET':
        collection = request.GET.get('collection', None)
        if not collection:
            collection = request.session.get('collection', None)
            if collection is None:
                return JsonResponse({'msg':'no collection found'})
        if collection:
            tags = get_tags_collection(collection)
            areas = get_areas_collection(collection)
            collection = Collection.objects.get(collection_id=collection)
            options = collection.options
            if not options:
                options = {}
                keys_options = []
            else:
                keys_options = list(options.keys())
            union = tags + areas
            json_opt = {}
            for k in union:
                if k not in keys_options:
                    options[k] = 'rgba(65, 105, 225, 1)'
                    json_opt[k] = options[k]
                else:
                    json_opt[k] = options[k]

            return JsonResponse(json_opt)

        return HttpResponse(status=500)

    if request.method == 'POST':
        try:
            collection = json.loads(request.body)['collection']
            options = json.loads(request.body)['options']
            collection = Collection.objects.get(collection_id=collection)
            collection.options = options
            collection.save()
            # with connection.cursor() as cursor:
            #     with transaction.atomic():
            #         cursor.execute("UPDATE collection SET options=%s where collection_id=%s",[json.dumps(options),collection])

            return JsonResponse(options)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

    if request.method == 'DELETE':
        try:
            collection = json.loads(request.body)['collection']
            type = json.loads(request.body)['type']
            tags = get_tags_collection(collection)
            areas = get_areas_collection(collection)
            if type == 'tags':
                union = tags
            else:
                union = areas
            collection = Collection.objects.get(collection_id=collection)
            options = collection.options
            if options is None:
                options = {}
            for k in union:
                options[k] = 'rgba(65, 105, 225, 1)'

            collection.options = options
            collection.save()
            # with connection.cursor() as cursor:
            #     with transaction.atomic():
            #         cursor.execute("UPDATE collection SET options=%s where collection_id=%s", [json.dumps(options), collection.collection_id])

            return JsonResponse(options)
        except Exception as e:
            return HttpResponse(status=500)


def get_collection_areas(request):
    """This view return the semantics areas associated to the collection"""

    collection = request.GET.get('collection', None)
    if collection is None:
        collection = request.session.get('collection', None)

    areas = get_areas_collection(collection)
    json_dict = {'areas': areas}
    return JsonResponse(json_dict)

import base64
def get_document_content(request):
    """This view returns the content of the document in json."""

    doc_id = request.GET.get('document_id', None)
    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    username = request.session['username']
    topic = request.session['topic']
    if (request.GET.get('user') is not None):
        username = request.GET.get('user')
    user = User.objects.get(username=username, name_space=name_space)
    if doc_id is not None:
        document = Document.objects.get(document_id=doc_id, language=request.session['language'])
        content = document.document_content
        new_content = {}

        collection = document.collection_id
        if collection.type == 'Image':
            new_content['image'] = base64.b64encode(document.image).decode('utf-8')
        topic = Topic.objects.get(id=topic)
        new_content['mentions'] = create_new_content(document, user,topic)
        new_content['empty'] = content

        return JsonResponse(new_content)


def get_cur_collection_documents(request):
    """This view returns a list of ids of the documents stored in the current collection. A json is returned where for each id is returned if the document has been annotated by the current user"""

    collection = Collection.objects.get(collection_id=request.session['collection'])
    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    user = User.objects.get(username=request.session['username'], name_space=name_space)
    docs = Document.objects.filter(collection_id=collection)

    docs_list = []

    for document in docs:
        gt = GroundTruthLogFile.objects.filter(document_id=document, username=user, name_space=name_space).exists()
        json_doc = {'id': document.document_content['doc_id'], 'hashed_id': document.document_id, 'annotated': gt}
        docs_list.append(json_doc)

    # print(docs_list)

    docs_list = sorted(docs_list, key=lambda x: x['id'])
    # print(docs_list)
    return JsonResponse(docs_list, safe=False)


def get_collections(request):
    """This method returns the list of collections in the database shared by the user. if the GET request contains a parameter collection, it is returned the description of the requested collection"""

    collection_param = request.GET.get('collection', None)

    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    user = User.objects.get(username=request.session['username'], name_space=name_space)
    collections = ShareCollection.objects.filter(username=user)
    json_collections = {}
    json_collections['collections'] = []
    for c in collections:
        cid = c.collection_id_id
        json_boj = {}
        json_boj['type'] = c.status

        c = Collection.objects.get(collection_id=cid)
        batches = Document.objects.filter(collection_id=c).values('batch').annotate(total=Count('batch')).order_by(
            'total')

        json_boj['batch'] = []
        for b in batches:
            j_b = {}
            batch = 'batch ' + str(b['batch'])
            j_b[batch] = b['total']
            json_boj['batch'].append(j_b)

        json_boj['name'] = c.name
        json_boj['id'] = cid
        json_boj['description'] = c.description
        creator = ShareCollection.objects.filter(collection_id=c, creator=True)
        json_boj['creator'] = creator.username_id
        json_boj['name_space'] = creator.username.name_space_id
        json_boj['members'] = []
        time = str(c.insertion_time)
        before_p = time.split('+')
        first_split = before_p[0].split('.')[0]
        time = first_split + '+' + before_p[1]
        json_boj['insertion_time'] = time
        # json_boj['task'] = CollectionHasTask.objects.get(collection_id=c).task_id.name
        # types = CollectionHasTask.objects.filter(collection_id=c)
        # types = [c.annotation_type.name for c in types]
        json_boj['annotation_type'] = c.annotation_type.name
        json_boj['date'] = time.split()[0]
        json_boj['labels'] = []
        json_boj['documents_count'] = (Document.objects.filter(collection_id=cid).count())
        docs = Document.objects.filter(collection_id=cid)
        json_boj['annotations_count'] = (GroundTruthLogFile.objects.filter(document_id__in=docs).distinct('document_id').count())
        json_boj['perc_annotations_all'] = float(
            round((json_boj['annotations_count'] / json_boj['documents_count']) * 100, 2))
        json_boj['user_annotations_count'] = (
            GroundTruthLogFile.objects.filter(username=user, name_space=name_space, document_id__in=docs).count())
        json_boj['perc_annotations_user'] = float(
            round((json_boj['user_annotations_count'] / json_boj['documents_count']) * 100, 2))

        shared_with = ShareCollection.objects.filter(collection_id=c.collection_id)
        for el in shared_with:
            us = User.objects.get(name_space=request.session['name_space'], username=el.username_id)
            if us.username != c.username:
                json_boj['members'].append({'username': us.username, 'profile': us.profile})

        # controllo se sono tutti gli utenti appartengono a un profile esatto
        profiles = User.objects.all().values('profile')
        profiles = [p['profile'] for p in profiles]
        for p in profiles:
            users = User.objects.filter(profile=p)
            new_json_members = [j for j in json_boj['members'] if j['profile'] == p]

            if len(users) == len(new_json_members):
                json_boj['members'] = [j for j in json_boj['members'] if j['profile'] != p]
                # json_boj['members'].append({'username': 'All' + p, 'profile':p})

        has_label = CollectionHasLabel.objects.filter(collection_id=c.collection_id)
        for el in has_label:
            # label = Label.objects.get(name=el.name_id)
            json_boj['labels'].append(el.name_id)
        json_boj['labels'] = list(set(json_boj['labels']))
        json_collections['collections'].append(json_boj)

        if collection_param is not None and collection_param == cid:  # in this case it was reqeusted a specific collection
            return JsonResponse(json_boj)

    json_collections['collections'] = sorted(json_collections['collections'], key=lambda x: x['insertion_time'])
    return JsonResponse(json_collections)


def get_documents_table(request):
    collection = request.GET.get('collection', None)
    collection = Collection.objects.get(collection_id=collection)
    documents = Document.objects.filter(collection_id=collection)
    # mode = NameSpace.objects.get(name_space = request.session['name_space'])
    json_resp = {'documents': []}
    cursor = connection.cursor()

    for document in documents:
        ns = NameSpace.objects.filter(name_space='Human')
        # ns = [namespace.name_space for name_space in ns]
        for name in ns:
            json_doc = {}
            # json_doc[name.name_space] = {}
            json_doc['name_space'] = name.name_space
            if "document_id" in list(document.document_content.keys()):
                json_doc['document_id'] = document.document_content['doc_id']
            else:
                json_doc['document_id'] = document.document_id
            json_doc['document_id_hashed'] = document.document_id
            json_doc['language'] = document.language
            json_doc['batch'] = document.batch
            # content = document.document_content
            # json_doc['title'] = document.document_content['title']
            json_doc['content'] = document.document_content
            json_doc['annotators_list'] = []
            json_doc['annotations'] = GroundTruthLogFile.objects.filter(name_space=name, document_id=document).count()
            gt = GroundTruthLogFile.objects.filter(name_space=name, document_id=document).values('username').distinct()
            for g in gt:
                user = User.objects.get(name_space=name, username=g['username'])
                json_doc['annotators_list'].append(user.username)

            json_doc['annotations'] = GroundTruthLogFile.objects.filter(document_id=document, name_space=name).count()
            json_doc['annotators_list_names'] = (json_doc['annotators_list'])
            json_doc['annotators_list'] = len(json_doc['annotators_list'])
            gts = GroundTruthLogFile.objects.filter(name_space=name, document_id=document).order_by('-insertion_time')
            if (gts.exists()):
                json_doc['last_annotation'] = str(gts.first().insertion_time)
            # json_doc['document_level_annotations_count'] = 0
            # json_doc['mention_level_annotations_count'] = 0
            json_doc['mentions_count'] = Annotate.objects.filter(document_id=document, name_space=name).count()
            json_doc['concepts_count'] = Associate.objects.filter(document_id=document, name_space=name).count()
            json_doc['labels_count'] = AnnotateLabel.objects.filter(document_id=document, name_space=name).count()
            json_doc['relationships_count'] = RelationshipPredConcept.objects.filter(
                subject_document_id=document.document_id,
                name_space=name).count() + RelationshipObjConcept.objects.filter(
                subject_document_id=document.document_id,
                name_space=name).count() + RelationshipSubjConcept.objects.filter(
                object_document_id=document.document_id,
                name_space=name).count() + RelationshipObjMention.objects.filter(document_id=document,
                                                                                 name_space=name).count() + RelationshipSubjMention.objects.filter(
                document_id=document, name_space=name).count() + RelationshipPredMention.objects.filter(
                document_id=document, name_space=name).count() + Link.objects.filter(
                subject_document_id=document.document_id, name_space=name).count()
            json_doc['assertions_count'] = CreateFact.objects.filter(document_id=document, name_space=name).count()
            json_resp['documents'].append(json_doc)

    return JsonResponse(json_resp)


def get_annotation_mentions(request):
    """returns the distinct mentions for the desired document"""

    document = request.GET.get("document", None)
    document = Document.objects.get(document_id=document)
    ns = NameSpace.objects.filter(name_space='Human')
    json_doc = {}

    for name in ns:
        json_doc['name_space'] = name.name_space
        json_doc['mentions'] = []
        annotations = Annotate.objects.filter(document_id=document, name_space=name).order_by('start').values('start',
                                                                                                              'stop').distinct(
            'start', 'stop')
        for annotation in annotations:
            mention = Mention.objects.get(document_id=document, start=annotation['start'], stop=annotation['stop'])
            text = mention.mention_text
            location_in_text = return_start_stop_for_frontend(mention.start, mention.stop, document.document_content)
            if location_in_text['position'].endswith('value'):
                location_in_text = location_in_text['position'].replace('_value', '') + ' - [' + str(
                    location_in_text['start']) + ':' + str(location_in_text['stop']) + ']'
            else:
                location_in_text = location_in_text['position'].replace('_key', '') + '(key) - [' + str(
                    location_in_text['start']) + ':' + str(location_in_text['stop']) + ']'

            count = Annotate.objects.filter(document_id=document, name_space=name, start=mention,
                                            stop=mention.stop).count()
            users = Annotate.objects.filter(document_id=document, name_space=name, start=mention,
                                            stop=mention.stop).values('username').distinct('username')
            users = [u['username'] for u in users]
            json_doc['mentions'].append(
                {'start': annotation['start'], 'stop': annotation['stop'], 'location_in_text': location_in_text,
                 'annotators': users, 'mention_text': text, 'count': count})
    return JsonResponse(json_doc)


def get_annotation_concepts(request):
    """returns the distinct concepts for the desired document"""

    document = request.GET.get("document", None)
    document = Document.objects.get(document_id=document)
    ns = NameSpace.objects.filter(name_space='Human')
    json_doc = {}

    for name in ns:
        json_doc['name_space'] = name.name_space
        json_doc['concepts'] = []
        annotations = Associate.objects.filter(document_id=document, name_space=name).order_by('start', 'stop').values(
            'start', 'concept_url', 'name',
            'stop').distinct(
            'start', 'stop', 'concept_url', 'name')
        for annotation in annotations:
            mention = Mention.objects.get(document_id=document, start=annotation['start'], stop=annotation['stop'])
            location_in_text = return_start_stop_for_frontend(mention.start, mention.stop, document.document_content)
            if location_in_text['position'].endswith('value'):
                location_in_text = location_in_text['position'].replace('_value', '') + '- [' + str(
                    location_in_text['start']) + ':' + str(location_in_text['stop']) + ']'
            else:
                location_in_text = location_in_text['position'].replace('_key', '') + '(key) - [' + str(
                    location_in_text['start']) + ':' + str(location_in_text['stop']) + ']'

            concept = annotation['concept_url']
            concept = Concept.objects.get(concept_url=concept)
            area = annotation['name']
            area = SemanticArea.objects.get(name=area)
            text = mention.mention_text
            count = Associate.objects.filter(document_id=document, concept_url=concept, name=area, name_space=name,
                                             start=mention, stop=mention.stop).count()
            users = Associate.objects.filter(document_id=document, concept_url=concept, name=area, name_space=name,
                                             start=mention, stop=mention.stop).values('username').distinct('username')
            users = [u['username'] for u in users]
            json_doc['concepts'].append(
                {'start': annotation['start'], 'stop': annotation['stop'], 'mention_text': text,
                 'concept_url': concept.concept_url,
                 'concept_name': concept.concept_name, 'location_in_text': location_in_text, 'annotators': users,
                 'concept_area': area.name, 'count': count})
    return JsonResponse(json_doc)


def get_annotation_labels(request):
    """returns the distinct mentions for the desired document"""

    document = request.GET.get("document", None)
    document = Document.objects.get(document_id=document)
    ns = NameSpace.objects.filter(name_space='Human')
    json_doc = {}

    for name in ns:
        json_doc['name_space'] = name.name_space
        json_doc['labels'] = []
        labels = AnnotateLabel.objects.filter(document_id=document, name_space=name).distinct('label')
        for l in labels:
            count = AnnotateLabel.objects.filter(label=l.label, document_id=document, name_space=name).count()
            label = l.name_id
            json_doc['labels'].append({'label': label, 'count': count})

    return JsonResponse(json_doc)


def get_annotation_assertions(request):
    document = request.GET.get("document", None)
    document = Document.objects.get(document_id=document)
    ns = NameSpace.objects.filter(name_space='Human')
    json_doc = {}
    for name in ns:
        json_doc['name_space'] = name.name_space
        json_doc['assertions'] = []
        annotations = CreateFact.objects.filter(document_id=document, name_space=name.name_space).values(
            'subject_concept_url', 'object_concept_url', 'predicate_concept_url', 'subject_name', 'object_name',
            'predicate_name').distinct('subject_concept_url', 'object_concept_url', 'predicate_concept_url',
                                       'subject_name', 'object_name', 'predicate_name')

        for annotation in annotations:
            subject_concept = Concept.objects.get(concept_url=annotation['subject_concept_url'])
            predicate_concept = Concept.objects.get(concept_url=annotation['predicate_concept_url'])
            object_concept = Concept.objects.get(concept_url=annotation['object_concept_url'])
            subject_area = SemanticArea.objects.get(name=annotation['subject_name'])
            object_area = SemanticArea.objects.get(name=annotation['object_name'])
            predicate_area = SemanticArea.objects.get(name=annotation['predicate_name'])

            count = CreateFact.objects.filter(document_id=document,
                                              subject_concept_url=annotation['subject_concept_url'],
                                              subject_name=annotation['subject_name'],
                                              object_concept_url=annotation['object_concept_url'],
                                              object_name=annotation['object_name'],
                                              predicate_concept_url=annotation['predicate_concept_url'],
                                              predicate_name=annotation['predicate_name']
                                              ).count()
            users = CreateFact.objects.filter(document_id=document,
                                              subject_concept_url=annotation['subject_concept_url'],
                                              subject_name=annotation['subject_name'],
                                              object_concept_url=annotation['object_concept_url'],
                                              object_name=annotation['object_name'],
                                              predicate_concept_url=annotation['predicate_concept_url'],
                                              predicate_name=annotation['predicate_name']
                                              ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['assertions'].append({'count': count,
                                           'annotators': users,
                                           'annotators_count': len(users),
                                           'subject_concept_url': subject_concept.concept_url,
                                           'subject_concept_name': subject_concept.concept_name,
                                           'subject_concept_area': subject_area.name,
                                           'object_concept_url': object_concept.concept_url,
                                           'object_concept_name': object_concept.concept_name,
                                           'object_concept_area': object_area.name,
                                           'predicate_concept_url': predicate_concept.concept_url,
                                           'predicate_concept_name': predicate_concept.concept_name,
                                           'predicate_concept_area': predicate_area.name
                                           })
    return JsonResponse(json_doc)


def get_annotation_relationships(request):
    document = request.GET.get("document", None)
    document = Document.objects.get(document_id=document)
    ns = NameSpace.objects.filter(name_space='Human')
    json_doc = {}
    for name in ns:
        json_doc['name_space'] = name.name_space
        json_doc['relationships'] = []
        annotations = Link.objects.filter(subject_document_id=document.document_id, name_space=name).values(
            'object_start', 'object_stop', 'subject_start', 'subject_stop', 'predicate_start',
            'predicate_stop').distinct('object_start', 'object_stop', 'subject_start', 'subject_stop',
                                       'predicate_start', 'predicate_stop')

        for annotation in annotations:
            subject_mention = Mention.objects.get(document_id=document, start=annotation['subject_start'],
                                                  stop=annotation['subject_stop'])
            js_sub_ret = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop,
                                                        document.document_content)
            subject_location_in_text = js_sub_ret['position']
            if subject_location_in_text.endswith('_value'):
                subject_location_in_text = subject_location_in_text.replace('_value', '')
            else:
                subject_location_in_text = subject_location_in_text.replace('_key', ' (key)')
            predicate_mention = Mention.objects.get(document_id=document, start=annotation['predicate_start'],
                                                    stop=annotation['predicate_stop'])
            js_pred_ret = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop,
                                                         document.document_content)
            predicate_location_in_text = js_pred_ret['position']
            if predicate_location_in_text.endswith('_value'):
                predicate_location_in_text = predicate_location_in_text.replace('_value', '')
            else:
                predicate_location_in_text = predicate_location_in_text.replace('_key', ' (key)')
            object_mention = Mention.objects.get(document_id=document, start=annotation['object_start'],
                                                 stop=annotation['object_stop'])
            js_obj_ret = return_start_stop_for_frontend(object_mention.start, object_mention.stop,
                                                        document.document_content)
            object_location_in_text = js_obj_ret['position']
            if object_location_in_text.endswith('_value'):
                object_location_in_text = object_location_in_text.replace('_value', '')
            else:
                object_location_in_text = object_location_in_text.replace('_key', ' (key)')

            count = Link.objects.filter(subject_document_id=document.document_id, name_space=name,
                                        subject_start=annotation['subject_start'],
                                        subject_stop=annotation['subject_stop'],
                                        object_start=annotation['object_start'],
                                        object_stop=annotation['object_stop'],
                                        predicate_start=annotation['predicate_start'],
                                        predicate_stop=annotation['predicate_stop'],
                                        ).count()
            users = Link.objects.filter(subject_document_id=document.document_id, name_space=name,
                                        subject_start=annotation['subject_start'],
                                        subject_stop=annotation['subject_stop'],
                                        object_start=annotation['object_start'],
                                        object_stop=annotation['object_stop'],
                                        predicate_start=annotation['predicate_start'],
                                        predicate_stop=annotation['predicate_stop'],
                                        ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count,
                                              'annotators': users,
                                              'annotators_count': len(users),
                                              'subject_location_in_text': subject_location_in_text,
                                              'subject_start': js_sub_ret['start'],
                                              'subject_stop': js_sub_ret['stop'],
                                              'subject_mention_text': subject_mention.mention_text,
                                              'object_start': js_obj_ret['start'],
                                              'object_stop': js_obj_ret['stop'],
                                              'object_location_in_text': object_location_in_text,
                                              'predicate_location_in_text': predicate_location_in_text,
                                              'object_mention_text': object_mention.mention_text,
                                              'predicate_start': js_pred_ret['start'],
                                              'predicate_stop': js_pred_ret['stop'],
                                              'predicate_mention_text': predicate_mention.mention_text
                                              })

        annotations = RelationshipSubjConcept.objects.filter(object_document_id=document.document_id,
                                                             name_space=name).values('name', 'concept_url',
                                                                                     'object_start', 'object_stop',
                                                                                     'predicate_start',
                                                                                     'predicate_stop').distinct('name',
                                                                                                                'concept_url',
                                                                                                                'object_start',
                                                                                                                'object_stop',
                                                                                                                'predicate_start',
                                                                                                                'predicate_stop')

        for annotation in annotations:
            concept = Concept.objects.get(concept_url=annotation['concept_url'])
            area = SemanticArea.objects.get(name=annotation['name'])
            predicate_mention = Mention.objects.get(document_id=document, start=annotation['predicate_start'],
                                                    stop=annotation['predicate_stop'])
            object_mention = Mention.objects.get(document_id=document, start=annotation['object_start'],
                                                 stop=annotation['object_stop'])
            js_pred_ret = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop,
                                                         document.document_content)
            js_obj_ret = return_start_stop_for_frontend(object_mention.start, object_mention.stop,
                                                        document.document_content)
            object_location_in_text = js_obj_ret['position']
            if object_location_in_text.endswith('_value'):
                object_location_in_text = object_location_in_text.replace('_value', '')
            else:
                object_location_in_text = object_location_in_text.replace('_key', ' (key)')
            predicate_location_in_text = js_pred_ret['position']
            if predicate_location_in_text.endswith('_value'):
                predicate_location_in_text = predicate_location_in_text.replace('_value', '')
            else:
                predicate_location_in_text = predicate_location_in_text.replace('_key', ' (key)')
            count = RelationshipSubjConcept.objects.filter(object_document_id=document.document_id,
                                                           name_space=name,
                                                           concept_url=concept,
                                                           name=annotation['name'],
                                                           object_start=annotation['object_start'],
                                                           object_stop=annotation['object_stop'],
                                                           predicate_start=annotation['predicate_start'],
                                                           predicate_stop=annotation['predicate_stop'],
                                                           ).count()
            users = RelationshipSubjConcept.objects.filter(object_document_id=document.document_id,
                                                           name_space=name,
                                                           concept_url=concept,
                                                           name=annotation['name'],
                                                           object_start=annotation['object_start'],
                                                           object_stop=annotation['object_stop'],
                                                           predicate_start=annotation['predicate_start'],
                                                           predicate_stop=annotation['predicate_stop'],
                                                           ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count, 'annotators': users, 'annotators_count': len(users),

                                              'subject_concept_url': concept.concept_url,
                                              'subject_concept_area': area.name,
                                              'subject_concept_name': concept.concept_name,
                                              'object_start': js_obj_ret['start'],
                                              'object_stop': js_obj_ret['stop'],
                                              'object_mention_text': object_mention.mention_text,
                                              'predicate_start': js_pred_ret['start'],
                                              'predicate_stop': js_pred_ret['stop'],
                                              'predicate_mention_text': predicate_mention.mention_text,
                                              'predicate_location_in_text': predicate_location_in_text,
                                              'object_location_in_text': object_location_in_text

                                              })

        annotations = RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,
                                                            name_space=name).values('name', 'concept_url',
                                                                                    'subject_start', 'subject_stop',
                                                                                    'predicate_start',
                                                                                    'predicate_stop').distinct('name',
                                                                                                               'concept_url',
                                                                                                               'subject_start',
                                                                                                               'subject_stop',
                                                                                                               'predicate_start',
                                                                                                               'predicate_stop')

        for annotation in annotations:
            concept = Concept.objects.get(concept_url=annotation['concept_url'])
            area = SemanticArea.objects.get(name=annotation['name'])
            predicate_mention = Mention.objects.get(document_id=document, start=annotation['predicate_start'],
                                                    stop=annotation['predicate_stop'])
            subject_mention = Mention.objects.get(document_id=document, start=annotation['subject_start'],
                                                  stop=annotation['subject_stop'])
            js_pred_ret = return_start_stop_for_frontend(predicate_mention.start, predicate_mention.stop,
                                                         document.document_content)
            js_subj_ret = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop,
                                                         document.document_content)
            predicate_location_in_text = js_pred_ret['position']
            if predicate_location_in_text.endswith('_value'):
                predicate_location_in_text = predicate_location_in_text.replace('_value', '')
            else:
                predicate_location_in_text = predicate_location_in_text.replace('_key', ' (key)')
            subject_location_in_text = js_subj_ret['position']
            if subject_location_in_text.endswith('_value'):
                subject_location_in_text = subject_location_in_text.replace('_value', '')
            else:
                subject_location_in_text = subject_location_in_text.replace('_key', ' (key)')
            count = RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,
                                                          name_space=name,
                                                          concept_url=concept,
                                                          name=annotation['name'],
                                                          subject_start=annotation['subject_start'],
                                                          subject_stop=annotation['subject_stop'],
                                                          predicate_start=annotation['predicate_start'],
                                                          predicate_stop=annotation['predicate_stop'],
                                                          ).count()
            users = RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,
                                                          name_space=name,
                                                          concept_url=concept,
                                                          name=annotation['name'],
                                                          subject_start=annotation['subject_start'],
                                                          subject_stop=annotation['subject_stop'],
                                                          predicate_start=annotation['predicate_start'],
                                                          predicate_stop=annotation['predicate_stop'],
                                                          ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count,
                                              'annotators': users,
                                              'annotators_count': len(users),

                                              'object_concept_url': concept.concept_url,
                                              'object_concept_area': area.name,
                                              'object_concept_name': concept.concept_name,
                                              'subject_start': js_subj_ret['start'],
                                              'subject_stop': js_subj_ret['stop'],
                                              'subject_mention_text': subject_mention.mention_text,
                                              'predicate_start': js_pred_ret['start'],
                                              'predicate_stop': js_pred_ret['stop'],
                                              'predicate_mention_text': predicate_mention.mention_text,
                                              'predicate_location_in_text': predicate_location_in_text,
                                              'subject_location_in_text': subject_location_in_text
                                              })

        annotations = RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,
                                                             name_space=name).values('name', 'concept_url',
                                                                                     'subject_start', 'subject_stop',
                                                                                     'object_start',
                                                                                     'object_stop').distinct('name',
                                                                                                             'concept_url',
                                                                                                             'subject_start',
                                                                                                             'subject_stop',
                                                                                                             'object_start',
                                                                                                             'object_stop')
        for annotation in annotations:
            concept = Concept.objects.get(concept_url=annotation['concept_url'])
            area = SemanticArea.objects.get(name=annotation['name'])
            object_mention = Mention.objects.get(document_id=document, start=annotation['object_start'],
                                                 stop=annotation['object_stop'])
            subject_mention = Mention.objects.get(document_id=document, start=annotation['subject_start'],
                                                  stop=annotation['subject_stop'])

            js_obj_ret = return_start_stop_for_frontend(object_mention.start, object_mention.stop,
                                                        document.document_content)
            js_subj_ret = return_start_stop_for_frontend(subject_mention.start, subject_mention.stop,
                                                         document.document_content)

            object_location_in_text = js_obj_ret['position']
            if object_location_in_text.endswith('_value'):
                object_location_in_text = object_location_in_text.replace('_value', '')
            else:
                object_location_in_text = object_location_in_text.replace('_key', ' (key)')
            subject_location_in_text = js_subj_ret['position']
            if subject_location_in_text.endswith('_value'):
                subject_location_in_text = subject_location_in_text.replace('_value', '')
            else:
                subject_location_in_text = subject_location_in_text.replace('_key', ' (key)')
            count = RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,
                                                           name_space=name,
                                                           concept_url=concept,
                                                           name=annotation['name'],
                                                           subject_start=annotation['subject_start'],
                                                           subject_stop=annotation['subject_stop'],
                                                           object_start=annotation['object_start'],
                                                           object_stop=annotation['object_stop'],
                                                           ).count()

            users = RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,
                                                           name_space=name,
                                                           concept_url=concept,
                                                           name=annotation['name'],
                                                           subject_start=annotation['subject_start'],
                                                           subject_stop=annotation['subject_stop'],
                                                           object_start=annotation['object_start'],
                                                           object_stop=annotation['object_stop'],
                                                           ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count, 'annotators': users, 'annotators_count': len(users),

                                              'predicate_concept_url': concept.concept_url,
                                              'predicate_concept_area': area.name,
                                              'predicate_concept_name': concept.concept_name,
                                              'subject_start': js_subj_ret['start'],
                                              'subject_stop': js_subj_ret['stop'],
                                              'subject_mention_text': subject_mention.mention_text,
                                              'object_start': js_obj_ret['start'],
                                              'object_stop': js_obj_ret['stop'],
                                              'object_mention_text': object_mention.mention_text,
                                              'subject_location_in_text': subject_location_in_text,
                                              'object_location_in_text': object_location_in_text
                                              })

        annotations = RelationshipSubjMention.objects.filter(document_id=document, name_space=name).values(
            'object_concept_url', 'start', 'stop', 'predicate_concept_url', 'object_name', 'predicate_name').distinct(
            'object_concept_url', 'start', 'stop', 'predicate_concept_url', 'object_name', 'predicate_name')

        for annotation in annotations:
            mention = Mention.objects.get(document_id=document, start=annotation['start'], stop=annotation['stop'])
            js_ret = return_start_stop_for_frontend(mention.start, mention.stop, document.document_content)
            predicate_concept = Concept.objects.get(concept_url=annotation['predicate_concept_url'])
            object_concept = Concept.objects.get(concept_url=annotation['object_concept_url'])
            object_area = SemanticArea.objects.get(name=annotation['object_name'])
            predicate_area = SemanticArea.objects.get(name=annotation['predicate_name'])
            subject_location_in_text = js_ret['position']
            if subject_location_in_text.endswith('_value'):
                subject_location_in_text = subject_location_in_text.replace('_value', '')
            else:
                subject_location_in_text = subject_location_in_text.replace('_key', ' (key)')
            count = RelationshipSubjMention.objects.filter(document_id=document,
                                                           start=mention, stop=mention.stop,
                                                           object_concept_url=annotation['object_concept_url'],
                                                           object_name=annotation['object_name'],
                                                           predicate_concept_url=annotation['predicate_concept_url'],
                                                           predicate_name=annotation['predicate_name']
                                                           ).count()
            users = RelationshipSubjMention.objects.filter(document_id=document,
                                                           start=mention, stop=mention.stop,
                                                           object_concept_url=annotation['object_concept_url'],
                                                           object_name=annotation['object_name'],
                                                           predicate_concept_url=annotation['predicate_concept_url'],
                                                           predicate_name=annotation['predicate_name']
                                                           ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count, 'annotators': users,
                                              'annotators_count': len(users),

                                              'subject_start': js_ret['start'],
                                              'subject_stop': js_ret['stop'],
                                              'subject_location_in_text': subject_location_in_text,
                                              'subject_mention_text': mention.mention_text,
                                              'object_concept_url': object_concept.concept_url,
                                              'object_concept_name': object_concept.concept_name,
                                              'object_concept_area': object_area.name,
                                              'predicate_concept_url': predicate_concept.concept_url,
                                              'predicate_concept_name': predicate_concept.concept_name,
                                              'predicate_concept_area': predicate_area.name
                                              })

        annotations = RelationshipObjMention.objects.filter(document_id=document, name_space=name).values(
            'subject_concept_url', 'start', 'stop', 'predicate_concept_url', 'subject_name', 'predicate_name').distinct(
            'subject_concept_url', 'start', 'stop', 'predicate_concept_url', 'subject_name', 'predicate_name')
        for annotation in annotations:
            mention = Mention.objects.get(document_id=document, start=annotation['start'], stop=annotation['stop'])

            predicate_concept = Concept.objects.get(concept_url=annotation['predicate_concept_url'])
            subject_concept = Concept.objects.get(concept_url=annotation['subject_concept_url'])
            subject_area = SemanticArea.objects.get(name=annotation['subject_name'])
            predicate_area = SemanticArea.objects.get(name=annotation['predicate_name'])
            js_ret = return_start_stop_for_frontend(mention.start, mention.stop, document.document_content)
            object_location_in_text = js_ret['position']
            if object_location_in_text.endswith('_value'):
                object_location_in_text = object_location_in_text.replace('_value', '')
            else:
                object_location_in_text = object_location_in_text.replace('_key', ' (key)')
            count = RelationshipObjMention.objects.filter(document_id=document,
                                                          subject_concept_url=subject_concept.concept_url,
                                                          subject_name=subject_area.name,
                                                          predicate_concept_url=predicate_concept.concept_url,
                                                          predicate_name=predicate_area.name,
                                                          start=mention, stop=mention.stop
                                                          ).count()
            users = RelationshipObjMention.objects.filter(document_id=document,
                                                          subject_concept_url=subject_concept.concept_url,
                                                          subject_name=subject_area.name,
                                                          predicate_concept_url=predicate_concept.concept_url,
                                                          predicate_name=predicate_area.name,
                                                          start=mention, stop=mention.stop
                                                          ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count, 'annotators': users,
                                              'annotators_count': len(users),

                                              'object_start': js_ret['start'],
                                              'object_stop': js_ret['stop'],
                                              'object_location_in_text': object_location_in_text,
                                              'object_mention_text': mention.mention_text,
                                              'subject_concept_url': subject_concept.concept_url,
                                              'subject_concept_name': subject_concept.concept_name,
                                              'subject_concept_area': subject_area.name,
                                              'predicate_concept_url': predicate_concept.concept_url,
                                              'predicate_concept_name': predicate_concept.concept_name,
                                              'predicate_concept_area': predicate_area.name
                                              })

        annotations = RelationshipPredMention.objects.filter(document_id=document, name_space=name).values(
            'subject_concept_url', 'start', 'stop', 'object_concept_url', 'subject_name', 'object_name').distinct(
            'subject_concept_url', 'start', 'stop', 'object_concept_url', 'subject_name', 'object_name')
        for annotation in annotations:
            mention = Mention.objects.get(document_id=document, start=annotation['start'], stop=annotation['stop'])
            js_ret = return_start_stop_for_frontend(mention.start, mention.stop, document.document_content)
            location_in_text = js_ret['position']
            predicate_location_in_text = js_ret['position']
            if predicate_location_in_text.endswith('_value'):
                predicate_location_in_text = predicate_location_in_text.replace('_value', '')
            else:
                predicate_location_in_text = predicate_location_in_text.replace('_key', ' (key)')
            object_concept = Concept.objects.get(concept_url=annotation['object_concept_url'])
            subject_concept = Concept.objects.get(concept_url=annotation['subject_concept_url'])
            subject_area = SemanticArea.objects.get(name=annotation['subject_name'])
            object_area = SemanticArea.objects.get(name=annotation['object_name'])

            count = RelationshipPredMention.objects.filter(document_id=document,
                                                           subject_concept_url=subject_concept.concept_url,
                                                           subject_name=subject_area.name,
                                                           object_concept_url=object_concept.concept_url,
                                                           object_name=object_area.name,
                                                           start=mention, stop=mention.stop
                                                           ).count()
            users = RelationshipPredMention.objects.filter(document_id=document,
                                                           subject_concept_url=subject_concept.concept_url,
                                                           subject_name=subject_area.name,
                                                           object_concept_url=object_concept.concept_url,
                                                           object_name=object_area.name,
                                                           start=mention, stop=mention.stop
                                                           ).values('username').distinct('username')
            users = [x['username'] for x in users]
            json_doc['relationships'].append({'count': count, 'annotators': users,
                                              'annotators_count': len(users),

                                              'predicate_start': js_ret['start'],
                                              'predicate_stop': js_ret['stop'],
                                              'predicate_location_in_text': predicate_location_in_text,
                                              'predicate_mention_text': mention.mention_text,
                                              'subject_concept_url': subject_concept.concept_url,
                                              'subject_concept_name': subject_concept.concept_name,
                                              'subject_concept_area': subject_area.name,
                                              'object_concept_url': object_concept.concept_url,
                                              'object_concept_name': object_concept.concept_name,
                                              'object_concept_area': object_area.name
                                              })

    return JsonResponse(json_doc)


def delete_single_document(request):
    """This view removes a document from a collection"""

    document = json.loads(request.body)
    document = Document.objects.get(document_id=document['document'])
    collection = document.collection_id
    try:
        with transaction.atomic():
            Annotate.objects.filter(document_id=document).delete()

            CreateFact.objects.filter(document_id=document).delete()
            RelationshipPredMention.objects.filter(document_id=document).delete()
            RelationshipObjMention.objects.filter(document_id=document).delete()
            RelationshipSubjMention.objects.filter(document_id=document).delete()
            RelationshipSubjConcept.objects.filter(object_document_id=document.document_id).delete()
            RelationshipObjConcept.objects.filter(subject_document_id=document.document_id).delete()
            RelationshipPredConcept.objects.filter(object_document_id=document.document_id).delete()
            Link.objects.filter(object_document_id=document.document_id).delete()

            Associate.objects.filter(document_id=document).delete()
            AnnotateLabel.objects.filter(document_id=document).delete()
            GroundTruthLogFile.objects.filter(document_id=document).delete()
            Mention.objects.filter(document_id=document.document_id).delete()
            if document.document_id == request.session['document']:
                name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                user = User.objects.filter(username=request.session['username'], name_space=name_space)
                gts = GroundTruthLogFile.objects.filter(username__in=user).order_by('-insertion_time')
                for g in gts:
                    document = g.document_id
                    if document.collection_id_id == request.session['collection']:
                        request.session['document'] = document.document_id
                        break
                if gts.count() == 0:
                    doc = Document.objects.filter(collection_id=collection).first()
                    request.session['document'] = doc.document_id
            Document.objects.filter(document_id=document.document_id).delete()

            return JsonResponse({'msg': 'ok'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': e})


def get_users_list(request):
    """This method returns the list of users"""

    name_space = NameSpace.objects.get(name_space=request.session['name_space'])
    users = User.objects.filter(name_space=name_space).all()
    users_list = {}
    users_list['users'] = []
    for u in users:
        json_user = {}
        json_user['username'] = u.username
        json_user['profile'] = u.profile
        json_user['name_space'] = u.name_space_id
        json_user['orcid'] = u.orcid
        json_user['ncbi_key'] = u.ncbi_key
        if json_user not in users_list['users']:
            users_list['users'].append(json_user)
    return JsonResponse(users_list)


def get_count_per_label(request):
    """This view returns for each label the number of documents it has been associated to"""

    collection = request.GET.get('collection', None)
    json_resp = {}
    collection = Collection.objects.get(collection_id=collection)
    labels = CollectionHasLabel.objects.filter(collection_id=collection)
    for label in labels:
        json_resp[label.name] = 0

    labels_with_count = AnnotateLabel.objects.filter(collection_id=collection).values('name').annotate(
        total=Count('label')).order_by('total')
    for label in labels_with_count:
        json_resp[label['name']] = label['total']

    return json_resp


def get_count_per_user(request):
    """This view returns for each user the number of documents she annotated (given a collection)"""

    collection = request.GET.get('collection', None)
    json_resp = {}
    collection = Collection.objects.get(collection_id=collection)
    users = ShareCollection.objects.filter(collection_id=collection)
    for user in users:
        gt = GroundTruthLogFile.objects.filter(collection_id=collection, username=user).values(
            'document_id').distinct().count()
        json_resp[user.username] = gt

    return json_resp


def get_labels_list(request):
    """This view returns the list of labels associated to a collection"""

    collection = request.GET.get('collection', None)
    collection = Collection.objects.get(collection_id=collection)
    labels = CollectionHasLabel.objects.filter(collection_id=collection)
    json_labels = {}
    json_labels['labels'] = []
    for label in labels:
        json_labels['labels'].append(label.name_id)
    return JsonResponse(json_labels)


def get_members_list(request):
    """This view returns the list of memebrs associated to a collection"""

    collection = request.GET.get('collection', None)
    collection = Collection.objects.get(collection_id=collection)
    shared = ShareCollection.objects.filter(collection_id=collection)
    json_boj = {}
    json_boj['members'] = []
    for us in shared:
        us1 = User.objects.get(name_space=request.session['name_space'], username=us.username_id)
        if us1.username != request.session['username']:
            json_boj['members'].append({'username': us.username, 'profile': us.profile, 'status': us.status})

    # controllo se sono tutti gli utenti appartengono a un profile esatto
    profiles = User.objects.all().values('profile')
    profiles = [p['profile'] for p in profiles]


    for p in profiles:
        users = User.objects.filter(profile=p)
        new_json_members = [j for j in json_boj['members'] if j['profile'] == p]

        if len(users) == len(new_json_members):
            json_boj['members'] = [j for j in json_boj['members'] if j['profile'] != p]
            # json_boj['members'].append({'username': 'All' + p, 'profile': p})

    return JsonResponse(json_boj)


def get_collection_documents(request):
    """This view returns the list of documents associated to a collection"""

    docs_to_ret = {}
    docs_to_ret['documents'] = []
    collection = request.GET.get('coll', None)
    # collection_to_find = request.session['collection']
    collection = Collection.objects.get(collection_id=collection)
    documents = Document.objects.filter(collection_id=collection)
    for doc in documents:
        json_obj = doc.document_content
        # pid = json_obj.get('document_id', '')
        #
        # if pid == '':
        #     json_obj['document_id'] = doc.document_id

        language = json_obj.get('language', '')
        if language == '':
            json_obj['language'] = doc.language

        docs_to_ret['documents'].append(json_obj)

    return JsonResponse(docs_to_ret)


def get_user_annotation_count_per_collection(request):
    """This view returns the total count of documents a user annotated in a collection"""

    collection = request.GET.get('collection', None)
    mode = NameSpace.objects.get(name_space=request.session['name_space'])
    user = request.GET.get('user', None)
    if collection is not None and user is not None:
        collection = Collection.objects.get(collection_id=collection)
        user = User.objects.get(name_space=mode, username=user)
        gt = GroundTruthLogFile.objects.filter(username=user, collection_id=collection).exclude(revised=False).values(
            'document_id').distinct()
        return JsonResponse({'count': gt.count()})
    return JsonResponse({'error': 'error'})


def download_template_concepts(request):
    if request.method == 'GET':
        format = request.GET.get('type', None)

        if format == 'json':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './static/templates_to_download/template_concepts.json')
            with open(path, 'r') as f:
                json_resp = json.load(f)
                return JsonResponse(json_resp)
        elif format == 'doc_json':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './static/templates_to_download/template_documents.json')
            with open(path, 'r') as f:
                json_resp = json.load(f)
                return JsonResponse(json_resp)
        elif format == 'topic_json':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './static/templates_to_download/template_topics.json')
            with open(path, 'r') as f:
                json_resp = json.load(f)
                return JsonResponse(json_resp)
        elif format == 'csv':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './static/templates_to_download/template_concepts.csv')

            content = open(path, 'r')
            return HttpResponse(content, content_type='text/csv')


# ADD DATA
from django.core.mail import send_mail


# def create_new_collection(request):
#
#     """This method allows to create a new collection. The uploaded documents are inserted in the database"""
#
#     try:
#         with transaction.atomic():
#
#             name = request.POST.get('name', None)
#             labels = request.POST.get('labels', None)
#             description = request.POST.get('description', None)
#             to_enc = name + request.session['username']
#             username = request.session['username']
#             collection_id = hashlib.md5(to_enc.encode()).hexdigest()
#             share_with = request.POST.get('members', None)
#             # if share_with in ['All Professor', 'All Student', 'All Beginner','All Expert', 'All Tech','All Admin']:
#             #     members = User.objects.filter(profile = share_with.split('All')[1].strip())
#             #     share_with = [m.username for m in members]
#             # else:
#             if share_with == '' or share_with is None:
#                 share_with = []
#             else:
#                 share_with = share_with.split(',')
#
#
#             if labels == '' or labels is None:
#                 labels = []
#             else:
#                 labels = labels.split(',')
#
#             collection = Collection.objects.create(collection_id=collection_id,description=description,name=name,insertion_time=Now(),username = request.session['username'],name_space=request.session['name_space'])
#
#             name_space = NameSpace.objects.get(name_space = request.session['name_space'])
#             creator = User.objects.filter(username = request.session['username'],name_space = name_space)
#             for c in creator: # gestisco i vari name space
#                 ShareCollection.objects.create(collection_id=collection, username=c.username, name_space=c.name_space,status='Creator')
#             for user in share_with:
#                 if user != request.session['username']:
#                     us = User.objects.get(username=user,name_space=name_space)
#                     ShareCollection.objects.create(collection_id=collection, username=us,name_space=us.name_space,status='invited')
#
#
#             for label in labels:
#                 if not Label.objects.filter(name=label).exists():
#                     label = Label.objects.create(name=label)
#                 else:
#                     label = Label.objects.get(name=label)
#                 if not CollectionHasLabel.objects.filter(collection_id=collection, name = label).exists():
#                     CollectionHasLabel.objects.create(collection_id=collection,name = label)
#
#             files = request.FILES.items()
#             for file, filename in files:
#                 if filename.endswith('json'):
#                     upload_json_concepts(file, name_space, username, collection)
#                 elif filename.endswith('csv'):
#                     upload_csv_concepts(file, name_space, username, collection)
#
#             pubmed_ids = request.POST.get('pubmed_ids', None)
#             if pubmed_ids is not None:
#                 pubmed_ids = pubmed_ids.split()
#                 for pid in pubmed_ids:
#                     json_val = insert_articles_of_PUBMED(pid)
#                     if json_val:
#                         to_enc_id = request.session['username'] + str(datetime.now())
#                         pid = hashlib.md5(to_enc_id.encode()).hexdigest()
#                         if not Document.objects.filter(document_id=pid).exists():
#                             Document.objects.create(batch=1, document_id=pid,
#                                                     provenance='pubmed', language='english', document_content=json_val,
#                                                     insertion_time=Now(), collection_id=collection)
#
#             openaire_ids = request.POST.get('openaire_ids', None)
#             if openaire_ids is not None:
#                 openaire_ids = openaire_ids.split()
#                 # for pid in openaire_ids:
#                 json_val = insert_articles_of_OpenAIRE(openaire_ids)
#                 if json_val:
#                     for doc in json_val['documents']:
#                         # pid = doc['document_id']
#                         to_enc_id = request.session['username'] + str(datetime.now())
#                         pid = hashlib.md5(to_enc_id.encode()).hexdigest()
#                         if not Document.objects.filter(document_id=pid).exists():
#                             Document.objects.create(batch=1, document_id=pid,
#                                                     provenance='openaire', language='english', document_content=json_val,
#                                                     insertion_time=Now(), collection_id=collection)
#
#             semantic_ids = request.POST.get('semantic_ids', None)
#             if semantic_ids is not None:
#                 semantic_ids = semantic_ids.split()
#                 # for pid in openaire_ids:
#                 json_val = insert_articles_of_semantic(semantic_ids)
#                 if json_val:
#                     for doc in json_val['documents']:
#                         # pid = doc['document_id']
#                         to_enc_id = request.session['username'] + str(datetime.now())
#                         pid = hashlib.md5(to_enc_id.encode()).hexdigest()
#                         if not Document.objects.filter(document_id=pid).exists():
#                             Document.objects.create(batch=1,  document_id=pid,
#                                                     provenance='semantic scholar', language='english', document_content=json_val,
#                                                     insertion_time=Now(), collection_id=collection)
#             files = request.FILES.items()
#             for file,filename in files:
#                 json_contents = create_json_content_from_file(file)
#                 for json_content in json_contents:
#                     # pid = ''
#                     language = 'english'
#                     # if 'document_id' in list(json_content.keys()):
#                     #     pid = json_content['document_id']
#                     # else:
#                     #     to_enc_id = collection_id + str(json_contents.index(json_content))
#                     #     pid = hashlib.md5(to_enc_id.encode()).hexdigest()
#
#                     if 'language' in list(json_content.keys()) and not json_content['language'].lower() == 'english':
#                         language = json_content['language']
#
#                     # for k,v in json_content.items():
#                     #     json_content[k] = re.sub('\s+', ' ', v)
#                     to_enc_id = request.session['username'] + str(datetime.now())
#                     pid = hashlib.md5(to_enc_id.encode()).hexdigest()
#                     Document.objects.create(batch = 1,collection_id=collection,document_id=pid,language=language, document_content=json_content,insertion_time=Now())
#
#
#
#     except Exception as e:
#         print(e)
#         json_resp = {'error':e}
#
#     else:
#         json_resp = {'message':'ok'}
#     finally:
#         return JsonResponse(json_resp)


def add_member(request):
    """This view adds new members to a collection: once added they can have access to the collection's documents"""

    try:
        with transaction.atomic():
            json_resp = {'msg': 'ok'}
            # name_space = NameSpace.objects.get(name_space=request.session['name_space'])
            request_body_json = json.loads(request.body)
            members = request_body_json['members']
            # for m in members:
            # if m in ['All Professor','All Student','All Tech','All Beginner','All Expert','All Admin'] :
            #     members_all = User.objects.filter(profile = m['username'].split('All')[1].strip()).exclude(username = request.session['username'])
            #     members_all = [{'username':m.username} for m in members_all if m['username'] != request.session['username']]
            #     members = members + members_all
            collection = request_body_json['collection']
            collection = Collection.objects.get(collection_id=collection)
            # members = list(set(members))

            for member in members:
                # if member not in ['All Professor','All Student','All Tech','All Beginner','All Expert','All Admin']:
                name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                users = User.objects.filter(username=member, name_space=name_space)
                for user in users:
                    if not ShareCollection.objects.filter(collection_id=collection, username=user,
                                                          name_space=user.name_space).exists():
                        ShareCollection.objects.create(collection_id=collection, username=user,
                                                       name_space=user.name_space, status='invited')
    except Exception as e:
        print(e)
        json_resp = {'error': e}
    finally:
        return JsonResponse(json_resp)


def add_labels(request):
    """This view adds new labels to a collection"""

    try:
        with transaction.atomic():
            json_resp = {'msg': 'ok'}

            request_body_json = json.loads(request.body)
            labels = request_body_json['labels'].replace('\\n', '\n').split('\n')
            labels = [l.strip() for l in labels if l != '']
            collection = request_body_json['collection']
            collection = Collection.objects.get(collection_id=collection)
            for label in labels:
                if not Label.objects.filter(name=label).exists():
                    label_to_add = Label.objects.create(name=label)
                else:
                    label_to_add = Label.objects.get(name=label)
                if not CollectionHasLabel.objects.filter(collection_id=collection, label=label_to_add).exists():
                    CollectionHasLabel.objects.create(collection_id=collection, label=label_to_add)


    except Exception as e:
        print(e)
        json_resp = {'error': e}
    finally:
        return JsonResponse(json_resp)


def transfer_annotations(request):
    """This view transfer the annotations of a predefined user to the logged in user. If overwrite is true the
    annotations of the new user will overwrite the one of the current logged in user."""

    collection = request.POST.get('collection', None)
    user_from = request.POST.get('user', None)
    user_to = request.session['username']
    overwrite = request.POST.get('overwrite', None)
    json_resp = {'msg': 'ok'}
    try:
        with transaction.atomic():
            collection = Collection.objects.get(collection_id=collection)
            modes = NameSpace.objects.all()
            for mode in modes:
                user_from = User.objects.get(username=user_from, name_space=mode)
                user_to = User.objects.get(username=user_to, name_space=mode)
                annotate_rows = Annotate.objects.filter(username=user_from, name_space=mode, collection_id=collection)
                associate_rows = Associate.objects.filter(username=user_from, name_space=mode, collection_id=collection)
                link_rows = Link.objects.filter(username=user_from, name_space=mode, object_collection_id=collection)
                # relationship_rows = Relationship.objects.filter(username = user_from, name_space = mode, object_collection_id = collection)
                annotate_label_rows = AnnotateLabel.objects.filter(username=user_from, name_space=mode,
                                                                   collection_id=collection)

                if not overwrite:
                    AnnotateLabel.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                    Annotate.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                    Associate.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                    # Relationship.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                    Link.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                    GroundTruthLogFile.objects.filter(username=user_to, name_space=mode,
                                                      collection_id=collection).delete()
                #
                #
                # copy annotate
                for annotation in annotate_rows:
                    # se sovrascrivo
                    if overwrite:
                        # Annotate.objects.filter(username=user_to, name_space=mode, collection_id=collection).delete()
                        Annotate.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                document_id=annotation.document_id,
                                                language=annotation.language, start=annotation.start,
                                                stop=annotation.stop, insertion_time=annotation.insertion_time)
                    elif not overwrite and not Annotate.objects.filter(username=user_to,
                                                                       document_to=annotation.document_id,
                                                                       name_space=mode,
                                                                       collection_id=collection).exists():
                        Annotate.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                document_id=annotation.document_id,
                                                language=annotation.language, start=annotation.start,
                                                stop=annotation.stop,
                                                insertion_time=annotation.insertion_time)
                # copy associate
                for annotation in associate_rows:
                    if overwrite:
                        Associate.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                 document_id=annotation.document_id,
                                                 language=annotation.language, start=annotation.start,
                                                 stop=annotation.stop,
                                                 insertion_time=annotation.insertion_time,
                                                 concept_url=annotation.concept_url)
                    elif not overwrite and not Associate.objects.filter(username=user_to,
                                                                        document_to=annotation.document_id,
                                                                        name_space=mode,
                                                                        collection_id=collection).exists():
                        Associate.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                 document_id=annotation.document_id,
                                                 language=annotation.language, start=annotation.start,
                                                 stop=annotation.stop,
                                                 insertion_time=annotation.insertion_time,
                                                 concept_url=annotation.concept_url)
                # copy link

                # copy relationship

                # copy annotate_label
                for annotation in annotate_label_rows:
                    if overwrite:
                        AnnotateLabel.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                     document_id=annotation.document_id,
                                                     language=annotation.language,
                                                     insertion_time=annotation.insertion_time, name=annotation.name)
                    elif not overwrite and not AnnotateLabel.objects.filter(username=user_to,
                                                                            document_to=annotation.document_id,
                                                                            name_space=mode,
                                                                            collection_id=collection).exists():
                        AnnotateLabel.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                     document_id=annotation.document_id,
                                                     language=annotation.language,
                                                     insertion_time=annotation.insertion_time, label=annotation.name)

                # copy ground_truth_log_file
                ground_truth_log_file_rows = GroundTruthLogFile.objects.filter(username=user_from, name_space=mode,
                                                                               collection_id=collection)
                for annotation in ground_truth_log_file_rows:
                    if overwrite:
                        GroundTruthLogFile.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                          document_id=annotation.document_id,
                                                          gt_type=annotation.gt_type, gt_json=annotation.gt_json,
                                                          language=annotation.language, revised=False,
                                                          insertion_time=annotation.insertion_time)
                    elif not overwrite and not GroundTruthLogFile.objects.filter(username=user_to,
                                                                                 document_to=annotation.document_id,
                                                                                 name_space=mode,
                                                                                 collection_id=collection).exists():
                        GroundTruthLogFile.objects.create(username=user_to, name_space=mode, collection_id=collection,
                                                          document_id=annotation.document_id,
                                                          gt_type=annotation.gt_type,
                                                          gt_json=annotation.gt_json,
                                                          language=annotation.language, revised=False,
                                                          insertion_time=annotation.insertion_time)
    except Exception as e:
        json_resp = {'error': e}
    finally:
        return JsonResponse(json_resp)


def check_json_csv_fields(request):
    """This method detects new fields in csv and json uploaded documents"""

    fields = {'csv': [], 'json': []}
    csv_files = []
    json_files = []

    for filename, file in request.FILES.items():
        if filename.endswith('csv'):
            csv_files.append(file)
        if filename.startswith('json'):
            json_files.append(file)

    csv_fields = get_csv_fields(csv_files)
    json_fields = get_json_fields(csv_files)

    if len(csv_fields) > 1:
        fields['csv'] = csv_fields
    if len(json_fields) > 1:
        fields['json'] = json_fields

    # fields['fields'] = list(set(fields['csv'] + fields['json']))

    return JsonResponse(fields)


def get_fields(request):
    """This view returns the list of keys of the document"""

    document_id = request.session['document']
    print('session doc', request.session['document'])
    language = request.session['language']
    keys = get_fields_list(document_id, language)
    json_resp = {}
    json_resp['fields'] = keys

    if all(x in keys for x in request.session['fields_to_ann']):
        request.session['fields'] = keys
        json_resp['fields_to_ann'] = request.session['fields_to_ann']
    else:
        json_resp['fields'] = keys
        json_resp['fields_to_ann'] = keys
    return JsonResponse(json_resp)


# DELETE

def delete_member_from_collection(request):
    """This method delete a member from ShareCollection: this means that that member won't see that collection anymore hence she won't be able to annotate its documents."""

    request_body_json = json.loads(request.body)
    try:
        with transaction.atomic():
            json_resp = {'msg': 'ok'}
            members = []
            member = request_body_json['member']
            collection = request_body_json['collection']
            members.append(member)
            # if member in ['All Professor','All Student','All Tech','All Beginner','All Expert','All Admin']:
            #     # escludo già lo username della sessione perché se sono in questo metodo vuole dire che è entrato l'owenr
            #     members = User.objects.filter(profile = member.split('All')[1].strip()).exclude(username = request.session['username'])
            #     members = [m.username for m in members if m.username != request.session['username']]
            #     # members = list(set(members))

            # delete the annotation of that member for that collection first
            for member in members:
                name_space = NameSpace.objects.get(name_space=request.session['name_space'])
                users = User.objects.filter(username=member, name_space=name_space)
                collection = Collection.objects.get(collection_id=collection)
                for user in users:
                    documents = Document.objects.filter(collection_id=collection)
                    Annotate.objects.filter(document_id__in=documents, username=user, name_space=name_space).delete()
                    Associate.objects.filter(document_id__in=documents, username=user, name_space=name_space).delete()
                    AnnotateLabel.objects.filter(document_id__in=documents, username=user,
                                                 name_space=name_space).delete()
                    CreateFact.objects.filter(document_id__in=documents, username=user, name_space=name_space).delete()

                    RelationshipObjMention.objects.filter(document_id__in=documents, username=user,
                                                          name_space=name_space).delete()
                    RelationshipPredMention.objects.filter(document_id__in=documents, username=user,
                                                           name_space=name_space).delete()
                    RelationshipSubjMention.objects.filter(document_id__in=documents, username=user,
                                                           name_space=name_space).delete()

                    documents_ids_list = [x.document_id for x in documents]
                    RelationshipObjConcept.objects.filter(predicate_document_id__in=documents_ids_list, username=user,
                                                          name_space=name_space).delete()
                    RelationshipPredConcept.objects.filter(object_document_id__in=documents_ids_list, username=user,
                                                           name_space=name_space).delete()
                    RelationshipSubjConcept.objects.filter(object_document_id__in=documents_ids_list, username=user,
                                                           name_space=name_space).delete()
                    Link.objects.filter(predicate_document_id__in=documents_ids_list, username=user,
                                        name_space=name_space).delete()

                    ShareCollection.objects.filter(collection_id=collection, username=user,
                                                   name_space=name_space).delete()
                    GroundTruthLogFile.objects.filter(document_id__in=documents, username=user,
                                                      name_space=name_space).delete()

                # Collection.objects.filter(collection_id=collection).delete()
    except Exception as e:
        print(e)
        json_resp = {'error': 'an error occurred'}
        return JsonResponse(json_resp)
    else:
        return JsonResponse(json_resp)


def delete_annotation_all(request):
    """This view removed all the annotations for the document of the session"""

    user = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    document = request.session['document']
    if not document:
        return redirect('doctron_app:loginPage')

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=user, name_space=name_space)
    user_iaa = User.objects.get(username="IAA-Inter Annotator Agreement", name_space=name_space)

    language = request.session['language']
    document = Document.objects.get(document_id=request.session['document'], language=language)
    json_resp = {'msg': 'ok'}
    topic = Topic.objects.get(id=request.session['topic'])
    try:
        with transaction.atomic():
            Annotate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document).delete()
            Associate.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document).delete()
            AssociateTag.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document).delete()
            AnnotateLabel.objects.filter(username=user,topic_id=topic, name_space=name_space, document_id=document).delete()
            Link.objects.filter(username=user, name_space=name_space,topic_id=topic, subject_document_id=document.document_id).delete()
            CreateFact.objects.filter(username=user, name_space=name_space, topic_id=topic,document_id=document).delete()
            RelationshipObjMention.objects.filter(username=user, name_space=name_space, topic_id=topic,document_id=document).delete()
            RelationshipObjConcept.objects.filter(username=user, name_space=name_space,topic_id=topic,
                                                  subject_document_id=document.document_id).delete()
            RelationshipSubjConcept.objects.filter(username=user, name_space=name_space,topic_id=topic,
                                                   object_document_id=document.document_id).delete()
            RelationshipSubjMention.objects.filter(username=user, name_space=name_space, topic_id=topic,document_id=document).delete()
            RelationshipPredConcept.objects.filter(username=user, name_space=name_space,topic_id=topic,
                                                   subject_document_id=document.document_id).delete()
            RelationshipPredMention.objects.filter(username=user, name_space=name_space,topic_id=topic, document_id=document).delete()
            GroundTruthLogFile.objects.filter(username=user, name_space=name_space, topic_id=topic,document_id=document).delete()
            json_resp['document'] = create_new_content(document, user,topic)

            Annotate.objects.filter(username=user_iaa, name_space=name_space,topic_id=topic, document_id=document).delete()
            Associate.objects.filter(username=user_iaa, name_space=name_space,topic_id=topic, document_id=document).delete()
            AssociateTag.objects.filter(username=user_iaa, name_space=name_space,topic_id=topic, document_id=document).delete()
            AnnotateLabel.objects.filter(username=user_iaa, name_space=name_space,topic_id=topic, document_id=document).delete()
            Link.objects.filter(username=user_iaa, name_space=name_space,topic_id=topic,
                                subject_document_id=document.document_id).delete()
            CreateFact.objects.filter(username=user_iaa, name_space=name_space, topic_id=topic,document_id=document).delete()
            RelationshipObjMention.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space,
                                                  document_id=document).delete()
            RelationshipObjConcept.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space,
                                                  subject_document_id=document.document_id).delete()
            RelationshipSubjConcept.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space,
                                                   object_document_id=document.document_id).delete()
            RelationshipSubjMention.objects.filter(username=user_iaa, topic_id=topic,name_space=name_space,
                                                   document_id=document).delete()
            RelationshipPredConcept.objects.filter(username=user_iaa, topic_id=topic,name_space=name_space,
                                                   subject_document_id=document.document_id).delete()
            RelationshipPredMention.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space,
                                                   document_id=document).delete()
            AnnotateObject.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space, document_id=document).delete()
            GroundTruthLogFile.objects.filter(username=user_iaa,topic_id=topic, name_space=name_space, document_id=document).delete()

    except Exception as e:
        json_resp = {'error': e}

    return JsonResponse(json_resp)


def delete_collection(request):
    """This method delete a member from ShareCollection: this means that that member won't see that collection anymore hence she won't be able to annotate its documents."""

    request_body_json = json.loads(request.body)
    try:
        with transaction.atomic():
            lista = []
            json_resp = {'msg': 'ok'}
            collection = request_body_json['collection']
            # cursor = connection.cursor()
            documents = Document.objects.filter(collection_id=collection)
            Annotate.objects.filter(document_id__in=documents).delete()
            Associate.objects.filter(document_id__in=documents).delete()
            AnnotateLabel.objects.filter(document_id__in=documents).delete()
            CreateFact.objects.filter(document_id__in=documents).delete()

            RelationshipObjMention.objects.filter(document_id__in=documents).delete()
            RelationshipPredMention.objects.filter(document_id__in=documents).delete()
            RelationshipSubjMention.objects.filter(document_id__in=documents).delete()

            documents_ids_list = [x.document_id for x in documents]
            RelationshipObjConcept.objects.filter(predicate_document_id__in=documents_ids_list).delete()
            RelationshipPredConcept.objects.filter(object_document_id__in=documents_ids_list).delete()
            RelationshipSubjConcept.objects.filter(object_document_id__in=documents_ids_list).delete()
            Link.objects.filter(predicate_document_id__in=documents_ids_list).delete()

            ShareCollection.objects.filter(collection_id=collection).delete()
            Document.objects.filter(collection_id=collection).delete()
            GroundTruthLogFile.objects.filter(document_id__in=documents).delete()

            CollectionHasLabel.objects.filter(collection_id=collection).delete()
            AddConcept.objects.filter(collection_id=collection).delete()
            Collection.objects.filter(collection_id=collection).delete()
            Document.objects.filter(collection_id=collection).delete()

            # cursor.execute('DELETE FROM collection WHERE collection_id = %s',[collection])
            # delete the annotation of that member for that collection first
    except Exception as e:
        json_resp = {'error': 'an error occurred'}
        return JsonResponse(json_resp)
    else:
        return JsonResponse(json_resp)


def generate_suggestion(request):
    """This view returns a suggestion"""

    user = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    document = request.session['document']
    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=user, name_space=name_space)

    document = Document.objects.get(document_id=document, language=language)

    start = request.GET.get('start', None)
    stop = request.GET.get('stop', None)
    position = request.GET.get('position', None)
    position = '_'.join(position.split('_')[:-1])
    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)

    mention = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
    associations = Associate.objects.filter(start=mention, stop=mention.stop, document_id=document).values(
        'concept_url').order_by('concept_url').annotate(count=Count('concept_url'))

    json_resp = {}
    return JsonResponse(json_resp)


def upload(request):
    username = request.session['username']
    name_space = request.session['name_space']
    collection = request.session['collection']
    collection_obj = Collection.objects.get(collection_id=collection)
    json_resp = {'msg': 'ok'}
    try:
        if request.method == 'POST':
            with transaction.atomic():
                new_batch = request.POST.get('new_batch')
                max_batch = Document.objects.filter(collection_id=collection_obj).order_by('-batch').first()
                batch = max_batch.batch
                if new_batch != 'false':
                    batch = batch + 1

                files = request.FILES.items()
                annotation = request.POST.get("type_annotation")
                for filename, file in files:
                    if filename.startswith('concept'):

                        if file.name.endswith('json'):
                            upload_json_concepts(file, name_space, username, collection_obj)
                        elif file.name.endswith('csv'):
                            upload_csv_concepts(file, name_space, username, collection_obj)
                    elif filename.startswith('annotation'):

                        # for file, filename in files:
                        if file.name.endswith('json'):
                            upload_json_files(file, name_space, annotation, username)
                        elif file.name.endswith('csv'):
                            upload_csv_files(file, name_space, annotation, username)

                    elif filename.startswith('document'):
                        print('document')
                        json_contents = create_json_content_from_file(file)
                        print(len(json_contents))
                        for json_content in json_contents:
                            pid = ''

                            language = 'english'
                            # if 'document_id' in list(json_content.keys()):
                            #     pid = json_content['document_id']
                            # else:
                            #     to_enc_id = collection + request.session['username']
                            #     pid = hashlib.md5(to_enc_id.encode()).hexdigest()

                            if 'language' in list(json_content.keys()) and not json_content[
                                                                                   'language'].lower() == 'english':
                                language = json_content['language']
                            to_enc_id = request.session['username'] + str(datetime.now())
                            pid = hashlib.md5(to_enc_id.encode()).hexdigest()
                            if not Document.objects.filter(document_id=pid).exists():
                                print("adding", pid)
                                # collection = Collection.objects.get(collection_id=collection)
                                # for k,v in json_content.items():
                                #     json_content[k] = re.sub('\s+', ' ', v)

                                Document.objects.create(batch=batch, collection_id=collection_obj, provenance='user',
                                                        document_id=pid,
                                                        language=language,
                                                        document_content=json_content, insertion_time=Now())
                pubmed_ids = request.POST.get('pubmed_ids', '')
                if pubmed_ids == '':
                    pubmed_ids = None
                collection = Collection.objects.get(collection_id=collection)
                if pubmed_ids is not None:

                    pubmed_ids = pubmed_ids.split()
                    for pid in pubmed_ids:
                        try:
                            json_val = insert_articles_of_PUBMED(pid)
                        except Exception as e:
                            json_resp = {'error': 'Not found'}
                            json_val = None
                            return JsonResponse(json_resp, status=500)
                        if json_val:

                            to_enc_id = request.session['username'] + str(datetime.now())
                            pid = hashlib.md5(to_enc_id.encode()).hexdigest()
                            if not Document.objects.filter(document_id=pid, language='english',
                                                           collection_id=collection).exists():
                                Document.objects.create(batch=batch, document_id=pid,
                                                        provenance='pubmed', language='english',
                                                        document_content=json_val,
                                                        insertion_time=Now(), collection_id=collection)

                openaire_ids = request.POST.get('openaire_ids', '')
                if openaire_ids == '':
                    openaire_ids = None
                if openaire_ids is not None:
                    openaire_ids = openaire_ids.split()
                    json_val = insert_articles_of_OpenAIRE(openaire_ids)
                    if json_val['documents'] == []:
                        json_resp = {'error': 'Not found'}
                        raise Exception
                    if json_val:
                        for doc in json_val['documents']:
                            to_enc_id = request.session['username'] + str(datetime.now())
                            pid = hashlib.md5(to_enc_id.encode()).hexdigest()

                            if not Document.objects.filter(document_id=pid, language='english',
                                                           collection_id=collection).exists():
                                Document.objects.create(batch=batch, document_id=pid,
                                                        provenance='openaire', language='english', document_content=doc,
                                                        insertion_time=Now(), collection_id=collection)

                semantic_ids = request.POST.get('semantic_ids', '')
                if semantic_ids == '':
                    semantic_ids = None

                if semantic_ids is not None:
                    semantic_ids = semantic_ids.split()
                    json_val = insert_articles_of_semantic(semantic_ids)
                    if json_val['documents'] == []:
                        json_resp = {'error': 'Not found'}
                        raise Exception
                    if json_val:
                        for doc in json_val['documents']:
                            to_enc_id = request.session['username'] + str(datetime.now())
                            pid = hashlib.md5(to_enc_id.encode()).hexdigest()
                            if not Document.objects.filter(document_id=pid, language='english',
                                                           collection_id=collection).exists():
                                Document.objects.create(batch=batch, document_id=pid,
                                                        provenance='semantic scholar', language='english',
                                                        document_content=doc,
                                                        insertion_time=Now(), collection_id=collection)
        return JsonResponse(json_resp)
    except Exception as e:
        print(e)
        if (json_resp['error']):
            return JsonResponse(json_resp, status=500)
        return JsonResponse({'error': e}, status=500)


from doctron_app.utils_download_bioc import *


def download_annotations(request):
    """This view allows to download the annotations of one or more users related to a collection"""

    user = request.session['username']
    name_space = request.session['name_space']
    # document = request.session['document']
    collection = request.session['collection']
    format = request.GET.get('format', None)
    annotation = request.GET.get('annotation', None)
    annotators = request.GET.get('annotators', None)
    document = request.GET.get('document', None)

    batch = request.GET.get('batch', None)
    json_resp = {}
    json_resp['annotations'] = []
    if format == 'json':
        json_resp = create_json_to_download(annotation, annotators, batch, name_space, document, collection)
        return JsonResponse(json_resp)

    elif format == 'csv':
        resp = create_csv_to_download(annotation, annotators, batch, name_space, document, collection)
        return resp
    elif format == 'xml':
        resp = create_bioc_xml(annotation, annotators, batch, user, name_space, document, collection)
        return HttpResponse(resp, content_type='application/xml')


from doctron_app.utils_upload_documents import *


def upload_annotations(request):
    """This view allows to upload the annotations of one or more users related to a collection"""

    user = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    collection = request.session['collection']
    format = ''
    annotation = request.GET.get('annotation', None)
    files = request.FILES.items()
    json_resp = {'msg': 'ok'}
    try:
        for file, filename in files:
            if filename.endswith('json'):
                upload_json_files(file, name_space, annotation, user)
            elif filename.endswith('csv'):
                upload_csv_files(file, name_space, annotation, user)
        return JsonResponse(json_resp)
    except Exception as e:
        json_resp = {'error': e}

        return JsonResponse(json_resp)


def copy_mention(request):
    """This view copies in the table annotate the annotation of a user in the logged in user annotation"""

    username = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    document = request.session['document']
    collection = request.session['collection']

    name_space = NameSpace.objects.get(name_space=name_space)
    user = User.objects.get(username=username, name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    json_body = json.loads(request.body)
    mention = json_body['mention']
    json_resp = copy_mention_aux(user, name_space, document, language, mention)
    return JsonResponse(json_resp)


def copy_mention_concept(request):
    """This view copies in the table annotate the annotation of a user in the logged in user annotation"""

    username = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    document = request.session['document']
    collection = request.session['collection']
    json_body = json.loads(request.body)
    json_resp = copy_concepts_aux(username, name_space, document, language, json_body)
    return JsonResponse(json_resp)


def copy_assertion(request):
    """This view copies in the table createfact the assertion of a user in the logged in user annotation"""

    username = request.session['username']
    name_space = request.session['name_space']
    language = request.session['language']
    document = request.session['document']
    json_body = json.loads(request.body)
    assertion = json_body['assertion']
    json_resp = {}
    # json_resp = copy_assertion(username,name_space,document,language,assertion)
    return JsonResponse(json_resp)


def copy_label(request):
    """This view adds a copied label to the logged in user"""

    username = request.session['username']
    language = request.session['language']
    document = request.session['document']
    name_space = request.session['name_space']

    json_body = json.loads(request.body)
    label = json_body['label']
    json_resp = copy_labels(username, name_space, label, document, language)
    return JsonResponse(json_resp)


def copy_relation(request):
    """This view adds a copied relation to the logged in user"""

    username = request.session['username']
    language = request.session['language']
    document = request.session['document']
    name_space = request.session['name_space']

    json_body = json.loads(request.body)
    relation = json_body['relation']

    subject = relation['subject']
    predicate = relation['predicate']
    object = relation['object']

    json_resp = copy_relation(username, name_space, document, language, subject, predicate, object)
    return JsonResponse(json_resp)


def copy_annotation(request):
    """This view copies all the annotation of a user"""

    username = request.session['username']
    language = request.session['language']
    document = request.session['document']
    name_space = request.session['name_space']
    body_json = json.loads(request.body)
    username_source = body_json['user']
    name_space = NameSpace.objects.get(name_space=name_space)
    document = Document.objects.get(document_id=document, language=language)
    user = User.objects.get(username=username, name_space=name_space)
    user_source = User.objects.get(username=username_source, name_space=name_space)
    try:
        with transaction.atomic():
            if username_source is not None:
                # copy mentions
                for annotation in Annotate.objects.filter(document_id=document, username=user_source,
                                                          name_space=name_space, language=language):
                    mention = Mention.objects.get(start=annotation.start_id, stop=annotation.stop, document_id=document,
                                                  language=language)
                    annotation = Annotate.objects.filter(document_id=document, username=user, name_space=name_space,
                                                         language=language, start=mention,
                                                         stop=mention.stop)
                    if not annotation.exists():
                        Annotate.objects.create(document_id=document, username=user, name_space=name_space,
                                                language=language,
                                                start=mention, insertion_time=Now(),
                                                stop=mention.stop)

                for annotation in Associate.objects.filter(document_id=document, username=user_source,
                                                           name_space=name_space,
                                                           language=language):
                    mention = Mention.objects.get(start=annotation.start_id, stop=annotation.stop, document_id=document,
                                                  language=language)
                    concept = Concept.objects.get(concept_url=annotation.concept_url_id)
                    name = SemanticArea.objects.get(name=annotation.name_id)
                    annotation = Associate.objects.filter(document_id=document, username=user, name_space=name_space,
                                                          language=language, start=mention,
                                                          stop=mention.stop, concept_url=concept, name=name)
                    if not annotation.exists():
                        Associate.objects.create(document_id=document, username=user, name_space=name_space,
                                                 language=language,
                                                 start=mention, insertion_time=Now(),
                                                 stop=mention.stop, concept_url=concept, name=name)

                for annotation in AnnotateLabel.objects.filter(document_id=document, username=user_source,
                                                               name_space=name_space,
                                                               language=language):
                    label = Label.objects.get(name=annotation.name_id)
                    annotation = AnnotateLabel.objects.filter(document_id=document, username=user,
                                                              name_space=name_space,
                                                              language=language, label=label)
                    if not annotation.exists():
                        AnnotateLabel.objects.create(document_id=document, username=user, name_space=name_space,
                                                     language=language,
                                                     insertion_time=Now(), label=label)

                for annotation in CreateFact.objects.filter(document_id=document, username=user_source,
                                                            name_space=name_space,
                                                            language=language):

                    facts = CreateFact.objects.filter(document_id=document, username=user, name_space=name_space,
                                                      language=language,
                                                      subject_concept_url=annotation.subject_concept_url,
                                                      subject_name=annotation.subject_name,
                                                      object_concept_url=annotation.object_concept_url,
                                                      object_name=annotation.object_name,
                                                      predicate_concept_url=annotation.predicate_concept_url,
                                                      predicate_name=annotation.predicate_name)
                    if not facts.exists():
                        CreateFact.objects.create(document_id=document, username=user, name_space=name_space,
                                                  insertion_time=Now(),
                                                  language=language,
                                                  subject_concept_url=annotation.subject_concept_url,
                                                  subject_name=annotation.subject_name,
                                                  object_concept_url=annotation.object_concept_url,
                                                  object_name=annotation.object_name,
                                                  predicate_concept_url=annotation.predicate_concept_url,
                                                  predicate_name=annotation.predicate_name)

                for annotation in RelationshipObjMention.objects.filter(document_id=document, username=user_source,
                                                                        name_space=name_space,
                                                                        language=language):
                    mention = Mention.objects.get(document_id=document, language=language, start=annotation.start_id,
                                                  stop=annotation.stop)
                    rels = RelationshipObjMention.objects.filter(document_id=document, username=user,
                                                                 name_space=name_space,
                                                                 language=language, start=mention,
                                                                 stop=mention.stop,
                                                                 subject_concept_url=annotation.subject_concept_url,
                                                                 subject_name=annotation.subject_name,
                                                                 predicate_concept_url=annotation.predicate_concept_url,
                                                                 predicate_name=annotation.predicate_name)
                    if not rels.exists():
                        RelationshipObjMention.objects.create(document_id=document, username=user,
                                                              name_space=name_space,
                                                              language=language, start=mention, stop=mention.stop,
                                                              subject_concept_url=annotation.subject_concept_url,
                                                              insertion_time=Now(),
                                                              subject_name=annotation.subject_name,
                                                              predicate_concept_url=annotation.predicate_concept_url,
                                                              predicate_name=annotation.predicate_name)

                for annotation in RelationshipSubjMention.objects.filter(document_id=document, username=user_source,
                                                                         name_space=name_space,
                                                                         language=language):
                    mention = Mention.objects.get(document_id=document, language=language, start=annotation.start_id,
                                                  stop=annotation.stop)
                    rels = RelationshipSubjMention.objects.filter(document_id=document, username=user,
                                                                  name_space=name_space,
                                                                  language=language, start=mention,
                                                                  stop=mention.stop,
                                                                  object_concept_url=annotation.object_concept_url,
                                                                  object_name=annotation.object_name,
                                                                  predicate_concept_url=annotation.predicate_concept_url,
                                                                  predicate_name=annotation.predicate_name)
                    if not rels.exists():
                        RelationshipSubjMention.objects.filter(document_id=document, username=user,
                                                               name_space=name_space,
                                                               language=language, start=mention,
                                                               stop=mention.stop, insertion_time=Now(),
                                                               object_concept_url=annotation.object_concept_url,
                                                               object_name=annotation.object_name,
                                                               predicate_concept_url=annotation.predicate_concept_url,
                                                               predicate_name=annotation.predicate_name)

                for annotation in RelationshipPredMention.objects.filter(document_id=document, username=user_source,
                                                                         name_space=name_space,
                                                                         language=language):
                    mention = Mention.objects.get(document_id=document, language=language, start=annotation.start_id,
                                                  stop=annotation.stop)
                    rels = RelationshipPredMention.objects.filter(document_id=document, username=user,
                                                                  name_space=name_space,
                                                                  language=language, start=mention,
                                                                  stop=mention.stop,
                                                                  object_concept_url=annotation.object_concept_url,
                                                                  object_name=annotation.object_name,
                                                                  subject_concept_url=annotation.subject_concept_url,
                                                                  subject_name=annotation.subject_name)
                    if not rels.exists():
                        RelationshipPredMention.objects.create(document_id=document, username=user,
                                                               name_space=name_space, insertion_time=Now(),
                                                               language=language, start=mention,
                                                               stop=mention.stop,
                                                               object_concept_url=annotation.object_concept_url,
                                                               object_name=annotation.object_name,
                                                               subject_concept_url=annotation.subject_concept_url,
                                                               subject_name=annotation.subject_name)

                for annotation in RelationshipPredConcept.objects.filter(subject_document_id=document.document_id,
                                                                         username=user_source,
                                                                         name_space=name_space,
                                                                         subject_language=language):
                    concept = annotation.concept_url
                    area = annotation.name

                    rels = RelationshipPredConcept.objects.filter(subject_document_id=annotation.subject_document_id,
                                                                  subject_language=annotation.subject_language,
                                                                  object_document_id=annotation.object_document_id,
                                                                  object_language=annotation.object_language,
                                                                  username=user, name_space=name_space,
                                                                  concept_url=concept, name=area,
                                                                  subject_start=annotation.subject_start,
                                                                  subject_stop=annotation.subject_stop,
                                                                  object_start=annotation.object_start,
                                                                  object_stop=annotation.object_stop)
                    if not rels.exists():
                        RelationshipPredConcept.objects.create(subject_document_id=annotation.subject_document_id,
                                                               subject_language=annotation.subject_language,
                                                               insertion_time=Now(),
                                                               object_document_id=annotation.object_document_id,
                                                               object_language=annotation.object_language,
                                                               username=user, name_space=name_space,
                                                               concept_url=concept, name=area,
                                                               subject_start=annotation.subject_start,
                                                               subject_stop=annotation.subject_stop,
                                                               object_start=annotation.object_start,
                                                               object_stop=annotation.object_stop)

                for annotation in RelationshipSubjConcept.objects.filter(object_document_id=document.document_id,
                                                                         username=user_source,
                                                                         name_space=name_space,
                                                                         object_language=language):
                    concept = annotation.concept_url
                    area = annotation.name

                    rels = RelationshipSubjConcept.objects.filter(object_document_id=annotation.object_document_id,
                                                                  object_language=annotation.object_language,
                                                                  predicate_document_id=annotation.predicate_document_id,
                                                                  predicate_language=annotation.predicate_language,
                                                                  username=user, name_space=name_space,
                                                                  concept_url=concept, name=area,
                                                                  predicate_start=annotation.predicate_start,
                                                                  predicate_stop=annotation.predicate_stop,
                                                                  object_start=annotation.object_start,
                                                                  object_stop=annotation.object_stop)
                    if not rels.exists():
                        RelationshipSubjConcept.objects.create(object_document_id=annotation.object_document_id,
                                                               object_language=annotation.object_language,
                                                               insertion_time=Now(),
                                                               predicate_document_id=annotation.predicate_document_id,
                                                               predicate_language=annotation.predicate_language,
                                                               username=user, name_space=name_space,
                                                               concept_url=concept,
                                                               name=area, predicate_start=annotation.predicate_start,
                                                               predicate_stop=annotation.predicate_stop,
                                                               object_start=annotation.object_start,
                                                               object_stop=annotation.object_stop)

                for annotation in RelationshipObjConcept.objects.filter(subject_document_id=document.document_id,
                                                                        username=user_source,
                                                                        name_space=name_space,
                                                                        subject_language=language):
                    concept = annotation.concept_url
                    area = annotation.name

                    rels = RelationshipObjConcept.objects.filter(subject_document_id=annotation.subject_document_id,
                                                                 subject_language=annotation.subject_language,
                                                                 predicate_document_id=annotation.predicate_document_id,
                                                                 predicate_language=annotation.predicate_language,
                                                                 username=user, name_space=name_space,
                                                                 concept_url=concept, name=area,
                                                                 predicate_start=annotation.predicate_start,
                                                                 predicate_stop=annotation.predicate_stop,
                                                                 subject_start=annotation.subject_start,
                                                                 subject_stop=annotation.subject_stop)
                    if not rels.exists():
                        RelationshipObjConcept.objects.create(subject_document_id=annotation.subject_document_id,
                                                              subject_language=annotation.subject_language,
                                                              insertion_time=Now(),
                                                              predicate_document_id=annotation.predicate_document_id,
                                                              predicate_language=annotation.predicate_language,
                                                              username=user, name_space=name_space,
                                                              concept_url=concept, name=area,
                                                              predicate_start=annotation.predicate_start,
                                                              predicate_stop=annotation.predicate_stop,
                                                              subject_start=annotation.subject_start,
                                                              subject_stop=annotation.subject_stop)

                for annotation in Link.objects.filter(subject_document_id=document.document_id,
                                                      username=user_source,
                                                      name_space=name_space,
                                                      subject_language=language):

                    rels = Link.objects.filter(subject_document_id=annotation.subject_document_id,
                                               subject_language=annotation.subject_language,
                                               predicate_document_id=annotation.predicate_document_id,
                                               predicate_language=annotation.predicate_language,
                                               object_document_id=annotation.object_document_id,
                                               object_language=annotation.object_language,
                                               username=user, name_space=name_space,
                                               subject_start=annotation.subject_start,
                                               subject_stop=annotation.subject_stop,
                                               predicate_start=annotation.predicate_start,
                                               predicate_stop=annotation.predicate_stop,
                                               object_start=annotation.object_start,
                                               object_stop=annotation.object_stop)
                    if not rels.exists():
                        Link.objects.filter(subject_document_id=annotation.subject_document_id,
                                            subject_language=annotation.subject_language,
                                            predicate_document_id=annotation.predicate_document_id,
                                            predicate_language=annotation.predicate_language,
                                            object_document_id=annotation.object_document_id,
                                            object_language=annotation.object_language,
                                            username=user, name_space=name_space,
                                            subject_start=annotation.subject_start, insertion_time=Now(),
                                            subject_stop=annotation.subject_stop,
                                            predicate_start=annotation.predicate_start,
                                            predicate_stop=annotation.predicate_stop,
                                            object_start=annotation.object_start,
                                            object_stop=annotation.object_stop)

        update_gt(user, name_space, document, language,topic)
        return JsonResponse({'msg': 'ok'})
    except Exception as e:
        json_resp = {'error': e}

        print(e)
        return JsonResponse(json_resp)


# from .autotron.parser import parser_auto
# from RelAnno import tron
# def autotron_annotation(request):
#
#     username = request.session['username']
#     name_space = request.session['name_space']
#     document = request.session['document']
#     language = request.session['language']
#     collection = request.session['collection']
#
#     name_space = NameSpace.objects.get(name_space = name_space)
#     user = User.objects.get(username = username, name_space = name_space)
#     document = Document.objects.get(document_id = document, language = language)
#
#     try:
#             if request.method == 'POST':
#                 body_req = json.loads(request.body)
#                 task = body_req['task']
#                 if document.provenance.lower() != 'pubmed':
#                     # tron.updateTask(task)
#                     doc_id = (document.document_id.split('_pubmed')[0].strip())
#                     # annotation = tron.annotate(doc_id)
#                     # annotation = {'title': {'text': "Alterations in brain 5-hydroxytryptamine metabolism during the 'withdrawal' phase after chronic treatment with diazepam and bromazepam.", 'concepts': [], 'relations': []}, 'abstract': {'text': '1 Daily administration of diazepam or bromazepam (10 mg/kg) for 22 days significantly increased the activity of mid-brain tryptophan hydroxylase by 36% and 39%, respectively. The concentration of tryptophan was also enhanced in the mid-brain region of rats subjected to benzodiazepine treatment.2 Chronic therapy with either of the two anti-anxiety agents enhanced the endogenous levels of 5-hydroxytryptamine and 5-hydroxyindoleacetic acid in cerebral cortex, hypothalamus, pons-medulla, mid-brain and striatum.3 Whereas diazepam treatment decreased (13%) the activity of monoamine oxidase in mid-brain, bromazepam failed to exert any effect, suggesting that the observed elevation in 5-hydroxy-indoleacetic acid levels is not associated with enhanced deamination of 5-hydroxytryptamine.4 Discontinuation of treatment for 48 h significantly decreased the activity of mid-brain tryptophan hydroxylase to levels that were significantly lower than those seen for benzodiazepine-treated and normal rats. The concentrations of mid-brain tryptophan and 5-hydroxytryptamine were also reduced in various brain regions examined.5 Withdrawal from diazepam or bromazepam therapy further augmented the levels of brain 5-hydroxyindoleacetic acid.6 The results demonstrate that the depressant effects on behaviour of these agents are accompanied by increased metabolism of 5-hydroxytryptamine in the brain. Withdrawal from these minor tranquillizers, on the other hand, reduces the synthesis of this indoleamine.', 'concepts': [{'id': 'D007029', 'name': 'D007029', 'type': 'Disease', 'pos': [461, 12]}], 'relations': []}}
#                     print(annotation)
#                     # annotation = {'title': {'text': 'In search of triple-negative DCIS: tumor-type dependent model of breast cancer progression from DCIS to the invasive cancer.', 'concepts': [{'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [35, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [65, 13]}, {'id': 'D009362', 'name': 'D009362', 'type': 'Disease', 'pos': [108, 15]}], 'relations': []}, 'abstract': {'text': 'This paper is based on the idea that ductal breast cancer in situ (DCIS) precedes the invasive breast cancer (invBC), although the triple-negative invBCs almost lack their DCIS precursor. Reported incidences of breast tumor types in DCIS and in invasive BCs suggest that probabilities of tumor progression might differ among tumor types, and these differences can have some impact on our patients. Reported data from several papers on incidences of the four breast tumor types-luminal A, luminal B, HER2, and triple negative-are used to compare tumor-type incidences for DCIS and for the invasive BC. The pooled distributions differed (Chi                 (2) = 97.05, p < 0.0001), suggesting a strong selection pressure that reduces the number of triple-negative DCIS lesions at the time of breast tumor diagnosis. Reported shares of DCIS in all newly diagnosed breast cancers range in large screening trials from 9 to 26 %, so in making a population model, three values are arbitrarily chosen: one DCIS out of ten breast cancers (the 10 % share), one DCIS out of seven breast cancers (one seventh or the 14.3 % share), and one out of five (the 20 % share). By using these shares and the pooled data of tumor-type incidences, values are calculated that would be expected from a hypothetical population in which types of DCIS and invasive BC are distributed accordingly to the reported incidences. The model predicts that the shares of breast cancer tumor types in the modeled population (DCIS plus invasive BCs) are 39 % for luminal A, 20 % for luminal B, 11 % for HER2 positive, and 30 % for the triple-negative cancers. Some 59 % of all breast tumors are expected to be hormone receptor positive, and HER2 to be overexpressed in 31 %. Simulated probabilities of tumor progression were used to calculate the number of tumor progression t(1/2) that has passed before the time of diagnosis. Calculated relative t(1/2) durations in the modeled population suggest that the triple-negative DCIS cases were fastest in tumor progression, three times faster than the HER2-positive tumors and near twice as fast as luminal A. Luminal A is the model slower than luminal B DCIS, suggesting that although their progression depends on estrogen exposure, HER2 overexpression in luminal B tumors adds some speed in tumor progression. The model results suggest that quick tumor progression might be the main feature of the triple-negative breast tumors, leading to seldom triple-negative DCIS at the time of breast cancer diagnosis. Applying approach of the presented model to the real data from a well-defined population seems warranted.', 'concepts': [{'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [44, 13]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [86, 22]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [110, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [211, 12]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [288, 5]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [325, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [458, 12]}, {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [499, 4]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [545, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [792, 12]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [863, 14]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1016, 14]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1071, 14]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1204, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1436, 19]}, {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [1566, 4]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1614, 7]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1640, 13]}, {'id': '3164', 'name': 'NR4A1', 'type': 'Gene', 'pos': [1673, 16]}, {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [1704, 4]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1765, 5]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1820, 5]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2014, 5]}, {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [2061, 4]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2075, 6]}, {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [2243, 4]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2302, 5]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2358, 5]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [2425, 13]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [2494, 13]}], 'relations': [{'subject': {'id': '3164', 'name': 'NR4A1', 'type': 'Gene', 'pos': [1673, 16]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1640, 13]}}, {'subject': {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [1704, 4]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1640, 13]}}, {'subject': {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [2243, 4]}, 'predicate': {'id': '', 'name': 'Oncogene', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2014, 5]}}, {'subject': {'id': '2064', 'name': 'ERBB2', 'type': 'Gene', 'pos': [2243, 4]}, 'predicate': {'id': '', 'name': 'Oncogene', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2075, 6]}}]}}
#                     # annotation = {'title': {'text': 'Change of Circulating and Tissue-Based miR-20a in Human Cancers and Associated Prognostic Implication: A Systematic Review and Meta-Analysis.', 'concepts': [{'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [39, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [56, 7]}], 'relations': []}, 'abstract': {'text': "Background: Previous literatures have investigated the change of miR-20a expression level in the progression of multiple cancers and its influence on patients' survival outcome, but results of now-available evidence are inconsistent. Objective: To elucidate the prognostic value of circulating and tissue-based miR-20a for patients with various cancers. Methods: A systematic search and review of eligible publications were carried out in three electronic databases including the Cochrane Library, PubMed, and Embase, and the methodological quality of included studies was assessed according to Newcastle-Ottawa Scale (NOS). Hazard ratios (HRs) and corresponding 95% confidence intervals (CIs) for overall survival (OS), recurrence-free survival (RFS), disease-free survival (DFS), and progressive-free survival (PFS) of each study were pooled using a random effect model. Results: In total, 24 studies involving 4186 samples of multiple cancers published in 20 articles were included in the statistical analysis. As for circulating miR-20a, five kinds of cancers containing gastric cancer, lymphoma, glioblastoma, prostate cancer, and non-small-cell lung cancer reported upregulated level in patients compared with normal healthy control, and overexpressed circulating miR-20a could confer an unfavorable factor for OS (HR = 1.71, 95% CIs: 1.43 -2.04, p < 0.01) and DFS (HR = 1.90, 95% CIs: 1.45-2.49, p < 0.01). As for tissue-based samples, 6 kinds of malignancies including colorectal cancer, salivary adenoid cystic carcinoma, gallbladder carcinoma, colon cancer, gastrointestinal cancer, and alveolar rhabdomyosarcoma revealed upregulated miR-20a expression level compared with paired nontumorous tissue, of which high expression of miR-20a was significantly associated with poor OS (HR = 2.74, 95% CIs: 1.38-5.42, p < 0.01) and DFS (HR = 2.68, 95% CIs: 1.32-5.45, p < 0.01); meanwhile, other 5 tumors containing breast cancer, cutaneous squamous cell carcinoma, hepatocellular carcinoma, oral squamous cell carcinoma, and epithelial ovarian cancer demonstrated downregulated miR-20a expression level compared with benign tissue, of which low miR-20a expression was significantly related to shorter OS (HR = 3.48, 95% CIs: 2.00-6.06, p < 0.01) and PFS/RFS (HR = 4.05, 95% CIs: 2.89-5.66, p < 0.01). Conclusion: Change of circulating and tissue-based miR-20a expression possesses vital prognostic implication for human cancers. Augmented expression of circulating miR-20a predicts poor survival outcome for patients with cancers. Tissue-based miR-20a level may be upregulated or downregulated depending on cancer types; in the former condition, high expression of tissue miR-20a is a risk factor for unfavorable prognosis and in the latter condition low expression of tissue miR-20a is associated with shorter survival.", 'concepts': [{'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [65, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [121, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [311, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [345, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [938, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1056, 7]}, {'id': 'D013274', 'name': 'D013274', 'type': 'Disease', 'pos': [1075, 14]}, {'id': 'D008223', 'name': 'D008223', 'type': 'Disease', 'pos': [1091, 8]}, {'id': 'D005909', 'name': 'D005909', 'type': 'Disease', 'pos': [1101, 12]}, {'id': 'D011471', 'name': 'D011471', 'type': 'Disease', 'pos': [1115, 15]}, {'id': 'D002289', 'name': 'D002289', 'type': 'Disease', 'pos': [1136, 26]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1454, 12]}, {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1477, 17]}, {'id': 'D003528', 'name': 'D003528', 'type': 'Disease', 'pos': [1496, 33]}, {'id': 'D005706', 'name': 'D005706', 'type': 'Disease', 'pos': [1531, 21]}, {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1554, 12]}, {'id': 'D004067', 'name': 'D004067', 'type': 'Disease', 'pos': [1568, 23]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1900, 6]}, {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1918, 13]}, {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1933, 33]}, {'id': 'D006528', 'name': 'D006528', 'type': 'Disease', 'pos': [1968, 24]}, {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1994, 28]}, {'id': 'D000077216', 'name': 'D000077216', 'type': 'Disease', 'pos': [2028, 25]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2355, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2423, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2468, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2525, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2547, 7]}, {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2610, 6]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2675, 7]}, {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2779, 7]}], 'relations': [{'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1056, 7]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D013274', 'name': 'D013274', 'type': 'Disease', 'pos': [1075, 14]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D008223', 'name': 'D008223', 'type': 'Disease', 'pos': [1091, 8]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005909', 'name': 'D005909', 'type': 'Disease', 'pos': [1101, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D011471', 'name': 'D011471', 'type': 'Disease', 'pos': [1115, 15]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1033, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002289', 'name': 'D002289', 'type': 'Disease', 'pos': [1136, 26]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1056, 7]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D013274', 'name': 'D013274', 'type': 'Disease', 'pos': [1075, 14]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D008223', 'name': 'D008223', 'type': 'Disease', 'pos': [1091, 8]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005909', 'name': 'D005909', 'type': 'Disease', 'pos': [1101, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D011471', 'name': 'D011471', 'type': 'Disease', 'pos': [1115, 15]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1270, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002289', 'name': 'D002289', 'type': 'Disease', 'pos': [1136, 26]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1454, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1477, 17]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D003528', 'name': 'D003528', 'type': 'Disease', 'pos': [1496, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005706', 'name': 'D005706', 'type': 'Disease', 'pos': [1531, 21]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1554, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D004067', 'name': 'D004067', 'type': 'Disease', 'pos': [1568, 23]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1900, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1918, 13]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1933, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D006528', 'name': 'D006528', 'type': 'Disease', 'pos': [1968, 24]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1994, 28]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1644, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D000077216', 'name': 'D000077216', 'type': 'Disease', 'pos': [2028, 25]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1454, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1477, 17]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D003528', 'name': 'D003528', 'type': 'Disease', 'pos': [1496, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005706', 'name': 'D005706', 'type': 'Disease', 'pos': [1531, 21]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1554, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D004067', 'name': 'D004067', 'type': 'Disease', 'pos': [1568, 23]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1900, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1918, 13]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1933, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D006528', 'name': 'D006528', 'type': 'Disease', 'pos': [1968, 24]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1994, 28]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [1738, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D000077216', 'name': 'D000077216', 'type': 'Disease', 'pos': [2028, 25]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1454, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1477, 17]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D003528', 'name': 'D003528', 'type': 'Disease', 'pos': [1496, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005706', 'name': 'D005706', 'type': 'Disease', 'pos': [1531, 21]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1554, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D004067', 'name': 'D004067', 'type': 'Disease', 'pos': [1568, 23]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1900, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1918, 13]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1933, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D006528', 'name': 'D006528', 'type': 'Disease', 'pos': [1968, 24]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1994, 28]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2081, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D000077216', 'name': 'D000077216', 'type': 'Disease', 'pos': [2028, 25]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1454, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1477, 17]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D003528', 'name': 'D003528', 'type': 'Disease', 'pos': [1496, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D005706', 'name': 'D005706', 'type': 'Disease', 'pos': [1531, 21]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D015179', 'name': 'D015179', 'type': 'Disease', 'pos': [1554, 12]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D004067', 'name': 'D004067', 'type': 'Disease', 'pos': [1568, 23]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [1900, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D001943', 'name': 'D001943', 'type': 'Disease', 'pos': [1918, 13]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1933, 33]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D006528', 'name': 'D006528', 'type': 'Disease', 'pos': [1968, 24]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D002294', 'name': 'D002294', 'type': 'Disease', 'pos': [1994, 28]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2148, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D000077216', 'name': 'D000077216', 'type': 'Disease', 'pos': [2028, 25]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2468, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2525, 7]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2547, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2610, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2675, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2610, 6]}}, {'subject': {'id': '406982', 'name': 'MIR20A', 'type': 'Gene', 'pos': [2779, 7]}, 'predicate': {'id': '', 'name': 'Biomarker', 'type': 'GCA'}, 'object': {'id': 'D009369', 'name': 'D009369', 'type': 'Disease', 'pos': [2610, 6]}}]}}
#
#                     parser_auto(user, collection, document, annotation, pubmed=True)
#                 else:
#                     # tron.updateTask(task)
#                     annotation = {'text': {'text': 'This paper is based on the idea that ductal breast cancer in situ (DCIS) precedes the invasive breast cancer (invBC), although the triple-negative invBCs almost lack their DCIS precursor. Reported incidences of breast tumor types in DCIS and in invasive BCs suggest that probabilities of tumor progression might differ among tumor types, and these differences can have some impact on our patients. Reported data from several papers on incidences of the four breast tumor types-luminal A, luminal B, HER2, and triple negative-are used to compare tumor-type incidences for DCIS and for the invasive BC. The pooled distributions differed (Chi                 (2) = 97.05, p < 0.0001), suggesting a strong selection pressure that reduces the number of triple-negative DCIS lesions at the time of breast tumor diagnosis. Reported shares of DCIS in all newly diagnosed breast cancers range in large screening trials from 9 to 26 %, so in making a population model, three values are arbitrarily chosen: one DCIS out of ten breast cancers (the 10 % share), one DCIS out of seven breast cancers (one seventh or the 14.3 % share), and one out of five (the 20 % share). By using these shares and the pooled data of tumor-type incidences, values are calculated that would be expected from a hypothetical population in which types of DCIS and invasive BC are distributed accordingly to the reported incidences. The model predicts that the shares of breast cancer tumor types in the modeled population (DCIS plus invasive BCs) are 39 % for luminal A, 20 % for luminal B, 11 % for HER2 positive, and 30 % for the triple-negative cancers. Some 59 % of all breast tumors are expected to be hormone receptor positive, and HER2 to be overexpressed in 31 %. Simulated probabilities of tumor progression were used to calculate the number of tumor progression t(1/2) that has passed before the time of diagnosis. Calculated relative t(1/2) durations in the modeled population suggest that the triple-negative DCIS cases were fastest in tumor progression, three times faster than the HER2-positive tumors and near twice as fast as luminal A. Luminal A is the model slower than luminal B DCIS, suggesting that although their progression depends on estrogen exposure, HER2 overexpression in luminal B tumors adds some speed in tumor progression. The model results suggest that quick tumor progression might be the main feature of the triple-negative breast tumors, leading to seldom triple-negative DCIS at the time of breast cancer diagnosis. Applying approach of the presented model to the real data from a well-defined population seems warranted.', 'concepts': [{'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [67, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [172, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [51, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [102, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [233, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [218, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [288, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [325, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1412777', 'name': 'BCS1L gene', 'score': '0.46', 'type': 'Gene', 'pos': [254, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1825598', 'name': 'IMPACT gene', 'score': '0.46', 'type': 'Gene', 'pos': [374, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1647, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [571, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [465, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [545, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '0.92', 'type': 'Gene', 'pos': [567, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '0.92', 'type': 'Gene', 'pos': [580, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [477, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [488, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [1321, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1204, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [1489, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1522, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1542, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1562, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1590, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1443, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1614, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1412777', 'name': 'BCS1L gene', 'score': '0.46', 'type': 'Gene', 'pos': [1508, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [1526, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [1546, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1450, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [764, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [799, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [2474, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [2358, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [2432, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [2501, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [1987, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [2164, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2014, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2075, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2276, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2302, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2108, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2119, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2154, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2266, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1765, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1820, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [835, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [1000, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [1053, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [870, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [1023, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [1078, 7]}], 'relations': []}}
#
#                     for key,value in document.document_content.items():
#                         # annotation = tron.annotate(value)
#                         # print(annotation)
#                         if key == 'abstract':
#                             parser_auto(user, collection, document, annotation, pubmed=False,position = key)
#                 update_gt(user,name_space,document,language)
#
#                 return JsonResponse({"msg":"ok"})
#
#     except Exception as e:
#         print(e)
#         JsonResponse({"error": e})

# def autotron_annotation(request):
#     return HttpResponse(status = 500)

# from .autotron.parser import parser_auto
# from RelAnno import tron


def autotron_annotation(request):
    return JsonResponse({'msg':'ok'})
    # username = request.session['username']
    # name_space = request.session['name_space']
    # document = request.session['document']
    # language = request.session['language']
    # collection = request.session['collection']
    #
    # name_space = NameSpace.objects.get(name_space=name_space)
    # user = User.objects.get(username=username, name_space=name_space)
    # document = Document.objects.get(document_id=document, language=language)
    # #
    # try:
    #     if request.method == 'POST':
    #         body_req = json.loads(request.body)
    #         task = body_req['task']
    #         tron.updateTask(task)
    #         # print()
    #         if document.provenance.lower() == 'pubmed':
    #             doc_id = (document.document_content['document_id'].split('pubmed_')[1].strip())
    #             # print(doc_id)
    #             annotation = tron.annotate(doc_id)
    #
    #             parser_auto(user, collection, document, annotation, pubmed=True)
    #         else:
    #             # annotation = {'text': {'text': 'This paper is based on the idea that ductal breast cancer in situ (DCIS) precedes the invasive breast cancer (invBC), although the triple-negative invBCs almost lack their DCIS precursor. Reported incidences of breast tumor types in DCIS and in invasive BCs suggest that probabilities of tumor progression might differ among tumor types, and these differences can have some impact on our patients. Reported data from several papers on incidences of the four breast tumor types-luminal A, luminal B, HER2, and triple negative-are used to compare tumor-type incidences for DCIS and for the invasive BC. The pooled distributions differed (Chi                 (2) = 97.05, p < 0.0001), suggesting a strong selection pressure that reduces the number of triple-negative DCIS lesions at the time of breast tumor diagnosis. Reported shares of DCIS in all newly diagnosed breast cancers range in large screening trials from 9 to 26 %, so in making a population model, three values are arbitrarily chosen: one DCIS out of ten breast cancers (the 10 % share), one DCIS out of seven breast cancers (one seventh or the 14.3 % share), and one out of five (the 20 % share). By using these shares and the pooled data of tumor-type incidences, values are calculated that would be expected from a hypothetical population in which types of DCIS and invasive BC are distributed accordingly to the reported incidences. The model predicts that the shares of breast cancer tumor types in the modeled population (DCIS plus invasive BCs) are 39 % for luminal A, 20 % for luminal B, 11 % for HER2 positive, and 30 % for the triple-negative cancers. Some 59 % of all breast tumors are expected to be hormone receptor positive, and HER2 to be overexpressed in 31 %. Simulated probabilities of tumor progression were used to calculate the number of tumor progression t(1/2) that has passed before the time of diagnosis. Calculated relative t(1/2) durations in the modeled population suggest that the triple-negative DCIS cases were fastest in tumor progression, three times faster than the HER2-positive tumors and near twice as fast as luminal A. Luminal A is the model slower than luminal B DCIS, suggesting that although their progression depends on estrogen exposure, HER2 overexpression in luminal B tumors adds some speed in tumor progression. The model results suggest that quick tumor progression might be the main feature of the triple-negative breast tumors, leading to seldom triple-negative DCIS at the time of breast cancer diagnosis. Applying approach of the presented model to the real data from a well-defined population seems warranted.', 'concepts': [{'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [67, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [172, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [51, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [102, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [233, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [218, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [288, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [325, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1412777', 'name': 'BCS1L gene', 'score': '0.46', 'type': 'Gene', 'pos': [254, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1825598', 'name': 'IMPACT gene', 'score': '0.46', 'type': 'Gene', 'pos': [374, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1647, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [571, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [465, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [545, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '0.92', 'type': 'Gene', 'pos': [567, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '0.92', 'type': 'Gene', 'pos': [580, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [477, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [488, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [1321, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1204, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [1489, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1522, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1542, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1562, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C4321252', 'name': 'WWOX wt Allele', 'score': '1.84', 'type': 'Gene', 'pos': [1590, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1443, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1614, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C1412777', 'name': 'BCS1L gene', 'score': '0.46', 'type': 'Gene', 'pos': [1508, 3]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [1526, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.46', 'type': 'Disease', 'pos': [1546, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [1450, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [764, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [799, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '8.29', 'type': 'Disease', 'pos': [2474, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [2358, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [2432, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '0.46', 'type': 'Disease', 'pos': [2501, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [1987, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '16.58', 'type': 'Disease', 'pos': [2164, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2014, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2075, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2276, 6]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '1.84', 'type': 'Disease', 'pos': [2302, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2108, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642345', 'name': 'Luminal A Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2119, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2154, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C3642346', 'name': 'Luminal B Breast Carcinoma', 'score': '0.92', 'type': 'Disease', 'pos': [2266, 9]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1765, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0027651', 'name': 'Neoplasms', 'score': '0.92', 'type': 'Disease', 'pos': [1820, 5]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [835, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [1000, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0007124', 'name': 'Noninfiltrating Intraductal Carcinoma', 'score': '24.86', 'type': 'Disease', 'pos': [1053, 4]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [870, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [1023, 7]}, {'id': 'http://linkedlifedata.com/resource/umls/id/C0006826', 'name': 'Malignant Neoplasms', 'score': '1.38', 'type': 'Disease', 'pos': [1078, 7]}], 'relations': []}}
    #
    #             for key, value in document.document_content.items():
    #
    #                 if key == 'abstract':
    #                     # print(key)
    #                     annotation = tron.annotate(value)
    #                     # print(annotation)
    #                     if annotation['text']['concepts'] != [] or annotation['text']['relations'] != []:
    #                         parser_auto(user, collection, document, annotation, pubmed=False, position=key)
    #         update_gt(user, name_space, document, language,topic)
    #
    #         return JsonResponse({"msg": "ok"})
    #
    # except Exception as e:
    #     print(e)
    #     JsonResponse({"error": e})


def get_suggestion(request):
    """This view given a mention provides suggestions"""

    username = request.session['username']
    name_space = request.session['name_space']
    document = request.session['document']
    topic = request.session['topic']
    language = request.session['language']
    if request.method == 'POST':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        topic = Topic.objects.get(id=topic)
        document = Document.objects.get(document_id=document, language=language)
        json_body = json.loads(request.body)
        association = json_body.get('association', None)
        relation = json_body.get('relation', None)
        try:
            with transaction.atomic():
                if association is not None:
                    start = association['start']
                    stop = association['stop']
                    position = association['position']
                    start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                    concept = association['concept_url']
                    name = association['concept_area']
                    mention = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
                    concept = Concept.objects.get(concept_url=concept)
                    area = SemanticArea.objects.get(name=name)

                    if not Associate.objects.filter(username=user, name_space=name_space, document_id=document,
                                                    language=language,topic_id=topic,
                                                    start=mention, stop=mention.stop, concept_url=concept,
                                                    name=area).exists():
                        Associate.objects.create(username=user, name_space=name_space, document_id=document,
                                                 language=language, insertion_time=Now(),topic_id=topic,
                                                 start=mention, stop=mention.stop, concept_url=concept, name=area)
                    update_gt(user, name_space, document, language,topic)
                    json_to_ret = {}
                    json_to_ret['tags'] = generate_tag_list_splitted(username, name_space.name_space,
                                                                     document.document_id, language,topic.id)
                    json_to_ret['concepts'] = generate_associations_list_splitted(username, name_space.name_space,
                                                                                  document.document_id, language,topic.id)
                    rels = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                       document.language,topic.id)
                    # json_to_ret['relationships'] = transform_relationships_list(rels, document.document_id, username,
                    #                                                             name_space.name_space)
                    json_to_ret['relationships'] = rels
                    return JsonResponse(json_to_ret)
                elif relation is not None:
                    subject = relation['subject']
                    predicate = relation['predicate']
                    object = relation['object']
                    if subject['mention'] != {} and predicate['mention'] != {} and object['mention'] != {}:
                        mention_s = subject['mention']
                        mention_p = predicate['mention']
                        mention_o = object['mention']
                        mention_s_start, mention_s_stop = return_start_stop_for_backend(mention_s['start'],
                                                                                        mention_s['stop'],
                                                                                        mention_s['position'],
                                                                                        document.document_content)
                        mention_p_start, mention_p_stop = return_start_stop_for_backend(mention_p['start'],
                                                                                        mention_p['stop'],
                                                                                        mention_p['position'],
                                                                                        document.document_content)
                        mention_o_start, mention_o_stop = return_start_stop_for_backend(mention_o['start'],
                                                                                        mention_o['stop'],
                                                                                        mention_o['position'],
                                                                                        document.document_content)

                        mention_s_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_s_start, stop=mention_s_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        mention_p_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_p_start, stop=mention_p_stop)
                        if not Annotate.objects.filter(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        mention_o_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_o_start, stop=mention_o_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_o_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_o_obj, stop=mention_o_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        if not Link.objects.filter(username=user, name_space=name_space,
                                                   subject_document_id=document.document_id,
                                                   subject_language=document.language, subject_start=mention_s_start,
                                                   subject_stop=mention_s_stop,topic_id=topic,
                                                   predicate_start=mention_p_start, predicate_stop=mention_p_stop,
                                                   object_start=mention_o_start,
                                                   object_stop=mention_o_stop).exists():
                            Link.objects.create(username=user, name_space=name_space,topic_id=topic,
                                                subject_document_id=document.document_id,
                                                object_document_id=document.document_id,
                                                predicate_document_id=document.document_id,
                                                subject_language=document.language, object_language=document.language,
                                                predicate_language=document.language, subject_start=mention_s_start,
                                                subject_stop=mention_s_stop,
                                                predicate_start=mention_p_start, predicate_stop=mention_p_stop,
                                                object_start=mention_o_start, insertion_time=Now(),
                                                object_stop=mention_o_stop)

                    if subject['mention'] != {} and predicate['mention'] != {} and object['concept'] != {}:
                        mention_s = subject['mention']
                        mention_p = predicate['mention']

                        mention_s_start, mention_s_stop = return_start_stop_for_backend(mention_s['start'],
                                                                                        mention_s['stop'],
                                                                                        mention_s['position'],
                                                                                        document.document_content)
                        mention_p_start, mention_p_stop = return_start_stop_for_backend(mention_p['start'],
                                                                                        mention_p['stop'],
                                                                                        mention_p['position'],
                                                                                        document.document_content)

                        mention_s_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_s_start, stop=mention_s_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        mention_p_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_p_start, stop=mention_p_stop)
                        if not Annotate.objects.filter(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        concept = Concept.objects.get(concept_url=object['concept']['concept_url'])
                        area = SemanticArea.objects.get(name=object['concept']['concept_area'])
                        if not RelationshipObjConcept.objects.filte(username=user, name_space=name_space,
                                                                    subject_document_id=document.document_id,
                                                                    subject_language=document.language,
                                                                    subject_start=mention_s_start,
                                                                    subject_stop=mention_s_stop,
                                                                    predicate_start=mention_p_start,topic_id=topic,
                                                                    predicate_stop=mention_p_stop, concept_url=concept,
                                                                    name=area).exists():
                            RelationshipObjConcept.objects.create(username=user, name_space=name_space,
                                                                  subject_document_id=document.document_id,
                                                                  predicate_document_id=document.document_id,
                                                                  subject_language=document.language,
                                                                  insertion_time=Now(),topic_id=topic,
                                                                  predicate_language=document.language,
                                                                  subject_start=mention_s_start,
                                                                  subject_stop=mention_s_stop,
                                                                  predicate_start=mention_p_start,
                                                                  predicate_stop=mention_p_stop,
                                                                  concept_url=concept, name=area)

                    if subject['mention'] == {} and predicate['concept'] != {} and object['mention'] != {}:
                        mention_s = subject['mention']
                        mention_o = object['mention']
                        mention_s_start, mention_s_stop = return_start_stop_for_backend(mention_s['start'],
                                                                                        mention_s['stop'],
                                                                                        mention_s['position'],
                                                                                        document.document_content)

                        mention_o_start, mention_o_stop = return_start_stop_for_backend(mention_o['start'],
                                                                                        mention_o['stop'],
                                                                                        mention_o['position'],
                                                                                        document.document_content)

                        mention_s_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_s_start, stop=mention_s_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_s_obj, stop=mention_s_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        mention_o_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_o_start, stop=mention_o_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_o_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_o_obj, stop=mention_o_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)
                        concept = Concept.objects.get(concept_url=predicate['concept']['concept_url'])
                        area = SemanticArea.objects.get(name=predicate['concept']['concept_area'])
                        if not RelationshipPredConcept.objects.filte(username=user, name_space=name_space,
                                                                     subject_document_id=document.document_id,
                                                                     subject_language=document.language,
                                                                     subject_start=mention_s_start,
                                                                     subject_stop=mention_s_stop,topic_id=topic,
                                                                     object_start=mention_o_start,
                                                                     object_stop=mention_o_stop,
                                                                     concept_url=concept,
                                                                     name=area).exists():
                            RelationshipPredConcept.objects.create(username=user, name_space=name_space,
                                                                   subject_document_id=document.document_id,
                                                                   object_document_id=document.document_id,
                                                                   subject_language=document.language,topic_id=topic,
                                                                   insertion_time=Now(),
                                                                   object_language=document.language,
                                                                   subject_start=mention_s_start,
                                                                   subject_stop=mention_s_stop,
                                                                   object_start=mention_o_start,
                                                                   object_stop=mention_o_stop,
                                                                   concept_url=concept, name=area)
                    if subject['concept'] != {} and predicate['mention'] != {} and object['mention'] != {}:
                        mention_p = predicate['mention']
                        mention_o = object['mention']

                        mention_p_start, mention_p_stop = return_start_stop_for_backend(mention_p['start'],
                                                                                        mention_p['stop'],
                                                                                        mention_p['position'],
                                                                                        document.document_content)
                        mention_o_start, mention_o_stop = return_start_stop_for_backend(mention_o['start'],
                                                                                        mention_o['stop'],
                                                                                        mention_o['position'],
                                                                                        document.document_content)

                        mention_p_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_p_start, stop=mention_p_stop)
                        if not Annotate.objects.filter(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_p_obj, stop=mention_p_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        mention_o_obj = Mention.objects.get(document_id=document, language=language,
                                                            start=mention_o_start, stop=mention_o_stop)
                        if not Annotate.objects.filter(start=mention_s_obj, stop=mention_o_stop, document_id=document,
                                                       language=language, username=user,topic_id=topic,
                                                       name_space=name_space).exists():
                            Annotate.objects.create(start=mention_o_obj, stop=mention_o_stop, document_id=document,
                                                    insertion_time=Now(),topic_id=topic,
                                                    language=language, username=user, name_space=name_space)

                        concept = Concept.objects.get(concept_url=subject['concept']['concept_url'])
                        area = SemanticArea.objects.get(name=subject['concept']['concept_area'])

                        if not RelationshipSubjConcept.objects.filte(username=user, name_space=name_space,
                                                                     predicate_document_id=document.document_id,
                                                                     predicate_language=document.language,
                                                                     predicate_start=mention_p_start,
                                                                     predicate_stop=mention_p_stop,
                                                                     object_start=mention_o_start,
                                                                     object_stop=mention_o_stop,
                                                                     concept_url=concept,topic_id=topic,
                                                                     name=area).exists():
                            RelationshipSubjConcept.objects.create(username=user, name_space=name_space,
                                                                   predicate_document_id=document.document_id,
                                                                   object_document_id=document.document_id,
                                                                   predicate_language=document.language,
                                                                   insertion_time=Now(),topic_id=topic,
                                                                   object_language=document.language,
                                                                   predicate_start=mention_p_start,
                                                                   predicate_stop=mention_p_stop,
                                                                   object_start=mention_o_start,
                                                                   object_stop=mention_o_stop,
                                                                   concept_url=concept,
                                                                   name=area)
                    if subject['concept'] != {} and predicate['concept'] != {} and object['mention'] != {}:
                        start, stop = object['mention']['start'], object['mention']['stop']
                        position = object['mention']['position']
                        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                        mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
                        if not Annotate.objects.filter(username=user, name_space=name_space, start=mention,topic_id=topic,
                                                       stop=mention.stop).exists():
                            Annotate.objects.create(username=user, name_space=name_space, start=mention,
                                                    insertion_time=Now(),topic_id=topic,
                                                    stop=mention.stop)
                        concept_su = subject['concept']
                        concept_pr = predicate['concept']

                        if not RelationshipObjMention.objects.filter(username=user, name_space=name_space,
                                                                     document_id=document, language=language,
                                                                     start=mention, stop=mention.stop,topic_id=topic,
                                                                     subject_concept_url=concept_su['concept_url'],
                                                                     subject_name=concept_su['concept_area'],
                                                                     predicate_concept_url=concept_pr['concept_url'],
                                                                     predicate_name=concept_pr['concept_area']
                                                                     ).exists():
                            RelationshipObjMention.objects.create(username=user, name_space=name_space,
                                                                  insertion_time=Now(),topic_id=topic,
                                                                  document_id=document, language=language,
                                                                  start=mention, stop=mention.stop,
                                                                  subject_concept_url=concept_su['concept_url'],
                                                                  subject_name=concept_su['concept_area'],
                                                                  predicate_concept_url=concept_pr['concept_url'],
                                                                  predicate_name=concept_pr['concept_area']
                                                                  )
                    if subject['mention'] != {} and predicate['concept'] != {} and object['concept'] != {}:
                        start, stop = subject['mention']['start'], subject['mention']['stop']
                        position = subject['mention']['position']
                        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                        mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
                        if not Annotate.objects.filter(username=user, name_space=name_space, start=mention,topic_id=topic,
                                                       stop=mention.stop).exists():
                            Annotate.objects.create(username=user, name_space=name_space, start=mention,topic_id=topic,
                                                    insertion_time=Now(),
                                                    stop=mention.stop)
                        concept_obj = object['concept']
                        concept_pr = predicate['concept']

                        if not RelationshipSubjMention.objects.filter(username=user, name_space=name_space,
                                                                      document_id=document, language=language,
                                                                      start=mention,topic_id=topic,
                                                                      stop=mention.stop,
                                                                      object_concept_url=concept_obj['concept_url'],
                                                                      object_name=concept_obj['concept_area'],
                                                                      predicate_concept_url=concept_pr['concept_url'],
                                                                      predicate_name=concept_pr['concept_area']
                                                                      ).exists():
                            RelationshipSubjMention.objects.create(username=user, name_space=name_space,
                                                                   insertion_time=Now(),topic_id=topic,
                                                                   document_id=document, language=language,
                                                                   start=mention,
                                                                   stop=mention.stop,
                                                                   object_concept_url=concept_obj['concept_url'],
                                                                   object_name=concept_obj['concept_area'],
                                                                   predicate_concept_url=concept_pr['concept_url'],
                                                                   predicate_name=concept_pr['concept_area']
                                                                   )
                    if subject['concept'] != {} and predicate['mention'] != {} and object['concept'] != {}:
                        start, stop = predicate['mention']['start'], predicate['mention']['stop']
                        position = predicate['mention']['position']
                        start, stop = return_start_stop_for_backend(start, stop, position, document.document_content)
                        mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)
                        if not Annotate.objects.filter(username=user, name_space=name_space, start=mention,topic_id=topic,
                                                       stop=mention.stop).exists():
                            Annotate.objects.create(username=user, name_space=name_space, start=mention,topic_id=topic,
                                                    insertion_time=Now(),
                                                    stop=mention.stop)
                        concept_obj = object['concept']
                        concept_s = subject['concept']

                        if not RelationshipPredMention.objects.filter(username=user, name_space=name_space,topic_id=topic,
                                                                      document_id=document, language=language,
                                                                      start=mention,
                                                                      stop=mention.stop,
                                                                      object_concept_url=concept_obj['concept_url'],
                                                                      object_name=concept_obj['concept_area'],
                                                                      subject_concept_url=concept_s['concept_url'],
                                                                      subject_name=concept_s['concept_area']
                                                                      ).exists():
                            RelationshipPredMention.objects.create(username=user, name_space=name_space,topic_id=topic,
                                                                   insertion_time=Now(),
                                                                   document_id=document, language=language,
                                                                   start=mention,
                                                                   stop=mention.stop,
                                                                   object_concept_url=concept_obj['concept_url'],
                                                                   object_name=concept_obj['concept_area'],
                                                                   subject_concept_url=concept_s['concept_url'],
                                                                   subject_name=concept_s['concept_area']
                                                                   )

                    update_gt(user, name_space, document, language,topic)
                    json_to_ret = {}
                    json_to_ret['concepts'] = generate_associations_list_splitted(username, name_space.name_space,
                                                                                  document.document_id, language,topic.id)
                    json_to_ret['tags'] = generate_tag_list_splitted(username, name_space.name_space,
                                                                     document.document_id, language,topic.id)
                    rels = generate_relationships_list(user.username, name_space.name_space, document.document_id,
                                                       document.language,topic.id)
                    # json_to_ret['relationships'] = transform_relationships_list(rels, document.document_id, username,
                    #                                                             name_space)
                    json_to_ret['relationships'] = rels
                    return JsonResponse(json_to_ret)
        except Exception as e:
            print(e)
            return JsonResponse({'error': e})


    elif request.method == 'GET':
        name_space = NameSpace.objects.get(name_space=name_space)
        user = User.objects.get(username=username, name_space=name_space)
        document = Document.objects.get(document_id=document, language=language)
        mention = request.GET.get('mention')
        mention1 = json.loads(mention)
        position = '_'.join(mention1['id'].split('_')[:-1])
        start, stop = return_start_stop_for_backend(mention1['start'], mention1['stop'], position,
                                                    document.document_content)
        mention = Mention.objects.get(start=start, stop=stop, document_id=document, language=language)

        suggested_annotations = {}
        suggested_annotations['associations'] = []
        associations_user = Associate.objects.filter(name_space=name_space, start=mention, stop=mention.stop,
                                                     username=user)
        # if associations.count() == 0:
        associations = Associate.objects.filter(name_space=name_space, start=mention, stop=mention.stop).distinct(
            'start', 'stop', 'concept_url', 'name')

        for association in associations:
            concept = association.concept_url
            area = association.name
            count = Associate.objects.filter(name_space=name_space, start=mention, stop=mention.stop,
                                             concept_url=concept, name=area).exclude(username=user).count()
            json_obj = {}
            json_obj['concept_url'] = concept.concept_url
            json_obj['concept_name'] = concept.concept_name
            json_obj['concept_area'] = area.name
            json_obj['start'] = mention1['start']
            json_obj['stop'] = mention1['stop']
            json_obj['position'] = position
            json_obj['concept_area'] = area.name
            json_obj['count'] = count
            if not Associate.objects.filter(name_space=name_space, start=mention, stop=mention.stop, username=user,
                                            name=area, concept_url=concept).exists():
                suggested_annotations['associations'].append(json_obj)

        suggested_annotations['relations'] = []
        # MAGARI IN FUTURO
        # links_s = Link.objects.filter(name_space = name_space,subject_document_id = document.document_id,subject_language = document.language).exclude(username = user)
        # for link in links_s:
        #     if(link.subject_start == start and link.subject_stop == stop) or (link.object_start == start and link.object_stop == stop) or (link.predicate_start == start and link.predicate_stop == stop):
        #         mention_s = Mention.objects.get(document_id = document, language = language, start = link.subject_start,stop = link.subject_stop)
        #         mention_p = Mention.objects.get(document_id = document, language = language, start = link.predicate_start,stop = link.predicate_stop)
        #         mention_o = Mention.objects.get(document_id = document, language = language, start = link.object_start,stop = link.object_stop)
        #         json_obj = {}
        #         json_obj['count'] = Link.objects.filter(name_space = name_space,subject_document_id = document.document_id,subject_language = document.language, subject_start = mention.start, subject_stop = mention.stop,
        #                                                 predicate_start = link.predicate_start,predicate_stop = link.predicate_stop,
        #                                                 object_start = link.object_start, object_stop = link.object_stop).exclude(username = user).count()
        #
        #         json_obj['subject'] = {}
        #         json_obj['subject']['mention'] = {}
        #         json_obj['subject']['concept'] = {}
        #         json_obj['predicate'] = {}
        #         json_obj['predicate']['mention'] = {}
        #         json_obj['predicate']['concept'] = {}
        #         json_obj['object'] = {}
        #         json_obj['object']['mention'] = {}
        #         json_obj['object']['concept'] = {}
        #         json_mention_source = return_start_stop_for_frontend(mention_s.start, mention_s.stop,
        #                                                              document.document_content)
        #         json_obj['subject']['mention']['start'] = json_mention_source['start']
        #         json_obj['subject']['mention']['stop'] = json_mention_source['stop']
        #         json_obj['subject']['mention']['position'] = json_mention_source['position']
        #         json_obj['subject']['mention']['mention_text'] = mention_s.mention_text
        #
        #         json_mention_p = return_start_stop_for_frontend(mention_p.start, mention_p.stop,
        #                                                              document.document_content)
        #         json_obj['predicate']['mention']['start'] = json_mention_p['start']
        #         json_obj['predicate']['mention']['stop'] = json_mention_p['stop']
        #         json_obj['predicate']['mention']['position'] = json_mention_p['position']
        #
        #         json_obj['predicate']['mention']['mention_text'] = mention_p.mention_text
        #
        #         json_mention_tar = return_start_stop_for_frontend(mention_o.start, mention_o.stop,
        #                                                              document.document_content)
        #         json_obj['object']['mention']['start'] = json_mention_tar['start']
        #         json_obj['object']['mention']['stop'] = json_mention_tar['stop']
        #         json_obj['object']['mention']['position'] = json_mention_tar['position']
        #         json_obj['object']['mention']['mention_text'] = mention_o.mention_text
        #         if not Link.objects.filter(name_space = name_space,subject_document_id = document.document_id,subject_language = document.language, subject_start = mention.start, subject_stop = mention.stop,
        #                                                 predicate_start = link.predicate_start,predicate_stop = link.predicate_stop,
        #                                                 object_start = link.object_start, object_stop = link.object_stop,username = user).exists():
        #             suggested_annotations['relations'].append(json_obj)
        #
        #
        # rel_sub_men = RelationshipSubjMention.objects.filter(document_id = document, name_space = name_space, start = mention, stop = mention.stop)
        # for link in rel_sub_men:
        #     mention_s = Mention.objects.get(document_id=document, language=language, start=link.start_id,
        #                                     stop=link.stop)
        #     concept = Concept.objects.get(concept_url = link.predicate_concept_url)
        #     name = SemanticArea.objects.get(name = link.predicate_name)
        #     concept_o = Concept.objects.get(concept_url = link.object_concept_url)
        #     name_o = SemanticArea.objects.get(name = link.object_name)
        #     json_obj = {}
        #     json_obj['count'] = RelationshipSubjMention.objects.filter(name_space=name_space,
        #                                                              document_id=document, language=language, start=mention_s,
        #                                                              stop=mention_s.stop,
        #                                                              object_concept_url=concept_o.concept_url,
        #                                                              object_name=name_o.name,
        #                                                              predicate_concept_url=concept.concept_url,
        #                                                              predicate_name=name.name
        #                                                              ).exclude(username = user).count()
        #     json_obj['subject'] = {}
        #     json_obj['subject']['mention'] = {}
        #     json_obj['subject']['concept'] = {}
        #     json_obj['predicate'] = {}
        #     json_obj['predicate']['mention'] = {}
        #     json_obj['predicate']['concept'] = {}
        #     json_obj['object'] = {}
        #     json_obj['object']['mention'] = {}
        #     json_obj['object']['concept'] = {}
        #
        #     json_mention_source = return_start_stop_for_frontend(mention_s.start, mention_s.stop,
        #                                                          document.document_content)
        #     json_obj['subject']['mention']['start'] = json_mention_source['start']
        #     json_obj['subject']['mention']['stop'] = json_mention_source['stop']
        #     json_obj['subject']['mention']['position'] = json_mention_source['position']
        #     json_obj['subject']['mention']['mention_text'] = mention_s.mention_text
        #
        #     json_obj['predicate']['concept']['concept_url'] = concept.concept_url
        #     json_obj['predicate']['concept']['concept_name'] = concept.concept_name
        #     json_obj['predicate']['concept']['concept_area'] = name.name
        #
        #     json_obj['object']['concept']['concept_url'] = concept_o.concept_url
        #     json_obj['object']['concept']['concept_name'] = concept_o.concept_name
        #     json_obj['object']['concept']['concept_area'] = name_o.name
        #
        #     if not RelationshipSubjMention.objects.filter(username=user, name_space=name_space,
        #                                                              document_id=document, language=language, start=mention_s,
        #                                                              stop=mention_s.stop,
        #                                                              object_concept_url=concept_o.concept_url,
        #                                                              object_name=name_o.name,
        #                                                              predicate_concept_url=concept.concept_url,
        #                                                              predicate_name=name.name
        #                                                              ).exists():
        #
        #         suggested_annotations['relations'].append(json_obj)
        #
        #
        #
        #
        #
        #
        #
        #
        #
        # rel_obj_men = RelationshipObjMention.objects.filter(document_id = document, name_space = name_space, start = mention, stop = mention.stop).exclude(username = user)
        # for link in rel_obj_men:
        #     mention_s = Mention.objects.get(document_id=document, language=language, start=link.start,
        #                                     stop=link.stop)
        #     concept = Concept.objects.get(concept_url=link.predicate_concept_url)
        #     name = SemanticArea.objects.get(name=link.predicate_name)
        #     concept_o = Concept.objects.get(concept_url=link.subject_concept_url)
        #     name_o = SemanticArea.objects.get(name=link.subject_name)
        #     json_obj = {}
        #     json_obj['count'] = RelationshipObjMention.objects.filter(name_space=name_space,
        #                                                              document_id = document, language = language, start = mention, stop = mention.stop,
        #                                                              subject_concept_url = concept_o.concept_url,subject_name = name_o.name,
        #                                                              predicate_concept_url = concept.concept_url,predicate_name = name.name
        #                                                              ).exclude(username = user).count()
        #     json_obj['subject'] = {}
        #     json_obj['subject']['mention'] = {}
        #     json_obj['subject']['concept'] = {}
        #     json_obj['predicate'] = {}
        #     json_obj['predicate']['mention'] = {}
        #     json_obj['predicate']['concept'] = {}
        #     json_obj['object'] = {}
        #     json_obj['object']['mention'] = {}
        #     json_obj['object']['concept'] = {}
        #
        #     json_mention_source = return_start_stop_for_frontend(mention_s.start, mention_s.stop,
        #                                                          document.document_content)
        #     json_obj['object']['mention']['start'] = json_mention_source['start']
        #     json_obj['object']['mention']['stop'] = json_mention_source['stop']
        #     json_obj['object']['mention']['stop'] = json_mention_source['position']
        #     json_obj['object']['mention']['mention_text'] = mention_s.mention_text
        #
        #     json_obj['predicate']['concept']['concept_url'] = concept.concept_url
        #     json_obj['predicate']['concept']['concept_name'] = concept.concept_name
        #     json_obj['predicate']['concept']['concept_area'] = name.name
        #
        #     json_obj['subject']['concept']['concept_url'] = concept_o.concept_url
        #     json_obj['subject']['concept']['concept_name'] = concept_o.concept_name
        #     json_obj['subject']['concept']['concept_area'] = name_o.name
        #     if not RelationshipObjMention.objects.filter(username=user, name_space=name_space,
        #                                                              document_id = document, language = language, start = mention, stop = mention.stop,
        #                                                              subject_concept_url = concept_o.concept_url,subject_name = name_o.name,
        #                                                              predicate_concept_url = concept.concept_url,predicate_name = name.name
        #                                                              ).exists():
        #         suggested_annotations['relations'].append(json_obj)
        #
        #
        #
        #
        #
        # rel_pred_men = RelationshipPredMention.objects.filter(document_id = document, name_space = name_space, start = mention, stop = mention.stop).exclude(username = user)
        # for link in rel_pred_men:
        #     mention_s = Mention.objects.get(document_id=document, language=language, start=link.start,
        #                                     stop=link.stop)
        #     concept = Concept.objects.get(concept_url=link.object_concept_url)
        #     name = SemanticArea.objects.get(name=link.object_name)
        #     concept_o = Concept.objects.get(concept_url=link.subject_concept_url)
        #     name_o = SemanticArea.objects.get(name=link.subject_name)
        #     json_obj = {}
        #     json_obj['subject'] = {}
        #     json_obj['subject']['mention'] = {}
        #     json_obj['subject']['concept'] = {}
        #     json_obj['predicate'] = {}
        #     json_obj['predicate']['mention'] = {}
        #     json_obj['predicate']['concept'] = {}
        #     json_obj['object'] = {}
        #     json_obj['object']['mention'] = {}
        #     json_obj['object']['concept'] = {}
        #
        #     json_mention_source = return_start_stop_for_frontend(mention_s.start, mention_s.stop,
        #                                                          document.document_content)
        #     json_obj['predicate']['mention']['start'] = json_mention_source['start']
        #     json_obj['predicate']['mention']['stop'] = json_mention_source['stop']
        #     json_obj['predicate']['mention']['position'] = json_mention_source['position']
        #     json_obj['predicate']['mention']['mention_text'] = mention_s.mention_text
        #
        #     json_obj['object']['concept']['concept_url'] = concept.concept_url
        #     json_obj['object']['concept']['concept_name'] = concept.concept_name
        #     json_obj['object']['concept']['concept_area'] = name.name
        #
        #     json_obj['subject']['concept']['concept_url'] = concept_o.concept_url
        #     json_obj['subject']['concept']['concept_name'] = concept_o.concept_name
        #     json_obj['subject']['concept']['concept_area'] = name_o.name
        #     if not RelationshipPredMention.objects.filter(username=user, name_space=name_space,
        #                                                               document_id=document, language=language, start=mention,
        #                                                               stop=mention.stop,
        #                                                               object_concept_url=concept.concept_url,
        #                                                               object_name=name.name,
        #                                                               subject_concept_url=concept_o.concept_url,
        #                                                               subject_name=name_o.name
        #                                                               ).exists():
        #         suggested_annotations['relations'].append(json_obj)
        #
        #
        #
        #
        #
        #
        # rel_subj_con = RelationshipSubjConcept.objects.filter(predicate_document_id = document,predicate_language = document.language, name_space = name_space).exclude(username = user)
        # for link in rel_subj_con:
        #     if (link.object_start == mention.start and link.object_stop == mention.stop) or (link.predicate_start == mention.start and link.predicate_stop == mention.stop):
        #         mention_o = Mention.objects.get(object_document_id=document, object_language=language,
        #                                         start=link.object_start,
        #                                         stop=link.object_stop)
        #         mention_p = Mention.objects.get(predicate_document_id=document, predicate_language=language,
        #                                         start=link.predicate_start,
        #                                         stop=link.predicate_stop)
        #         concept = link.concept_url
        #         name = link.name
        #
        #         json_obj = {}
        #         json_obj['subject'] = {}
        #         json_obj['subject']['mention'] = {}
        #         json_obj['subject']['concept'] = {}
        #         json_obj['predicate'] = {}
        #         json_obj['predicate']['mention'] = {}
        #         json_obj['predicate']['concept'] = {}
        #         json_obj['object'] = {}
        #         json_obj['object']['mention'] = {}
        #         json_obj['object']['concept'] = {}
        #
        #         json_mention_source = return_start_stop_for_frontend(mention_p.start, mention_p.stop,
        #                                                              document.document_content)
        #         json_obj['predicate']['mention']['start'] = json_mention_source['start']
        #         json_obj['predicate']['mention']['stop'] = json_mention_source['stop']
        #         json_obj['predicate']['mention']['position'] = json_mention_source['position']
        #         json_obj['predicate']['mention']['mention_text'] = mention_p.mention_text
        #
        #         json_mention_t = return_start_stop_for_frontend(mention_o.start, mention_o.stop,
        #                                                              document.document_content)
        #         json_obj['object']['mention']['start'] = json_mention_t['start']
        #         json_obj['object']['mention']['stop'] = json_mention_t['stop']
        #         json_obj['object']['mention']['position'] = json_mention_t['position']
        #         json_obj['object']['mention']['mention_text'] = mention_o.mention_text
        #
        #         json_obj['subject']['concept']['concept_url'] = concept.concept_url
        #         json_obj['subject']['concept']['concept_name'] = concept.concept_name
        #         json_obj['subject']['concept']['concept_area'] = name.name
        #         if not RelationshipSubjConcept.objects.filter(username=user, name_space=name_space,
        #                                                              predicate_document_id=document.document_id,
        #                                                              predicate_language=document.language,
        #                                                              predicate_start=mention_p.start,
        #                                                              predicate_stop=mention_p.stop,
        #                                                              object_start=mention_o.start,
        #                                                              object_stop= mention_o.stop,
        #                                                              concept_url=concept,
        #                                                              name=name).exists():
        #             suggested_annotations['relations'].append(json_obj)
        #
        #
        #
        #
        #
        #
        # rel_obj_con = RelationshipObjConcept.objects.filter(predicate_document_id = document,predicate_language = document.language, name_space = name_space).exclude(username = user)
        # for link in rel_obj_con:
        #     if (link.subject_start == mention.start and link.subject_stop == mention.stop) or (link.predicate_start == mention.start and link.predicate_stop == mention.stop):
        #         mention_o = Mention.objects.get(object_document_id=document, object_language=language,
        #                                         start=link.subject_start,
        #                                         stop=link.subject_stop)
        #         mention_p = Mention.objects.get(predicate_document_id=document, predicate_language=language,
        #                                         start=link.predicate_start,
        #                                         stop=link.predicate_stop)
        #         concept = link.concept_url
        #         name = link.name
        #
        #         json_obj = {}
        #         json_obj['subject'] = {}
        #         json_obj['subject']['mention'] = {}
        #         json_obj['subject']['concept'] = {}
        #         json_obj['predicate'] = {}
        #         json_obj['predicate']['mention'] = {}
        #         json_obj['predicate']['concept'] = {}
        #         json_obj['object'] = {}
        #         json_obj['object']['mention'] = {}
        #         json_obj['object']['concept'] = {}
        #
        #         json_mention_s = return_start_stop_for_frontend(mention_p.start, mention_p.stop,
        #                                                         document.document_content)
        #         json_obj['predicate']['mention']['start'] = json_mention_s['start']
        #         json_obj['predicate']['mention']['stop'] = json_mention_s['stop']
        #         json_obj['predicate']['mention']['position'] = json_mention_s['position']
        #         json_obj['predicate']['mention']['mention_text'] = mention_p.mention_text
        #
        #         json_mention_t = return_start_stop_for_frontend(mention_o.start, mention_o.stop,
        #                                                         document.document_content)
        #         json_obj['subject']['mention']['start'] = json_mention_t['start']
        #         json_obj['subject']['mention']['stop'] = json_mention_t['stop']
        #         json_obj['subject']['mention']['position'] = json_mention_t['position']
        #         json_obj['subject']['mention']['mention_text'] = mention_o.mention_text
        #
        #         json_obj['object']['concept']['concept_url'] = concept.concept_url
        #         json_obj['object']['concept']['concept_name'] = concept.concept_name
        #         json_obj['object']['concept']['concept_area'] = name.name
        #         if not RelationshipObjConcept.objects.filte(username = user, name_space = name_space, subject_document_id = document.document_id,
        #                                        subject_language = document.language, subject_start = mention_o.start,subject_stop = mention_o.stop,
        #                                        predicate_start = mention_p.start,predicate_stop = mention_p.stop,concept_url = concept, name=name).exists():
        #             suggested_annotations['relations'].append(json_obj)
        #
        #
        #
        #
        # rel_pred_con = RelationshipPredConcept.objects.filter(subject_document_id = document,subject_language = document.language, name_space = name_space).exclude(username = user)
        # for link in rel_pred_con:
        #     if (link.subject_start == mention.start and link.subject_stop == mention.stop) or (
        #             link.object_start == mention.start and link.object_stop == mention.stop):
        #         mention_s = Mention.objects.get(object_document_id=document, object_language=language,
        #                                         start=link.subject_start,
        #                                         stop=link.subject_stop)
        #         mention_o = Mention.objects.get(predicate_document_id=document, predicate_language=language,
        #                                         start=link.object_start,
        #                                         stop=link.object_stop)
        #         concept = link.concept_url
        #         name = link.name
        #
        #         json_obj = {}
        #         json_obj['subject'] = {}
        #         json_obj['subject']['mention'] = {}
        #         json_obj['subject']['concept'] = {}
        #         json_obj['predicate'] = {}
        #         json_obj['predicate']['mention'] = {}
        #         json_obj['predicate']['concept'] = {}
        #         json_obj['object'] = {}
        #         json_obj['object']['mention'] = {}
        #         json_obj['object']['concept'] = {}
        #
        #         json_mention_t = return_start_stop_for_frontend(mention_s.start, mention_s.stop,
        #                                                         document.document_content)
        #         json_obj['subject']['mention']['start'] = json_mention_t['start']
        #         json_obj['subject']['mention']['stop'] = json_mention_t['stop']
        #         json_obj['subject']['mention']['position'] = json_mention_t['position']
        #         json_obj['subject']['mention']['mention_text'] = mention_s.mention_text
        #
        #         json_mention_o = return_start_stop_for_frontend(mention_o.start, mention_o.stop,
        #                                                         document.document_content)
        #         json_obj['object']['mention']['start'] = json_mention_o['start']
        #         json_obj['object']['mention']['stop'] = json_mention_o['stop']
        #         json_obj['object']['mention']['position'] = json_mention_o['position']
        #         json_obj['object']['mention']['mention_text'] = mention_o.mention_text
        #
        #         json_obj['predicate']['concept']['concept_url'] = concept.concept_url
        #         json_obj['predicate']['concept']['concept_name'] = concept.concept_name
        #         json_obj['predicate']['concept']['concept_area'] = name.name
        #         if not RelationshipPredConcept.objects.filte(username=user, name_space=name_space,
        #                                                             subject_document_id=document.document_id,
        #                                                             subject_language=document.language,
        #                                                             subject_start=mention_s.start,
        #                                                             subject_stop=mention_s.stop,
        #                                                             object_start=mention_o.start,
        #                                                             object_stop=mention_o.stop,
        #                                                              concept_url=concept,
        #                                                             name=area).exists():
        #             suggested_annotations['relations'].append(json_obj)

        return JsonResponse(suggested_annotations)


def copy_all_annotations_for_user_study(request):
    """This view copies all the annotations of a user to another user. If user to is None, the annotations
    are copied to all the members of the collection"""

    if request.method == 'GET':
        # json_body = json.loads(request.body)
        # user_from = json_body['user_from']
        # uto = json_body['user_to']
        user_from = 'OrnellaIrrera'
        uto = ''
        user_to = None if uto == '' else uto
        name_space = request.session.get('name_space', 'Human')
        collection = request.session.get('collection', False)
        print(collection)
        collection = 'a7883136529a4394027a47788b6b4628'
        # collection = '6f5a0883499d911858b6eaed681f6a92'
        collection = Collection.objects.get(collection_id=collection)

        user_from = User.objects.filter(username=user_from, name_space=name_space)
        if user_from.exists() == False:
            return HttpResponse(status=500)
        user_from = user_from.first()
        if user_to is not None:
            user_to = User.objects.filter(username=user_to, name_space=name_space)
            if not user_to.exists():
                return HttpResponse(status=500)
        else:
            user_to = ShareCollection.objects.filter(collection_id=collection, status='accepted')
            if not user_to.exists():
                return HttpResponse(status=500)
            user_to = [u.username for u in user_to]

        if not name_space:
            return redirect('doctron_app:loginPage')
        name_space = NameSpace.objects.get(name_space=name_space)

        try:
            with transaction.atomic():

                # get annotations of user from
                documents = Document.objects.filter(collection_id=collection)
                documents_ids = [d.document_id for d in documents]
                annotate = Annotate.objects.filter(username=user_from, name_space=name_space, document_id__in=documents)
                associate = Associate.objects.filter(username=user_from, name_space=name_space,
                                                     document_id__in=documents)
                link = Link.objects.filter(username=user_from, name_space=name_space,
                                           subject_document_id__in=documents_ids)
                assertions = CreateFact.objects.filter(username=user_from, name_space=name_space,
                                                       document_id__in=documents)
                ground_truth_log_file = GroundTruthLogFile.objects.filter(username=user_from, name_space=name_space,
                                                                          document_id__in=documents)
                relationship_obj_mention = RelationshipObjMention.objects.filter(username=user_from,
                                                                                 name_space=name_space,
                                                                                 document_id__in=documents)
                relationship_obj_concept = RelationshipObjConcept.objects.filter(username=user_from,
                                                                                 name_space=name_space,
                                                                                 subject_document_id__in=documents_ids)
                relationship_subj_mention = RelationshipSubjMention.objects.filter(username=user_from,
                                                                                   name_space=name_space,
                                                                                   document_id__in=documents)
                relationship_subj_concept = RelationshipSubjConcept.objects.filter(username=user_from,
                                                                                   name_space=name_space,
                                                                                   object_document_id__in=documents_ids)
                relationship_pred_mention = RelationshipPredMention.objects.filter(username=user_from,
                                                                                   name_space=name_space,
                                                                                   document_id__in=documents)
                relationship_pred_concept = RelationshipPredConcept.objects.filter(username=user_from,
                                                                                   name_space=name_space,
                                                                                   object_document_id__in=documents_ids)

                for u in user_to:
                    for a in annotate:
                        start = a.start_id
                        document = a.document_id
                        language = a.language
                        stop = a.stop

                        start = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
                        Annotate.objects.create(username=u, name_space=name_space, document_id=document,
                                                language=language,
                                                start=start, stop=stop, insertion_time=Now())

                    for a in associate:
                        start = a.start_id
                        stop = a.stop
                        document = a.document_id
                        language = a.language

                        start = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)

                        concept_url = a.concept_url_id
                        concept_url = Concept.objects.get(concept_url=concept_url)

                        name = a.name_id
                        name = SemanticArea.objects.get(name=name)
                        Associate.objects.create(username=u, name_space=name_space, document_id=document,
                                                 language=language,
                                                 start=start, stop=stop, concept_url=concept_url, name=name,
                                                 insertion_time=Now())

                    for a in ground_truth_log_file:
                        gt_json = a.gt_json
                        revised = a.revised
                        document = a.document_id
                        language = a.language
                        GroundTruthLogFile.objects.create(username=u, name_space=name_space, document_id=document,
                                                          language=language,
                                                          gt_json=gt_json, revised=revised, insertion_time=Now())

                    for a in link:
                        subject_document_id = a.subject_document_id
                        object_document_id = a.object_document_id
                        predicate_document_id = a.predicate_document_id
                        subject_language = a.subject_language
                        object_language = a.object_language
                        predicate_language = a.predicate_language
                        subject_start = a.subject_start
                        subject_stop = a.subject_stop
                        predicate_start = a.predicate_start
                        predicate_stop = a.predicate_stop
                        object_start = a.object_start
                        object_stop = a.object_stop
                        Link.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                            subject_document_id=subject_document_id,
                                            object_document_id=object_document_id,
                                            predicate_document_id=predicate_document_id,
                                            subject_language=subject_language,
                                            object_language=object_language, predicate_language=predicate_language,
                                            subject_start=subject_start, subject_stop=subject_stop,
                                            predicate_start=predicate_start,
                                            predicate_stop=predicate_stop, object_start=object_start,
                                            object_stop=object_stop)

                    for a in assertions:
                        document_id = a.document_id
                        language = a.language
                        subject_concept_url = a.subject_concept_url
                        object_concept_url = a.object_concept_url
                        predicate_concept_url = a.predicate_concept_url
                        subject_name = a.subject_name
                        object_name = a.object_name
                        predicate_name = a.predicate_name

                        CreateFact.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                  document_id=document_id, language=language,
                                                  subject_concept_url=subject_concept_url,
                                                  object_concept_url=object_concept_url,
                                                  predicate_concept_url=predicate_concept_url,
                                                  subject_name=subject_name,
                                                  object_name=object_name, predicate_name=predicate_name)

                    for a in relationship_pred_mention:
                        document_id = a.document_id
                        language = a.language
                        start = a.start_id
                        stop = a.stop

                        start = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
                        subject_concept_url = a.subject_concept_url
                        object_concept_url = a.object_concept_url
                        subject_name = a.subject_name
                        object_name = a.object_name

                        RelationshipPredMention.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                               document_id=document_id, language=language,
                                                               subject_concept_url=subject_concept_url,
                                                               object_concept_url=object_concept_url,
                                                               start=start, subject_name=subject_name,
                                                               object_name=object_name, stop=stop)

                    for a in relationship_subj_mention:
                        document_id = a.document_id
                        language = a.language
                        start = a.start_id
                        stop = a.stop

                        start = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)

                        predicate_concept_url = a.predicate_concept_url
                        predicate_name = a.predicate_name
                        object_name = a.object_name
                        object_concept_url = a.object_concept_url

                        RelationshipSubjMention.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                               document_id=document_id, language=language,
                                                               predicate_concept_url=predicate_concept_url,
                                                               object_concept_url=object_concept_url,
                                                               start=start, predicate_name=predicate_name,
                                                               object_name=object_name, stop=stop)

                    for a in relationship_obj_mention:
                        document_id = a.document_id
                        language = a.language
                        start = a.start_id
                        stop = a.stop

                        start = Mention.objects.get(document_id=document, language=language, start=start, stop=stop)
                        subject_concept_url = a.subject_concept_url
                        subject_name = a.subject_name
                        predicate_name = a.predicate_name
                        predicate_concept_url = a.predicate_concept_url

                        RelationshipObjMention.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                              document_id=document_id, language=language,
                                                              predicate_concept_url=predicate_concept_url,
                                                              subject_name=subject_name,
                                                              start=start, predicate_name=predicate_name,
                                                              subject_concept_url=subject_concept_url, stop=stop)

                    for a in relationship_obj_concept:
                        subject_document_id = a.subject_document_id
                        predicate_document_id = a.predicate_document_id
                        subject_language = a.object_language
                        predicate_language = a.predicate_language
                        subject_start = a.subject_start
                        subject_stop = a.subject_stop
                        predicate_start = a.predicate_start
                        predicate_stop = a.predicate_stop
                        concept_url = a.concept_url_id
                        name = a.name_id
                        concept_url = Concept.objects.get(concept_url=concept_url)
                        name = SemanticArea.objects.get(name=name)

                        RelationshipObjConcept.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                              subject_document_id=subject_document_id,
                                                              predicate_document_id=predicate_document_id,
                                                              subject_language=subject_language,
                                                              predicate_language=predicate_language,
                                                              subject_start=subject_start, subject_stop=subject_stop,
                                                              predicate_start=predicate_start,
                                                              predicate_stop=predicate_stop, concept_url=concept_url,
                                                              name=name)
                    for a in relationship_subj_concept:
                        object_document_id = a.object_document_id
                        predicate_document_id = a.predicate_document_id
                        object_language = a.object_language
                        predicate_language = a.predicate_language
                        object_start = a.object_start
                        object_stop = a.object_stop
                        predicate_start = a.predicate_start
                        predicate_stop = a.predicate_stop
                        concept_url = a.concept_url_id
                        name = a.name_id
                        concept_url = Concept.objects.get(concept_url=concept_url)
                        name = SemanticArea.objects.get(name=name)

                        RelationshipSubjConcept.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                               object_document_id=object_document_id,
                                                               predicate_document_id=predicate_document_id,
                                                               object_language=object_language,
                                                               predicate_language=predicate_language,
                                                               object_start=object_start, object_stop=object_stop,
                                                               predicate_start=predicate_start,
                                                               predicate_stop=predicate_stop, concept_url=concept_url,
                                                               name=name)

                    for a in relationship_pred_concept:
                        object_document_id = a.object_document_id
                        subject_document_id = a.subject_document_id
                        object_language = a.object_language
                        subject_language = a.subject_language
                        object_start = a.object_start
                        object_stop = a.object_stop
                        subject_start = a.subject_start
                        subject_stop = a.subject_stop
                        concept_url = a.concept_url_id
                        concept_url = Concept.objects.get(concept_url=concept_url)

                        name = a.name_id
                        name = SemanticArea.objects.get(name=name)

                        RelationshipPredConcept.objects.create(username=u, name_space=name_space, insertion_time=Now(),
                                                               object_document_id=object_document_id,
                                                               subject_document_id=subject_document_id,
                                                               object_language=object_language,
                                                               subject_language=subject_language,
                                                               object_start=object_start, object_stop=object_stop,
                                                               subject_start=subject_start,
                                                               subject_stop=subject_stop, concept_url=concept_url,
                                                               name=name)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

        return HttpResponse(status=200)


def create_coehns(request):
    """This viws computes the coehns kappa for a pair of users"""

    collection = request.GET.get('collection', None)
    user1 = request.GET.get('user1', None)
    user2 = request.GET.get('user2', None)
    document = request.GET.get('document', None)
    if None in [user1, user2, collection]:
        return HttpResponse(status=500)
    collection = Collection.objects.get(collection_id=collection)
    documents = Document.objects.filter(collection_id=collection)
    if document != '' and document != 'All':
        documents = Document.objects.filter(document_id=document)

    json_obj = {}
    for tipo in ['mentions', 'concepts', 'relations', 'assertions', 'labels']:
        json_obj[tipo] = create_cohen([user1, user2], collection, documents, tipo)

    return JsonResponse(json_obj)


def create_fleiss_overview(request):
    """This view returns an overview of the fleiss kappa among rounds"""

    collection = request.GET.get('collection', None)
    documents = request.GET.get('document', None)
    if documents == '':
        documents = None
    collectionround = collection.split('_round')[0]
    collections = Collection.objects.filter(collection_id__startswith=collectionround)
    if documents is not None:
        documents = Document.objects.filter(document_id=documents)
    else:
        documents = Document.objects.filter(collection_id=collectionround)
    json_obj = {}
    for c in collections:
        new_id = 'iteration_1'
        if 'iteration' in c.collection_id:
            new_id = 'iteration_' + str(c.collection_id.split('_round_')[-1])
        json_obj[new_id] = {}
        json_obj[new_id]['iteration'] = new_id
        json_obj[new_id]['mentions'] = global_mentions_agreement(c.collection_id, documents)
        json_obj[new_id]['concepts'] = global_concepts_agreement(c.collection_id, documents)
        json_obj[new_id]['labels'] = global_labels_agreement(c.collection_id, documents)
        json_obj[new_id]['relationships'] = global_relationships_agreement(c.collection_id, documents)
        json_obj[new_id]['assertions'] = global_createfact_agreement(c.collection_id, documents)

    return JsonResponse(json_obj)


def create_new_round(request):
    """This view creates a new round of annotations"""

    json_body = json.loads(request.body)
    collection = json_body.get('collection', None)
    name_space = request.session['name_space']
    copy_all = False # this variable is true if we need to copy also annotations. In this case leave false
    if name_space:
        name_space = NameSpace.objects.get(name_space=name_space)
    if not name_space or not collection:
        return HttpResponse(status=500)

    collection = collection.split('_')[0]
    collections = Collection.objects.filter(collection_id__startswith=collection)
    new_id = collection + '_iteration_2'
    n = 2
    prev_n = None
    for c in collections:
        if 'iteration' in c.collection_id:
            numb = c.collection_id.split('_iteration_')[-1]
            print(numb)

            n = int(numb) + 1
            prev_n = n - 1
            new_id = c.collection_id[0:-1] + str(n)
            prev_id = c.collection_id[0:-1] + str(prev_n)

    if prev_n:
        print(prev_id)
        collection = Collection.objects.get(collection_id=prev_id)
    else:
        collection = Collection.objects.get(collection_id=collection)



    with transaction.atomic():
        # create the collection
        new_collection = Collection.objects.create(collection_id=new_id, name=collection.name + ' iteration ' + str(n),
                                                   description=collection.description, username=collection.username,
                                                   name_space=collection.name_space, insertion_time=Now())

        # copy the annotators
        users = ShareCollection.objects.filter(collection_id=collection)
        for u in users:
            ShareCollection.objects.create(collection_id=new_collection, username=u.username, name_space=name_space,
                                           status=u.status,reviewer=False,admin=u.admin)

        labels = CollectionHasLabel.objects.filter(collection_id=collection)
        for u in labels:
            CollectionHasLabel.objects.create(collection_id=new_collection, label=u.name, values=u.values)

        # copy documents
        documents = Document.objects.filter(collection_id=collection)
        doc_list = [d.document_id for d in documents]

        for i,d in enumerate(documents):
            Document.objects.create(document_id=d.document_id + '_iteration_'+str(n), collection_id=new_collection,
                                    language=d.language,
                                    provenance=d.provenance, document_content=d.document_content, batch=d.batch,
                                    insertion_time=Now())
        # copy concepts
        cursor = connection.cursor()
        concepts = AddConcept.objects.filter(collection_id=collection).values('concept_url', 'name', 'username',
                                                                              'name_space', 'insertion_time',
                                                                              'collection_id')
        for a in concepts:
            cursor.execute(
                "INSERT INTO add_concept (concept_url,name,insertion_time,username,name_space,collection_id) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                [a['concept_url'], a['name'], a['insertion_time'], a['username'], a['name_space'], new_id])
        tags = CollectionHasTag.objects.filter(collection_id=collection).values('name',
                                                                                'collection_id')
        for a in tags:
            cursor.execute(
                "INSERT INTO collection_has_tag ('name','collection_id') "
                "VALUES (%s,%s)",
                [a['name'],  new_id])
    if copy_all:
        with transaction.atomic():
            cursor = connection.cursor()
            # copy mentions

            mentions = Mention.objects.filter(document_id__in=documents).values('start', 'stop', 'document_id', 'language',
                                                                                'mention_text')
            for m in mentions:
                doc = Document.objects.get(document_id=m['document_id'] + '_round_' + str(n))
                Mention.objects.create(start=m['start'], stop=m['stop'], document_id=doc, language=m['language'],
                                       mention_text=m['mention_text'])
            annotations = Annotate.objects.filter(document_id__in=documents).values('start', 'stop', 'username',
                                                                                    'name_space', 'insertion_time',
                                                                                    'document_id', 'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO annotate (start,stop,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['username'], a['name_space'], a['document_id'] + '_round_' + str(n),
                     a['language'],
                     a['insertion_time']])
                # copy concepts
            annotations = Associate.objects.filter(document_id__in=documents).values('start', 'stop', 'concept_url',
                                                                                     'name', 'username',
                                                                                     'name_space',
                                                                                     'insertion_time',
                                                                                     'document_id',
                                                                                     'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO associate (start,stop,concept_url,name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['concept_url'], a['name'], a['username'], a['name_space'],
                     a['document_id'] + '_round_' + str(n), a['language'],
                     a['insertion_time']])


            annotations = AssociateTag.objects.filter(document_id__in=documents).values('start', 'stop',
                                                                                        'name', 'username',
                                                                                        'name_space',
                                                                                        'insertion_time',
                                                                                        'document_id',
                                                                                        'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO associate_tag (start,stop,name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['name'], a['username'], a['name_space'],
                     a['document_id'] + '_round_' + str(n), a['language'],
                     a['insertion_time']])

            annotations = GroundTruthLogFile.objects.filter(document_id__in=documents)
            for a in annotations:
                d = a.document_id_id + '_round_' + str(n)
                d = Document.objects.get(document_id=d)

                GroundTruthLogFile.objects.create(document_id=d, language=a.language, gt_json=a.gt_json,
                                                  insertion_time=Now(), username=a.username, name_space=a.name_space)
                # copy labels
            annotations = AnnotateLabel.objects.filter(document_id__in=documents).values('label', 'username',
                                                                                         'name_space',
                                                                                         'insertion_time',
                                                                                         'document_id', 'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO annotate_label (name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    [a['name'], a['username'], a['name_space'], a['document_id'] + '_round_' + str(n), a['language'],
                     a['insertion_time']])

            # copy facts
            annotations = CreateFact.objects.filter(document_id__in=documents).values('subject_concept_url',
                                                                                      'subject_name',
                                                                                      'object_concept_url',
                                                                                      'object_name',
                                                                                      'predicate_concept_url',
                                                                                      'predicate_name', 'username',
                                                                                      'name_space', 'insertion_time',
                                                                                      'document_id', 'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO create_fact (subject_concept_url,object_concept_url,predicate_concept_url,subject_name,object_name,predicate_name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['subject_concept_url'], a['object_concept_url'], a['predicate_concept_url'], a['subject_name'],
                     a['object_name'], a['predicate_name'], a['username'], a['name_space'],
                     a['document_id'] + '_round_' + str(n),
                     a['language'], a['insertion_time']])

            # copy relations
            annotations = RelationshipSubjMention.objects.filter(document_id__in=documents).values('start', 'stop',
                                                                                                   'object_concept_url',
                                                                                                   'object_name',
                                                                                                   'predicate_concept_url',
                                                                                                   'predicate_name',
                                                                                                   'username',
                                                                                                   'name_space',
                                                                                                   'insertion_time',
                                                                                                   'document_id',
                                                                                                   'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationsp_subj_mention (start,stop,object_concept_url,object_name,predicate_concept_url,predicate_name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['object_concept_url'], a['object_name'], a['predicate_concept_url'],
                     a['predicate_name'], a['username'], a['name_space'], a['document_id'] + '_round_' + str(n),
                     a['language'],
                     a['insertion_time']])

            annotations = RelationshipObjMention.objects.filter(document_id__in=documents).values('start', 'stop',
                                                                                                  'subject_concept_url',
                                                                                                  'subject_name',
                                                                                                  'predicate_concept_url',
                                                                                                  'predicate_name',
                                                                                                  'username',
                                                                                                  'name_space',
                                                                                                  'insertion_time',
                                                                                                  'document_id',
                                                                                                  'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationship_obj_mention (start,stop,subject_concept_url,subject_name,predicate_concept_url,predicate_name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['subject_concept_url'], a['subject_name'], a['predicate_concept_url'],
                     a['predicate_name'], a['username'], a['name_space'], a['document_id'] + '_round_' + str(n),
                     a['language'],
                     a['insertion_time']])

            annotations = RelationshipPredMention.objects.filter(document_id__in=documents).values('start', 'stop',
                                                                                                   'subject_concept_url',
                                                                                                   'subject_name',
                                                                                                   'object_concept_url',
                                                                                                   'object_name',
                                                                                                   'username',
                                                                                                   'name_space',
                                                                                                   'insertion_time',
                                                                                                   'document_id',
                                                                                                   'language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationship_pred_mention (start,stop,subject_concept_url,subject_name,object_concept_url,object_name,username,name_space,document_id,language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['start'], a['stop'], a['subject_concept_url'], a['subject_name'], a['object_concept_url'],
                     a['object_name'], a['username'], a['name_space'], a['document_id'] + '_round_' + str(n), a['language'],
                     a['insertion_time']])

            annotations = Link.objects.filter(subject_document_id__in=doc_list).values('subject_start', 'subject_stop',
                                                                                       'object_start', 'object_stop',
                                                                                       'predicate_start',
                                                                                       'predicate_stop',
                                                                                       'username', 'name_space',
                                                                                       'insertion_time',
                                                                                       'object_document_id',
                                                                                       'object_language',
                                                                                       'subject_document_id',
                                                                                       'subject_language',
                                                                                       'predicate_document_id',
                                                                                       'predicate_language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO link (subject_start,subject_stop,object_start,object_stop,predicate_start,predicate_stop,username,name_space,object_document_id,object_language,predicate_document_id,predicate_language,subject_document_id,subject_language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['subject_start'], a['subject_stop'], a['object_start'], a['object_stop'], a['predicate_start'],
                     a['predicate_stop'], a['username'], a['name_space'], a['object_document_id'] + '_round_' + str(n),
                     a['object_language'],
                     a['predicate_document_id'] + '_round_' + str(n), a['predicate_language'],
                     a['subject_document_id'] + '_round_' + str(n), a['subject_language'],
                     a['insertion_time']])

            annotations = RelationshipSubjConcept.objects.filter(object_document_id__in=doc_list).values('concept_url',
                                                                                                         'name',
                                                                                                         'object_start',
                                                                                                         'object_stop',
                                                                                                         'predicate_start',
                                                                                                         'predicate_stop',
                                                                                                         'username',
                                                                                                         'name_space',
                                                                                                         'insertion_time',
                                                                                                         'object_document_id',
                                                                                                         'object_language',
                                                                                                         'predicate_document_id',
                                                                                                         'predicate_language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationship_subj_concept (concept_url,name,object_start,object_stop,predicate_start,predicate_stop,username,name_space,object_document_id,object_language,predicate_document_id,predicate_language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['concept_url'], a['name'], a['object_start'], a['object_stop'], a['predicate_start'],
                     a['predicate_stop'], a['username'], a['name_space'], a['object_document_id'] + '_round_' + str(n),
                     a['object_language'], a['predicate_document_id'] + '_round_' + str(n), a['predicate_language'],
                     a['insertion_time']])

            annotations = RelationshipObjConcept.objects.filter(subject_document_id__in=doc_list).values('concept_url',
                                                                                                         'name',
                                                                                                         'subject_start',
                                                                                                         'subject_stop',
                                                                                                         'predicate_start',
                                                                                                         'predicate_stop',
                                                                                                         'username',
                                                                                                         'name_space',
                                                                                                         'insertion_time',
                                                                                                         'subject_document_id',
                                                                                                         'subject_language',
                                                                                                         'predicate_document_id',
                                                                                                         'predicate_language')

            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationship_obj_concept (concept_url,name,subject_start,subject_stop,predicate_start,predicate_stop,username,name_space,subject_document_id,subject_language,predicate_document_id,predicate_language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['concept_url'], a['name'], a['subject_start'], a['subject_stop'], a['predicate_start'],
                     a['predicate_stop'], a['username'], a['name_space'], a['subject_document_id'] + '_round_' + str(n),
                     a['subject_language'], a['predicate_document_id'] + '_round_' + str(n),
                     a['predicate_language'], a['insertion_time']])

            annotations = RelationshipPredConcept.objects.filter(subject_document_id__in=doc_list).values('concept_url',
                                                                                                          'name',
                                                                                                          'object_start',
                                                                                                          'object_stop',
                                                                                                          'subject_start',
                                                                                                          'subject_stop',
                                                                                                          'username',
                                                                                                          'name_space',
                                                                                                          'insertion_time',
                                                                                                          'subject_document_id',
                                                                                                          'subject_language',
                                                                                                          'object_document_id',
                                                                                                          'object_language')
            for a in annotations:
                cursor.execute(
                    "INSERT INTO relationship_pred_concept (concept_url,name,object_start,object_stop,subject_start,subject_stop,username,name_space,subject_document_id,subject_language,object_document_id,object_language,insertion_time) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [a['concept_url'], a['name'], a['object_start'], a['object_stop'], a['subject_start'],
                     a['subject_stop'], a['username'], a['name_space'], a['subject_document_id'] + '_round_' + str(n),
                     a['subject_language'], a['object_document_id'] + '_round_' + str(n), a['object_language'],
                     a['insertion_time']])

    return HttpResponse(status=200)


def change_role(request):
    role = request.GET.get('role',None)
    user = request.session.get('username',None)
    topic = request.session.get('topic',None)
    collection = request.session.get('collection',None)
    json_resp = {'documents':[],'document_id':''}
    try:
        if not (user and topic and role and collection):
            return HttpResponse(status = 200)

        if user and role and collection and topic:
            collection = Collection.objects.get(collection_id = collection)
            topic_obj = Topic.objects.get(id = topic)
            name_space = NameSpace.objects.get(name_space=request.session['name_space'])
            user = User.objects.get(username=request.session['username'], name_space=name_space)
            docs = Document.objects.filter(collection_id=collection)

            gts = GroundTruthLogFile.objects.filter(document_id__in=docs, username=user,topic_id=topic_obj,
                                                    name_space=name_space).order_by("-insertion_time")

            split_docs = Split.objects.filter(collection_id=collection, username=user)
            if role.lower() == 'reviewer' and ShareCollection.objects.filter(username = user,name_space=name_space,collection_id=collection,reviewer=True).exists():
                split_docs = SplitReviewer.objects.filter(collection_id=collection, username=user)
            elif role.lower() == 'admin' and ShareCollection.objects.filter(username = user,name_space=name_space,collection_id=collection,admin=True).exists():
                split_docs = [] # consider all

            annotated_docs = [x.document_id for x in gts]
            annotated_docs_id = [x.document_id for x in annotated_docs]
            not_annotated_docs = [x for x in docs if x.document_id not in annotated_docs_id]
            docs_list = []
            split_docs_ids = [s.document_id.document_id for s in split_docs]

            for document in annotated_docs:
                json_doc = {'id': document.document_content['doc_id'], 'hashed_id': document.document_id,
                            'annotated': True, 'batch': document.batch}
                if len(split_docs_ids) == 0:  # a chi non sono assegnati docs può vederli tutti
                    json_doc['split'] = 'all'
                elif document.document_id in split_docs_ids or role.lower() == 'admin':
                    json_doc['split'] = 'yes'
                else:
                    json_doc['split'] = 'no'
                #
                docs_list.append(json_doc)
            #
            for document in not_annotated_docs:
                json_doc = {'id': document.document_content['doc_id'], 'hashed_id': document.document_id,
                            'annotated': False, 'batch': document.batch}
                if len(split_docs_ids) == 0:  # a chi non sono assegnati docs può vederli tutti
                    json_doc['split'] = 'all'
                elif document.document_id in split_docs_ids or role.lower() == 'admin':
                    json_doc['split'] = 'yes'
                else:
                    json_doc['split'] = 'no'
                docs_list.append(json_doc)
            #
            # # print(docs_list)
            #
            #docs_list = sorted(docs_list, key=lambda x: int(x['id']))
            docs_list = sorted(
                docs_list,
                key=lambda x: (
                    # Prova a convertire 'id' in int, altrimenti usa direttamente la stringa
                    int(x['id']) if x['id'].isdigit() else x['id']
                )
            )

            json_resp['documents'] = docs_list
            json_resp['document_id'] = docs_list[0]['hashed_id']

            if SessionDoc.objects.filter(username=user,role=role,document_id__in=docs,topic_id=topic_obj).exists():
                sessions = SessionDoc.objects.filter(username=user,role=role,document_id__in=docs).order_by('-last_view')
                session = sessions.first()
                document = session.document_id
                json_resp['document_id'] = document.document_id

            elif GroundTruthLogFile.objects.filter(document_id__in=docs,username=user,topic_id=topic_obj).exists() and role.lower() == 'annotator':
                d = GroundTruthLogFile.objects.filter(document_id__in=docs,username=user,topic_id=topic_obj).order_by('-insertion_time')
                docs_ids = [doc.document_id for doc in docs]
                gt_ids = [doc.document_id_id for doc in d]
                for doc in docs_ids:
                    if doc in gt_ids:
                        json_resp['document_id'] = doc
                        break

            request.session['document'] = json_resp['document_id']
            document = Document.objects.get(document_id = json_resp['document_id'])
            with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO session_doc ( document_id, language, username, name_space, role, last_view,collection_id,topic_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (username, name_space, collection_id, role, topic_id)
                DO UPDATE SET
                    last_view = %s, document_id =%s, language = %s;""",
                               [document.document_id, document.language, user.username, user.name_space_id, role, datetime.now(),document.collection_id_id,topic,datetime.now(),document.document_id,document.language])

            request.session['role'] = role
            return JsonResponse(json_resp)

    except Exception as e:
        print(e)
        return HttpResponse(status=500)

    return HttpResponse(status = 500)



def topic(request):
    if request.method == 'GET':
        json_resp = {'topics':[]}
        collection = request.session.get('collection',None)
        if collection is not None:
            collection = Collection.objects.get(collection_id=collection)
            topics = Topic.objects.filter(collection_id = collection)
            if request.GET.get('topic',None) is not None:
                topic = request.GET.get('topic',None)
                t = Topic.objects.filter(topic_id=topic,collection_id = collection)
                if t.exists():
                    t = t.first()
                    json_resp['topics'].append({k:v for k,v in t.details.items() if k != 'query_id' and k != 'topic_id'})
                    request.session['topic'] = t.id
                    with connection.cursor() as cursor:
                        cursor.execute("""INSERT INTO session_doc (document_id, language, username, name_space, role, last_view,collection_id,topic_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                        ON CONFLICT (username, name_space, collection_id, role,topic_id)
                        DO UPDATE SET
                            last_view = %s,document_id=%s,language=%s;""",[request.session['document'],request.session['language'],request.session['username'],request.session['name_space'],request.session['role'],datetime.now(),request.session['collection'],request.session['topic'],datetime.now(),request.session['document'],request.session['language']])

            else:
                for t in topics:
                    json_resp['topics'].append(t.details)
        return JsonResponse(json_resp)

    elif request.method == 'POST':
        body_json = json.loads(request.body)
        if body_json.get('topic',None) is not None:
            collection = Collection.objects.get(collection_id = request.session['collection'])
            topic = Topic.objects.get(collection_id = collection,topic_id = body_json['topic'])
            request.session['topic'] = topic.id
            return HttpResponse(status=200)


def comment(request):
    document = request.session.get('document',None)
    collection = request.session.get('collection',None)
    username = request.session.get('username',None)
    name_space = request.session.get('name_space',None)
    topic = request.session.get('topic',None)
    if None in [document,collection,topic,username,name_space]:
        return HttpResponse(status = 500)

    if request.method == 'GET':
        # select all comments
        document = Document.objects.get(document_id=document)
        topic = Topic.objects.get(id=topic)
        ns = NameSpace.objects.get(name_space=name_space)
        username = User.objects.get(username=username, name_space=ns)
        collection = Collection.objects.get(collection_id = collection)
        mode = collection.modality
        if mode == 'Competitive' or mode == 'Collaborative restricted':
            topic_comments = TopicComment.objects.filter(topic_id = topic)
            topic_comments = [{'comment':t.comment,'username':username.username} for t in topic_comments]
            doc_comments = DocumentComment.objects.filter(document_id = document)
            doc_comments = [{'comment':t.comment,'username':username.username} for t in doc_comments]
        elif mode == 'Collaborative open':
            topic_comments = TopicComment.objects.filter(topic_id = topic,username = username)
            topic_comments = [{'comment':t.comment,'username':username.username} for t in topic_comments]
            doc_comments = DocumentComment.objects.filter(document_id = document,username = username)
            doc_comments = [{'comment':t.comment,'username':username.username} for t in doc_comments]

        json_resp = {'topic':topic_comments,'document':doc_comments}
        return JsonResponse(json_resp)


    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            type = body['type']
            comment = body['comment']
            document = Document.objects.get(document_id=request.session['document'])
            topic = Topic.objects.get(id=request.session['topic'])
            ns = NameSpace.objects.get(name_space=request.session['name_space'])
            username = User.objects.get(username=request.session['username'], name_space=ns)
            if type == 'document' and comment != '':
                DocumentComment.objects.create(username = username, name_space = ns,comment=comment, document_id = document,language = document.language)
            elif type == 'document' and comment == '':
                DocumentComment.objects.filter(username = username, name_space = ns, document_id = document,language = document.language).delete()

            if type == 'topic' and comment != '':
                TopicComment.objects.create(username = username, name_space = ns,comment=comment, topic_id = topic)
            elif type == 'topic' and comment == '':
                TopicComment.objects.filter(username = username, name_space = ns, topic_id = topic).delete()


            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status = 500)
    return HttpResponse(status = 500)

# fine