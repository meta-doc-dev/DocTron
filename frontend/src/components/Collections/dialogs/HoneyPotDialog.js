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
import Autocomplete from "@mui/material/Autocomplete";
import Checkbox from "@mui/material/Checkbox";

import TextField from '@mui/material/TextField';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;
function HoneyPotDialog(props){


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
                Create honeypot
            </DialogTitle>
            <DialogContent>
                Select some (or all) documents which will be shared across all the members of the collection.
                All the members will annotate these documents. No member is aware of the documents added to the hnoeypot.
                <Autocomplete
                    multiple
                    id="checkboxes-tags-demo"
                    sx={{marginTop: '10px', width: '100% !important'}}
                    options={props.documents}
                    disableCloseOnSelect
                    onChange={(event, value) => {
                        let users = []
                        value.map(e=>users.push(e))
                        props.sethoneypot(users)
                    }}

                    getOptionLabel={(option) => option.id}
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
                                {option.id}
                            </li>
                        );
                    }}
                    style={{ width: 500 }}
                    renderInput={(params) => (
                        <TextField {...params} label="Honeypot" placeholder="Honeypot" />
                    )}
                />

             {/*   {props.loading ? <div>
                    <div className='loading'><CircularProgress /></div>
                </div>: <div></div>}*/}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>Back</Button>
                <Button onClick={props.createpot} autoFocus>
                    Ok
                </Button>
            </DialogActions>
        </Dialog>
    );

}
export default HoneyPotDialog