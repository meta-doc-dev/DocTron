import {Col, ProgressBar, Row} from "react-bootstrap";

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

import './conceptmodal.css'
import {CircularProgress} from "@mui/material";
import KeyboardBackspaceIcon from '@mui/icons-material/KeyboardBackspace';
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, styled} from "@mui/material/styles";
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import Alert from '@mui/material/Alert';
import SelectConcept from "./SelectConcept";
import {ConceptContext} from "../../../BaseIndex";
export const RelationConceptContext = createContext('')


export default function RelationshipModal(props) {
    const {
        username,snackmessage,opensnack,relationshipslist,binaryrel,
        concepts,collectionslist,newfactin,curannotator,modality,view,showrelspannel,inarel,
        document_id,relationship,
        collection,
        mentions,curconcept,newfact,
        mentiontohighlight,modifyrel,readonlyrelation,
        startrange,sourcetext,sourceconcepts,targettext,targetconcepts,predicatetext,predicateconcepts,
        curmention,collectionconcepts,documentdescription,
        endrange,areascolors,predicate,source,target
    } = useContext(AppContext);

    const [MentionsList, SetMentionsList] = mentions

    const [ConceptsList,SetConceptsList] = collectionconcepts
    const {area,url,name,urlname,description,areas,conceptslist} =  useContext(ConceptContext);

    const [End, SetEnd] = endrange
    const [Areas,SetAreas] = useState(false)
    const [Area,SetArea] = useState(null)
    const [Description,SetDescription] = useState(null)
    const [Name,SetName] = useState(null)
    const [Url,SetUrl] = useState(null)
    const [UrlName,SetUrlName] = useState(false)
    const [Concepts,SetConcepts] = concepts;
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const [RelationshipsList,SetRelationshipsList] = relationshipslist

    const [BinaryRel,SetBinaryRel] = binaryrel;
    const [NewFactInterno,SetNewFactInterno] = newfactin

    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Modality,SetModality] = modality
    const [View,SetView] = view
    const [ShowRels, SetShowRels] = showrelspannel

    const [Relationship,SetRelationship] = relationship
    const [InARel,SetInARel] = inarel
    const [Modify,SetModify] = modifyrel
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = readonlyrelation
    const [NewFact,SetNewFact] = newfact

    const [Predicate,SetPredicate] = predicate

    const [UpdateConcepts,SetUpdateConcepts] = useState(false)
    const [ShowAlertError,SetShowAlertError] = useState(false)
    const [ShowAlertSuccess,SetShowAlertSuccess] = useState(false)


    const [ShowAlert, SetShowAlert] = useState(false)

    const [ShowAlertWarningArea,SetShowAlertWarningArea] = useState(false)

    const [Source,SetSource] = source;
    const [Target,SetTarget] = target;
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts,SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] = targettext




    function handleClose(){
        props.setshowconceptmodal(false)
        SetName(null)
        SetUrl(null)
        SetArea(null)
        SetDescription(null)
        SetShowAlertWarningArea(false)
        SetShowAlert(false)
        SetUrlName(null)

    }
    useEffect(()=>{

        if(ConceptsList){
            var aa = []
            ConceptsList.map(elemento=>{
                var area = elemento['area']
                if(aa.indexOf(area) === -1){
                    aa.push(area)
                }
            })
            console.log('areas',aa)
            SetAreas(aa)

        }

    },[ConceptsList])





    function submitRelationship(predicate_concepts){

        if(Modality === 2){
            console.log('ecco')
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Saving...'})
            let source = {}
            let predicate = {}
            let target = {}
            let source_mention = {start: null, stop: null}
            let predicate_mention = {start: null, stop: null}
            let target_mention = {start: null, stop: null}


            if (Source) {
                source_mention = MentionsList.find(x => x.mentions === Source)

            }
            if (Predicate) {
                predicate_mention = MentionsList.find(x => x.mentions === Predicate)

            }
            if (Target) {
                target_mention = MentionsList.find(x => x.mentions === Target)

            }

            let source_concepts = SourceConcepts
            let target_concepts = TargetConcepts


            source['mention'] = source_mention
            predicate['mention'] = predicate_mention
            target['mention'] = target_mention
            source['concepts'] = source_concepts
            predicate['concepts'] = predicate_concepts
            target['concepts'] = target_concepts
            if(Modality === 2 || View === 4) {
                SetOpenSnack(true)
                SetSnackMessage({'message': 'You cannot annotate this document'})
            }else if(AnnotationTypes.indexOf('Relationships annotation') === -1){
                    SetOpenSnack(true)
                    SetSnackMessage({'message': 'Relationships annotation is not allowed here'})
            }else {
                if (!Modify) {
                    axios.post('relationships/insert', {
                        source: source,
                        predicate: predicate,
                        target: target
                    }).then(response => {
                        SetRelationshipsList(response.data)
                        SetUpdateConcepts(true)

                        /*SetSource(false)
                        SetPredicate(false)
                        SetTarget(false)
                        SetTargetText(false)
                        SetPredicateText(false)
                        SetSourceText(false)
                        SetTargetConcepts(false)
                        SetPredicateConcepts(false)
                        SetSourceConcepts(false)*/
                        SetShowAlertSuccess(true)
                        SetInARel(false)
                        SetBinaryRel(false)
                        SetNewFact(false)
                        SetModify(false)
                        SetNewFactInterno(false)
                        SetShowReadOnlyRelation(true);
                        SetSnackMessage({'message': 'Saved'})

                    }).catch(error => SetShowAlertError(true))
                    console.log(source, predicate, target)


                } else {
                    axios.post('relationships/update', {
                        prev_subject: Relationship['subject'],
                        prev_predicate: Relationship['predicate'],
                        prev_object: Relationship['object'],
                        source: source,
                        predicate: predicate,
                        target: target
                    }).then(response => {
                        SetUpdateConcepts(true)

                        SetRelationshipsList(response.data)
                        SetSource(false)
                        SetPredicate(false)
                        SetTarget(false)
                        SetNewFact(false)
                        SetTargetText(false)
                        SetPredicateText(false)
                        SetSourceText(false)
                        SetTargetConcepts(false)
                        SetPredicateConcepts(false)
                        SetSourceConcepts(false)
                        SetShowAlertSuccess(true)
                        SetInARel(false)
                        SetModify(false)
                        SetNewFactInterno(false)
                        SetSnackMessage({'message': 'Saved'})

                        SetShowReadOnlyRelation(true);
                    }).catch(error => {
                        SetShowAlertError(true);
                        console.log(error)
                    })


                    console.log(source, predicate, target)
                }
            }
        }
    }



    function submitNewConcept(e){
        e.preventDefault();
        e.stopPropagation();
        let area = 'Default'
        if(Url === null || Name === null || Area === null){
            SetShowAlert(true)
        }else{

            if(Area !== null){
                area = Area.area
            }

        }
        let description = ''
        let existing_concept = ConceptsList.filter(x=>x.url === Url.url)
        if(existing_concept.length === 1){
            description = existing_concept[0].description
        }
        else{
            description = Description
        }
        let concept = {concept_url: Url.url,concept_name:Name.name,concept_area:area,concept_description:description}
        if(props.relation === 'predicate'){
            let predicates = PredicateConcepts ? PredicateConcepts : []

            let new_list = [...predicates,concept]
            SetPredicateConcepts(new_list)
            SetPredicateText(Name.name)

            if(Source && Target){
                console.log('eccomi qua')
                console.log(Source)
                console.log(SourceText)
                console.log(TargetText)
                console.log(Target)
                submitRelationship(new_list)
            }
        }
        else if(props.relation === 'target'){
            let targets = TargetConcepts ? TargetConcepts : []

            let new_list = [...targets,concept]
            SetTargetConcepts(new_list)
            SetTargetText(Name.name)
        }
        else if(props.relation === 'source'){
            let sources = SourceConcepts ? SourceConcepts : []
            let new_list = [...sources,concept]
            SetSourceConcepts(new_list)
            SetSourceText(Name.name)
        }
        handleClose()

    }


    useEffect(()=>{
        if(ConceptsList){
            if(Area === null || (Url === null || Name === null)){
                SetShowAlertWarningArea(false)
            }
            if(Url !== null || Name !== null){
                SetShowAlert(false)

            }
            if(Url !== null && Name !== null && Area !== null){
                ConceptsList.map(x=>{
                    if(x.name === Name.name && x.url === Url.url && x.area !== Area.area){
                        SetShowAlertWarningArea(true)
                    }
                })
            }

        }

    },[Name,Url,Area])






    return (
    <Dialog
        open={props.showconceptmodal}
        onClose={handleClose}

        // hideBackdrop={true}
        // disableEnforceFocus={true}

        // PaperComponent={PaperComponent}
        // aria-labelledby="draggable-dialog-title"
    >
        <RelationConceptContext.Provider value={{area1:[Area,SetArea],areas1:[Areas,SetAreas],name1:[Name,SetName],conceptslist1:[ConceptsList,SetConceptsList],description1:[Description,SetDescription],urlname1:[UrlName,SetUrlName],url1:[Url,SetUrl]}}>

            <div style={{padding:'2%',width:'500px'}}>
                {(Areas && ConceptsList ) ? <>
                    <SelectConcept type={'relationship'} handleclose ={handleClose}   />

                </> :<div className='loading'>
                    <CircularProgress />
                </div>
                    }


            </div>
            <div style={{margin:'3%'}}>
                {ShowAlert && <Alert sx={{marginBottom: '3%'}} severity="error">Please, set an Area, a Name and a URL for the new concept, then, confirm.</Alert>}
                {ShowAlertWarningArea && Area !== null && <Alert severity="warning">This concept already exists and is associated to a different area. If you confirm, this concept
                    will be available also for <b>{Area.area}</b> area.</Alert>}
            </div>

            <DialogActions>


                <Button autoFocus onClick={handleClose}>
                    Cancel
                </Button>
               <Button onClick={submitNewConcept}>Confirm</Button>
            </DialogActions>

        </RelationConceptContext.Provider>

    </Dialog>
);
}