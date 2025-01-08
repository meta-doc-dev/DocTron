import {Col, Row} from "react-bootstrap";

import React, {useState, useEffect, useContext, createContext, useRef} from "react";

import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import './instructions.css'

const checkedIcon = <CheckBoxIcon fontSize="small" />;


export default function Demo(props){
    const [AnnotationInterface,SetAnnotationInterface] = useState(false)
    const [CollectionInterface,SetCollectionInterface] = useState(false)
    const [StatisticsInterface,SetStatisticsInterface] = useState(false)


    useEffect(() => {
        document.title = 'Instructions';
    }, []);

    function scroll(e,elem){
        e.preventDefault()
        document.getElementsByClassName(elem).item(0).scrollIntoView({ behavior: "smooth"})
    }


    return(
        <div style={{padding:"5% 10%"}}>
            <h1 style={{textAlign:"center"}}>Tutorial</h1>
            <Row>
            {/*<Col md={2}></Col>*/}
            <Col md={12}>
            <div>Here you can find a set of short videos showing the features of MetaTron</div>
            <div id = 'annotation_types'>
            <h2>Annotation Types</h2>
            <div>
                <div>
                    <h4>1 - Mentions annotation</h4>
                    <p className='dem'>
                        Mentions are textual spans in a document referring to an entity. There are three possible ways to annotate
                        a mention:<br/>
                        <ol>
                            <li><b>Drag and drop from the first to the last character of the mention:</b> this method is useful
                                when the mention does not comprise words single spaces separated
                            </li>
                            <li>
                                <b>Double click on the word:</b> this method is useful to select a single word
                            </li>
                            <li>
                                <b>Click on the first and on the last words of a mention</b>: this method is useful when the mention
                                comprises two or more words single spaces separated.
                            </li>
                        </ol>
                    </p><br/>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/mentions_annotation.mp4" />
                    </video>
                        <div>Video 1: mentions annotation</div>
                    </div>
                </div>
                <div>
                    <h5>1.1 - Mention panel</h5>
                    <p className='dem'>The mention panel allows to act directly on the mention. The mention panel can be opened right-clicking
                        on a mention.<br/>

                        <ol>
                            <li><b>Info</b>: Display some information about the annotation time, number of annotators, linked concepts </li>
                            <li><b>Suggestions</b>: Display suggestions on concepts to link to the selected mentions. The suggestions are
                            based on the annotations of the other members of the collection. It is possible to accept the suggestion and the
                            concept will be immediately linked.
                                <br/>
                                <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                    <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/suggestion.mp4" />
                                </video>
                                    <div>Video 2: Annotation suggestion from the mention panel</div>
                                </div>
                            </li>
                            <li><b>Annotate all</b>: Annotate all the mentions with the same content of the selected mention in the document. If the mention
                            is also linked to a concept, all the mentions found will be also linked to that concept.
                            <br/>
                                <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                    <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/annotate_all.mp4" />
                                </video>
                                    <div>Video 3: Annotate all the mention with the same textual content of the selected mention</div>

                                </div>

                            </li>
                            <li><b>Add Concept</b>: Allows to select a concept to link to a mention</li>
                            <li><b>Add Relationship</b>: Allows to select a relationship having the mention as subject</li>
                            <li><b>Delete</b>: Delete the mention and the concepts, and relationships involving the mention</li>
                        </ol>

                    </p>
                </div>
                <div>
                    <h4>2 - Concepts Linking annotation</h4>
                    <p className='dem'>To link a concept to a mention, open the mention panel of s mention and click on <i>Add concept</i>. On
                        the modal select the concept type, the name, and URI (if needed). A description will automatically appear once selected the concept.
                        It is possible to filter the list of concepts according to the concept type. It is possible to type
                        the first chars of a concept and the list will filtered keeping all the concepts whose name contain the typed chars.
                    </p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/concepts_annotation.mp4" />
                    </video>
                        <div>Video 4: concepts linking annotation</div>
                    </div>
                </div>
                <div>
                    <h4>3 - Relationships annotation</h4>
                    <p className='dem'>To create a new relationship, open the mention panel of s mention and click on <i>Add relationship</i>.
                        Once clicked, MetaTron will enter in <i>relationship mode</i> and the selected mention will be the subject of the relationship. On the right,
                        a relationship panel provides an overview of the relationship.
                        Relationships comprehend a subject, a predicate and an object. Each of them can be a mention or a concept. Each relationship must contain
                        at least a mention. To select new mentions composing the relationship, right-click on the target mention and select the role -- e.g., subject, predicate, object.
                        To select a concept instead, click on the <i>Add predicate, Add subject</i> or <i>Add object</i> buttons on the relationship panel. This buttons are
                        available if the subject, predicate or object have not been assigned nor to a mention nor to a concept.

                        <br/><br/>
                        If a relationship has subject and object mentions, there are two possible ways to define a predicate:
                        <ol>
                            <li>Click on the <i>+ PREDICATE</i> and type the relation predicate</li>
                            <li>Click on <i>Add predicate</i> in the relationship panel and select the predicate concept</li>
                        </ol>
                    </p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/full_rel.mp4" />
                    </video>
                        <div>Video 5: three relationships annotations. The first one consists in typing the predicate, the second
                        one in adding a predicate concepts, the third one has the subject mention and the predicate and object concepts.</div>
                    </div>
                </div>
                <div>
                    <h4>4 - Assertions annotation</h4>
                    <p className='dem'>Assertions are compose of a subject, a predicate and an object. Differently from the relationships,
                    all the three elements must be concepts. To select a new assertions, go to the <i>+ ASSERTION</i> button in the
                    main interface. An assertion panel is displayed and it is possible to add subject, predicate and object via the
                    <i>Add subject, Add predicate</i> and <i>Add object</i> buttons.</p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/assertion_annotation.mp4" />
                    </video><div className={'caption'}>Video 6: Assertion annotation</div></div>
                </div>
                <div>
                    <h4>5 - Labels annotation</h4>
                    <p className='dem'>Labels are classes associated to the entire document. To select one or more labels, click on <i>Annotations</i> button
                    on the main interface and select the <i>labels</i> option. The list of labels will appear and each label is a button that can selected or deselected.</p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/labels_annotation.mp4" />
                    </video><div className={'caption'}>Video 7: labels annotation</div></div>
                </div>
            </div>
                <div id = 'annotations_list'>
                    <h2>Annotations overview</h2>
                    <p className='dem'>The <i>Annotation</i> button provides an overview of the annotations performed for each annotation type for the current document.
                    For what concerns mentions and concepts, it is possible to check the annotated concepts and mentions. For the relationships and assertions instead,
                        it is possible to edit and delete each relationship and assertion annotated. The labels have been already described above.
                    </p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/annotations.mp4" />
                    </video><div className={'caption'}>Video 8: annotations list for each annotation type</div></div>
                </div>
                <div id={'sidebar'}>
                    <h2>The Sidebar</h2>
                    <p className='dem'>
                    The vertical sidebar on the left of the main interface provides a set of functionalities that can be
                    accessed while annotating the collection.
                    <br/>
                    <ol>
                        <li><b>Change document</b>: change the document to annotate. It is possible to filter by ID, batch, annotated and not annotated documents;
                        <br/>
                            <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/change_doc.mp4" />
                            </video><div className={'caption'}>Video 9: sidebar change document, collections and settings</div></div>
                        </li>
                        <li><b>Change collection</b>: change the collection between those associated to the user. Each collection is provided with the percentage of documents annotated so far by the user;</li>
                        <li><b>Copy annotations</b>: check the annotators of the collection and copy one or more of her annotations. It is possible also to get and edit the annotations selected via majority voting among all the annotations ;
                        <br/>
                            <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/members.mp4" />
                            </video><div className={'caption'}>Video 10: Copy the annotation of a member, or the annotation obtained via majority voting</div></div>

                        </li>
                        <li><b>Statistics</b>: get an overview of the statistics of the document's annotations;
                            <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/quickstats.mp4" />
                            </video><div>Video 11: statistics of the current document</div><br/>
                </div>
                        </li>
                        <li><b>Settings</b>: change app settings;</li>
                        <li><b>Download</b>: download the annotations for the current document. It is possible to select the annotation type, the file format, and the annotator;</li>
                        <li><b>Upload</b>: upload new documents, concepts, or annotations. In this last case, it is possible to upload a csv file with the annotations to upload. All the annotations will be able for the user;</li>
                        <li><b>Settings</b>: change app settings;</li>
                        <li><b>View settings</b>: Add/hide the concepts from the interface;</li>
                        <li><b>Automatic annotation</b>: Automatic annotation with AutoTron: two modes are possible: GCA - annotates relationships, GDA - annotates assertions;
                                <br/>
                            <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/autotron_gca.mp4" />
                            </video>
                                <div className={'caption'}>Video 12: AutoTron Gene Cancer association</div>
                            </div><br/>
                            <div className='videoclass'><video width="900px" height="600px" controls="controls">
                                <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/autotron_gda.mp4" />
                            </video>
                                <div className={'caption'}>Video 13: AutoTron Gene Disease association</div></div>


                        </li>
                    </ol>
                    </p>



                </div>
                <div id = 'collection'>
                    <h2>The Collections Page</h2>
                    <p className='dem'>The collection web page allows to navigate between the collections the user can annotate, and create new collections. </p>
                    <h4>Add a new collection</h4>
                    <p className='dem'>To create a new collection, click on <i>Add collection</i> button on the top of the page: the user
                    that creates a new collection is asked to specify: the collection name, the description, a set of labels, a set of concepts, the annotators invited to annotate the collection,
                    the list of documents that can be uploaded in JSON, CSV, PDF, TXT formats, a list of IDS or DOIs whose abstract and title will be downloaded from Sementic Scholar, OpenAIRE and PubMed.</p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/new_collection.mp4" />
                    </video>                    <div className={'caption'}>Video 14: create a new collection</div></div>
                </div>

                    <h4>Collection's documents overview</h4>
                    <p className='dem'>Clicking on the <i>Documents</i> button placed under a collection, it is possible to access to the collection's documents overview.
                    The page hosts a table where each row represents a document and shows data such as: the id, the date of last annotation and, for each annotation type
                    shows all the annotations, the number of annotators and their names. In addition, it is possible also to download the annotations, view the document's text and delete the document (and all the related annotations).</p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/documents.mp4" />
                    </video>                    <div className={'caption'}>Video 15: collection documents table</div></div>

                </div>
                <div>
                    <h2>The Statistics Page</h2>
                    <p className='dem'>
                    The statistics web page contains the annotations statistics of the collection. Global statistics concern
                        all the annotators of the collection, while personal statistics concern the user. From the global and
                        personal statistics it is possible to check the statistics related to all the documents of the collection or
                        to a specific document chosen by the user.<br/> Statistics include the following information:<br/>
                        <ul>
                            <li><b>General statistics: </b> these statistics provides an overview of the count of annotated documents, annotators, and number of annotations for each annotation type. For each
                            type is also provided the value of agreement computed via Fleiss' kappa;</li>
                            <li><b>Concepts overview: </b> these statistics concern the concepts linked to the mentions and involved in one or more relationships/assertions. These statistics give an overview of the
                            concept types and concept names used to annotate the collection;</li>
                            <li><b>Documents annotations overview: </b> For each document it is provided an histogram with the number of annotations for each type</li>
                            <li><b>Annotators overview: </b> Number of annotators for each document;</li>
                            <li><b>Concept types overview: </b> pie charts showing the distribution of concept types among subject, predicate and objects;</li>
                        </ul>


                    </p>
                    <div className='videoclass'><video width="900px" height="600px" controls="controls">
                        <source type="video/mp4" src="https://metatron.dei.unipd.it/static/video/stats.mp4" />
                    </video>
                    <div className={'caption'}>Video 16: statistics page</div>
                    </div>
                </div>








                </Col>
            </Row>

        </div>
    );
}