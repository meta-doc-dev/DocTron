import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import BorderColorIcon from "@mui/icons-material/BorderColor";
import BarChartIcon from "@mui/icons-material/BarChart";
import DownloadIcon from "@mui/icons-material/Download";
import {CollectionsBookmarkOutlined} from "@material-ui/icons";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Alert from "@mui/material/Alert";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import {CircularProgress} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import Checkbox from "@mui/material/Checkbox";

import TextField from '@mui/material/TextField';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;
function SplitDialog(props){

/*    const [Members, SetMembers] = useState([])
    useEffect(()=>{
        let members = []
        props.collection.members.map(m=>{
            members.push({'username':m})
        })
        SetMembers(members)
    },[props.collection.members])*/


    return(
        <Dialog
            open={props.open}
            fullWidth
            maxWidth='md'
            onClose={props.handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >

            <DialogContent>
                {!props.loading ? <div>
                    <h5>Split documents and topics across members</h5>
                    The entire collection can be distributed among its members, splitting the documents (or topics) into equal portions so that each user is assigned a unique set of documents (or topics).
                    If only documents are split, each user will evaluate a subset of documents across all topics. If only topics are split, each user will evaluate all documents on a subset of topics. If both documents and topics are split, each user will evaluate a subset of documents on a subset of topics.
                    Reviewer(s) and admin(s) are excluded.
                    <FormGroup>
                        <FormControlLabel onChange={()=>props.set_topic(prev=>!prev)} control={<Checkbox />} label="Topics" />
                        <FormControlLabel onChange={()=>props.set_doc(prev=>!prev)} control={<Checkbox />} label="Documents" />
                    </FormGroup>


                </div> : <div className='loading'>
                    <CircularProgress/>
                </div>}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>Back</Button>
                <Button disaled={props.loading} onClick={props.split} autoFocus>
                    Ok
                </Button>
            </DialogActions>
        </Dialog>
    );

}

export default SplitDialog