import axios from "axios";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import './sidebar.css'

import './typescss.css'
import {AppContext} from "../../App";

import MentionsListClass from "../RightSideMenu/mentions/MentionsListClass";
import ConceptsListClass from "../RightSideMenu/associations/ConceptsListClass";
import TagsListClass from "../RightSideMenu/tags/TagsListClass";
import RelationshipsListComp from "../RightSideMenu/relationships/RelationshipsListComp";
import LabelsClass from "../RightSideMenu/labels/Labels";
import FactsListComp from "../RightSideMenu/relationships/FactsListComp";
import PointsListClass from "../RightSideMenu/mentions/PointsListClass";
import Button from "@mui/material/Button";
import CreateFact from "@components/Document/ToolBar/CreateFactComponent";
// "react-color": "^3.0.0-beta.3",

export default function ShowTypes(props) {
    const {
        collection, factslist,
        labels,curannotator,
        username,
        annotationtypes,points,
        tags_split,
        relationshipslist,
        concepts,annotationtype,
        view, annotatedlabels,document_id,
        mentions,snackmessage,opensnack
    } = useContext(AppContext);

    const [DocumentID,SetDocumentID] = document_id

    const [CollectionDescription,SetCollectionDescription] = useState(false)
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const [value, setValue] = useState(4)
    const [Username, SetUsername] = username
    const [View, SetView] = view
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [AnnotationType, SetAnnotationType] = annotationtype
    const [Collection, SetCollection] = collection
    const [Labels, SetLabels] = labels
    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [MentionsList, SetMentionsList] = mentions
    const [ConceptsList, SetConceptsList] = concepts
    const [TagsSplitted, SetTagsSplitted] = tags_split
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [RelationshipsList, SetRelationshipsList] = relationshipslist
    const [FactsList, SetFactsList] = factslist
    const [Points, setPoints] = points

    useEffect(() => {
        setValue(View)
    }, [View]);

    /*    function handleChangeRadio(e){
            e.preventDefault();
            e.stopPropagation()
            console.log(e.target.value)
            let val = parseInt(e.target.value)
            setValue(val)
            SetView(val)
        }*/

    useEffect(() => {
        if (Collection) {

            axios.get('collections/labels')
                .then(response => {
                    console.log(response.data)
                    SetLabels(response.data)
                })


        }
    }, [Collection])

    function copyAnnotation(e){
        e.preventDefault()
        e.stopPropagation()
        SetOpenSnack(true)
        SetSnackMessage({'message':'Copying...'})
        axios.post('copy_annotation',{user:CurAnnotator}).then(response=> {
            console.log(response)
            SetSnackMessage({'message':'Copied'})
        })
            .catch(error=> {
                    console.log(error)
                    SetSnackMessage({'message': 'ERROR'})
                }

            )

    }


    return (
        <div className={'annOver'}>

            <h5>Annotations overview</h5>
            <div style={{fontSize: '0.6rem'}}>
                <div><h6>Annotator: {CurAnnotator}</h6></div>
                {CurAnnotator !== Username && <div>
                    <Button color={'primary'} size={'small'} sx={{fontSize:'0.7rem'}} onClick={(e)=>{
                        copyAnnotation(e)
                    }}>Copy annotation</Button> <Button sx={{fontSize:'0.7rem'}} vcolor={'primary'} size={'small'} onClick={()=> {
                    SetCurAnnotator(Username);

                }}>Back to my workspace</Button>
                </div>}
                {/*<div>The allowed annotation types are:
                    <ul> {AnnotationTypes.map(type => <li>{type}</li>)}</ul>
                    <hr/>
                </div>*/}

                <div>
                    {Labels && AnnotatedLabels && AnnotationTypes && AnnotationType === "Graded labeling" &&
                        <div style={{margin: '10px 0px'}}>
                            <LabelsClass/></div>}

                    {MentionsList && MentionsList.length > 0 && AnnotationTypes && AnnotationType === "Passages annotation" &&
                        <div style={{margin: '10px 0px'}}>
                            <MentionsListClass/></div>}
                    {MentionsList && MentionsList.length === 0 && AnnotationTypes && AnnotationType === "Passages annotation" &&
                        <div style={{margin: '10px 0px'}}>
                            Passages found: 0
                        </div>
                    }
                    {Points &&  AnnotationType === "Object detection" &&
                        <div style={{margin: '10px 0px'}}>
                            <PointsListClass/></div>}
                    {Points && Points['points'].length === 0 && AnnotationType === "Object detection" &&
                        <div style={{margin: '10px 0px'}}>
                            Objects found: 0
                        </div>
                    }
                    {ConceptsList && ConceptsList.length > 0 && AnnotationTypes && AnnotationType === "Entity linking" &&
                        <div style={{margin: '10px 0px'}}>
                            <ConceptsListClass/></div>}
                    {ConceptsList && ConceptsList.length === 0 && AnnotationTypes && AnnotationType === "Entity linking" &&
                        <div style={{margin: '10px 0px'}}>
                            Entities linked: 0
                        </div>
                    }
                    {TagsSplitted && TagsSplitted.length > 0 && AnnotationTypes && AnnotationType === "Entity tagging" &&
                        <div style={{margin: '10px 0px'}}>
                            <TagsListClass/></div>}
                    {TagsSplitted && TagsSplitted.length === 0 && AnnotationTypes && AnnotationType === "Entity tagging" &&
                        <div style={{margin: '10px 0px'}}>
                            Entities tagged: 0
                        </div>
                    }
                    {ConceptsList && RelationshipsList && RelationshipsList.length > 0 && AnnotationTypes && (AnnotationType === "Relationships annotation") &&
                        <div style={{margin: '10px 0px'}}>
                            <RelationshipsListComp/></div>}
                    {ConceptsList && RelationshipsList && RelationshipsList.length === 0 && AnnotationTypes && (AnnotationType === "Relationships annotation") &&
                        <div style={{margin: '10px 0px'}}>
                            Relationships found: 0
                        </div>
                    }
                    { FactsList && FactsList.length > 0 && AnnotationTypes && (AnnotationType === "Facts annotation") &&

                        <div style={{margin: '10px 0px'}}>
                            <CreateFact/>
                            <FactsListComp/></div>}
                    { FactsList && FactsList.length === 0 && AnnotationTypes && (AnnotationType === "Facts annotation") &&
                        <div style={{margin: '10px 0px'}}>
                            Facts found: 0
                            <CreateFact/>

                        </div>
                    }


                        </div>
                        </div>


                        </div>

                        );
                    }
