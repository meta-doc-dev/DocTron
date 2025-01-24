import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";

import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete, {createFilterOptions} from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import EditIcon from '@mui/icons-material/Edit';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';

import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {
    faChevronLeft, faPalette,
    faChevronRight, faExclamationTriangle,
    faGlasses,
    faInfoCircle,
    faList, faPlusCircle,
    faProjectDiagram, faArrowLeft, faArrowRight, faTrash, faSave, faFileInvoice
} from "@fortawesome/free-solid-svg-icons";
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import DocumentToolBar from "../../Document/ToolBar/DocumentToolBar";
import AddIcon from '@mui/icons-material/Add';
import Collapse from "@material-ui/core/Collapse";
import Paper from "@mui/material/Paper";
import '../annotation.css'
// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import DraggableModal from "../concepts/DraggableConceptModal";
import {DeleteRange} from "../../HelperFunctions/HelperFunctions";
import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";
import ReplayCircleFilledIcon from '@mui/icons-material/ReplayCircleFilled';
import {ArrowContext} from "../../Document/DocumentFinal_2";
import RelationshipModal from "../concepts/RelationshipConceptModal";
import submitRelationship from "./QuickPredicateModal";
import {ConceptContext} from "../../../BaseIndex";
import DescriptionDialog from "../concepts/DescriptionDialog";
import QuickPredicateModal from "./QuickPredicateModal";
export default function ArrowLabelComponent(props){
    const { modifyrel,inarel,newfact,readonlyrelation,relationship,newfactin,source,predicate,target,opensnack,binaryrel,snackmessage,curannotator,collectionconcepts,relationshipslist,showrelspannel,predicatetext,predicateconcepts,targettext,sourcetext,targetconcepts,sourceconcepts } = useContext(AppContext);

    const [Modify,SetModify] = modifyrel
    const [ShowRels, SetShowRels] = showrelspannel
    const [ShowModal,SetShowModal] = useState(false)
    const [Source,SetSource] = source
    const [Predicate,SetPredicate] = predicate
    const [Target,SetTarget] = target
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] = targettext
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts, SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [InARel,SetInARel] = inarel;
    const [Relationship,SetRelationship] = relationship

    const [ShowDescription,SetShowDescription] = useState(false)
    const [ShowConceptModal,SetShowConceptModal] = useState(false)
    const [NewRel,SetNewRel] = useState(false)
    const [UpdateConcepts,SetUpdateConcepts] = useState(false)
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [CollectionConcepts,SetCollectionConcepts] = collectionconcepts
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const [BinaryRel,SetBinaryRel] = binaryrel;
    const [NewFactInterno,SetNewFactInterno] = newfactin
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = readonlyrelation
    const [NewFact,SetNewFact] = newfact


    const [ShowAlertError,SetShowAlertError] = useState(false)
    const [ShowAlertSuccess,SetShowAlertSuccess] = useState(false)

    // useEffect(()=>{
    //     if(UpdateConcepts){
    //         console.log('qua 2')
    //         axios.get('collections/concepts')
    //             .then(response=>{
    //                 SetCollectionConcepts(response.data)
    //                 SetUpdateConcepts(false)
    //             })
    //         axios.get('relationships',{params:{user:CurAnnotator}})
    //             .then(response=>{
    //                 SetRelationshipsList(response.data)
    //             })
    //     }
    //
    // },[UpdateConcepts])




    return (
        <>{InARel &&
    <div>
        {props.label ?
            <>{props.label.startsWith('mention_') ? <></> :

                <div>

                    <Chip label={props.label} size="small" color="info" onClick={(e) => {
                        e.preventDefault()
                        SetRelationship(RelationshipsList[props.index])
                    }} variant="contained"/>


                </div>

            }</>

            :
            <>
                {ShowModal && <QuickPredicateModal showconceptmodal={ShowModal}
                                                   setshowconceptmodal={SetShowModal}/>}
                {ShowDescription && <DescriptionDialog show={ShowDescription} setshow={SetShowDescription}
                                                       area={PredicateConcepts[0]['concept_area']}
                                                       name={PredicateConcepts[0]['concept_name']}
                                                       url={PredicateConcepts[0]['concept_url']}
                                                       description={PredicateConcepts[0]['concept_description']}/>}
                {ShowConceptModal && <RelationshipModal relation={'predicate'} setconcepts_list={SetPredicateConcepts}
                                                        concepts_list={PredicateConcepts}
                                                        showconceptmodal={ShowConceptModal}
                                                        setshowconceptmodal={SetShowConceptModal}
                                                        settext={SetPredicateText}/>}

                {(!PredicateConcepts || PredicateConcepts.length === 0) ? <>
                        <div>
                            <Button
                                onClick={() => {
                                    SetShowModal(prev => !prev)
                                }} color='success' variant={"contained"} size={'small'}>
                                <AddIcon/>

                                Predicate</Button></div>
                        <div>
                            <Button
                                onClick={() => {
                                    SetNewRel(true);
                                    SetShowConceptModal(prev => !prev)
                                }} color='success' variant={"contained"} size={'small'}>
                                <AddIcon/>

                                Concept</Button>
                        </div>
                    </> :
                    <><Button
                        onClick={() => {
                            SetShowDescription(prev => !prev)
                        }} color={'success'} variant={"contained"} size={'small'}>
                        <>{PredicateConcepts[0]['concept_name']}</>
                    </Button>
                        {(Modify && ShowRels) && <Button
                            onClick={() => {
                                SetPredicate(false)
                                SetPredicateText(false)
                                SetPredicateConcepts(false)
                                SetNewRel(false)
                            }} color='error' variant={"contained"} size={'small'}>
                            <DeleteIcon/></Button>}
                    </>
                }



        </>}


    </div>}</>

    )
}