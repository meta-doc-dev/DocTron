import {Col, Row} from "react-bootstrap";

import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
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

// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../../App";
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
import {DeleteRange} from "../../../HelperFunctions/HelperFunctions";
import Radio from "@mui/material/Radio";



export default function DeleteMentionModal(props) {

    const {
        username,
        users,
        collectionslist,
        document_id,
        concepts,
        tags_split,
        mentions,documentdescription,
        mentiontohighlight,
        startrange,
        endrange
    } = useContext(AppContext);
    const [MentionToHighlight, SetMentionToHighlight] = mentiontohighlight
    const [DocumentID, SetDocumentID] = document_id
    const [TagsSplitted,SetTagsSplitted] = tags_split
    const [MentionsList, SetMentionsList] = mentions
    const [Start, SetStart] = startrange
    const [End, SetEnd] = endrange
    const [ConceptsList, SetConceptsList] = concepts
    const [ShowAddConceptModal, SetShowAddConceptModal] = useState(false)
    const [contextMenu, setContextMenu] = useState(null);
    const inputEl = useRef(null);
    const [DocumentDesc,SetDocumentDesc] = documentdescription
    const [MentionsInvolved,SetMentionsInvolved] = useState([])
    const [value,SetValue] = useState(0)
    const [SelectedMention,SetSetSelectedMention] = useState(false)

    function handleChangeRadio(e){
        e.preventDefault()
        e.stopPropagation()
        let v = e.target.value
        SetValue(parseInt(v))

        // let selected = MentionsInvolved[v]
        //
        // SetSetSelectedMention(selected)
    }


    useEffect(()=>{
        let mentions = []

        props.mention.mentions.split(' ').map(m=>{
            // let mentions_involved = document.getElementsByClassName('.'+m)
            console.log(m,MentionsList)
            mentions.push(MentionsList.filter(x=>x['mentions'] === m)[0])
        })
        SetMentionsInvolved(mentions)
        console.log(mentions)
        if(mentions.length === 1){
            SetSetSelectedMention(mentions[0])
        }

    },[props.mention])







    function DeleteMention(e,mention,position){
        e.preventDefault()
        e.stopPropagation()
        axios.delete('mentions/delete',{data:{start:SelectedMention.start,stop:SelectedMention.stop,mention_text:SelectedMention.mention_text,position:position}})
            .then(response=>{

                SetDocumentDesc(response.data['document'])
                SetMentionsList(response.data['mentions'])
                SetConceptsList(response.data['concepts'])
                SetTagsSplitted(response.data['tags'])
                // SetConceptsList(filtered)
                SetSetSelectedMention(false)
                props.setshow(false)

            })
    }

    function handleClose(e){
        e.stopPropagation()
        e.preventDefault()
        props.setshow(false)
    }

    // useEffect(()=>{
    //     console.log('passed mention',props.mention)
    // },[props.mention])

    return (
        <Dialog
            open={props.show}
            onClose={handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                Delete mention
            </DialogTitle>
            <DialogContent>
                {SelectedMention  ? <DialogContentText id="alert-dialog-description">
                    Deleting the mention <b>{SelectedMention.mention_text}</b> will remove all the relationships and linked concepts.
                </DialogContentText> :
                    <DialogContentText id="alert-dialog-description">
                        Which mention do you want to remove?
                        <div>
                            {MentionsInvolved.map((m,i)=>
                                <div>

                                <Radio
                                    checked={value === i}
                                    onClick={handleChangeRadio}
                                    value={i}
                                    aria-label={m.mention_text}
                                />{' '}{m.mention_text}</div>
                                    )
                                    }

                        </div>

                    </DialogContentText>}
            </DialogContent>
            <DialogActions>
                <Button onClick={(e)=>{handleClose(e)}}>No</Button>
                {(MentionsInvolved.length === 1 || SelectedMention) ? <Button onClick={(e)=>DeleteMention(e,SelectedMention,props.position)}>Confirm</Button> :
                <Button onClick={(e)=> {
                    e.preventDefault();
                    e.stopPropagation()
                    console.log(value, MentionsInvolved[value])
                    SetSetSelectedMention(MentionsInvolved[value])
                }}>Yes</Button>}

            </DialogActions>
        </Dialog>
    );
}