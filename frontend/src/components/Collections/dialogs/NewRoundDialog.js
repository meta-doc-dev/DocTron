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
import {CircularProgress} from "@mui/material";


function DeleteMemberDialog(props){
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
                Create a new round?
            </DialogTitle>
            <DialogContent>
                This action will duplicate the collection and its annotation. This will be done for each new round. Each round will start with the annotations
                of the previous one.
                {props.loading ? <div>
                    <div className='loading'><CircularProgress /></div>
                </div>: <div></div>}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>No</Button>
                <Button onClick={props.createRound} autoFocus>
                    Yes
                </Button>
            </DialogActions>
        </Dialog>
    );

}
export default DeleteMemberDialog