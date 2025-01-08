import Button from "@mui/material/Button";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Alert from "@mui/material/Alert";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import {CircularProgress} from "@mui/material";
import Checkbox from "@mui/material/Checkbox";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import {AppContext} from "../../../App";


function ReviseDialog(props){


    const { username } = useContext(AppContext);

    const [Username,SetUsername] = username

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
                Revise collection
            </DialogTitle>
            <DialogContent>
                <>You will have assigned a set of annotations to review.</>
                <hr/>

                {props.loading ? <div>
                    <div className='loading'><CircularProgress /></div>
                </div>: <div></div>}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>No</Button>
                <Button onClick={props.revise} autoFocus>
                    Start revising
                </Button>

            </DialogActions>
        </Dialog>
    );

}
export default ReviseDialog