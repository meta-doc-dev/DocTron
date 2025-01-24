import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import {useParams} from "react-router-dom";
import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import Breadcrumbs from "@mui/material/Breadcrumbs";
import Link from '@mui/material/Link';
import React, {useState, useEffect, useContext, createContext, useRef, useTransition} from "react";
import Badge from 'react-bootstrap/Badge'
import Typography from '@mui/material/Typography';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import './document.css'
import {useXarrow, Xwrapper} from 'react-xarrows';
import Draggable from 'react-draggable';
import {CircularProgress, linearProgressClasses} from "@mui/material";
import {AppContext} from "../../App";
import {
    clearConceptsFromBorder,
    clearMentionsFromBorder,
    DeleteRange,
    waitForElm
} from "../HelperFunctions/HelperFunctions";
import DocumentTable from "./DocumentTable";
import Mention from "../Annotations/mentions/Mention";
import Chip from "@mui/material/Chip";
import ParagraphDoc from "./DocumentContent/ParagraphDoc";
import RelMention from "../Annotations/mentions/RelationshipMention";
import Xarrow from "react-xarrows";
import ArrowLabelComponent from "../Annotations/relationship/ArrowLabelComponent";
import SelectArrowComponent from "../Annotations/relationship/SelectArrowComponent";
import {ConceptContext} from "../../BaseIndex";
import OverlayConceptComponent from "../Annotations/relationship/OverlayConceptComponent";
import OverlayRelComponent from "../Annotations/relationship/OverlayRelComponent";
import Paper from "@mui/material/Paper";

export const ArrowContext = createContext('')


const boxStyle = {padding: '5px'};

export default function DocumentImage(props) {
    const {
        concepts,
        areascolors,
        role,
        sourceall,
        openall,
        inarel,
        annotationtypes,
        targetall,
        predicateall,
        autoannotation,
        opensnack,
        snackmessage,
        view,
        tags_split,
        saving,
        modality,
        loadingann,
        newmention,
        annotatedlabels,
        username,
        modifyrel,
        curannotator,
        sourceconcepts,
        predicateconcepts, factslist,
        targetconcepts,
        predicatetext,
        sourcetext,
        targettext,
        relationshipslist,
        predicate,
        source,
        target,
        documentdescription,
        currentdiv,
        firstsel,
        mentions_splitted,
        secondsel,
        document_id,
        relationship,
        mentions,
        startrange,
        endrange,
        topic,
        fields,
        fieldsToAnn
    } = useContext(AppContext);
    const {sparrow, ptarrow, starrow, starrowfloat, ptarrowfloat, sparrowfloat} = useContext(ConceptContext);
    const [LoadingNewAnn, SetLoadingNewAnn] = loadingann
    const [Modify, SetModify] = modifyrel
    const [OpenAll, SetOpenAll] = openall
    const [ShowConceptModal, SetShowConceptModal] = useState(false)
    const [RelationshipsList, SetRelationshipsList] = relationshipslist
    const [StartAnchorSP, SetStartAnchorSP] = useState("auto")
    const [StartAnchorPT, SetStartAnchorPT] = useState("auto")
    const [StartAnchorST, SetStartAnchorST] = useState("auto")
    const [EndAnchorSP, SetEndAnchorSP] = useState("auto")
    const [EndAnchorST, SetEndAnchorST] = useState("auto")
    const [EndAnchorPT, SetEndAnchorPT] = useState("auto")
    const [NewMention, SetNewMention] = newmention
    const [ChangeSTOff, SetChangeSTOff] = useState(false)
    const [ChangePTOff, SetChangePTOff] = useState(false)
    const [ChangeSPOff, SetChangeSPOff] = useState(false)
    const [Username, SetUsername] = username
    const [Topic, SetTopic] = topic
    const [Modality, SetModality] = modality
    const [SortedKeysDocumentDesc, SetSortedKeysDocumentDesc] = useState([])
    const [SnackMessage, SetSnackMessage] = snackmessage;
    const [OpenSnack, SetOpenSnack] = opensnack
    const [AutoAnnotate, SetAutoAnnotate] = autoannotation
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [ColorArrowSP, SetColorArrowSP] = useState('#495057')
    const [ColorArrowPT, SetColorArrowPT] = useState('#495057')
    const [ColorArrowST, SetColorArrowST] = useState('#495057')
    const [WidthArrowSP, SetWidthArrowSP] = useState('1.8')
    const [WidthArrowST, SetWidthArrowST] = useState('1.8')
    const [WidthArrowPT, SetWidthArrowPT] = useState('1.8')
    const [SelectedArrow, SetSelectedArrow] = useState(false)

    const [OverlappingSP, SetOverlappingSP] = useState(false)
    const [OverlappingST, SetOverlappingST] = useState(false)
    const [OverlappingPT, SetOverlappingPT] = useState(false)

    const [SourceElem, SetSourceElem] = useState(false)
    const [PredicateElem, SetPredicateElem] = useState(false)
    const [TargetElem, SetTargetElem] = useState(false)
    const [LoadingDoc, SetLoadingDoc] = useState(false)
    const [ParentSecondSelected, SetParentSecondSelected] = useState(false)
    const [ParentFirstSelected, SetParentFirstSelected] = useState(false)
    const [DocumentID, SetDocumentID] = document_id
    const [MentionsList, SetMentionsList] = mentions
    const [MentionsListSplitted, SetMentionsListSplitted] = mentions_splitted
    const [ConceptsList, SetConceptsList] = concepts
    const [TagsSplitted, SetTagsSplitted] = tags_split
    const [Start, SetStart] = startrange
    const [End, SetEnd] = endrange
    const [View, SetView] = view
    const [CurrentDiv, SetCurrentDiv] = currentdiv
    const [InARel, SetInARel] = inarel
    const [FirstSelected, SetFirstSelected] = firstsel
    const [SecondSelected, SetSecondSelected] = secondsel

    const [FactsList, SetFactsList] = factslist

    const [DocumentDesc, SetDocumentDesc] = documentdescription
    const [DocumentDescEmpty, SetDocumentDescEmpty] = useState(false)
    const [Saving, SetSaving] = saving
    const [FieldsToAnn, SetFieldsToAnn] = fieldsToAnn
    const [Fields, SetFields] = fields
    const [Relationship, SetRelationship] = relationship
    const [AreasColors, SetAreasColors] = areascolors
    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [AllRels, SetAllRels] = useState([])
    const [SPArrow, SetSPArrow] = sparrow
    const [PTArrow, SetPTArrow] = ptarrow
    const [STArrow, SetSTArrow] = starrow
    const [Image,SetImage] = useState(null)
    const [STArrowFloat, SetSTArrowFloat] = starrowfloat
    const [SPArrowFloat, SetSPArrowFloat] = ptarrowfloat
    const [PTArrowFloat, SetPTArrowFloat] = ptarrowfloat

    const [LoadMen, SetLoadMen] = useState(false)
    const [LoadRel, SetLoadRel] = useState(false)
    const [LoadConc, SetLoadConc] = useState(false)
    const [LoadTags, SetLoadTags] = useState(false)
    const [LoadLab, SetLoadLab] = useState(false)


    useEffect(() => {
        if (LoadingNewAnn && MentionsList && ConceptsList && AnnotatedLabels) {
            SetLoadingNewAnn(false)
        }
    }, [MentionsList, ConceptsList, AnnotatedLabels])


    useEffect(() => {
        if ((DocumentID && CurAnnotator) || LoadingNewAnn) {
            axios.get('get_document_content', {params: {document_id: DocumentID, user: CurAnnotator}})
                .then(response => {

                    console.log('response',response.data)
                    SetDocumentDesc(response.data['mentions'])
                    SetDocumentDescEmpty(response.data['empty'])
                    if (response.data['image']) {
                        SetImage(`data:image/png;base64,${response.data['image']}`);
                    }
                    //SetImage(response.data['image'])
                })
            // GET FIELDS OF A DOCUMENT
            axios.get("get_fields").then(response => {
                var fields = response.data['fields']
                var fields_to_ann = response.data['fields_to_ann']
                if (FieldsToAnn === []) {
                    SetFieldsToAnn(fields)
                } else {
                    SetFieldsToAnn(fields_to_ann)
                }
                if (!Fields || Fields.length === 0 || (Fields.length > 0 && Fields.some(r => fields.indexOf(r) === -1))) {
                    SetFields(fields)

                }

            })




            async function fetchLabels() {
                const response = await axios.get('get_annotated_labels', {params: {user: CurAnnotator}});
                SetAnnotatedLabels(response.data['labels'])
                SetLoadLab(true)

                return response
            }

            fetchLabels()




            async function fetchFacts() {
                const response = await axios.get('facts', {params: {user: CurAnnotator}});
                console.log('request', response)
                SetFactsList(response.data)
                return response
            }

            fetchFacts()

        }
    }, [DocumentID, CurAnnotator, AutoAnnotate, LoadingNewAnn, Topic])


    return (
        <div>
            {(!DocumentID || DocumentDesc.length === 0 || LoadingNewAnn || !ConceptsList || !TagsSplitted || !MentionsList || !DocumentDesc || AutoAnnotate || !FieldsToAnn) ?
                <div className='loading'>
                    <CircularProgress/>
                </div> :
                <div className='paper_doc' id='paper_doc'
                     style={{paddingBottom: '2.5%', position: 'relative'}}>

              {/*      {DocumentDesc.map((mention_key, i) => <>
                        {FieldsToAnn.indexOf(mention_key.slice(0, mention_key.lastIndexOf("_"))) !== -1 && <>


                            <div className='tab tab_value'>
                                    <span id={mention_key}>
                                        {DocumentDesc[mention_key].map((obj, i) => <>
                                            {
                                                <>

                                                    {obj['type'].startsWith('no_') ?

                                                        <span>
                                                                                                    <ParagraphDoc
                                                                                                        chiave={mention_key}
                                                                                                        id={mention_key + '_' + i.toString()}
                                                                                                        testo={obj['text']}/>
                                                                                                </span>

                                                        :


                                                        <span
                                                            className={'mention_span'}>
                                                                                                    {!InARel && <Mention
                                                                                                        id={mention_key + '_' + i.toString()}

                                                                                                        start={obj['start']}
                                                                                                        stop={obj['stop']}
                                                                                                        loc={mention_key}
                                                                                                        class={obj['mentions']}
                                                                                                        mention_text={obj['text']}
                                                                                                        mention={obj}
                                                                                                        tagsList={TagsSplitted.filter(x => (x.position.includes(mention_key) || mention_key.includes(x.position)) && x.start === obj['start'] && x.stop === obj['stop'])}
                                                                                                        concepts={ConceptsList.filter(x => (x.position.includes(mention_key) || mention_key.includes(x.position)) && x.start === obj['start'] && x.stop === obj['stop'])}/>}

                                                            {InARel && <><RelMention
                                                                id={mention_key + '_' + i.toString()}

                                                                start={obj['start']} stop={obj['stop']}
                                                                loc={mention_key} class={obj['mentions']}
                                                                mention_text={obj['text']} mention={obj}
                                                                tagsList={TagsSplitted.filter(x => (x.position.includes(mention_key) || mention_key.includes(x.position)) && x.start === obj['start'] && x.stop === obj['stop'])}
                                                                concepts={ConceptsList.filter(x => (x.position.includes(mention_key) || mention_key.includes(x.position)) && x.start === obj['start'] && x.stop === obj['stop'])}/>


                                                            </>}
                                                                                                </span>}

                                                </>

                                            }</>)}


                            </span></div>
                        </>}
                    </>)}*/}
                    <Paper elevation={2}>

                        <div style={{margin:'10px 0px',textAlign:'center'}}>
                            <span><b>Doc ID: </b></span><span>{DocumentDescEmpty['doc_id']}</span>

                            {Image ? <img style={{width:'80%',margin:'10px'}} src={Image} alt="Fetched from server"/> : <div>ciao</div>}
                        </div>

                    </Paper>


                </div>}
        </div>

    );
}



