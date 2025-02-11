import './App.css';
// import LabelList from "./components/Labels/LabelList";
import {AppContext} from './App';
import React, {useState, useEffect, useContext, useCallback, useMemo, createContext} from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import {styled} from '@mui/material/styles';
import Collapse from '@mui/material/Collapse';
import {Container, Row, Col} from 'react-bootstrap';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import {CSSTransition} from 'react-transition-group';

import Divider from '@mui/material/Divider';
import {CollectionsBookmarkOutlined} from "@mui/icons-material";
import ActualPosition from "./components/BaseComponents/ActualPosition";
// import PassageLabelsList from "./components/Passages/PassageLabelsList";
import Chip from '@mui/material/Chip';
import DocumentToolBar from "./components/Document/ToolBar/DocumentToolBar";
import Document from "./components/Document/DocumentFinal_2";
import TopicInfo from "./components/Topic/TopicInfo";
import LabelsClass from "./components/RightSideMenu/labels/Labels";
import MentionsListClass from "./components/RightSideMenu/mentions/MentionsListClass";
import DraggableModal from "./components/Annotations/concepts/DraggableConceptModal";
import FilterComponent from "./components/SideBar/utils/Filter";
import MembersComponent from "./components/SideBar/Members";
import CollectionsComponent from "./components/SideBar/ChangeCollections";
import ChangeDocumentComppnent from "./components/SideBar/ChangeDocument";
import SummaryStatsComponent from "./components/SideBar/StatsStummary";
import ConceptsListClass from "./components/RightSideMenu/associations/ConceptsListClass";

import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import Button from "@mui/material/Button";
// axios.defaults.xsrfCookieName = "csrftoken";
// axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
import {DeleteRange, ClickOnBaseIndex} from './components/HelperFunctions/HelperFunctions'
import ChangeSettingsComponent from "./components/SideBar/ChangeSettings";
import {HuePicker} from "react-color";
import RelationshipComponent from "./components/RightSideMenu/relationships/RelationshipComponent";
import ChangeViews from "./components/SideBar/ChangeViews";
import DownloadDocument from "./components/SideBar/DownloadDocuments";
import UploadDocument from "./components/SideBar/UploadDocuments";
import RelationshipsClass from "./components/RightSideMenu/relationships/RelationshipsClass";
import Dialog from "@mui/material/Dialog";
import AssertionsList from "./components/RightSideMenu/assertions/AssertionsComponent";
import AutomaticAnnotation from "./components/SideBar/AutomaticAnnotation";
import DraggableModalTag from "./components/Annotations/tag/DraggableTagModal";
import TagsListClass from "./components/RightSideMenu/tags/TagsListClass";
import ShowTypes from "./components/SideBar/ShowTypes";
import RolesComponent from "./components/SideBar/RolesComponent";
import ChangeTopic from "./components/SideBar/ChangeTopic";
import CreateFact from "./components/Document/ToolBar/CreateFactComponent";
import DocumentImage from "./components/Document/DocumentImage";
import DocumentImageSelect from "./components/Document/DocumentImageSelect";

export const ConceptContext = createContext('')
export const RelSearchContext = createContext('')


const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

function BaseIndex() {
    const {
        username,
        relationshipslist,
        showtasks,
        role,
        showroles,
        showtopics,
        relationship,
        showtypes,
        showtagspannel,
        addtagmodal,
        binaryrel,
        collection,
        opensnack,
        modality,
        startrange,
        currentdiv,
        endrange,
        tags,
        snackmessage,
        secondsel,
        firstsel,
        predicate,
        modifyrel,
        showautomaticannotation,
        profile,
        curannotator,
        newrelation,
        source,
        newfact,
        newfactin,
        readonlyrelation,
        enablerelation,
        sourcetext,
        sourceconcepts,
        targettext,
        targetconcepts,
        predicatetext,
        predicateconcepts,
        target,
        collectionconcepts,
        showfactspannel,
        annotators,
        showupload,
        showdownload,
        curmention,
        showview,
        users,
        showlabelspannel,
        showmentionsspannel,
        showrelspannel,
        showconceptspannel,
        showsettings,
        areascolors,
        documentlist,
        showdocs,
        collectionslist,
        collectiondocuments,
        annotatedlabels,
        fieldsToAnn,
        fields,
        showmembers,
        showfilter,
        showstats,
        showcollections,
        expand,
        inarel,
        labels,
        addconceptmodal,
        annotation,
        mentions,
        document_id,
        concepts,topicType,
        collType
    } = useContext(AppContext);
    const [UsersList, SetUsersList] = users

    const [CurMention, SetCurMention] = curmention;
    const [ShowFacts, SetShowFacts] = showfactspannel
    const [Start, SetStart] = startrange
    const [End, SetEnd] = endrange
    const [CollectionType,SetCollectionType] = collType
    const [TopicType,SetTopicType] = topicType
    const [Annotation, SetAnnotation] = annotation
    const [Relationship, SetRelationship] = relationship
    const [ShowRoles, SetShowRoles] = showroles
    const [Tags, SetTags] = tags
    const [BinaryRel, SetBinaryRel] = binaryrel
    const [ShowLabels, SetShowLabels] = showlabelspannel
    const [ShowMentions, SetShowMentions] = showmentionsspannel
    const [ShowConcepts, SetShowConcepts] = showconceptspannel
    const [ShowRels, SetShowRels] = showrelspannel
    const [ShowTags, SetShowTags] = showtagspannel
    const [ShowAutoAnno, SetShowAutoAnno] = showautomaticannotation;
    const [DocumentID, SetDocumentID] = document_id
    const [Expand, SetExpand] = expand
    const [NewRelation, SetNewRelation] = newrelation
    const [Collection, SetCollection] = collection
    const [Username, SetUsername] = username
    const [CollList, SetCollList] = collectionslist
    const [Labels, SetLabels] = labels
    const [InARel, SetInARel] = inarel;
    const [NewFact, SetNewFact] = newfact;
    const [ShowTopics, SetShowTopics] = showtopics
    const [SnackMessage, SetSnackMessage] = snackmessage;
    const [OpenSnack, SetOpenSnack] = opensnack
    const [ShowAddConceptModal, SetShowAddConceptModal] = addconceptmodal
    const [ShowAddTagModal, SetShowAddTagtModal] = addtagmodal
    const [CollectionDescription, SetCollectionDescription] = useState(false)
    const [Annotators, SetAnnotators] = annotators
    const [ShowDocs, SetShowDocs] = showdocs
    const [ShowMembers, SetShowMembers] = showmembers
    const [ShowSettings, SetShowSettings] = showsettings
    const [ShowUpload, SetShowUpload] = showupload
    const [ShowStats, SetShowStats] = showstats
    const [ShowCollections, SetShowCollections] = showcollections
    const [ShowView, SetShowView] = showview
    const [ShowFilter, SetShowFilter] = showfilter
    const [ShowDownload, SetShowDownload] = showdownload
    const [ShowTasks, SetShowTasks] = showtasks
    const [Fields, SetFields] = fields
    const [Role, SetRole] = role
    const [CollectionDocuments, SetCollectionDocuments] = collectiondocuments

    const [FieldsToAnn, SetFieldsToAnn] = fieldsToAnn
    const [DisplayDocuments, SetDisplayDocuments] = useState([])
    const [ClickedSideBut, SetClickedSideBut] = useState(false)
    const [ClickedAnnoBut, SetClickedAnnoBut] = useState(false)
    const [CollectionConcepts, SetCollectionConcepts] = collectionconcepts
    const [AreasColors, SetAreasColors] = areascolors
    const [Modality, SetModality] = modality
    const [Modify, SetModify] = modifyrel
    const [Source, SetSource] = source
    const [ShowAnnoTypes, SetShowAnnoTypes] = showtypes
    const [Predicate, SetPredicate] = predicate
    const [Target, SetTarget] = target
    const [SourceText, SetSourceText] = sourcetext
    const [PredicateText, SetPredicateText] = predicatetext
    const [TargetText, SetTargetText] = targettext
    const [SourceConcepts, SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts, SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts, SetTargetConcepts] = targetconcepts
    const [SPArrow, SetSPArrow] = useState(false)
    const [PTArrow, SetPTArrow] = useState(false)
    const [STArrow, SetSTArrow] = useState(false)
    const [SPArrowFloat, SetSPArrowFloat] = useState(false)
    const [PTArrowFloat, SetPTArrowFloat] = useState(false)
    const [STArrowFloat, SetSTArrowFloat] = useState(false)
    const [SearchSubject, SetSearchSubject] = useState(false)
    const [SearchPredicate, SetSearchPredicate] = useState(false)
    const [SearchObject, SetSearchObject] = useState(false)
    const [FirstSelected, SetFirstSelected] = firstsel
    const [SecondSelected, SetSecondSelected] = secondsel
    const [ShowReadOnlyRelation, SetShowReadOnlyRelation] = readonlyrelation
    const [EnableRelationCreation, SetEnableRelationCreation] = enablerelation
    const [NewFactInterno, SetNewFactInterno] = newfactin
    const [Area, SetArea] = useState(null)
    const [Description, SetDescription] = useState(null)
    const [Name, SetName] = useState(null)
    const [Areas, SetAreas] = useState(false)
    const [Url, SetUrl] = useState(null)
    const [UrlName, SetUrlName] = useState(null)
    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [AreaSearch, SetAreaSearch] = useState(null)
    const [UrlSearch, SetUrlSearch] = useState(null)
    const [NameSearch, SetNameSearch] = useState(null)
    const [Profile, SetProfile] = profile
    const [CurrentDiv, SetCurrentDiv] = currentdiv

    const [ColSx, SetColSx] = useState(3)
    const [ColDx, SetColDx] = useState(0)
    const [ColDoc, SetColDoc] = useState(9)



    useEffect(() => {
        if (!InARel) {
            SetBinaryRel(false)
            SetNewRelation(false)
            SetExpand(false)
        }


    }, [InARel])

    useEffect(() => {
        if (!NewRelation) {
            SetShowAnnoTypes(true)
            SetNewRelation(false)
            SetExpand(false)
            SetNewFact(false)
        }


    }, [NewRelation])

    useEffect(()=>{
        if(NewRelation){
            SetExpand(true)
            SetShowAnnoTypes(false)
        }else{
            SetExpand(false)
            SetShowAnnoTypes(true)
        }
    },[NewRelation])


    useEffect(()=>{
        if(Modify){
            SetShowAnnoTypes(false)
            SetExpand(true)
        }else{
            SetShowAnnoTypes(true)
            SetExpand(false)
        }
    },[Modify])

    const [state, setState] = React.useState({
        vertical: 'top',
        horizontal: 'right',
    });

    const {vertical, horizontal} = state;

    useEffect(() => {
        if (Role) {
            axios.get('change_role', {params: {role: Role}})
                .then(response => {
                    SetDisplayDocuments(response.data['documents'])
                    SetCollectionDocuments(response.data['documents'])
                    SetDocumentID(response.data['document_id'])
                })
        }


    }, [Role])


    /*    useEffect(()=>{
            axios.get('collections/documents')
                .then(response=>{
                    SetDisplayDocuments(response.data)
                })
        },[Collection])*/

    useEffect(() => {
        if (!InARel) {
            Array.from(document.querySelectorAll('div[class^="bulls"]')).forEach(e => e.remove());
            Array.from(document.querySelectorAll('div[class^="source"], div[class^="predicate"], div[class^="target"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
            Array.from(document.querySelectorAll('[id^="source"], [id^="predicate"], [id^="target"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
        }

    }, [InARel]);
    useEffect(() => {

        if (DocumentID) {
            // console.log('fields',Fields,FieldsToAnn)

            // GET FIELDS OF A DOCUMENT
            axios.get("get_fields").then(response => {
                var fields = response.data['fields']
                var fields_to_ann = response.data['fields_to_ann']
                // console.log('fields',fields,fields_to_ann)
                if (FieldsToAnn === []) {
                    SetFieldsToAnn(fields)
                } else {
                    SetFieldsToAnn(fields_to_ann)
                }
                if (!Fields || Fields.length === 0 || (Fields.length > 0 && Fields.some(r => fields.indexOf(r) === -1))) {
                    SetFields(fields)

                }

            })

            // GET ANNOTATORS
            async function fetchAnnotators() {
                const response = await axios.get('get_annotators');
                // console.log('request',response)
                SetAnnotators(response.data)
                return response
            }

            fetchAnnotators()

            // GET LABELS OF A DOCUMENT
            // async function fetchLabels(){
            //     const response = await axios.get('get_annotated_labels',{params:{user:CurAnnotator}});
            //     // console.log('request',response)
            //     SetAnnotatedLabels(response.data)
            //     if(LoadingNewAnno){
            //         SetLoadingNewAnno(false)
            //     }
            //     return response
            // }
            // fetchLabels()

        }
    }, [DocumentID, CurAnnotator])


    const escFunction = useCallback((event) => {
        // console.log('chiave',event.key)
        if (event.key === "Escape") {
            SetRelationship(false)
            ClickOnBaseIndex(event, InARel, SetInARel)

        }
    }, []);


    useEffect(() => {
        document.addEventListener("keydown", escFunction, false);

        return () => {
            document.removeEventListener("keydown", escFunction, false);
        };
    }, []);


    // const document_comp = useMemo(() => <Document />, [InARel,SourceConcepts]);


    useEffect(() => {
        if (!InARel) {
            SetSourceConcepts(false)
            SetSourceText(false)
            SetSource(false)
            SetPredicateText(false)
            SetPredicateConcepts(false)
            SetPredicate(false)
            SetTargetConcepts(false)
            SetTargetText(false)
            SetTarget(false)
            SetNewRelation(false)

        }
        if (!ShowRels) {
            SetShowReadOnlyRelation(false)
            SetModify(false)
        }

    }, [InARel, ShowRels])


    useEffect(() => {
        if (Expand) {
            let element = document.getElementById('left-side-bar')
            if (element) {

                element.className = 'active'
            }
            SetShowLabels(false)
            SetShowFacts(false)
            SetShowMentions(false)
            SetShowConcepts(false)
            SetShowTags(false)
            SetShowRels(false)
        } else {
            let element = document.getElementById('left-side-bar')
            if (element) {
                element.classList.remove('active')

            }
        }
    }, [Expand])

    useEffect(() => {
        if (Expand && (Modify || ShowSettings || ShowAnnoTypes || ShowDocs || ShowTopics || ShowAutoAnno || ShowRoles || ShowDownload || ShowCollections || ShowUpload || ShowStats || ShowMembers || ShowFilter || ShowView || NewRelation || NewFact) && (!ShowLabels && !ShowMentions && !ShowConcepts && !ShowTags && !ShowRels && !ShowFacts)) {
            let element = document.getElementById('left-side-bar')
            if (element) {

                element.className = 'active'
            }
        } else {
            let element = document.getElementById('left-side-bar')
            if (element) {

                element.classList.remove('active')
            }
        }
    }, [Expand, NewRelation, NewFact, ShowSettings, ShowDocs, ShowTopics, ShowAnnoTypes, ShowRoles, ShowAutoAnno, ShowDownload, ShowUpload, ShowStats, ShowMembers, ShowFilter, ShowView, ShowCollections, ShowLabels, ShowMentions, ShowRels, ShowFacts, ShowTags, Modify, ShowConcepts])


    /*
        useEffect(()=>{

            if(!Expand && !ShowAnnoTypes && !InARel && !(ShowLabels || ShowMentions || ShowFacts || ShowRels || NewFact || ShowConcepts || ShowTags )){
                SetColDx(0)
                SetColSx(1)
                SetColDoc(11)
            }
            else if(!Expand && (ShowLabels || ShowMentions || ShowFacts || ShowRels || ShowConcepts  || ShowTags || NewFact )){ // ho tolot inarel
                SetColSx(0)
                SetColDx(3)
                SetColDoc(9)

            }else if(Expand && !InARel) {
                SetColDx(0)
                SetColSx(3)
                SetColDoc(9)
            }else if(ShowAnnoTypes){
                SetColDx(0)
                SetColSx(3)
                SetColDoc(9)
            }

            /!*        else if(InARel && !ShowRels && !NewRelation){
                        SetColSx(1)
                        SetColDx(0)
                        SetColDoc(11)
                    }*!/
            else if(InARel){
                SetColSx(3)
                SetColDx(0)
                SetColDoc(9)
            }

        },[Expand,NewRelation,ShowAnnoTypes,InARel,ShowConcepts,ShowFacts,ShowLabels,NewFact,ShowMentions,ShowRels,ShowTags])
    */

/*    useEffect(() => {
        if ((ShowLabels || ShowMentions || ShowFacts || ShowRels || ShowTags || ShowConcepts)) {
            SetShowStats(false)
            SetShowTopics(false)
            SetShowDocs(false)
            SetShowCollections(false)
            SetShowMembers(false)
            SetShowSettings(false)
            SetShowFilter(false)
            SetShowView(false)
            SetShowDownload(false)
            SetShowUpload(false)
            SetExpand(false);
            SetNewFact(false)
            SetSearchObject(false)
            SetSearchPredicate(false)
            SetSearchSubject(false)
            SetShowRoles(false)
            SetShowAutoAnno(false)
            SetShowAnnoTypes(true)

        }


    }, [ShowLabels, ShowMentions, ShowFacts, ShowRels, ShowTags, ShowConcepts])*/

    useEffect(() => {
        SetShowStats(false)
        SetShowDocs(false)
        SetShowTopics(false)
        SetShowCollections(false)
        SetShowMembers(false)
        SetShowSettings(false)
        SetShowFilter(false)
        SetShowView(false)
        SetShowDownload(false)
        SetShowUpload(false)
        SetExpand(false);
        SetNewFact(false)
        SetShowRels(false)
        SetShowConcepts(false)
        SetShowTags(false)
        SetShowLabels(false)
        SetShowFacts(false)
        SetShowMentions(false)
        SetSearchObject(false)
        SetSearchPredicate(false)
        SetSearchSubject(false)
        SetShowAutoAnno(false)
        SetInARel(false)
        SetBinaryRel(false)
        SetShowAnnoTypes(true)


    }, [CurAnnotator])




    useEffect(() => {
        if (NewFact) {
            SetShowConcepts(false)
            SetShowMentions(false)
            SetShowTags(false)
            SetShowLabels(false)
            SetShowRels(false)
            SetShowFacts(false)
            SetNewFactInterno(false)
        }
    }, [NewFact])

    const handleCloseSnack = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        SetOpenSnack(false)
        SetSnackMessage(false);
    };

    useEffect(() => {
        if (Collection) {
            axios.get('get_tags').then(response => SetTags(response.data['areas'])).catch(error => console.log(error))
            axios.get('collections/modality').then(response => SetModality(response.data['modality'])).catch(error => console.log(error))
            axios.get('collection_options', {params: {collection: Collection}}).then(response => SetAreasColors(response.data)).catch(error => console.log(error))
        }
    }, [Collection])

    useEffect(() => {
        if (ShowAddConceptModal || ShowAddTagModal) {
            SetSearchSubject(false)
            SetSearchObject(false)
            SetSearchPredicate(false)
        }
    }, [ShowAddConceptModal, ShowAddTagModal])


    return (

        <div className="baseindex">
            {OpenSnack && SnackMessage && < div>
                <Snackbar
                    anchorOrigin={{vertical, horizontal}}
                    open={OpenSnack && SnackMessage}
                    autoHideDuration={5000}
                    onClose={handleCloseSnack}
                    message={SnackMessage['message']}
                    key={vertical + horizontal}

                />


            </div>}

            <ConceptContext.Provider value={{
                areaSearch: [AreaSearch, SetAreaSearch],
                urlSearch: [UrlSearch, SetUrlSearch],
                nameSearch: [NameSearch, SetNameSearch],
                searchsubject: [SearchSubject, SetSearchSubject],
                searchpredicate: [SearchPredicate, SetSearchPredicate],
                searchobject: [SearchObject, SetSearchObject],
                sparrow: [SPArrow, SetSPArrow],
                ptarrow: [PTArrow, SetPTArrow],
                starrow: [STArrow, SetSTArrow],
                area: [Area, SetArea],
                areas: [Areas, SetAreas],
                name: [Name, SetName],
                conceptslist: [CollectionConcepts, CollectionConcepts],
                description: [Description, SetDescription],
                urlname: [UrlName, SetUrlName],
                url: [Url, SetUrl],
                sparrowfloat: [SPArrowFloat, SetSPArrowFloat],
                ptarrowfloat: [PTArrowFloat, SetPTArrowFloat],
                starrowfloat: [STArrowFloat, SetSTArrowFloat]
            }}>

                {ShowAddConceptModal && <DraggableModal showconceptmodal={ShowAddConceptModal && CurMention}
                                                        setshowconceptmodal={SetShowAddConceptModal}/>}
                {ShowAddTagModal && <DraggableModalTag showtagmodal={ShowAddTagModal && CurMention}
                                                       setshowtagmodal={SetShowAddTagtModal}/>}

                <div>

                    <Row>
                        {/*<SideBar />*/}
                        {<Col md={ColSx} onClick={(e) => {

                            DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)
                        }}>
                            {(ShowAnnoTypes || (InARel && !NewRelation) || !( ShowAutoAnno || ShowTopics || ShowUpload || ShowDownload || ShowSettings || ShowRoles || ShowFilter || ShowView || ShowDocs || ShowMembers || ShowRels || ShowCollections || NewFact || Modify || NewRelation)) &&
                                <div className={'foo-enter-active'}><ShowTypes/></div>}

                            {/*{<Col md={(!ShowLabels && !ShowMentions && !ShowConcepts && !ShowRels && !ShowFacts && !InARel && !NewFact  ) ? 2 : 1}>*/}
                            <div id='left-side-bar-content'>


                                <CSSTransition in={Expand === true} timeout={150} classNames="foo" appear
                                               onEntered={(e) => {
                                                   SetClickedSideBut(true)

                                               }}
                                               onExited={(e) => {
                                                   SetClickedSideBut(false)
                                               }}>
                                    <>{((!InARel || NewRelation) && !ShowLabels && !ShowConcepts && !ShowMentions && !ShowRels && !ShowFacts ) &&
                                        <div id='left-side-bar'>
                                            {ClickedSideBut && ShowStats && <><SummaryStatsComponent/></>}
                                            {/*// I cannot show Members in Competitive modality}*/}
                                            {ClickedSideBut && ShowMembers && Modality !== 1 && <>
                                                <MembersComponent/></>}
                                            {ClickedSideBut && ShowCollections && <><CollectionsComponent/></>}
                                            {ClickedSideBut && ShowRoles && <><RolesComponent/></>}
                                            {ClickedSideBut && ShowDocs && <><ChangeDocumentComppnent
                                                displayDocs={DisplayDocuments}
                                                setDisplayDocs={SetDisplayDocuments}/></>}
                                            {ClickedSideBut && ShowTopics && <><ChangeTopic/></>}
                                            {ClickedSideBut && ShowFilter && <><FilterComponent/></>}
                                            {ClickedSideBut && ShowSettings && <><ChangeSettingsComponent/></>}
                                            {ClickedSideBut && ShowView && <><ChangeViews/></>}
                                            {ClickedSideBut && ShowDownload && <><DownloadDocument/></>}
                                            {ClickedSideBut && ShowUpload && <><UploadDocument/></>}
                                            {ClickedSideBut && ShowAutoAnno && <><AutomaticAnnotation/></>}
                                            {ClickedSideBut && ShowAnnoTypes && <><ShowTypes/></>}
                                            {ClickedSideBut && (NewFact || Modify || NewRelation ) && <><RelationshipComponent /> </>}


                                        </div>}


                                    </>

                                </CSSTransition>
                            </div>

                        </Col>}

                        {/*{Expand && <Col md={2}>*/}


                        <Col md={ColDoc}>

                            {(Collection && Collection !== '') ? <div style={{padding: '1%', textAlign: 'justify'}}>
                                    <DocumentToolBar key={DisplayDocuments} documentList={DisplayDocuments}/>

                                    {TopicType === 'Textual' && <TopicInfo/>}
                                    {CollectionType === 'Textual' && <Document />}
                                    {CollectionType === 'Image' && <DocumentImageSelect/>}
                                    {/*{document_comp}*/}
                                </div> :
                                <div>
                                    {((Collection === '' || !Collection) && (CollList && CollList.filter(x => x.status !== 'Invited').length === 0)) && <>
                                        <h4>You have not any document to annotate yet. </h4>
                                        <Button href={'/collections'}>Create a new collection.</Button>

                                    </>}

                                </div>}
                            {/*</Paper>*/}
                        </Col>
                        {<Col md={ColDx} onClick={(e) => {

                            DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)
                        }}>


                        </Col>}

                        {/*</ConceptContext.Provider>*/}


                    </Row>
                </div>


            </ConceptContext.Provider>
        </div>
    );
}

export default BaseIndex;
