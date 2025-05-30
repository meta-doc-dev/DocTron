from django.urls import path
from . import views
from django.urls import path
from . import views
from .dashboard.collection_users import get_collection_users
from .get_collections import get_user_collections
from .dashboard.indivioual_stats import get_individual_statistics
from .dashboard.global_stats import get_global_statistics
from .dashboard.document_wise import get_individual_document_wise_statistics, get_global_document_wise_statistics, get_agreement_document_wise_statistics
from .dashboard.user_stat_cards import get_user_statistic_cards
from .user_collection_statistics import get_user_collection_statistics
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import views as auth_views



app_name='doctron_app'
urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('register', views.register, name='register'),
    path('demo', views.demo, name='demo'),
    path('index', views.index, name='index'),
    path('loginPage/<str:orcid_error>', views.loginPage, name='loginPage'),
    path('loginPage', views.loginPage, name='loginPage'),
    path('registration', views.registration, name='registration'),
    path('logout', views.logout, name='logout'),
    path('tutorial', views.tutorial, name='tutorial'),
    path('guidelines', views.guidelines, name='guidelines'),
    path('uploadAnnotations',views.uploadAnnotations, name='uploadAnnotations'),
    # stats
    path('dashboard/', views.dashboard, name='dashboard'),
    path('individual-statistics', get_individual_statistics, name='individual-statistics'),
    path('global-statistics', get_global_statistics, name='global-statistics'),
    path('get_user_collection_statistics', get_user_collection_statistics, name='get_user_collection_statistics'),
    path('user-collections', get_user_collections, name='get_user_collections'),
    path('jump-to-document', views.update_document_id_from_dashboard, name='update-document-id-from-dashboard'),
    path('collection-users', get_collection_users, name='get_collection_users'),
    path('document-wise-global', get_global_document_wise_statistics, name='document-wise-global'),
    path('document-wise-agreement', get_agreement_document_wise_statistics, name='document-wise-agreement'),
    path('document-wise', get_individual_document_wise_statistics, name='document-wise'),

    path('user-statistic-cards', get_user_statistic_cards, name='user-statistics'),

    path('dashboard/<path:subpath>/', views.dashboard, name='dashboard-catchall'),
    path('my_stats', views.my_stats, name='my_stats'),
    path('documents', views.documents, name='documents'),
    # path('statistics/<str:collection_id>', views.statistics, name='statistics'),
    # path('statistics/<str:collection_id>/<str:type>', views.statistics, name='statistics'),
    # path('statistics', views.statistics, name='statistics'),
    #path('create_coehns', views.create_coehns, name='create_coehns'),
    path('create_fleiss_overview', views.create_fleiss_overview, name='create_fleiss_overview'),
    path('create_new_round',views.create_new_round,name='create_new_round'),
    path('credits', views.credits, name='credits'),
    path('instructions', views.instructions, name='instructions'),
    path('uploadFile', views.uploadFile, name='uploadFile'),
    path('collections',views.collections,name='collections'),
    path('mentions',views.mentions,name='mentions'),
    path('object_detection',views.object_detection,name='object_detection'),
    path('relationships',views.relationships,name='relationships'),
    path('facts',views.facts,name='facts'),
    path('concepts',views.concepts,name='concepts'),
    path('labels',views.labels,name='labels'),
    path('tag',views.tag,name='tag'),
    path('topic',views.topic,name='topic'),
    path('split_users',views.split_users,name='split_users'),
    path('collection_options',views.collection_options,name='collection_options'),
    path('get_fields',views.get_fields,name='get_fields'),
    path('annotation_types',views.annotation_types,name='annotation_types'),
    path('get_annotators',views.get_annotators,name='get_annotators'),
    path('collections/<str:type>',views.collections,name='collections'),
    path('relationships/<str:type>',views.relationships,name='relationships'),
    path('object_detection/<str:type>',views.object_detection,name='object_detection'),
    path('facts/<str:type>',views.facts,name='facts'),
    path('mentions/<str:type>',views.mentions,name='mentions'),
    path('concepts/<str:type>',views.concepts,name='concepts'),
    path('tag/<str:type>', views.tag, name='tag'),
    path('labels/<str:type>',views.labels,name='labels'),
    path('get_collection_labels', views.get_collection_labels, name='get_collection_labels'),
    path('get_cur_collection_documents', views.get_cur_collection_documents, name='get_cur_collection_documents'),
    path('get_collection_concepts', views.get_collection_concepts, name='get_collection_concepts'),
    path('get_collection_areas', views.get_collection_areas, name='get_collection_areas'),
    path('set_new_fields', views.set_new_fields, name='set_new_fields'),
    path('get_batches', views.get_batches, name='get_batches'),
    path('update_document_id', views.update_document_id, name='update_document_id'),
    path('download_annotations', views.download_annotations, name='download_annotations'),
    path('get_mention_info', views.get_mention_info, name='get_mention_info'),
    path('generate_suggestion', views.generate_suggestion, name='generate_suggestion'),
    path('pending_invitations', views.pending_invitations, name='pending_invitations'),
    path('accept_invitation', views.accept_invitation, name='accept_invitation'),
    path('get_suggestion', views.get_suggestion, name='get_suggestion'),
    path('auto_annotation', views.auto_annotation, name='auto_annotation'),
    path('download_template_concepts', views.download_template_concepts, name='download_template_concepts'),
    path('change_collection_id', views.change_collection_id, name='change_collection_id'),
    path('upload', views.upload, name='upload'),
    path('add_admin', views.add_admin, name='add_admin'),
    path('add_reviewer', views.add_reviewer, name='add_reviewer'),
    path('revise_collection', views.revise_collection, name='revise_collection'),
    path('annotate/<str:type>', views.annotate, name='annotate'),
    path('signup_with_orcid', views.signup_with_orcid, name='signup_with_orcid'),
    path('login_with_orcid', views.login_with_orcid, name='login_with_orcid'),
    path('loginorcidcallback', views.loginorcidcallback, name='loginorcidcallback'),
    path('get_assertions', views.get_assertions, name='get_assertions'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('honeypot', views.honeypot, name='honeypot'),
    #path('update_last_doc', views.update_last_doc, name='update_last_doc'),
    path('password_reset/<str:token>', views.password_reset, name='password_reset'),
    path('loginorcidcallback/<str:type>', views.loginorcidcallback, name='loginorcidcallback'),

    # annotat
    # ANNOTATIONS - GET
    path('get_mentions', views.get_mentions, name='get_mentions'),
    path('get_concepts', views.get_concepts, name='get_concepts'),
    path('get_tags', views.get_tags, name='get_tags'),
    path('get_concepts_full', views.get_concepts_full, name='get_concepts_full'),
    path('get_annotated_labels', views.get_annotated_labels, name='get_annotated_labels'),

    # ANNOTATIONS - POST
    path('add_mentions', views.add_mentions, name='add_mentions'),
    path('add_relationship', views.add_relationship, name='add_relationship'),
    path('update_relationship', views.update_relationship, name='update_relationship'),
    path('annotate_label', views.annotate_label, name='annotate_label'),
    path('set_concept', views.set_concept, name='set_concept'),
    path('set_profile', views.set_profile, name='set_profile'),
    path('password', views.password, name='password'),
    path('unlink_orcid', views.unlink_orcid, name='unlink_orcid'),
    path('link', views.link, name='link'),
    path('link_orcid', views.link_orcid, name='link_orcid'),
    path('change_role', views.change_role, name='change_role'),
    path('comment', views.comment, name='comment'),

    # ANNOTATIONS - DELETE
    path('delete_single_mention', views.delete_single_mention, name='delete_single_mention'),
    path('delete_label', views.delete_label, name='delete_label'),
    path('delete_concept', views.delete_concept, name='delete_concept'),
    path('delete_relationship', views.delete_relationship, name='delete_relationship'),
    path('delete_annotation_all', views.delete_annotation_all, name='delete_annotation_all'),
    path('delete_single_document', views.delete_single_document, name='delete_single_document'),

    # ADD
    #path('create_new_collection', views.create_new_collection, name='create_new_collection'),
    path('add_member', views.add_member, name='add_member'),
    path('add_labels', views.add_labels, name='add_labels'),
    path('transfer_annotations',views.transfer_annotations,name='transfer_annotations'),
    path('add_new_concepts_in_batch', views.add_new_concepts_in_batch, name='add_new_concepts_in_batch'),

    # GET
    path('get_annotation_mentions', views.get_annotation_mentions, name='get_annotation_mentions'),
    path('get_annotation_concepts', views.get_annotation_concepts, name='get_annotation_concepts'),
    path('get_annotation_labels', views.get_annotation_labels, name='get_annotation_labels'),
    path('get_annotation_relationships', views.get_annotation_relationships, name='get_annotation_relationships'),
    path('get_annotation_assertions', views.get_annotation_assertions, name='get_annotation_assertions'),
    path('get_session_params', views.get_session_params, name='get_session_params'),
    path('get_collections', views.get_collections, name='get_collections'),
    path('get_users_list', views.get_users_list, name='get_users_list'),
    path('get_labels_list', views.get_labels_list, name='get_labels_list'),
    path('get_members_list', views.get_members_list, name='get_members_list'),
    path('get_collection_documents', views.get_collection_documents, name='get_collection_documents'),
    path('get_documents_table', views.get_documents_table, name='get_documents_table'),
    path('get_count_per_label', views.get_count_per_label, name='get_count_per_label'),
    path('get_count_per_user', views.get_count_per_user, name='get_count_per_user'),
    path('get_document_content',views.get_document_content,name='get_document_content'),
    path('get_user_annotation_count_per_collection', views.get_user_annotation_count_per_collection, name='get_user_annotation_count_per_collection'),
    path('get_collection_languages', views.get_collection_languages, name='get_collection_languages'),
    # DELETE
    path('delete_member_from_collection', views.delete_member_from_collection, name='delete_member_from_collection'),
    path('delete_collection', views.delete_collection, name='delete_collection'),

    # COPY
    path('copy_label', views.copy_label, name='copy_label'),
    path('copy_mention', views.copy_mention, name='copy_mention'),
    path('copy_assertion', views.copy_assertion, name='copy_assertion'),
    path('copy_mention_concept', views.copy_mention_concept, name='copy_mention_concept'),
    path('copy_annotation', views.copy_annotation, name='copy_annotation'),
    path('copy_all_annotations_for_user_study', views.copy_all_annotations_for_user_study, name='copy_all_annotations_for_user_study'),





]


