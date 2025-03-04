import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from gensim.parsing import strip_tags


class XMLParser:
    def __init__(self,path):
        with open(path, 'rb') as f:
            file = f.read()
            self.soup = BeautifulSoup(file, 'xml')
        # self.path = file_path
        # tree = ET.parse(file_path)
        # root = tree.getroot()
        # self.root = root
        # print(root.tag)

    def get_title(self):
        title_tmp = self.soup.find_all('title')
        title = title_tmp[0].get_text() if len(title_tmp) > 0 else ''
        title = strip_tags(title)
        title = title.replace('\n','')
        return title

    def get_keywords(self):
        keywords_tmp = self.soup.find_all('keywords')
        wordsRet = []
        if len(keywords_tmp) > 0:
            keywords_tmp = keywords_tmp[0]
            words = keywords_tmp.find_all('term')
            for el in words:
                wordsRet.append(el.get_text())
        wordsRet = [w.replace('\n','') for w in wordsRet]
        return wordsRet


    def get_abstract(self):
        abstract_tmp = self.soup.find_all('abstract')
        abstract = abstract_tmp[0].get_text() if len(abstract_tmp) > 0 else ''
        abstract = abstract.replace('\n','')
        abstract = strip_tags(abstract)
        return abstract



    def get_sections(self):
        json_body = {}
        body = self.soup.find('body')
        rows = body.find_all('row')
        for row in rows:
            row.extract()
        cells = body.find_all('cell')
        for row in cells:
            row.extract()
        graphics = body.find_all('graphic')
        for row in graphics:
            row.extract()
        labels = body.find_all('label')
        for row in labels:
            row.extract()
        c = 0
        for child in body.find_all(recursive=False):
            if child.find('head') and child.find('head').text != '':
                head = child.find('head').text
                for s in child.find_all('head'):
                    s.extract()
            else:
                head = f'section_{c}'
                c+=1
            json_body[head] = child.text

        return json_body

    def get_sections_old(self):
        json_body = {}
        body = self.soup.find('body')
        sections = body.find_all('div')
        head = body.find_all('head')
        c=0
        for div in sections:

            if div.find('p'):
                text_section = div.find('p').text
                if div.find("head"):
                    title_section = div.find('head').text
                    if title_section in list(json_body.keys()):
                        title_section = title_section + '_'+str(c)
                        c+=1
                    json_body[title_section] = text_section
            else:
                if div.find("head"):
                    title_section = div.find('head').text
                    json_body[title_section] = ""

        return json_body

    def get_captions(self):
        json_body = {}
        body = self.soup.find('body')
        figures = body.find_all('figure')
        caption_count = 0
        for fig in figures:
            if fig.find("figDesc"):
                text_section = fig.find('figDesc').text
                json_body['figure_'+str(caption_count)] = text_section
                caption_count += 1
        return json_body

    def get_notes(self):
        json_body = {}
        body = self.soup.find('body')
        if body:
            notes = body.find_all('note')
            caption_count = 0
            for fig in notes:

                json_body['note_'+str(caption_count)] = fig.text
                caption_count += 1

        return json_body

    def get_authors(self):
        authors = []
        # tg = [tag.name for tag in self.soup.find_all()]
        # print(tg)
        full = ''
        source_desc = self.soup.find_all('fileDesc')
        if len(source_desc) > 0:
            authors_xml = source_desc[0].find_all('author')

            for author_xml in authors_xml:
                author = {}
                pid = []
                name = author_xml.find('forename')
                surname = author_xml.find('surname')
                if name is not None and surname is not None:
                    author['affiliation'] = []


                    name = author_xml.find('forename').get_text()
                    surname = author_xml.find('surname').get_text()
                    fullname = name + ' ' + surname
                    author['name'] = name
                    author['surname'] = surname
                    author['fullname'] = fullname
                    full = full + ' ' + fullname
                    authors.append(author)
        return full

    def build_json_doc(self):
        json_doc = {}
        # json_doc['sk_metatron'] = ['title','authors','keywords','abstract']
        json_doc[f'title'] = self.get_title()
        json_doc[f'authors'] = self.get_authors()
        json_doc[f'abstract'] = self.get_abstract()
        json_doc[f'keywords'] = ', '.join(self.get_keywords())

        json_sections = self.get_sections()
        c = 4

        for k,v in json_sections.items():
            # json_doc['sk_metatron'].append(k)
            # k = f'{c}_{k}'
            c+=1
            json_doc[k] = v
        # for k,v in self.get_captions().items():
        #     # json_doc['sk_metatron'].append(k)
        #
        #     json_doc[k] = v
        # for k,v in self.get_notes().items():
        #     # json_doc['sk_metatron'].append(k)
        #
        #     json_doc[k] = v
        return json_doc






if __name__ == "__main__":
    parser = XMLParser('./files/2020.lrec-1.872.tei.xml')
    doc = parser.build_json_doc()
    print(doc)
