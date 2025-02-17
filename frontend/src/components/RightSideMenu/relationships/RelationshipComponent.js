import React, {useState, useEffect, useContext, createContext, useRef} from "react";

import 'bootstrap/dist/css/bootstrap.min.css';
import '../rightsidestyles.css'
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import Button from "@mui/material/Button";
import axios from "axios";

import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Snackbar from '@mui/material/Snackbar';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import {AppContext} from "../../../App";
import Chip from "@mui/material/Chip";

import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import RelationshipModal from "../../Annotations/concepts/RelationshipConceptModal";
import {createTheme, ThemeProvider} from "@mui/material/styles";

import ClearIcon from '@mui/icons-material/Clear';
import MuiAlert from '@mui/material/Alert';
import {ConceptContext} from "../../../BaseIndex";
import DialogTitle from "@mui/material/DialogTitle";
import {Dialog, DialogActions, DialogContent} from "@mui/material";
import DialogContentText from "@mui/material/DialogContentText";

const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});
export default function RelationshipComponent(props){
    const { concepts,newrelation,annotationtypes,binaryrel,inarel,factslist,newfactin,opensnack,modality,snackmessage,curannotator,view,labels,newfact,mentions,collectionconcepts,showrelspannel,showfactspannel,modifyrel,readonlyrelation,sourcetext,relationshipslist,sourceconcepts,targettext,targetconcepts,predicatetext,predicateconcepts,relationship,predicate,source,target } = useContext(AppContext);
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = readonlyrelation
    const [NewFact,SetNewFact] = newfact
    const [NewRelation, SetNewRelation] = newrelation

    const [ShowInstructionModal,SetShowInstructionModal] = useState(false)
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Modality,SetModality] = modality
    const [FactsList,SetFactsList] = factslist
    const [View,SetView] = view
    const [ShowRels, SetShowRels] = showrelspannel
    const [ShowFacts, SetShowFacts] = showfactspannel
    const [Labels,SetLabels] = labels
    const [Relationship,SetRelationship] = relationship
    const [InARel,SetInARel] = inarel
    const [Modify,SetModify] = modifyrel
    const [MentionsList,SetMentionsList] = mentions;
    const [ConceptsList,SetConceptsList] = concepts;
    const [ShowConceptModal,SetShowConceptModal] = useState(false)
    const [NodeType,SetNodeType] = useState(false)
    const [ShowAlertSuccess,SetShowAlertSuccess] = useState(false)
    const [ShowAlertError,SetShowAlertError] = useState(false)
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [Source,SetSource] = source;
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts,SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] =targettext
    const [Target,SetTarget] = target;
    const [Predicate,SetPredicate] = predicate;
    const [BinaryRel,SetBinaryRel] = binaryrel;
    const [NewFactInterno,SetNewFactInterno] = newfactin
    const [CollectionConcepts,SetCollectionConcepts] = collectionconcepts
    const [UpdateConcepts,SetUpdateConcepts] = useState(false)
    const [SourceBackup,SetSourceBackup] = useState(false);
    const [SourceConceptsBackup,SetSourceConceptsBackup] = useState(false);
    const [PredicateConceptsBackup,SetPredicateConceptsBackup] = useState(false);
    const [TargetConceptsBackup,SetTargetConceptsBackup] = useState(false);
    const [SourceTextBackup,SetSourceTextBackup] = useState(false);
    const [PredicateTextBackup,SetPredicateTextBackup] = useState(false);
    const [TargetTextBackup,SetTargetTextBackup] =useState(false);
    const [TargetBackup,SetTargetBackup] = useState(false);
    const [PredicateBackup,SetPredicateBackup] = useState(false);
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes


    useEffect(() => {
        if(BinaryRel && Source && Target){
            let concept = {concept_url: 'empty_concept_ID',concept_name:'',concept_area:'Relation predicate',concept_description:null}
            SetPredicateConcepts([concept])
        }
    }, [BinaryRel,Source,Target]);
    useEffect(()=>{
        // brutto ma forse necessario
        SetShowReadOnlyRelation(false)
        console.log('relationships',RelationshipsList)

        SetSourceBackup(_.cloneDeep(Source))
        SetSourceTextBackup(_.cloneDeep(SourceText))
        SetSourceConceptsBackup(_.cloneDeep(SourceConcepts))
        SetTargetBackup(_.cloneDeep(Target))
        SetTargetTextBackup(_.cloneDeep(TargetText))
        SetTargetConceptsBackup(_.cloneDeep(TargetConcepts))
        SetPredicateConceptsBackup(_.cloneDeep(PredicateConcepts))
        SetPredicateTextBackup(_.cloneDeep(PredicateText))
        SetPredicateBackup(_.cloneDeep(Predicate))
    },[])




    useEffect(()=>{
        let source_concepts = []
        if(Source && ConceptsList && MentionsList){
            ConceptsList.map(c=>{
                if(c.mentions === Source){
                    let concetto = {}
                    concetto['concept_url'] = c.concept.concept_url
                    concetto['concept_name'] = c.concept.concept_name
                    concetto['concept_area'] = c.concept.area
                    concetto['concept_description'] = c.concept.description

                    source_concepts.push(concetto)
                }
            })
            if(SourceConcepts === false  || SourceConcepts.length === 0){
                SetSourceConcepts(source_concepts)
            }
            let mention = MentionsList.filter(x=>x.mentions === Source)
            if(mention.length>0){
                SetSourceText(mention[0].mention_text)

        }


        }

    },[Source])

    useEffect(()=>{
        let source_concepts = []
        if(Predicate && ConceptsList && MentionsList){
            ConceptsList.map(c=>{
                if(c.mentions === Predicate){
                    let concetto = {}
                    concetto['concept_url'] = c.concept.concept_url
                    concetto['concept_name'] = c.concept.concept_name
                    concetto['concept_area'] = c.concept.area
                    concetto['concept_description'] = c.concept.description

                    source_concepts.push(concetto)
                }
            })
            if(PredicateConcepts === false || PredicateConcepts.length === 0){
                SetPredicateConcepts(source_concepts)
            }
            let mention = MentionsList.filter(x=>x.mentions === Predicate)
            if(mention.length > 0){
                SetPredicateText(mention[0].mention_text)

            }
        }

    },[Predicate])

    useEffect(()=>{
        let source_concepts = []
        if(Target && ConceptsList && MentionsList){
            ConceptsList.map(c=>{
                if(c.mentions === Target){
                    let concetto = {}
                    concetto['concept_url'] = c.concept.concept_url
                    concetto['concept_name'] = c.concept.concept_name
                    concetto['concept_area'] = c.concept.area
                    concetto['concept_description'] = c.concept.description

                    source_concepts.push(concetto)
                }
            })
            if(TargetConcepts === false || TargetConcepts.length === 0){
                SetTargetConcepts(source_concepts)
            }
            let mention = MentionsList.filter(x=>x.mentions === Target)
            if(mention.length > 0){
                SetTargetText(mention[0].mention_text)

            }
        }

    },[Target])


    function handleClick(e,nodetype){
        e.preventDefault()
        e.stopPropagation()
        console.log('clicked',nodetype)
        SetNodeType(nodetype)
        SetShowConceptModal(true)
    }


    const roletheme = createTheme({
        palette: {
            concept: {
                main: '#2156a5ed',
                contrastText: '#fff',
            },

            mention: {
                main: '#d78117ed',
                contrastText: '#fff',
            },
        },
    });

    function submitRelationship(e){
        e.preventDefault()
        e.stopPropagation()
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
            let predicate_concepts = PredicateConcepts
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
            }else if(AnnotationTypes.indexOf('Relationships annotation') === -1 && AnnotationTypes.indexOf('Facts annotation') === -1){
                    SetOpenSnack(true)
                    SetSnackMessage({'message': 'Relationships annotation is not allowed here'})
            }else {
                if (!Modify) {
                    if(Source || Predicate || Target){
                        axios.post('relationships/insert', {
                            source: source,
                            predicate: predicate,
                            target: target
                        }).then(response => {
                            SetRelationshipsList(response.data)
                            SetNewRelation(false)
                            SetUpdateConcepts(true)
                            SetSource(false)
                            SetPredicate(false)
                            SetTarget(false)
                            SetTargetText(false)
                            SetPredicateText(false)
                            SetShowReadOnlyRelation(false)
                            SetSourceText(false)
                            SetTargetConcepts(false)
                            SetPredicateConcepts(false)
                            SetSourceConcepts(false)
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetSnackMessage({'message': 'Saved'})

                        }).catch(error => SetShowAlertError(true))
                        console.log(source, predicate, target)


                    }else{
                        axios.post('facts/insert', {
                            source: source,
                            predicate: predicate,
                            target: target
                        }).then(response => {
                            SetFactsList(response.data)
                            SetUpdateConcepts(true)
                            SetSource(false)
                            SetPredicate(false)
                            SetTarget(false)
                            SetTargetText(false)
                            SetPredicateText(false)
                            SetShowReadOnlyRelation(false)
                            SetSourceText(false)
                            SetTargetConcepts(false)
                            SetPredicateConcepts(false)
                            SetSourceConcepts(false)
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetSnackMessage({'message': 'Saved'})

                        }).catch(error => SetShowAlertError(true))
                        console.log(source, predicate, target)

                    }

                } else {
                    if(Source || Predicate || Target){
                        axios.post('relationships/update', {
                            prev_subject: Relationship['subject'],
                            prev_predicate: Relationship['predicate'],
                            prev_object: Relationship['object'],
                            source: source,
                            predicate: predicate,
                            target: target
                        }).then(response => {
                            SetRelationshipsList(response.data)
                            SetNewRelation(false)
                            SetUpdateConcepts(true)
                            SetSource(false)
                            SetPredicate(false)
                            SetTarget(false)
                            SetTargetText(false)
                            SetPredicateText(false)
                            SetShowReadOnlyRelation(false)
                            SetSourceText(false)
                            SetTargetConcepts(false)
                            SetPredicateConcepts(false)
                            SetSourceConcepts(false)
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowReadOnlyRelation(true);
                            SetSnackMessage({'message': 'Saved'})
                        }).catch(error => {
                            SetShowAlertError(true);
                            console.log(error)
                        })
                    }else{
                        axios.post('facts/update', {
                            prev_subject: Relationship['subject'],
                            prev_predicate: Relationship['predicate'],
                            prev_object: Relationship['object'],
                            source: source,
                            predicate: predicate,
                            target: target
                        }).then(response => {
                            SetUpdateConcepts(true)

                            SetFactsList(response.data)


                            SetShowAlertSuccess(true)
                            //SetInARel(false)
                            SetBinaryRel(false)
                            SetNewFact(false)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetShowAlertSuccess(true)
                            //SetInARel(true)
                            SetModify(false)
                            SetNewFactInterno(false)
                            SetSnackMessage({'message': 'Saved'})

                            SetShowReadOnlyRelation(true);
                        }).catch(error => {
                            SetShowAlertError(true);
                            console.log(error)
                        })

                    }



                }
            }
        }
    }

    function backFunction(e){
        e.preventDefault();
        e.stopPropagation();
        SetSource(SourceBackup)
        SetPredicate(PredicateBackup)
        SetTarget(TargetBackup)
        SetTargetText(TargetTextBackup)
        SetPredicateText(PredicateTextBackup)
        SetPredicateConcepts(PredicateConceptsBackup)
        SetSourceText(SourceTextBackup)
        SetSourceConcepts(SourceConceptsBackup)
        SetTargetConcepts(TargetConceptsBackup)
        SetModify(false)
        SetNewFactInterno(false)
        SetShowReadOnlyRelation(true);
    }

    useEffect(()=>{
        axios.get('collections/concepts')
            .then(response=>{
                SetCollectionConcepts(response.data)
                SetUpdateConcepts(false)
            })
        axios.get('relationships',{params:{user:CurAnnotator}})
            .then(response=>{
                SetRelationshipsList(response.data)
            })
    },[UpdateConcepts])

    const handleClickOpen = () => {
        SetShowInstructionModal(true);
    };

    const handleClose = () => {
        SetShowInstructionModal(false);
    };


    return(
        <div>
            <Dialog
                open={ShowInstructionModal}
                onClose={handleClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    {(Source || Predicate || Target) ? "Add a new relationship" : "Add a new fact"}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        {(Source || Predicate || Target) ?

                            <div>A relationship is compose of a subject, a predicate, and an object. The subject is automatically
                            selected at the moment of relationship creation. It is possible to select the predicate and the
                            object mentions of the relationship by right clicking on the mention and selecting its role. This
                            procedure can be applied also to change the role of a mention, hence, if a mention is the subject, it is
                            possible to change its role to predicate (or object). To speed up the selection of the mentions
                            participating in a relationship, once selected the subject, it is possible to click on a different mention and
                            it will be automatically assigned the role of predicate. <hr/>
                            If the subject, predicate or object are concepts, it is possible to select it on the menu on the right,
                                clicking on the "Add subject" (predicate, object) buttons. In this case, the concept will not be associated
                                to a mention. Once clicked, a modal will appear allowing you to set the desired concept. <hr/>
                                If the subject and the object are two mentions, by clicking on the "+ PREDICATE" placed in the textual content in a
                                green button, it will be possible to add a string describing the relation type between the subject and the object. In
                                all the other cases, the concepts can be set relying on the panel on the right.
                            </div>


                            :
                            <div>In an assertion the subject, the predicate, and the object are three concepts. The concepts can be set by the
                            the panel on the right, by clicking on the "Add subject", "Add predicate" and "Add object" buttons: a modal will appear where
                            the concepts can be selected.</div>
                        }

                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} autoFocus>
                        Ok
                    </Button>
                </DialogActions>
            </Dialog>



            {ShowConceptModal && NodeType === 'source' && <RelationshipModal relation={'source'} setconcepts_list={SetSourceConcepts} concepts_list={SourceConcepts} showconceptmodal={ShowConceptModal} setshowconceptmodal={SetShowConceptModal} settext={SetSourceText}/>  }
            {ShowConceptModal && NodeType === 'target' && <RelationshipModal relation={'target'} setconcepts_list = {SetTargetConcepts} concepts_list={TargetConcepts} showconceptmodal={ShowConceptModal} setshowconceptmodal={SetShowConceptModal} settext={SetTargetText}/>  }
            {ShowConceptModal && NodeType === 'predicate' && <RelationshipModal relation={'predicate'} setconcepts_list = {SetPredicateConcepts} concepts_list={PredicateConcepts} showconceptmodal={ShowConceptModal} setshowconceptmodal={SetShowConceptModal} settext={SetPredicateText}/>  }
            <h3 style={{color:'black'}}>
                {(Source || Predicate || Target) ? <>Relationship</> : <>Fact</>}
            </h3>
            <div className={'rel_instr'} onClick={()=>SetShowInstructionModal(prev=>!prev)}>Help</div>
            {/*{MentionsList && <div><i><b>{MentionsList.length}</b> mentions</i></div>}*/}

            <div>
                <ThemeProvider theme={roletheme}>
                <i style={{color:'black'}}>To create a new relationship or a new fact, define a <b>subject</b>, a <b>predicate</b>, and an <b>object</b>.</i>

                <Accordion>
                    <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="panel1a-content"
                        id="panel1a-header"
                    >
                        <div>
                           <Typography variant={'subtitle1'} sx={{fontWeight:'bold'}}>Subject{' '}
                               <IconButton aria-label="delete" onClick={(e)=>{
                                   e.stopPropagation()
                                   e.preventDefault()
                                   SetSourceText(false);
                                   SetSourceConcepts(false)
                                   SetSource(false)
                               }}>
                                   <ClearIcon />
                               </IconButton>
                           </Typography>
                            {(!Source && (!SourceConcepts || SourceConcepts.length === 0)) && <>

                                <Typography >
                                    <Chip color="primary" size='small' variant={'outlined'} onClick={(e)=>handleClick(e,'source')} label={'Add subject'} />
                                </Typography>

                            </> }
                            {(!Source && SourceConcepts && SourceConcepts.length > 0) &&    <>

                                <Typography >
                                    <Chip color={'concept'} size='small' label={'Concept'} /> {SourceConcepts[0].concept_name}
                                </Typography>

                            </>

                            }



                            {(((Source && !SourceConcepts)||(Source && SourceConcepts)) && SourceText) &&    <>

                                <Typography >
                                    <Chip color={'mention'} size='small' label={'Mention'} /> {SourceText}
                                </Typography>
                                {SourceConcepts.map(concept=>
                                    <Typography >
                                        <Chip color={'concept'} size='small' label={'Concept'} /> {concept.concept_name}
                                    </Typography>)}



                            </>

                            }
                        </div>


                   </AccordionSummary>

                    <AccordionDetails>
                        <Typography>
                            {(SourceConcepts && SourceConcepts.length > 0) ? <>
                                <b>Concepts</b>
                                    {SourceConcepts.map(concept=>
                                        <Card variant="outlined" sx={{padding:'10px'}}>
                                            <CardContent>

                                                <Typography variant="subtitle1" component="div">
                                                    {concept.concept_name}
                                                </Typography>
                                                <Typography sx={{ mb: 1.5 }} color="text.secondary">
                                                    {concept.concept_area}
                                                </Typography>
                                                <Typography variant="body2">
                                                    <a href={concept.concept_url}>{concept.concept_url}</a>
                                                </Typography>
                                            </CardContent>

                                        </Card>

                                        )}

                               </>

                                : <>
                                {!Source ? <>Setting a <b>subject</b> is mandatory.</> : <>0 concepts</>}
                            </>}
                        </Typography>
                    </AccordionDetails>
                </Accordion>

                    {(BinaryRel === false || (PredicateConcepts && PredicateConcepts[0].concept_name !== '') || !PredicateConcepts || (PredicateConcepts && PredicateConcepts.length === 0)) && <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                        >
                            <div>
                                <Typography variant={'subtitle1'} sx={{fontWeight: 'bold'}}>Predicate{' '}
                                    <IconButton aria-label="delete" onClick={(e) => {
                                        e.stopPropagation()
                                        e.preventDefault()
                                        SetPredicateConcepts(false);
                                        SetPredicateText(false)
                                        SetPredicate(false)
                                    }}>
                                        <ClearIcon/>
                                    </IconButton></Typography>
                                {(!Predicate && (!PredicateConcepts || PredicateConcepts.length === 0)) && <>
                                    {/*<Typography sx={{ width: '10%', flexShrink: 0,color: 'text.secondary'  }}>*/}

                                    {/*</Typography>*/}
                                    <Typography>
                                        <Chip size='small' color="primary" variant={'outlined'}
                                              onClick={(e) => handleClick(e, 'predicate')} label={'Add predicate'}/>
                                    </Typography>

                                </>}
                                {(!Predicate && PredicateConcepts && PredicateConcepts.length > 0) && <>

                                    <Typography>
                                        <Chip size='small' color={'concept'}
                                              label={'Concept'}/> {PredicateConcepts[0].concept_name}
                                    </Typography>

                                </>

                                }


                                {(((Predicate && !PredicateConcepts) || (Predicate && PredicateConcepts)) && PredicateText) && <>

                                    <Typography>
                                        <Chip size='small' color={'mention'} label={'Mention'}/> {PredicateText}
                                    </Typography>
                                    {PredicateConcepts.map(concept =>
                                        <Typography>
                                            <Chip color={'concept'} size='small'
                                                  label={'Concept'}/> {concept.concept_name}
                                        </Typography>)}

                                </>

                                }
                            </div>

                        </AccordionSummary>

                        <AccordionDetails>
                            <Typography>
                                {((PredicateConcepts && PredicateConcepts.length > 0)) ? <>
                                        <b>Concepts</b>
                                        {PredicateConcepts.map(concept =>
                                            <Card variant="outlined" sx={{padding: '10px'}}>
                                                <CardContent>

                                                    <Typography variant="subtitle1" component="div">
                                                        {concept.concept_name}
                                                    </Typography>
                                                    <Typography sx={{mb: 1.5}} color="text.secondary">
                                                        {concept.concept_area}
                                                    </Typography>
                                                    <Typography variant="body2">
                                                        <a href={concept.concept_url}>{concept.concept_url}</a>
                                                    </Typography>
                                                </CardContent>

                                            </Card>
                                        )}

                                    </>

                                    : <>
                                        {!Predicate ? <>Setting a <b>predicate</b> is mandatory.</> : <>0 concepts</>}
                                    </>}
                            </Typography>
                        </AccordionDetails>
                    </Accordion>}
                <Accordion>
                    <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="panel1a-content"
                        id="panel1a-header"
                    >
                        <div>
                            <Typography variant={'subtitle1'}  sx={{fontWeight:'bold'}}>Object{' '}
                                <IconButton aria-label="delete" onClick={(e)=>{
                                    e.stopPropagation()
                                    e.preventDefault()
                                    SetTargetConcepts(false);
                                    SetTargetText(false)
                                    SetTarget(false)
                                }}>
                                    <ClearIcon />
                                </IconButton></Typography>
                            {(!Target && (!TargetConcepts || TargetConcepts.length === 0)) && <>
                                {/*<Typography sx={{ width: '10%', flexShrink: 0,color: 'text.secondary'  }}>*/}

                                {/*</Typography>*/}
                                <Typography >
                                    <Chip size='small' color="primary" variant={'outlined'} onClick={(e)=>handleClick(e,'target')} label={'Add object'} />
                                </Typography>

                            </> }
                            {(!Target && TargetConcepts && TargetConcepts.length > 0) &&    <>

                                <Typography >
                                    <Chip size='small' color={'concept'} label={'Concept'} /> {TargetConcepts[0].concept_name}
                                </Typography>

                            </>

                            }


                            {(((Target && !TargetConcepts)||(Target && TargetConcepts)) && TargetText) &&    <>

                                <Typography >
                                    <Chip size='small' color={'mention'} label={'Mention'} /> {TargetText}
                                </Typography>
                                {TargetConcepts.map(concept=>
                                    <Typography >
                                        <Chip color={'concept'} size='small' label={'Concept'} /> {concept.concept_name}
                                    </Typography>)}
                            </>

                            }
                        </div>

                    </AccordionSummary>

                    <AccordionDetails>
                        <Typography>
                            {((TargetConcepts && TargetConcepts.length > 0)) ? <>
                                    <b>Concepts</b>
                                    {TargetConcepts.map(concept=>
                                        <Card variant="outlined" sx={{padding:'10px'}}>
                                            <CardContent>

                                                <Typography variant="subtitle1" component="div">
                                                    {concept.concept_name}
                                                </Typography>
                                                <Typography sx={{ mb: 1.5 }} color="text.secondary">
                                                    {concept.concept_area}
                                                </Typography>
                                                <Typography variant="body2">
                                                    <a href={concept.concept_url}>{concept.concept_url}</a>
                                                </Typography>
                                            </CardContent>

                                        </Card>

                                    )}

                                </>

                                : <>
                                    {!Target ? <>Setting a <b>object</b> is mandatory.</> : <>0 concepts</>}
                                </>}
                        </Typography>
                    </AccordionDetails>
                </Accordion>

                </ThemeProvider>
                <div style={{margin: '20px'}}>
                    {ShowAlertSuccess &&
                        <Alert onClose={SetShowAlertSuccess(false)} severity="success" sx={{ width: '100%' }}>
                             Relationship save
                         </Alert>
                     }
                    {ShowAlertError &&
                        <Alert onClose={SetShowAlertError(false)} severity="error" sx={{ width: '100%' }}>
                            An error occurred
                        </Alert>
                    }
                    {((Modify && ShowRels) || (ShowFacts && NewFactInterno)) && <Button variant="contained" color={'secondary'} sx={{marginRight:'5px'}} onClick={
                        backFunction
                    }>Back</Button>}
                    <Button
                        onClick={submitRelationship}
                        variant="contained" disabled={((!SourceConcepts || SourceConcepts.length === 0) && !Source) || ((!PredicateConcepts || PredicateConcepts.length === 0) && !Predicate) || ((!TargetConcepts || TargetConcepts.length === 0 )&& !Target)}>Confirm</Button>

                </div>







            </div>


        </div>
    );
}