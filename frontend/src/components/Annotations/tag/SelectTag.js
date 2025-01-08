import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import React, {useContext} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import '../annotation.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import {ConceptContext} from "../../../BaseIndex";
import AutoCompleteWithAddTag from "./AutoCompleteWithAddTag";

export default function SelectTag(props){


    const {conceptslist} =  useContext(ConceptContext);
    const {tags} =  useContext(AppContext);

    const [ConceptsList,SetConceptsList] = conceptslist
    const [Tags,SetTags] = tags
    let names = []

    ConceptsList.map((c)=>{
        names.push(c.name)
    })


    return(
        <div>
            <DialogTitle style={{cursor: 'move'}} id="draggable-dialog-title">
                Select a tag
            </DialogTitle>
            <DialogContent>
                <i>if the selected tag does not exist, it will be created.</i>
                <div style={{paddingBottom:'8%'}}>
                </div>

                {Tags && <AutoCompleteWithAddTag type={props.type}/>}

            </DialogContent>
        </div>
    )
}
