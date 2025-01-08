import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import EditIcon from '@mui/icons-material/Edit';

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';

import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

// import './documents.css'
import {CircularProgress} from "@mui/material";
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
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Checkbox from "@mui/material/Checkbox";

import Autocomplete, {createFilterOptions} from '@mui/material/Autocomplete';
import axios from "axios";
import Alert from "@mui/material/Alert";


export default function QuickPredicateModal(props) {

    const {
        collectionconcepts,
        users, predicateconcepts, predicatetext,
        collectionslist,
        document_id,
        concepts, annotationtypes,
        collection, predicate,
        mentions, documentdescription, showrelspannel,
        mentiontohighlight, snackmessage, opensnack, relationshipslist, source, sourceconcepts,
        startrange, targetconcepts, targettext, sourcetext, target, binaryrel, newfactin,
        endrange, modifyrel, inarel, relationship, labels, view, modality, curannotator, readonlyrelation, newfact,
    } = useContext(AppContext);
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [SnackMessage, SetSnackMessage] = snackmessage;
    const [OpenSnack, SetOpenSnack] = opensnack
    const [RelationshipsList, SetRelationshipsList] = relationshipslist
    const [Source, SetSource] = source;
    const [SourceConcepts, SetSourceConcepts] = sourceconcepts
    const [TargetConcepts, SetTargetConcepts] = targetconcepts
    const [SourceText, SetSourceText] = sourcetext
    const [TargetText, SetTargetText] = targettext
    const [Target, SetTarget] = target;
    const [BinaryRel, SetBinaryRel] = binaryrel;
    const [NewFactInterno, SetNewFactInterno] = newfactin

    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [Modality, SetModality] = modality
    const [View, SetView] = view
    const [ShowRels, SetShowRels] = showrelspannel

    const [Relationship, SetRelationship] = relationship
    const [InARel, SetInARel] = inarel
    const [Modify, SetModify] = modifyrel
    const [ShowReadOnlyRelation, SetShowReadOnlyRelation] = readonlyrelation
    const [NewFact, SetNewFact] = newfact
    const [PredicateText, SetPredicateText] = predicatetext
    const [Predicate, SetPredicate] = predicate
    const [MentionsInvolved, SetMentionsInvolved] = useState([])
    const [SelectedMention, SetSetSelectedMention] = useState(false)
    const [MentionToHighlight, SetMentionToHighlight] = mentiontohighlight
    const [DocumentID, SetDocumentID] = document_id
    const [Collection, SetCollection] = collection
    const [MentionsList, SetMentionsList] = mentions
    const [Start, SetStart] = startrange
    const [End, SetEnd] = endrange
    const [CollectionConcepts, SetCollectionConcepts] = collectionconcepts
    const [ConceptsList, SetConceptsList] = concepts
    const [ShowAddConceptModal, SetShowAddConceptModal] = useState(false)
    const [contextMenu, setContextMenu] = useState(null);
    const inputEl = useRef(null);
    const [DocumentDesc, SetDocumentDesc] = documentdescription
    const [PredicateConcepts, SetPredicateConcepts] = predicateconcepts
    const [Value, setValue] = useState('')
    const [open, toggleOpen] = React.useState(false);
    const filter = createFilterOptions();
    const [UpdateConcepts, SetUpdateConcepts] = useState(false)
    const [ShowAlertError, SetShowAlertError] = useState(false)
    const [ShowAlertSuccess, SetShowAlertSuccess] = useState(false)
    const [JsonMapping, SetJsonMapping] = useState([{
        source: "Anat. Loc.",
        target: "Human/Animal",
        predicate: "located in"
    },
        {source: "Anat. Loc.", target: "Human/Animal", predicate: "located in"},
        {source: "Bacteria", target: "Microbiome", predicate: "part of"},
        {source: "Bacteria", target: "DDF", predicate: "influence"},
        {source: "Bacteria", target: "Gene", predicate: "change expression"},
        {source: "DDF", target: "Bacteria", predicate: "change abundance"},
        {source: "DDF", target: "Human/Animal", predicate: "affect"},
        {source: "DDF", target: "Microbiome", predicate: "change abundance"},
        {source: "Drug/Chem./Diet", target: "DDF", predicate: "change effect"},
        {source: "Drug/Chem./Diet", target: "Microbiome", predicate: "impact"},
        {source: "Drug/Chem./Diet", target: "Bacteria", predicate: "impact"},
        {source: "Drug/Chem./Diet", target: "Gene", predicate: "change expression"},
        {source: "Human/Animal", target: "Bio. technique", predicate: "used by"},
        {source: "Metabolite", target: "Microbiome", predicate: "produced by"},
        {source: "Metabolite", target: "Anat. Loc.", predicate: "located in"},
        {source: "Microbiome", target: "Bio. technique", predicate: "used by"},
        {source: "Microbiome", target: "Human/Animal", predicate: "located in"},
        {source: "Microbiome", target: "Gene", predicate: "change expression"},
        {source: "Microbiome", target: "DDF", predicate: "is linked to"},
        {source: "Microbiome", target: "Microbiome", predicate: "compared to"},
        {source: "Microbiome", target: "Anat. Loc.", predicate: "located in"},
        {source: "Neurot.", target: "Microbiome", predicate: "related to"},
        {source: "Neurot.", target: "Anat. Loc.", predicate: "located in"},
        {source: "*.", target: "*.", predicate: "associated with"}])
    const [Options, SetOptions] = useState(false)


    const [dialogValue, setDialogValue] = React.useState({
        url: '',
        name: '',
        area: '',
        description: '',
    });


    useEffect(() => {
        axios.get('collections/concepts')
            .then(response => {
                SetCollectionConcepts(response.data)
                SetUpdateConcepts(false)
            })
        axios.get('relationships', {params: {user: CurAnnotator}})
            .then(response => {
                SetRelationshipsList(response.data)
            })
    }, [UpdateConcepts])

    useEffect(() => {
        if (CollectionConcepts) {
            var new_opts = []
            var options = CollectionConcepts.filter(x => x['area'] === 'Relation predicate')
            if (JsonMapping && (Collection === '9ec6240e3b4ea92a8f57405a69e31a4f' || Collection === '33be8d0d958c56b0ae779b22e2c85023' || Collection === 'd55beda740114e3214aa62937ac90310' || Collection === '1cd9f4716c04e1be8b378f72ba950530')) {
                var json_obj = null
                options.map(x => {
                        JsonMapping.map(y => {
                            if (y.predicate === x.name) {
                                json_obj = y
                                let obj = {url: x.url, description: x.description, area: x.area}
                                obj.name = x.name + ' [' + json_obj.source + ', ' + json_obj.target + ']'
                                new_opts.push(obj)
                            }
                        })
                        /*          if(json_obj !== null){
                                      x.name = x.name + ' [' + json_obj.source + ', ' + json_obj.target + ']'
                                  }*/

                    }
                )
            }
            SetOptions(new_opts)
        }
    }, [CollectionConcepts])

    function addPredicate(e) {
        e.preventDefault()
        e.stopPropagation()
        var type = "Relation predicate"
        // var name = document.getElementById('predicate_string').value
        if (Value !== '') {
            let concept = {
                concept_url: Value.url,
                concept_name: Value.name,
                concept_area: type,
                concept_description: null
            }
            let predicates = PredicateConcepts ? PredicateConcepts : []
            let new_list = [...predicates, concept]

            if (!(Modify && ShowRels)) {
                submitRelationship(new_list)

            } else {
                SetPredicateConcepts(new_list)
                SetPredicateText(Value.name)
            }
            props.setshowconceptmodal(false)
        }

    }

    function submitRelationship(predicate_concepts) {

        if (Modality === 2) {
            console.log('ecco')
            SetOpenSnack(true)
            SetSnackMessage({'message': 'You cannot annotate this document'})
        } else {
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
            SetPredicateConcepts(predicate_concepts)
            SetPredicateText(predicate_concepts[0]['concept_name'])
            predicate_concepts.map(x => {
                if (JsonMapping && (Collection === '9ec6240e3b4ea92a8f57405a69e31a4f' || Collection === 'd55beda740114e3214aa62937ac90310' || Collection === '1cd9f4716c04e1be8b378f72ba950530')) {
                    x.concept_name = x.concept_url
                }
            })
            predicate['concepts'] = predicate_concepts

            target['concepts'] = target_concepts
            if (Modality === 2 || View === 4) {
                SetOpenSnack(true)
                SetSnackMessage({'message': 'You cannot annotate this document'})
            } else if (AnnotationTypes.indexOf('Entity linking') === -1) {
                SetOpenSnack(true)
                SetSnackMessage({'message': 'Entity linking is not allowed here'})
            } else {
                if (!Modify) {
                    axios.post('relationships/insert', {
                        source: source,
                        predicate: predicate,
                        target: target
                    }).then(response => {
                        SetRelationshipsList(response.data)
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
                        //SetShowReadOnlyRelation(true);
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
                        /*                SetSource(false)
                                        SetPredicate(false)
                                        SetTarget(false)
                                        SetNewFact(false)
                                        SetTargetText(false)
                                        SetPredicateText(false)
                                        SetSourceText(false)
                                        SetTargetConcepts(false)
                                        SetPredicateConcepts(false)
                                        SetSourceConcepts(false)*/
                        SetShowAlertSuccess(true)
                        SetShowReadOnlyRelation(true)
                        /*
                                                SetInARel(false)
                        */
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


    function handleClose(e) {
        e.stopPropagation()
        e.preventDefault()
        props.setshowconceptmodal(false)
        setDialogValue({
            url: '',
            name: '',
            area: '',
            description: '',
        });
        toggleOpen(false);
    }


    return (
        <Dialog
            open={props.showconceptmodal}
            onClose={handleClose}
            maxWidth={'sm'}
            fullWidth={'sm'}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >

            <DialogTitle id="alert-dialog-title">
                Add a predicate
            </DialogTitle>
            <DialogContent>

                <DialogContentText id="alert-dialog-description">
                    Type a predicate. This predicate will be available as a concept under the type:"Relation
                    Predicates".
                    <br/><br/>
                    {Options && <Autocomplete
                        value={Value}
                        onChange={(event, newValue) => {
                            if (typeof newValue === 'string') {
                                // timeout to avoid instant validation of the dialog's form.
                                setTimeout(() => {
                                    toggleOpen(true);
                                    setValue({
                                        name: newValue,
                                        url: newValue,
                                        area: 'Relation predicate',
                                        description: '',
                                    });
                                    setDialogValue({
                                        name: newValue,
                                        url: newValue,
                                        area: 'Relation predicate',
                                        description: '',
                                    });
                                });
                            } else if (newValue && newValue.inputValue) {
                                toggleOpen(true);
                                setValue({
                                    name: newValue.inputValue,
                                    url: newValue.inputValue,
                                    description: '',
                                    area: 'Relation predicate',
                                });
                                setDialogValue({
                                    name: newValue.inputValue,
                                    url: newValue.inputValue,
                                    description: '',
                                    area: 'Relation predicate',
                                });
                            } else {
                                setValue(newValue);
                            }
                        }}
                        filterOptions={(options, params) => {
                            const filtered = filter(options, params);

                            if (params.inputValue !== '') {
                                filtered.push({
                                    inputValue: params.inputValue,
                                    name: `Add "${params.inputValue}"`,
                                });
                            }

                            return filtered;
                        }}
                        id="predicate_rel"
                        options={Options}

                        getOptionLabel={(option) => {
                            // for example value selected with enter, right from the input
                            if (typeof option === 'string') {
                                return option;
                            }
                            if (option.inputValue) {
                                return option.inputValue;
                            }
                            return option.name;
                        }}
                        selectOnFocus
                        clearOnBlur
                        handleHomeEndKeys
                        renderOption={(props, option) => {
                            const {key, ...optionProps} = props;
                            return (
                                <li key={key} {...optionProps}>
                                    {/*
                                        <>{option.name} - [{JsonMapping['source']}, {JsonMapping['target']}</>
*/}
                                    <>{option.name}</>
                                </li>
                            );
                        }}
                        sx={{width: '100%'}}
                        freeSolo
                        renderInput={(params) => <TextField {...params} label="predicate"/>}
                    />}
                    {/*<Autocomplete*/}
                    {/*    selectOnFocus*/}
                    {/*    clearOnBlur*/}
                    {/*    handleHomeEndKeys*/}
                    {/*    freeSolo*/}
                    {/*    id="autocomplete_pred"*/}
                    {/*    sx={{marginTop: '10px', width: '100% !important'}}*/}
                    {/*    options={CollectionConcepts.filter(x=>x['area'] === 'Relation predicate')}*/}
                    {/*    getOptionLabel={(option) => {*/}
                    {/*        if (typeof option === 'string') {*/}
                    {/*            return option;*/}
                    {/*        }*/}
                    {/*        return option.name}*/}
                    {/*    }*/}
                    {/*    onChange={(event,newValue) => {*/}
                    {/*        SetValue(newValue)*/}
                    {/*    }}*/}
                    {/*    style={{ width: 500 }}*/}
                    {/*    renderInput={(params) => (*/}
                    {/*        <TextField {...params} id="predicate_string" sx={{width: "100%"}} label=predicate variant="outlined" />*/}

                    {/*        // <TextField {...params} label="Members" placeholder="Members" />*/}
                    {/*    )}*/}
                    {/*/>*/}
                </DialogContentText>
                {ShowAlertError &&
                    <Alert onClose={SetShowAlertError(false)} severity="error" sx={{width: '100%'}}>
                        An error occurred
                    </Alert>
                }
                {ShowAlertSuccess &&
                    <Alert onClose={SetShowAlertSuccess(false)} severity="success" sx={{width: '100%'}}>
                        Relationship save
                    </Alert>
                }
            </DialogContent>
            <DialogActions>
                <Button onClick={(e) => {
                    handleClose(e)
                }}>No</Button>
                <Button onClick={(e) => addPredicate(e)}>Confirm</Button>


            </DialogActions>
        </Dialog>
    );
}