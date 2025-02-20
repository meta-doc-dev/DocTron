import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import React, {useContext, useEffect, useState} from "react";
import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Mention from "../mentions/Mention";


import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import '../annotation.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import Chip from '@mui/material/Chip';
import {RelationConceptContext} from "./RelationshipConceptModal";
import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';
import AutoCompleteWithAdd from "./AutoCompleteWithAdd2";
import {ConceptContext} from "../../../BaseIndex";

export default function SelectConcept(props){

    const {inarel,newfact,newfactin,modifyrel} =  useContext(AppContext);
    const [InARel,SetInARel] = inarel
    const [NewFact,SetNewFact] = newfact
    const [Modify,SetModify] = modifyrel
    const [NewFactInterno,SetNewFactInterno] = newfactin

    const {area,url,name,urlname,description,areas,conceptslist} =  useContext(ConceptContext);
    const {area1,url1,name1,urlname1,description1,areas1,conceptslist1} =  useContext(RelationConceptContext);
    // const [Area,SetArea] = InARel ? area1 : area
    // const [Areas,SetAreas] = InARel ? areas1 : areas
    // const [ConceptsList,SetConceptsList] = InARel ? conceptslist1 : conceptslist

    // const [Name,SetName] =InARel ? name1 : name
    const [Url,SetUrl] = (InARel || NewFact || Modify || NewFactInterno) ? url1 : url
    // const [Description,SetDescription] = InARel ? description1 : description
    // const [Area,SetArea] = InARel ? area1 : area
    // const [Areas,SetAreas] = InARel ? areas1 : areas
    // const [ConceptsList,SetConceptsList] = InARel ? conceptslist1 : conceptslist

    // const [Url,SetUrl] = url
    const [Description,SetDescription] = description
    const [ConceptsList,SetConceptsList] = conceptslist
    let names = []
    ConceptsList.map((c)=>{
        names.push(c.name)
    })
    let urls = []
    ConceptsList.map((c)=>{
        urls.push(c.url)
    })

    return(
        <div>
            <DialogTitle style={{cursor: 'move'}} id="draggable-dialog-title">
                Select a Type and a Concept
            </DialogTitle>
            <DialogContent>
                <i>if the selected Concpet type or name  do not exist, they will be created.</i>
                <div style={{paddingBottom:'8%'}}>
                    {/*<i>Select a concept type, and a Concept Name</i>*/}

                </div>

                <AutoCompleteWithAdd type={props.type} />

                <div >
                    { Url !== null && Url && urls.indexOf(Url.url) === -1 &&
                    <div style={{marginTop:'2%'}}> You are adding a new concept. Providing a description is optional but recommended.
                    <div style={{marginTop:'2%'}}>
                    {/*    <TextField sx={{width:'100%'}} id="outlined-basic" onChange={(e)=>SetUrl(e.target.value)} required label="URL" variant="outlined" />*/}
                    {/*</div><br/>*/}
                        <TextField
                            sx={{width:'100%'}}
                            id="outlined-basic"
                            label="Description"
                            onChange={(e)=>SetDescription(e.target.value)}
                            multiline
                            rows={3}

                            variant="outlined" />

                    </div></div>}</div>



            </DialogContent>
        </div>
    )
}
