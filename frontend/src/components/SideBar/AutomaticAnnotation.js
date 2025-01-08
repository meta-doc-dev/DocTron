import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';
import RemoveIcon from '@mui/icons-material/Remove';
import axios from "axios";
import {ButtonGroup, InputLabel, Select} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import {AppContext} from "../../App";
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;


export default function AutomaticAnnotation(props){
    const { showautomaticannotation,autoannotation,documentdescription,expand, mentions,curannotator,annotatedlabels,concepts,annotators,relationshipslist } = useContext(AppContext);
    const [MentionsList,SetMentionsList] = mentions
    const [ConceptsList,SetConceptsList] = concepts
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [DocumentDesc,SetDocumentDesc] = documentdescription

    const [Expand,SetExpand] = expand

    const [AutoAnnotate,SetAutoAnnotate] = autoannotation
    const [value, setValue] = React.useState('');
    const [ShowAutoAnno,SetShowAutoAnno] = showautomaticannotation;

    const handleChange = (event) => {
        setValue(event.target.value);
    };

    const autoAnnotation = (e) =>{
        console.log('value',document.getElementById("demo-select-small").value)
        e.preventDefault()
        e.stopPropagation()

        SetAutoAnnotate(true)


        axios.post('autotron_annotation',{task:value}).then(resp=>{
            SetDocumentDesc(false)
            SetMentionsList(false);
            SetConceptsList(false);
            SetRelationshipsList(false);
            SetAnnotatedLabels(false);
            SetAutoAnnotate(false)
            SetShowAutoAnno(false)
            SetExpand(false)

        })
    }

    return(
        <div>
            <h5>
                AUTOTRON
            </h5>
            <div>Automatic annotate the current document.
                <hr/>
                Documents having a pubmed ID will have the mentions and the concepts extracted with <b>PUBTATOR</b> mesh/omim diseases ncbi gene, otherwise they will have the
            mentions and the concepts annotated with <b>METAMAP</b> umls cui concepts.  </div>
            <div><br/>
                Select your task.
                <div>
                    <FormControl sx={{ m: 1, minWidth: 120 }} size="small">
                        <InputLabel id="demo-select-small">Task</InputLabel>
                        <Select
                            labelId="demo-select-small"
                            id="demo-select-small"
                            // value={age}
                            label="Task"
                            onChange={handleChange}
                        >
                            <MenuItem value="">
                                <em>Select a a task</em>
                            </MenuItem>
                            <MenuItem value={"GCA"}>Gene Cancer Association</MenuItem>
                            <MenuItem value={"GDA"}>Gene Disease Association</MenuItem>

                        </Select>
                    </FormControl>
                </div>


                <Button variant="contained" disabled={value===''} onClick={autoAnnotation}>Annotate</Button>






            </div>
        </div>
    );
}