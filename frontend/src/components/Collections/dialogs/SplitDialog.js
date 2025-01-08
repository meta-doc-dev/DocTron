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
            <DialogTitle id="alert-dialog-title">
                Split documents across members
            </DialogTitle>
            <DialogContent>
                Select some (or all) the members to assign the documents to. The entire collection will be equally split across all the selected members.
                If you plan to create the honeypot, please, first create the honeypot and then split in order have the same number of documents assigned to each annotator.
                <Autocomplete
                    multiple
                    id="checkboxes-tags-demo"
                    sx={{marginTop: '10px', width: '100% !important'}}
                    options={props.collection.members}
                    disableCloseOnSelect
                    onChange={(event, value) => {
                        let users = []
                        value.map(e=>users.push(e))
                        props.setmembers(users)
                    }}
                    /*onChange={(event, newValue) => {
                        props.members[1](newValue);
                    }}*/
                    getOptionLabel={(option) => option.username}
                    renderOption={(props, option, { selected }) => {
                        const { key, ...optionProps } = props;
                        return (
                            <li key={key} {...optionProps}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{ marginRight: 8 }}
                                    checked={selected}
                                />
                                {option.username}
                            </li>
                        );
                    }}
                    style={{ width: 500 }}
                    renderInput={(params) => (
                        <TextField {...params} label="Members" placeholder="Members" />
                    )}
                />

             {/*   {props.loading ? <div>
                    <div className='loading'><CircularProgress /></div>
                </div>: <div></div>}*/}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>Back</Button>
                <Button onClick={props.split} autoFocus>
                    Ok
                </Button>
            </DialogActions>
        </Dialog>
    );

}
export default SplitDialog