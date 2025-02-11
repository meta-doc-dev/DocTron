import {Col, Row} from "react-bootstrap";

import axios from "axios";
import {ButtonGroup} from "@mui/material";
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
import Suggestions from "./Suggestions";



export default function CommentModal(props) {

    const {
        username,
        users,
        tags_split,
        document_id,
        concepts,
        collection,
        mentions,documentdescription,
        mentiontohighlight,
        startrange,
        endrange
    } = useContext(AppContext);

    const [MentionsInvolved,SetMentionsInvolved] = useState([])
    const [value,SetValue] = useState(0)
    const [SelectedMention,SetSetSelectedMention] = useState(false)
    const [MentionToHighlight, SetMentionToHighlight] = mentiontohighlight
    const [DocumentID, SetDocumentID] = document_id
    const [Collection, SetCollection] = collection
    const [MentionsList, SetMentionsList] = mentions
    const [Comment, SetComment] = useState("")
    const [End, SetEnd] = endrange
    const [ConceptsList, SetConceptsList] = concepts
    const [ShowAddConceptModal, SetShowAddConceptModal] = useState(false)
    const [contextMenu, setContextMenu] = useState(null);
    const inputEl = useRef(null);
    const [DocumentDesc,SetDocumentDesc] = documentdescription
    const [Loading,SetLoading] = useState(false)
    const [TagsSplitted,SetTagsSplitted] = tags_split


    useEffect(() => {
        if(SelectedMention){
            axios.get("mentions/comment",{params:{start:SelectedMention.start,position:props.position,stop:SelectedMention.stop,mention_text:SelectedMention.mention_text}})
                .then(response=>SetComment(response.data['comment']))
        }
    }, [SelectedMention]);


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


    function commentPassage(e,mention,position){
        e.preventDefault()
        e.stopPropagation()
        SetLoading(true)
        var comment = document.getElementById("comment").value

        axios.post('mentions/comment',{start:SelectedMention.start,position:position,stop:SelectedMention.stop,comment:comment})
            .then(response=>{
                props.setshow(false)
                SetLoading(false)

            })
    }




    function handleClose(e){
        e.stopPropagation()
        e.preventDefault()
        props.setshow(false)
    }
    function handleChangeRadio(e){
        e.preventDefault()
        e.stopPropagation()
        let v = e.target.value
        SetValue(parseInt(v))


    }


    return (
        <Dialog
            open={props.show}
            onClose={handleClose}
            maxWidth={'sm'}
            fullWidth={'sm'}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >

            <DialogTitle id="alert-dialog-title">
            </DialogTitle>
            {Loading === false && <DialogContent>
                {SelectedMention  ? <DialogContentText id="alert-dialog-description">

                        <div>
                            <h4>Comment passage</h4>

                            <TextField multiline
                                       rows={4} id="comment" sx={{margin: '10px 0', width: '100%'}} label="Comment"
                                       variant="outlined"/>

                            {Comment && <><h5>Your comment:</h5>
                                <div>{Comment}</div>
                            </>}
                        </div>


                    </DialogContentText> :
                    <DialogContentText id="alert-dialog-description">
                        <h4>Select passage</h4>
                        Which passage do you want to select?
                        <div>
                            {MentionsInvolved.map((m, i) =>
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

                    </DialogContentText>
                }
            </DialogContent>}
            {Loading === false && <DialogActions>
                <Button onClick={(e) => {
                    handleClose(e)
                }}>No</Button>
                {(MentionsInvolved.length === 1 || SelectedMention) ?
                    <Button onClick={(e) => commentPassage(e, SelectedMention, props.position)}>Confirm</Button> :
                    <Button onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation()
                        SetSetSelectedMention(MentionsInvolved[value])
                    }}>Yes</Button>}

            </DialogActions>}
        </Dialog>
    );
}