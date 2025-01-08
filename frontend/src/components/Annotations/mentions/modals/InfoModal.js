import {Col, Row} from "react-bootstrap";

import axios from "axios";
import {ButtonGroup, Dialog, DialogActions, DialogContent} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import {AppContext} from "../../../../App";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContentText from "@mui/material/DialogContentText";
import Button from "@mui/material/Button";
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;




export default function InfoModal(props) {

    const {
            mentions,modality

    } = useContext(AppContext);

    const [MentionsList, SetMentionsList] = mentions


    const [MentionsInvolved,SetMentionsInvolved] = useState([])
    const [value,SetValue] = useState(0)
    const [SelectedMention,SetSetSelectedMention] = useState(false)
    const [Info,SetInfo] = useState(false)
    const [Modality,SetModality] = modality

    useEffect(()=>{
        if(SelectedMention){
            axios.get('mentions/info',{params:{mention:SelectedMention}})
                .then(response=>SetInfo(response.data))
                .catch(error=>        props.setshow(false)
                )
        }
    },[SelectedMention])

    function handleChangeRadio(e){
        e.preventDefault()
        e.stopPropagation()
        let v = e.target.value
        SetValue(parseInt(v))
    }

    function handleClose(e){
        e.stopPropagation()
        e.preventDefault()
        props.setshow(false)
    }

    useEffect(()=>{
        let mentions = []

        props.mention.mentions.split(' ').map(m=>{
            console.log(m,MentionsList)
            mentions.push(MentionsList.filter(x=>x['mentions'] === m)[0])
        })
        SetMentionsInvolved(mentions)
        console.log(mentions)
        if(mentions.length === 1){
            SetSetSelectedMention(mentions[0])
        }

    },[props.mention])


    return (
        <Dialog
            open={props.show}
            onClose={handleClose}
            maxWidth={'sm'}
            fullWidth={'sm'}
        >
            <DialogTitle id="alert-dialog-title">
                {Info['text']}
            </DialogTitle>
            <DialogContent>
                {SelectedMention ? <DialogContentText id="alert-dialog-description">
                    {Info && <>
                        {/*<h5></h5>*/}
                        <div >
                            <Row>
                                <Col md={4}>Last update:</Col>
                                <Col md={8}>{Info['last_update']}</Col>
                            </Row>
                            {Modality !== 1 && <Row>
                                <Col md={4}>Mention annotators:</Col>
                                <Col md={8}>{Info['annotators_count']}</Col>
                            </Row>}
                        </div><hr/>
                        {Info['concepts'].length > 0 && <>
                            <h6>Concepts</h6>
                            {Info['concepts'].map(concept=><>
                                <div>
                                    <Row>
                                        <Col md={4}>Url:</Col>
                                        <Col md={8}>{concept.concept_url}</Col>
                                    </Row>
                                    <Row>
                                        <Col md={4}>Name:</Col>
                                        <Col md={8}>{concept.concept_name}</Col>
                                    </Row>
                                    <Row>
                                        <Col md={4}>Area:</Col>
                                        <Col md={8}>{concept.concept_area}</Col>
                                    </Row>
                                    <Row>
                                        <Col md={4}>Last update:</Col>
                                        <Col md={8}>{concept.last_update}</Col>
                                    </Row>
                                    <Row>
                                        <Col md={4}>Concept annotators:</Col>
                                        <Col md={8}>{concept.annotators_count}</Col>
                                    </Row>
                                </div><hr/>


                            </>)}
                        </>}

                    </>}


                </DialogContentText> :
                    <DialogContentText id="alert-dialog-description">
                        Select a mention
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
                <Button onClick={(e)=>{handleClose(e)}}>Close</Button>
                {(MentionsInvolved.length > 1 || !SelectedMention) &&
                    <Button onClick={(e)=> {
                        e.preventDefault();
                        e.stopPropagation()
                        SetSetSelectedMention(MentionsInvolved[value])
                    }}>Confirm</Button>}
            </DialogActions>
        </Dialog>
    );
}