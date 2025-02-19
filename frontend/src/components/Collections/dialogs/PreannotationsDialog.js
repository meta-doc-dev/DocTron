import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Alert from "@mui/material/Alert";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import {CircularProgress, TextField} from "@mui/material";
import axios from "axios";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import {ThemeProvider} from "@mui/material/styles";
import Input from "@mui/material/Input";


function PreannotationsDialog(props){

    const [Files,setFiles]=useState(null);

    function AddFiles() {
        var input = document.getElementById('files_to_upload');
        // SetInpuLength(input.files.length)
        var files = []
        if (input.files[0] !== undefined || input.files[0] !== null) {
            for (let ind = 0; ind < input.files.length; ind++) {
                if (input.files[ind].name.endsWith('csv') || input.files[ind].name.endsWith('json')) {
                    files.push(input.files[ind])
                }
            }
        }
        setFiles(files)


    }

    function addPreannotations(){
        if(Files.length>0){
            var formData = new FormData();
            formData.append('id', props.collection.id);

            if (Files) {

                for (let ind = 0; ind < Files.length; ind++) {
                    formData.append('annotations_' + ind.toString(), Files[ind]);

                }

            }



            axios({
                method: "post",
                url: "uploadAnnotations",
                data: formData,
                headers: {"Content-Type": "multipart/form-data"},
            })

                .then(function (response) {
                    //handle success
                    props.handleClose();
                })
                .catch(function (response) {
                    //handle error
                    console.log(response);


                });


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
                Upload annotations for collection: {props.name}
            </DialogTitle>
            <DialogContent>
                <div>Upload annotations for documents in {props.annotation}. Download <Button>Here</Button> the template.</div>
                <div>
                    <label htmlFor="files_to_upload">
                        <Input accept="*" id="files_to_upload" onChange={() => {
                            AddFiles()
                        }} multiple type="file"/>
                            <Button sx={{marginTop: '15px'}} variant="contained" color='neutral_updload'
                                    component="span" startIcon={<UploadFileIcon/>}>
                                Upload annotations
                            </Button>
                    </label>
                    {Files &&
                        <>
                            {Files.length > 0 && <b>Uploaded documents files:</b>
                            }
                            {Files.map(file =>
                                <div>
                                    <span>{file.name}</span>{' '}<span><IconButton onClick={() => {
                                    let conc = Files.map(x => x)
                                    conc = conc.filter(x => x.name !== file.name)
                                    setFiles(conc)
                                }}><DeleteIcon/></IconButton></span>
                                </div>
                            )}
                        </>}
                </div>


            </DialogContent>
            {props.admin === true && <DialogActions>
                <Button color='error' onClick={props.handleClose}>Close</Button>
                <Button onClick={addPreannotations} autoFocus>
                    Yes
                </Button>
            </DialogActions>}
        </Dialog>
    );

}

export default PreannotationsDialog