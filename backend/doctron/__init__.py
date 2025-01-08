# import nltk
# import time
# from doctron_app.autotron.src.tron import AutoTron
#
# # tron = ''
# st = time.time()
# nltk.download('punkt')
# end = time.time()
# print("downloaded punkt")
# st = time.time()
# print('Initializing Autotron models')
# tron = AutoTron("GCA")
# end = time.time()
# print('Autotron initialization completed in: ',str(end-st), ' seconds')

from __future__ import absolute_import, unicode_literals

# Questo importa Celery quando Django avvia
from doctron.celery import app as celery_app

__all__ = ('celery_app',)
