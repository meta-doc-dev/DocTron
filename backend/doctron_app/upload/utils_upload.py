import hashlib
from datetime import datetime

from django.core.files.storage import FileSystemStorage
import shutil

from doctron_app.pdf_parser.pdf_parser import *
import pandas as pd
import json
import os
from doctron_app.models import *
from django.http import HttpResponse


def get_csv_fields(files):
    """This method returns the list of columns in a list of csv files"""

    keys = []
    for file in files:
        try:
            if not file.name.endswith('csv'):
                return keys
            df = pd.read_csv(file)
            df = df.where(pd.notnull(df), None)
            df = df.reset_index(drop=True)
        except Exception as e:
            print(e)
            return keys
        else:
            col_list = ['document_id', 'language']
            for col in df:
                if col not in col_list and col not in keys:
                    keys.append(col.replace(' ', '_'))
    return keys


def get_json_fields(files):
    """This method returns the list of columns in a list of json files"""

    keys = []
    for file in files:
        data = json.load(file)
        keys = list(set(data.keys()))
        keys.extend([k for k in keys if k not in ['document_id', 'language']])
    return keys


from ..elaborate_xml import XMLParser
#from ..grobid_client_python.grobid_client.grobid_client import GrobidClient
import time
import random


def create_json_content_from_file(file):
    """This method converts the textual content in the file into json content"""

    contents = []
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    print(file.name)
    path_to_save = os.path.join(workpath, '../temp')

    if file.name.endswith('.csv'):
        df_file = pd.read_csv(file)
        df_file = df_file.where(pd.notnull(df_file), None)
        # df_file = df_file.reset_index(drop=True)
        df_file.columns = df_file.columns.str.replace(" ", "_")
        js_df = df_file.to_json(orient="index")
        parsed = json.loads(js_df)
        sorting = df_file.columns
        for k in list(parsed.keys()):
            report_json = parsed[k]
            if not 'doc_id' not in list(report_json.keys()):
                characters = string.ascii_letters + string.digits
                lines = ''.join(random.choice(characters) for _ in range(32))
                report_json['doc_id'] = hashlib.md5(lines.encode()).hexdigest()

            # report_json['sk_metatron'] = sorting
            # report_json['format'] = 'csv'
            contents.append(report_json)

    elif file.name.endswith('.json'):
        files = json.load(file)

        # TO DO: flatten json

        if len(list(files.keys())) == 1 and list(files.keys()) == ['documents']:
            documents = files['documents']
            for doc in documents:
                # doc['format'] = 'json'
                # doc['sk_metatron'] = list(doc.keys())
                if not 'doc_id' not in list(doc.keys()):
                    characters = string.ascii_letters + string.digits
                    lines = ''.join(random.choice(characters) for _ in range(32))
                    doc['doc_id'] = hashlib.md5(lines.encode()).hexdigest()
                contents.append(doc)
        else:
            # files['sk_metatron'] = list(files.keys())
            if not 'doc_id' not in list(files.keys()):
                characters = string.ascii_letters + string.digits
                lines = ''.join(random.choice(characters) for _ in range(32))
                files['doc_id'] = hashlib.md5(lines.encode()).hexdigest()
            contents.append(files)

    elif file.name.endswith('.txt'):
        lines = file.readlines()
        report_json = {}
        lines = [line.decode("utf-8") for line in lines]
        if lines[0].startswith('ID: ') or lines[0].startswith('id: '):
            report_json['doc_id'] = lines[0].split('ID:')[0].strip()
        else:
            report_json['doc_id'] = hashlib.md5(lines.encode()).hexdigest()

        lines = '\n'.join([line.replace('\n', '') + ' ' for line in lines[1:]])

        report_json['content'] = lines

        contents.append(report_json)

    elif file.name.endswith('.png') or file.name.endswith('.jpg') or file.name.endswith('.jpeg'):
        doc_id = file.name[:-4]
        report_json = {}
        report_json['doc_id'] = doc_id

        contents.append(report_json)



    elif file.name.endswith('.pdf'):
        print('entro in pdf')
        fs = FileSystemStorage(location=path_to_save)
        filename = fs.save(file.name, file)
        print(filename)
        workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        path_output = os.path.join(workpath, '../temp')
        config_path = os.path.join(workpath, '../grobid_client_python/config.json')
        f = open(config_path, 'r')
        data = json.load(f)
        print(data["grobid_server"])
        client = GrobidClient(config_path=config_path)
        st = time.time()
        client.process("processFulltextDocument", path_to_save, output=path_output)
        end = time.time()
        print(end - st)
        found_file = False
        while not found_file:
            time.sleep(1)
            file = os.listdir(path_output)
            file = [x for x in file if x.endswith('xml')]
            if len(file) > 0:
                found_file = True

        file = os.listdir(path_output)
        file = [x for x in file if x.endswith('xml')]
        if len(file) > 0:
            file = file[0]
        else:
            raise Exception("file not found")
        print(file)
        file_path = os.path.join(path_output, file)

        parser = XMLParser(file_path)
        json_doc = parser.build_json_doc()
        title = parser.get_title() + parser.get_authors()
        json_doc['doc_id'] = hashlib.md5(title.encode()).hexdigest()
        json_new_doc = {}
        json_new_doc['doc_id'] = json_doc['doc_id']
        json_new_doc['title'] = json_doc['title']
        line = '\n'
        for k, v in json_doc.items():
            if 'title' not in k:
                line += f'{str(k)}\n{str(v)}\n\n'
        json_new_doc['content'] = line
        contents.append(json_new_doc)
        for f in os.listdir(path_output):
            file = os.path.join(path_output, f)
            if os.path.isfile(file):
                print("removing", f, path_output)
                os.remove(file)
        # for path in [path_output, path_to_save]:
        #     for filename in os.listdir(path):
        #         file_path = os.path.join(path_output, filename)
        #         try:
        #             if os.path.isfile(file_path) or os.path.islink(file_path):
        #                 os.unlink(file_path)
        #             elif os.path.isdir(file_path):
        #                 shutil.rmtree(file_path)
        #         except Exception as e:
        #             print('Failed to delete %s. Reason: %s' % (file_path, e))

    return contents
