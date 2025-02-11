import './App.css';
import ReactDOM from "react-dom";
import React, {useState, useEffect, useContext, createContext} from "react";
import axios from "axios";
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import {Routes, useHistory} from "react-router-dom";
import {Container, Row, Col} from 'react-bootstrap';
// import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import {DeleteRange, ClickOnBaseIndex, waitForElm} from './components/HelperFunctions/HelperFunctions'
// import './components/General/first_row.css';
import {
    BrowserRouter as Router,
    Route,
    Link
} from "react-router-dom";
// import StartingMenu from "./components/SelectMenu/StartingMenu";
import BaseIndex from "./BaseIndex";
import Login from "./components/login/Login";
import Home from "./components/login/Home";
// import Tutorial from "./components/SideComponents/Tutorial";
// import Credits from "./components/SideComponents/Credits";
// import MyStats from "./components/SideComponents/MyStats";

// import ReportsStats from "./components/SideComponents/ReportsStats";
// import ReportsStats from "./components/ReportStatistics/ReportsStats";
// import InfoAboutConfiguration from "./components/MedConfiguration/InfoAboutConfiguration";
// import Configure from "./components/MedConfiguration/Configure";
// import UpdateConfiguration from "./components/MedConfiguration/UpdateConfiguration";
// import MembersStats from "./components/SideComponents/MembersStats";
// import ConfigureResult from "./components/MedConfiguration/ConfigureResult";
// import UploadFile from "./components/SideComponents/UploadFile";
// import Prova_BaseIndex from "./Prova_BaseIndex";
// import Login from "./components/login/Login"
import Axios from "axios";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.baseURL = window.baseurl;
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {styled, alpha} from '@mui/material/styles';
import SideBar from "./components/SideBar/PermanentSideBar";
import HeaderBar from "./components/BaseComponents/HeaderBar";
import StatisticsPage from "./components/Statistics/StatisticsPage";
import StatisticsCollection from "./components/Statistics/StatisticsCollection";
import InstructionsPage from "./components/Instructions/InstructionsPage";
import CreditsPage from "./components/Instructions/CreditsPage";
import {Collapse, Dialog, DialogActions, DialogContent, InputLabel, Select, TextField} from "@mui/material";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContentText from "@mui/material/DialogContentText";
import FormControl from "@mui/material/FormControl";
import Button from "@mui/material/Button";
import Demo from "./components/Instructions/Demo";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import SignUp from "./components/login/Signup";
import CollectionsList from "./components/Collections/CollectionsList";
import DocumentsPage from "./components/Document/DocumentsPage";
import ResetForm from "./components/BaseComponents/ResetForm";
import Reset from "./components/BaseComponents/Reset";
import DashboardPage from './components/Dashboard/DashboardPage';
import MyStatisticsPage from './components/Dashboard/components/tabs/MyStatisticsPage';
import GlobalStatisticsPage from './components/Dashboard/components/tabs/GlobalStatisticsPage';
import IAAPage from './components/Dashboard/components/tabs/IAAPage';
import TopicBasedStatsPage from './components/Dashboard/components/tabs/TopicBasedStatsPage';

export const AppContext = createContext('')

function App() {
    // const [ClickedCheck, SetClickedCheck] = useState(false)
    const [DocumentList, SetDocumentList] = useState(false)

    const [Modality, SetModality] = useState(0); // this is needed to set the annotation modality collaborative restricted (2), competetive (1), collaborative open (0)
    const [RemovedConcept, SetRemovedConcept] = useState(false);
    const [AnnotatedIndexList, SetAnnotatedIndexList] = useState([])
    const [DocumentDescription, SetDocumentDescription] = useState(false)
    const [Collection, SetCollection] = useState(false)

    const [RelationshipsList, SetRelationshipsList] = useState(false)
    const [FactsList, SetFactsList] = useState(false)
    const [useCase, SetUseCase] = useState('')
    const [Language, SetLanguage] = useState('')
    const [ShowModal, SetShowModal] = useState(false)
    const [Mention, SetMention] = useState('')
    const [AnnotationTypes, SetAnnotationTypes] = useState([])
    const [AnnotationType, SetAnnotationType] = useState(false)
    // const [Outcomes,SetOutcomes] = useState([])
    const [UsersListAnnotations, SetUsersListAnnotations] = useState([])
    // const [ReloadMentions,SetReloadMentions] = useState(false)
    const [Rows, SetRows] = useState([])
    const [Redir, SetRedir] = useState(0)
    const [MentionsList, SetMentionsList] = useState(false)
    const [ShowAnnoTypes, SetShowAnnoTypes] = useState(true)
    const [EnableRelationCreation, SetEnableRelationCreation] = useState(false)
    const [AllMentions, SetAllMentions] = useState([])
    const [checks, setChecks] = useState([])
    const [FinalCount, SetFinalCount] = useState(0)
    const [FinalCountReached, SetFinalCountReached] = useState(false)
    const [RadioChecked, SetRadioChecked] = useState(false)
    const [SemanticArea, SetSemanticArea] = useState([])
    const [LabelsToSave, SetLabelsToSave] = useState([])

    const [HighlightMention, SetHighlightMention] = useState(false)
    const [ArrayInsertionTimes, SetArrayInsertionTimes] = useState([])
    const [SavedGT, SetSavedGT] = useState(false)
    const [ShowBar, SetShowBar] = useState(false)
    const [Disabled_Buttons, SetDisable_Buttons] = useState(false)
    const [Username, SetUsername] = useState(false)
    const [Labels, SetLabels] = useState([])
    const [LabelsPassage, SetLabelsPassage] = useState([])
    // State for each ConceptList
    const [DocumentID, SetDocumentID] = useState(false)
    // const [MakeReq,SetMakeReq] = useState(false)
    // const [ShowErrorSnack, SetShowErrorSnack] = useState(false);
    const [ShowConceptModal, SetShowConceptModal] = useState(false)
    const [selectedConcepts, setSelectedConcepts] = useState({
        "Diagnosis": [],
        "Anatomical Location": [],
        "Test": [],
        "Procedure": [],
        "General Entity": []
    })
    const [Start, SetStart] = useState(false)
    const [End, SetEnd] = useState(false)
    const [Relationship, SetRelationship] = useState(false)
    const [OpenAll, SetOpenAll] = useState(false)
    const [FirstSelected, SetFirstSelected] = useState(false)
    const [SecondSelected, SetSecondSelected] = useState(false)
    const [CurrentDiv, SetCurrentDiv] = useState(false)
    const [Role, SetRole] = useState(false)
    const [Concepts, SetConcepts] = useState(false) // MENTIONS LIKE SPLITTED
    const [Tags, SetTags] = useState(false)
    const [TagsSplitted, SetTagsSplitted] = useState(false)
    const [CollectionTags, SetCollectionTags] = useState(false)
    // const [DeleteRangeState,SetDeleteRangeState] = useState(false)
    const [LoadingNewAnn, SetLoadingNewAnn] = useState(false)
    const [Fields, SetFields] = useState(false)
    const [FieldsToAnn, SetFieldsToAnn] = useState(false)
    const [NewMention, SetNewMention] = useState(false)
    const [BinaryRel, SetBinaryRel] = useState(false)
    const [Profile, SetProfile] = useState('')
    const [Annotation, SetAnnotation] = useState('')
    const [ShowAnnotationsStats, SetShowAnnotationsStats] = useState(false)
    const [showReportText, SetshowReportText] = useState(false);
    const [ShowAutoAnn, SetShowAutoAnn] = useState(false)
    const [ShowMemberGt, SetShowMemberGt] = useState(false)
    // const [ShowMajorityGt,SetShowMajorityGt] = useState(false)
    const [UserChosen, SetUserChosen] = useState(false)
    const [ShowMajorityModal, SetShowMajorityModal] = useState(false)
    const [ShowMajorityGroundTruth, SetShowMajorityGroundTruth] = useState(false)
    const [ReportType, SetReportType] = useState(false)
    const [UsersList, SetUsersList] = useState(false)
    const [BatchNumber, SetBatchNumber] = useState('')
    const [UpdateSingleReport, SetUpdateSingleReport] = useState(false)
    const [LoadingChangeGT, SetLoadingChangeGT] = useState(false)
    const [SelectedLang, SetSelectedLang] = useState('')
    const [TopicsList,SetTopicsList] = useState(false)
    const [Topic,SetTopic] = useState(false)
    const [Points,setPoints] = useState({'values':[],'points':[]})
    const [PointHigh,SetPointHigh] = useState(false)
    const [WindowRef] = useState(window.location.host)
    const [InARelationship, SetInARelationship] = useState(false)
    const [CollList, SetCollList] = useState(false)
    const [DashboardCollection, SetDashboardCollectionList] = useState([])
    const [contextMenu, setContextMenu] = React.useState(null);
    const [MentionToHighlight, SetMentionToHighlight] = useState(false)
    const [ShowAddConceptModal, SetShowAddConceptModal] = useState(false)
    const [AnnotatedLabels, SetAnnotatedLabels] = useState(false)
    const [ShowFilter, SetShowFilter] = useState(false)
    const [ShowDocs, SetShowDocs] = useState(false)
    const [ShowTopics, SetShowTopics] = useState(false)
    const [ShowMembers, SetShowMembers] = useState(false)
    const [ShowView, SetShowView] = useState(false)
    const [Expand, SetExpand] = useState(false)
    const [ShowStats, SetShowStats] = useState(false)
    const [ShowDownload, SetShowDownload] = useState(false)
    const [ShowRoles, SetShowRoles] = useState(false)
    const [ShowUpload, SetShowUpload] = useState(false)
    const [ShowCollections, SetShowCollections] = useState(false)
    const [Annotators, SetAnnotators] = useState(false)
    const [CollectionDocuments, SetCollectionDocuments] = useState(false)
    const [CurMention, SetCurMention] = useState(false)
    const [CurConcept, SetCurConcept] = useState(false)
    const [MentionsListSplitted, SetMentionsListSplitted] = useState(false)
    const [Saving, SetSaving] = useState(false)
    const [ShowSettings, SetShowSettings] = useState(false)
    const [AreasColors, SetAreasColors] = useState(false)
    const [ShowLabels, SetShowLabels] = useState(false)
    const [ShowMentions, SetShowMentions] = useState(false)
    const [ShowConcepts, SetShowConcepts] = useState(false)
    const [ShowAutoAnno, SetShowAutoAnno] = useState(false)
    const [ShowRels, SetShowRels] = useState(false)
    const [FontSize, SetFontSize] = useState(false)
    const [Interlines, SetInterlines] = useState(false)
    const [ShowFacts, SetShowFacts] = useState(false)
    const [Source, SetSource] = useState(false)
    const [SourceAll, SetSourceAll] = useState([])
    const [Predicate, SetPredicate] = useState(false)
    const [PredicateAll, SetPredicateAll] = useState([])
    const [Target, SetTarget] = useState(false)
    const [TargetAll, SetTargetAll] = useState([])
    const [SourceText, SetSourceText] = useState(false)
    const [PredicateText, SetPredicateText] = useState(false)
    const [TargetText, SetTargetText] = useState(false)
    const [SourceConcepts, SetSourceConcepts] = useState(false)
    const [PredicateConcepts, SetPredicateConcepts] = useState(false)
    const [TargetConcepts, SetTargetConcepts] = useState(false)
    const [ShowReadOnlyRelation, SetShowReadOnlyRelation] = useState(false)
    const [Password, SetPassowrd] = useState(false)
    const [OpenSnack, SetOpenSnack] = useState(false)
    const [SnackMessage, SetSnackMessage] = useState(false)
    const [AllRels, SetAllRels] = useState([])
    const [CollectionType,SetCollectionType] = useState("Textual")
    const [TopicType,SetTopicType] = useState("Textual")
    // const [PredicateId,SetPredicateId] = useState(false)
    // const [TargetId,SetTargetId] = useState(false)
    const [AutoAnnotate, SetAutoAnnotate] = useState(false)
    const [CurAnnotator, SetCurAnnotator] = useState(false)
    const [ConfirmMessage, SetConfirmMessage] = useState(false)
    const [NewFact, SetNewFact] = useState(false)
    const [NewRelation, SetNewRelation] = useState(false)
    const [NewAssertion, SetNewAssertion] = useState(false)
    const [CollectionConcepts, SetCollectionConcepts] = useState(false) // SINGLE CONCEPTS INTO WHICH EACH DOCUMENT IS SPLITTED
    const [View, SetView] = useState(3) // questo equivale a visualizzare mention e concetti e tag
    const [Counter, SetCounter] = useState(0)
    const [ModifyRel, SetModifyRel] = useState(false)
    const [NewFactInterno, SetNewFactInterno] = useState(false)
    const [OpenModal, SetOpenModal] = useState(false)
    const [PasswordValid, SetPasswordValid] = useState(false)
    const [Prof, SetProf] = useState("")
    const [Error, SetError] = useState(false)
    const [Valid, SetValid] = useState(false)
    const [OpenUnlink, SetOpenUnlink] = useState(false)
    const [OpenLink, SetOpenLink] = useState(false)
    const [PasswordVal, SetPasswordVal] = useState(false)
    const [PasswordValUp, SetPasswordValUp] = useState(false)
    const [passwordErrorUp, setPasswordErrorUp] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [PasswordConfirmed, SetPasswordConfirmed] = useState(false)
    const [Orcid, SetOrcid] = useState(false)
    const [ShowAddTagModal, SetShowAddTagModal] = useState(false)
    const [ShowTags, SetShowTags] = useState(false)
    const [Task, SetTask] = useState(false)
    const [ShowTasks, SetShowTasks] = useState(false)

    // useEffect(()=>{
    //     let font = window.localStorage.getItem('fontsize')
    //     let inter = window.localStorage.getItem('interlines')
    //     if(font === null){
    //         window.localStorage.setItem('fontsize','1.2rem')
    //     }
    //     if(inter === null){
    //         window.localStorage.setItem('interlines','2')
    //     }
    //
    //     waitForElm('#paper_doc').then(doc=>{
    //
    //         doc.style.fontSize = FontSize.toString()+'rem'
    //         doc.style.lineHeight = Interlines.toString()
    //         let font = window.localStorage.getItem('fontsize')
    //         let inter = window.localStorage.getItem('interlines')
    //         if(FontSize !== font){
    //             window.localStorage.setItem('fontsize',FontSize)
    //
    //         }
    //         if(Interlines !== inter){
    //             window.localStorage.setItem('interlines',Interlines)
    //
    //         }
    //     })
    // },[Interlines,FontSize])
    useEffect(() => {
        SetOrcid(window.orcid)
    }, [window.orcid])


    useEffect(() => {
        var username = window.username
        var profile = window.profile

        axios.get('annotation_types').then(response => {
            SetAnnotationTypes(response.data['types'])
        })
            .catch(error => {
                console.log('error', error)
            })

        // var BASEURL = window.baseurl
        console.log('username', username)
        console.log('profile', profile)
        if (username === '') {
            SetUsername(username)
            SetCurAnnotator(username)
            SetProfile(profile)
        }

        window.scrollTo(0, 0)


    }, [])

    useEffect(() => {
        if (window.localStorage.getItem('fontsize') !== null) {
            SetFontSize(window.localStorage.getItem('fontsize'))
        } else {
            SetFontSize('1.0rem')
        }

    }, [FontSize])

    useEffect(() => {

        if (window.localStorage.getItem('interlines') !== null) {
            SetInterlines(window.localStorage.getItem('interlines'))
        } else {
            SetInterlines('2')
        }
    }, [Interlines])


    useEffect(() => {
        console.log('collection', Collection)
        if (Collection) {
            axios.get('topic')
                .then(response => {
                    SetTopicsList(response.data['topics'])
                })

            axios.get('collections/modality')
                .then(response => {
                    SetModality(response.data['modality'])
                    SetCollectionType(response.data['collection_type'])
                    SetTopicType(response.data['topic_type']);

                })


            axios.get('collections/documents')
                .then(response => {
                    SetCollectionDocuments(response.data)
                })

            axios.get('collections/concepts')
                .then(response => {
                    SetCollectionConcepts(response.data)

                })


        }
    }, [Collection])


    useEffect(() => {
        // localStorage.clear();
        let username = ''
        if (Username && Username !== '') {
            username = Username
        }

        if (window.username !== '' && !Username) {
            SetUsername(window.username)
            SetCurAnnotator(window.username)
            SetProfile(window.profile)

        } else if (window.username !== '' || Username) {
            var orcid = '';
            console.log('entro', username, CurAnnotator)
            if (window.orcid !== '') {
                orcid = window.orcid
            }
            axios.get("get_session_params", {params: {orcid: orcid}}).then(response => {
                console.log('params', response.data)
                SetCollection(response.data['collection']);
                SetAnnotation(response.data['name_space']);
                SetRole(response.data['role']);
                // SetTask(response.data['task']);
                SetTopic(response.data['topic']);
                SetAnnotationType(response.data['annotation_type']);
                SetDocumentID(response.data['document']);

            })

            
            axios.get('collections/list').then(response => {
                SetCollList(response.data['collections'])
            })
                .catch(error => {
                    console.log('error', error)
                })

            axios.get('user-collections').then(response => {
                SetDashboardCollectionList(response.data)
            }).catch(error => {
                console.log('error', error)
            })



        }


    }, [Username])

    const handleChangeProf = (e) => {
        e.preventDefault()
        SetProf(e.target.value)
    }
    const SubmitProfile = (e) => {
        e.preventDefault()
        axios.post("set_profile", {profile: Prof}).then(res => {
            SetValid(true);
            SetProfile(Prof)
        }).catch(error => {
            SetError(true)
            console.log('error', error)
        })
    }
    const handleCloseModal = (e) => {
        e.preventDefault()
        SetOpenModal(false)
        SetPasswordConfirmed(false)
        SetPasswordValUp(false)
        SetPasswordValid(false)
        SetPassowrd(false)
        SetPasswordVal(false)
        setPasswordError("")
        setPasswordErrorUp("")
        SetOpenUnlink(false)
        SetOpenLink(false)
        SetValid(false)
        SetError(false)

    }

    function unlinkOrcid(e) {
        axios.post("unlink_orcid").then(res => {
            SetValid(true);
            handleCloseModal(e)
            SetOrcid(false)
        }).catch(error => {
            SetError(true)
        })
    }

    const handlePasswordChange = (event) => {
        const passwordValue = event.target.value;
        SetPasswordVal(passwordValue);
        console.log(/[0-9]/.test(passwordValue))
        console.log(/[A-Z]/.test(passwordValue))
        if (passwordValue.length < 8 || /[0-9]/.test(passwordValue) === false || /[A-Z]/.test(passwordValue) === false) {
            setPasswordError("Password must contain 8 chars, one number, one uppercase letter");
        } else {
            setPasswordError("");
        }
    };

    const handlePasswordUpChange = (event) => {
        const passwordValue = event.target.value;
        SetPasswordValUp(passwordValue);
        console.log(/[0-9]/.test(passwordValue))
        console.log(/[A-Z]/.test(passwordValue))
        if (passwordValue.length < 8 || /[0-9]/.test(passwordValue) === false || /[A-Z]/.test(passwordValue) === false) {
            setPasswordErrorUp("Password not compliant");
        } else if (passwordValue !== PasswordVal) {
            setPasswordErrorUp("Passwords not matching");
        } else {
            setPasswordErrorUp("");
        }
    };

    useEffect(() => {
        if (!OpenModal) {
            SetPasswordConfirmed(false)
            SetPasswordValUp(false)
            SetPasswordValid(false)
            SetPassowrd(false)
            SetPasswordVal(false)
            setPasswordError("")
            setPasswordErrorUp("")
            SetOpenUnlink(false)
            SetOpenLink(false)
            SetValid(false)
            SetError(false)
        }
    }, [OpenModal])



    useEffect(() => {
        if (OpenUnlink) {
            axios.get("password", {params: {username: Username}}).then(response => {
                if (response.status === 200 && response.data === 'none') {
                    SetPassowrd(true)

                } else if (response.status === 200) {
                    SetPasswordConfirmed(true)
                }
            })
        }
    }, [OpenUnlink])

    useEffect(() => {
        if (!InARelationship) {
            SetBinaryRel(false)
        }
    }, [InARelationship])

    function UpdatePassword(e) {
        e.preventDefault()
        axios.post("password", {password: PasswordVal}).then(r => {
            SetValid(true);
            SetPasswordConfirmed(true)
        }).catch((r) => SetError(true))
    }    

    return (
        <div className="App" id='app'>

            <AppContext.Provider value={{
                // showSnackReport:[ShowSnackReport,SetShowSnackReport]
                fontsize: [FontSize, SetFontSize],
                openmodal: [OpenModal, SetOpenModal],
                msg: [ConfirmMessage, SetConfirmMessage],
                loadingann: [LoadingNewAnn, SetLoadingNewAnn],
                curannotator: [CurAnnotator, SetCurAnnotator],
                newassertion: [NewAssertion, SetNewAssertion],
                newfactin: [NewFactInterno, SetNewFactInterno],
                target: [Target, SetTarget],
                predicateconcepts: [PredicateConcepts, SetPredicateConcepts],
                modifyrel: [ModifyRel, SetModifyRel],
                sourceconcepts: [SourceConcepts, SetSourceConcepts],
                targetconcepts: [TargetConcepts, SetTargetConcepts],
                sourcetext: [SourceText, SetSourceText],
                predicatetext: [PredicateText, SetPredicateText],
                newrelation: [NewRelation, SetNewRelation],
                showtypes: [ShowAnnoTypes, SetShowAnnoTypes],
                sourceall: [SourceAll, SetSourceAll],
                predicateall: [PredicateAll, SetPredicateAll],
                targetall: [TargetAll, SetTargetAll],
                targettext: [TargetText, SetTargetText],
                source: [Source, SetSource],
                predicate: [Predicate, SetPredicate],
                linea: [Interlines, SetInterlines],
                relationshipslist: [RelationshipsList, SetRelationshipsList],
                collectionconcepts: [CollectionConcepts, SetCollectionConcepts],
                showdownload: [ShowDownload, SetShowDownload],
                showupload: [ShowUpload, SetShowUpload],
                redir: [Redir, SetRedir],
                saving: [Saving, SetSaving],
                view: [View, SetView],
                showview: [ShowView, SetShowView],
                mentions_splitted: [MentionsListSplitted, SetMentionsListSplitted],
                enablerelation: [EnableRelationCreation, SetEnableRelationCreation],
                allrels: [AllRels, SetAllRels],
                showlabelspannel: [ShowLabels, SetShowLabels],
                showtagspannel: [ShowTags, SetShowTags],
                showmentionsspannel: [ShowMentions, SetShowMentions],
                showfactspannel: [ShowFacts, SetShowFacts],
                showconceptspannel: [ShowConcepts, SetShowConcepts],
                showrelspannel: [ShowRels, SetShowRels],
                expand: [Expand, SetExpand],
                areascolors: [AreasColors, SetAreasColors],
                showsettings: [ShowSettings, SetShowSettings],
                documentlist: [DocumentList, SetDocumentList],
                curmention: [CurMention, SetCurMention],
                curconcept: [CurConcept, SetCurConcept],
                showmembers: [ShowMembers, SetShowMembers],pointhigh:[PointHigh,SetPointHigh],
                collectiondocuments: [CollectionDocuments, SetCollectionDocuments],
                showfilter: [ShowFilter, SetShowFilter],
                showstats: [ShowStats, SetShowStats],
                showcollections: [ShowCollections, SetShowCollections],
                showdocs: [ShowDocs, SetShowDocs],
                showtopics: [ShowTopics, SetShowTopics],
                relationship: [Relationship, SetRelationship],
                documentdescription: [DocumentDescription, SetDocumentDescription],
                addconceptmodal: [ShowAddConceptModal, SetShowAddConceptModal],
                addtagmodal: [ShowAddTagModal, SetShowAddTagModal],
                task: [Task, SetTask],
                currentdiv: [CurrentDiv, SetCurrentDiv],
                mentiontohighlight: [MentionToHighlight, SetMentionToHighlight],
                firstsel: [FirstSelected, SetFirstSelected],
                secondsel: [SecondSelected, SetSecondSelected],
                labels: [Labels, SetLabels],
                labels_passage: [LabelsPassage, SetLabelsPassage],
                labelstosave: [LabelsToSave, SetLabelsToSave],
                annotatedlabels: [AnnotatedLabels, SetAnnotatedLabels],
                newfact: [NewFact, SetNewFact],
                collectionslist: [CollList, SetCollList],
                dashboardCollections: [DashboardCollection, SetDashboardCollectionList],
                document_id: [DocumentID, SetDocumentID],
                mentions: [MentionsList, SetMentionsList],
                startrange: [Start, SetStart],
                endrange: [End, SetEnd],factslist:[FactsList, SetFactsList],
                url: [WindowRef],collType:[CollectionType,SetCollectionType],
                topicType:[TopicType,SetTopicType],
                users: [UsersList, SetUsersList],
                usersListAnnotations: [UsersListAnnotations, SetUsersListAnnotations],
                collection: [Collection, SetCollection],
                annotators: [Annotators, SetAnnotators],
                modality: [Modality, SetModality],
                role: [Role, SetRole],
                showroles: [ShowRoles, SetShowRoles],
                selectedLang: [SelectedLang, SetSelectedLang],
                loadingChangeGT: [LoadingChangeGT, SetLoadingChangeGT],
                updateSingle: [UpdateSingleReport, SetUpdateSingleReport],
                batchNumber: [BatchNumber, SetBatchNumber],
                tablerows: [Rows, SetRows],
                report_type: [ReportType, SetReportType],
                showmajoritygt: [ShowMajorityGroundTruth, SetShowMajorityGroundTruth],
                showmajoritymodal: [ShowMajorityModal, SetShowMajorityModal],
                userchosen: [UserChosen, SetUserChosen],
                showmember: [ShowMemberGt, SetShowMemberGt],
                showautoannotation: [ShowAutoAnn, SetShowAutoAnn],
                showreporttext: [showReportText, SetshowReportText],
                showannotations: [ShowAnnotationsStats, SetShowAnnotationsStats],
                annotation: [Annotation, SetAnnotation],
                profile: [Profile, SetProfile],
                removedConcept: [RemovedConcept, SetRemovedConcept],
                indexList: [AnnotatedIndexList, SetAnnotatedIndexList],
                fields: [Fields, SetFields],
                fieldsToAnn: [FieldsToAnn, SetFieldsToAnn],
                binaryrel: [BinaryRel, SetBinaryRel],
                openall: [OpenAll, SetOpenAll],
                start: [Start, SetStart], points:[Points,setPoints],
                username: [Username, SetUsername],
                showOptions: [ShowModal, SetShowModal],
                language: [Language, SetLanguage],
                usecase: [useCase, SetUseCase],
                semanticArea: [SemanticArea, SetSemanticArea],
                radio: [RadioChecked, SetRadioChecked],
                finalcount: [FinalCount, SetFinalCount],
                reached: [FinalCountReached, SetFinalCountReached],
                showbar: [ShowBar, SetShowBar],
                insertionTimes: [ArrayInsertionTimes, SetArrayInsertionTimes],
                checks: [checks, setChecks],
                highlightMention: [HighlightMention, SetHighlightMention],
                annotationtypes: [AnnotationTypes, SetAnnotationTypes],
                annotationtype: [AnnotationType, SetAnnotationType],
                save: [SavedGT, SetSavedGT],
                disButton: [Disabled_Buttons, SetDisable_Buttons],
                selectedconcepts: [selectedConcepts, setSelectedConcepts],
                conceptModal: [ShowConceptModal, SetShowConceptModal],
                newmention: [NewMention, SetNewMention],
                mentionToAdd: [Mention, SetMention],
                opensnack: [OpenSnack, SetOpenSnack],topics:[TopicsList,SetTopicsList],topic:[Topic,SetTopic],
                snackmessage: [SnackMessage, SetSnackMessage],
                autoannotation: [AutoAnnotate, SetAutoAnnotate],
                readonlyrelation: [ShowReadOnlyRelation, SetShowReadOnlyRelation],
                showautomaticannotation: [ShowAutoAnno, SetShowAutoAnno],
                concepts: [Concepts, SetConcepts],
                showtasks:[ShowTasks, SetShowTasks],
                tags: [Tags, SetTags],
                tags_split: [TagsSplitted, SetTagsSplitted],
                inarel: [InARelationship, SetInARelationship],
                allMentions: [AllMentions, SetAllMentions]
            }}
            >


                {<Router>

                    <div>
                        {OpenModal && <Dialog
                            open={OpenModal === true && window.location.hostname === "metatron.dei.unipd.it"}
                            onClose={handleCloseModal}
                            maxWidth={"md"}
                            fullWidth={true}
                            aria-labelledby="alert-dialog-title"
                            aria-describedby="alert-dialog-description"
                        >
                            <DialogTitle id="alert-dialog-title">
                                {"Settings"}
                            </DialogTitle>
                            <DialogContent>
                                {(Profile === 'Default') && <div style={{margin: "20px"}}>
                                    <h6>Change your profile</h6>
                                    <FormControl>
                                        <Select
                                            labelId="demo-simple-select-label"
                                            id="demo-simple-select"
                                            value={Prof}
                                            sx={{width: "30%"}}
                                            onChange={(e) => handleChangeProf(e)}
                                        >
                                            <MenuItem value={""}>Select a profile</MenuItem>
                                            <MenuItem value={"Expert"}>Expert</MenuItem>
                                            <MenuItem value={"Beginner"}>Beginner</MenuItem>
                                            <MenuItem value={"Tech"}>Tech</MenuItem>
                                            <MenuItem value={"Student"}>Student</MenuItem>
                                            <MenuItem value={"Professor"}>Professor</MenuItem>
                                        </Select>
                                        <Button variant="contained" disabled={Prof === ""} sx={{marginTop: '2vh'}}
                                                onClick={(e) => SubmitProfile(e)}>Confirm</Button>

                                    </FormControl>
                                    <hr/>
                                </div>}
                                {(Orcid) ? <div style={{margin: "20px"}}>
                                    <Button variant="text" onClick={(e) => {
                                        e.preventDefault();
                                        SetOpenUnlink(prev => !prev)
                                    }} sx={{display: "inline-block"}}>Unlink </Button>
                                    <div style={{display: "inline-block"}}> your <img className={'orcid'}
                                                                                      src="https://metatron.dei.unipd.it/static/img/ORCID.png"
                                                                                      alt="ORCID iD logo"/> ORCID ID
                                    </div>
                                    <div style={{fontSize: '0.8rem', marginTop: "1%"}}>
                                        It will be always possible to link your ORCID ID again
                                    </div>
                                    {OpenUnlink && <Collapse in={OpenUnlink}>
                                        <div style={{margin: "20px"}}>
                                            Are you sure you want to unlink your ORCID ID?
                                            <div style={{marginTop: "2%"}}>
                                                {Password && !PasswordConfirmed && <div>
                                                    Please, set a password you can use to log in into Metatron. <br/>
                                                    Passwords must contain at least 8 chars, a number, an uppercase
                                                    letter
                                                    <div>
                                                        <TextField
                                                            id="password"
                                                            label="Password"
                                                            type="password"
                                                            onChange={handlePasswordChange}
                                                            error={passwordError !== ""}
                                                            helperText={passwordError}
                                                        />

                                                        <br/><br/>
                                                        <div>Insert your password again</div>
                                                        <div>
                                                            <TextField
                                                                id="password_check"
                                                                label="Password"
                                                                type="password"
                                                                onChange={handlePasswordUpChange}
                                                                error={passwordErrorUp !== ""}
                                                                helperText={passwordErrorUp}
                                                            />

                                                        </div>

                                                    </div>

                                                    <Button sx={{marginTop: '2%'}}
                                                            disabled={passwordErrorUp !== "" || passwordError !== ""}
                                                            onClick={UpdatePassword}>Confirm</Button>

                                                </div>}


                                                {PasswordConfirmed && <><Button
                                                    sx={{display: "inline-block", margin: "2%"}}
                                                    onClick={() => SetOpenUnlink(false)}>No</Button>
                                                    <Button variant="contained" onClick={unlinkOrcid}
                                                            sx={{
                                                                display: "inline-block",
                                                                margin: "2%"
                                                            }}>Yes</Button></>}
                                            </div>
                                        </div>
                                    </Collapse>}
                                    <hr/>
                                </div> : <div style={{margin: "20px"}}>
                                    <Button variant="text" onClick={(e) => {
                                        e.preventDefault();
                                        SetOpenLink(prev => !prev)
                                    }} sx={{display: "inline-block"}}>link </Button>
                                    <div style={{display: "inline-block"}}> your <img className={'orcid'}
                                                                                      src="https://metatron.dei.unipd.it/static/img/ORCID.png"
                                                                                      alt="ORCID iD logo"/> ORCID ID
                                    </div>
                                    <div style={{fontSize: '0.8rem', marginTop: "1%"}}>
                                        It will be always possible to unlink your ORCID ID again
                                    </div>
                                    {OpenLink && <Collapse in={OpenLink}>
                                        <div style={{margin: "20px"}}>
                                            Are you sure you want to link your ORCID ID?
                                            <div style={{marginTop: "2%"}}>
                                                <Button sx={{display: "inline-block", margin: "2%"}}
                                                        onClick={() => SetOpenLink(false)}>No</Button>
                                                <Button variant="contained" component={"a"}
                                                        href={"https://metatron.dei.unipd.it/link_orcid"}
                                                        sx={{display: "inline-block", margin: "2%"}}>Yes</Button>
                                            </div>
                                        </div>
                                    </Collapse>}
                                    <hr/>
                                </div>}
                                {Error && <b>An error occurred</b>}
                                {Valid && <b>Ok</b>}
                            </DialogContent>
                            <DialogActions>
                                <Button onClick={handleCloseModal} autoFocus>
                                    Close
                                </Button>
                            </DialogActions>
                        </Dialog>}

                        <Routes>

                            <Route path="/loginPage" element={<Login/>} exact />
                                
                            <Route path="/password_reset/:token" element={<ResetForm/>} exact />
                                
                            <Route path="/password_reset" element={<Reset message={window.errorMessage}/>} />
                                
                            <Route path="/demo" element={<Demo/>} exact />
                                
                            <Route path="/loginPage" element={<Login/>} exact />

                            <Route path="/signup" element={<SignUp/>} exact />
                                {/*<div>ciao</div>*/}

                            <Route path="/index" element={<div>
                                <SideBar/>

                                <HeaderBar counter={Counter}/>
                                <hr/>

                                <div className='maindiv'>

                                    <BaseIndex/>

                                </div>
                                {/*</div>*/}
                            </div>} exact />


                            <Route path="/collections" element={<div>

                            <HeaderBar counter={Counter}/>
                            <hr/>

                            <div className='maindiv'>
                                <CollectionsList/>

                            </div>

                            </div>} exact />


                            <Route path="/statistics" element={<div>

                            <HeaderBar counter={Counter}/>
                            <hr/>

                            <div className='maindiv'>
                                <StatisticsPage/>

                            </div>

                            </div>} exact />
                                
                            <Route path="/instructions" element={<div>

                            <HeaderBar/>
                            <hr/>

                            <div className='maindiv'>
                                <InstructionsPage/>

                            </div>

                            </div>} exact />

                            <Route path="/credits" element={<div>

                            <HeaderBar/>
                            <hr/>

                            <div className='maindiv'>
                                <CreditsPage/>

                            </div>

                            </div>} exact />

                            <Route path="/statistics/:collection_id" element={<div>

                            <HeaderBar counter={Counter}/>
                            <hr/>

                            <div className='maindiv'>
                                <StatisticsCollection/>

                            </div>

                            </div>} exact />


                            <Route path='/collections/:collection_id' element={<div>

                            <HeaderBar counter={Counter}/>
                            <hr/>

                            <div className='maindiv'>
                                <DocumentsPage/>

                            </div>
                            </div>} exact />

                            <Route path="/" element={<Home />} exact />

                            <Route path="" element={<Home/>} exact />

                            <Route path="/dashboard/*" element={
                                <>
                                    <HeaderBar counter={Counter}/>
                                    <DashboardPage />
                                </>
                            } />

                            <Route path="dashboard/*" element={
                                <>
                                    <HeaderBar counter={Counter}/>
                                    <DashboardPage />
                                </>
                            }>
                                <Route index element={<MyStatisticsPage />} />
                                <Route path="my-stats" element={<MyStatisticsPage />} />
                                <Route path="global-stats" element={<GlobalStatisticsPage />} />
                                <Route path="iaa" element={<IAAPage />} />
                                <Route path="topic-stats" element={<TopicBasedStatsPage />} />
                            </Route>
                        </Routes>
                    </div>
                </Router>}

            </AppContext.Provider>
        </div>
    );
}


export default App;
const rootElement = document.getElementById("root");
ReactDOM.render(<App/>, rootElement);