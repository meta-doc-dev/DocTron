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
// "react-color": "^3.0.0-beta.3",

export default function ShowTypes(props) {
    const {
        collection, factslist,
        labels,
        labels_passage,
        annotationtypes,points,
        tags_split,
        relationshipslist,
        concepts,annotationtype,
        view, annotatedlabels,
        mentions
    } = useContext(AppContext);

    const [value, setValue] = useState(4)
    const [View, SetView] = view
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [AnnotationType, SetAnnotationType] = annotationtype
    const [Collection, SetCollection] = collection
    const [Labels, SetLabels] = labels
    const [LabelsPassage, SetLabelsPassage] = labels_passage
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

    return (
        <div className={'annOver'}>

            <h5>Annotations overview</h5>
            <div style={{fontSize: '0.8rem'}}>
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
                    {Points && Points['points'].length > 0 && AnnotationTypes && AnnotationType === "Object detection" &&
                        <div style={{margin: '10px 0px'}}>
                            <PointsListClass /></div>}
                    {ConceptsList && ConceptsList.length > 0 && AnnotationTypes && AnnotationType === "Entity linking" &&
                        <div style={{margin: '10px 0px'}}>
                            <ConceptsListClass/></div>}
                    {TagsSplitted && TagsSplitted.length > 0 && AnnotationTypes && AnnotationType === "Entity tagging" &&
                        <div style={{margin: '10px 0px'}}>
                            <TagsListClass/></div>}
                    {ConceptsList && RelationshipsList && RelationshipsList.length > 0 && AnnotationTypes && (AnnotationType === "Relationships annotation") &&
                        <div style={{margin: '10px 0px'}}>
                            <RelationshipsListComp/></div>}
                    {ConceptsList && FactsList && FactsList.length > 0 && AnnotationTypes && (AnnotationType === "Facts annotation") &&
                        <div style={{margin: '10px 0px'}}>
                            <FactsListComp/></div>}


                </div>
            </div>


        </div>

    );
}
