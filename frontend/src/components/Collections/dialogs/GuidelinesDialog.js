import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import BorderColorIcon from "@mui/icons-material/BorderColor";
import BarChartIcon from "@mui/icons-material/BarChart";
import DownloadIcon from "@mui/icons-material/Download";
import {CollectionsBookmarkOutlined} from "@mui/icons-material";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Alert from "@mui/material/Alert";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import {CircularProgress, TextField} from "@mui/material";
import axios from "axios";


function GuidelinesDialog(props){
    const [Guidelines,SetGuidelines]=useState(null);

    useEffect(()=>{
        axios.get('guidelines',{params:{collection_id:props.id}})
            .then(response=>SetGuidelines(response.data['guidelines']))
    },[])

    function addGuidelines(e) {
        e.preventDefault();
        if(props.admin){
            axios.post('guidelines',
                {
                    collection_id: props.id,
                    guidelines: document.getElementById('guidelines').value
                }
            )
                .then(response => {
                    props.handleClose()

                })
                .catch(error => {
                    console.log(error)
                })
        }


    }


    return(
        <Dialog
            open={props.open}
            fullWidth
            maxWidth='md'
            onClose={props.handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                Guidelines for collection: {props.name}
            </DialogTitle>
            <DialogContent>
                <div>{props.admin ? <>Add a set of guidelines.</> : <>Read the guidelines before the annotation</>}</div>
                {props.admin ? <TextField
                    id="guidelines"
                    label="Guidelines"
                    sx={{'width': '100%',margin:'10px'}}
                    onChange={() => {
                        SetGuidelines(document.getElementById("guidelines").value)
                    }}
                    multiline
                    rows={10}
                    placeholder="Add guidelines"
                    value={Guidelines}
                /> : <div style={{margin:'10px'}}>{Guidelines}</div>}

            </DialogContent>
            {props.admin === true && <DialogActions>
                <Button color='error' onClick={props.handleClose}>Close</Button>
                <Button onClick={addGuidelines} autoFocus>
                    Yes
                </Button>
            </DialogActions>}
        </Dialog>
    );

}
export default GuidelinesDialog