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

Run a new terminal session and run ```docker compose up```. This procedure will take few minutes depending on your hardware and you internet connection. When the procedure is finished you can open a new browser winodw (chrome is recommended) and you can start uploading new documents.
Once that DocTron is up and running, open a new terminal and run ```docker-compose exec db bash -c "psql -U postgres -tc \"SELECT 1 FROM pg_database WHERE datname = 'doctron_db'\" | grep -q 1 || psql -U postgres -c 'CREATE DATABASE doctron_db;' && pg_restore -U postgres -d doctron_db -v backup_db_1.tar"```: this will setup the database restoring the database schema and providing some test collections (those provided in the online demo instance).

## Annotation Interface
In the annotation interface you can visualize your annotations and annotate collections' documents.
<p align="center">
   <img src="./img/ui.jpg" alt="logo" width="900px"/>
</p>

   1. In the main header it is possible to logout, and access to collection and statistics dashboard pages;
   2. In the document header it is possible to check the annotation template chosen, the collection name, topic and document ids. The document and topic are buttons which allow the user to add some comments;
   3. The vertical toolbar which allows users to: change role, change document, topic and collection, check other users' annotations, get an overview of the statistics of the collection, customize colors and font, upload new documents, concepts, annotations, download the annotation, automatically annotate the documents (from A to J in the figure).
   4. The annotation panel on the left allows you to visualize you annotations performed and edit or remove them accordingly;
   5. The part of the page where the textual document is subdivided into topic and document infomation;

