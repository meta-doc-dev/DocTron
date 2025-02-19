# DocTron version 1.0.0
<p align="center">
   <img src="./img/logo_1.png" alt="logo" />
</p>
DocTron is an open-source, collaborative, web-based annotation targeting IR domain. 
All the source code, the installation guidelines, and instructions to use the tool are availanle in this repository.

A set of videos illustrating the instructions on how to perform annotations and an overview of the features that DocTron provides is available at: https://doctron.dei.unipd.it/demo

## Requirements
A demo version of DocTron is available online at http://doctron.dei.unipd.it. Users can login with username and password "demo" and test DocTron functionalities.
In order to locally deploy DocTron in your computer or in a remote server you need Docker and docker-compose. To install them, you can follow the instructions available at: https://docs.docker.com/get-docker/ (Docker) and https://docs.docker.com/compose/install/ (docker-compose). 

Clone or donwload this repository. Open the **doctron** folder and, replace the url provided in the url.txt file with the url of the server where DocTron will be deployed. Your url must replace the default one: http://0.0.0.0:8000. 

Run a new terminal session and place inside ```backend``` folder --where there is the ```docker-compose.yml``` file-- and run 

```docker compose up```

This procedure will take few minutes depending on your hardware and you internet connection. When the procedure is finished you can open a new browser winodw (chrome is recommended) and you can start uploading new documents.
Once that DocTron is up and running, open a new terminal and run 

```docker-compose exec db bash -c "psql -U postgres -tc \"SELECT 1 FROM pg_database WHERE datname = 'doctron_db'\" | grep -q 1 || psql -U postgres -c 'CREATE DATABASE doctron_db;' && pg_restore -U postgres -d doctron_db -v backup_db_1.tar"```

this will setup the database restoring the database schema and providing some test collections (those provided in the online demo instance).

## UI - User interface
In the annotation interface you can visualize your annotations and annotate collections' documents.
<p align="center">
   <img src="./img/ui.jpg" alt="ui" width="900px"/>
</p>

   1. In the main header it is possible to logout, and access to collection and statistics dashboard pages;
   2. In the document header it is possible to check the annotation template chosen, the collection name, topic and document ids. The document and topic are buttons which allow the user to add some comments;
   3. The vertical toolbar which allows users to: change role, change document, topic and collection, check other users' annotations, get an overview of the statistics of the collection, customize colors and font, upload new documents, concepts, annotations, download the annotation, automatically annotate the documents (from A to J in the figure).
   4. The annotation panel on the left allows you to visualize you annotations performed and edit or remove them accordingly;
   5. The part of the page where the textual document is subdivided into topic and document infomation;

## Annotation templates 
DocTron provides 7 annotation templates you can use to annotate documents with respect to a topic. 
   1. **Graded labeling.** This annotation template consists of labels (e.g., relevance) associated with a range of values (e.g., integers from 0 to 3). Annotators must assign a value to each label, indicating that the label’s value is for the document concerning the specific topic. This template can be used for text-based and image-based topics and documents, as the graded labeling is applied at the document level and is not limited to specific sections of a text or portions of an image.
   2. **Passages annotation.** Passages are brief sections -—comprising one or more sentences—- within a textual document. Doctron allows users to identify these passages and annotate them accordingly. Users can select a passage by dragging from the first to the last character and then associate a graded label that indicates the significance of that passage concerning a topic. 
   3. **Entity tagging.** Entity tagging --or NER (Named Entity Recognition) consists in associating to the mentions --portions of text of some words identifiable in the textual document-- one or more labels, called tags --e.g., Person, Organization, Animal. In DocTron, to associate a tag to a mention, the mention has to be detected by dragging and dropping from the first to the last character of the mention. Then, it is possible to select the desired tag by clicking on the mention;
   4. **Entity linking.** Entity linking --or NER+L (Named Entity Recognition and Linking) consists in associating to the mentions the concepts belonging to a knowledge base. In DocTron, to associate a concept to a mention, the mention has to be detected by dragging and dropping from the first to the last character of the mention. Then, right clicking on the mention it is possible to open the concept panel where it is psosible to choose the concept or create a new one;
   5. **Relationships annotation.** A relationship is a triple composed of a subject, a predicate, and an object. At least one of them must be a mention in the textual document --either linked, tagged, or plain. For this reason it is a mention-level annotation template;
   7. **Facts annotation.** Facts are triples of concepts from a knowledge base, or tags composed of a subjects, a predicate and an object. In the same way as graded labeling, this a document level annotation type and is unlinked from the document being evaluated;
   8. **Objects detection.** An object is a portion of an image. To detect an object in an image in DocTron, users should identify the perimeter of the object. Objects can be associated with a graded label that identify the value of a label of the object with respect to the topic. An example is reported in the Figure above.
      
<p align="center">
   <img src="./img/objdec.jpg" alt="objdec" width="900px"/>
</p>

## Statistics dashboard 
In the statistics dashborard, reachable by clicking on _Statistics_ button of the main header, you can visualize statistics related to the collections.
<p align="center">
   <img src="./img/stats.jpg" alt="stats" width="900px"/>
</p>

   1. In the dashboard on the left it is possible to change collection basing on the annotation template;
   2. In the header it is possible to select which type of statistics to visualize --individual concern the single annotator, global concenr the entire set of annotators, while IAA contains an overview of the IAA metrics. In the image above there is an overview of the IAA metrics;
   3. Three cards provide an overview of the annotations;
   4. The table displays the Fleiss and Krippendorff’s alpha values for each document;
   5. The Coehn's Kappa is a symmetric matrix where for each pair of users (row and column) it is provided the Coehn's kappa value;


## Customizability and Collections
DocTron allows the users to create one or more  _collections_: a collection contains one or more documents which can be annotated by one or more users. To create a new collection go to COLLECTIONS button at the top of the main interface which will redirect to the collections page. This page contains the list of collections a user can annotate and a form to create a new collection. 

The collections a user can annotate contain the following information: creator, date of creation, descriptions, documents, number of annotators, annotators' names, labels list. It is possible to interact with the collections, in particular it is possible to:
1. load more information;
2. have an overview of the documents of the collection and the related annotations;
3. annotate the collection;
4. delete the collection (for the creator only)

<p align="center">
   <img src="./img/8.png" alt="logo" width="900px"/>
</p>

The documents page contains a table where each document is a row of the table. For each document it is possible to keep track of the annotation of each type. Users can see other annotators' annotations and download the related annotations.

<p align="center">
   <img src="./img/13.jpg" alt="logo" width="900px"/>
</p>

To create a new collection, click on ADD COLLECTION to open the form. To create a new collection the following information should be provided: (i) name, (ii) description, (iii) a list of members who can annotate the collection; (iv) a file containing the concepts that can be linked to the mentions or added in relationships and assertions; (v) one or more textual documents: documents can be uploaded in JSON, CSV, PDF, TXT; it is possible to annotate pubmed abstracts by providing a list of PMIDs, abstract from semantics scholar and openaire by providing a list of DOIs. In this case, the integration with external rest apis allows to automatically get the abstracts; (vi) a list of labels that can be used to classify the documents. Labels, members and documents can be updated at any time.
When a new member is added, it will not be automatically able to annotate the collection: an invitation is sent to them, and then, once that they accept the invitation, they will be able to annotate the documents.



