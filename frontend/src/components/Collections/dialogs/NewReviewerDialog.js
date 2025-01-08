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


function NewReviewerDialog(props){


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
                {props.type === 'reviewer' && <>New reviewers</>}
                {props.type === 'admin' && <>New admins</>}            </DialogTitle>
            <DialogContent>

                {props.type === 'reviewer' && <h6>Select the reviewer</h6>}
                {props.type === 'admin' && <h6>Select the admins</h6>}
                {props.type === 'reviewer' && <div>Reviewers can be set only once</div>}

                    {(props.collection.creator === Username ||(props.annotators && props.annotators.indexOf(Username) !== -1)) &&
                        <Autocomplete
                        id="checkboxes-tags-demo"
                        sx={{marginTop: '10px', width: '100% !important'}}
                        options={props.members.map(opt=>opt.username)}
                        multiple
                        //getOptionLabel={(option) => option}
                        value={props.annotators}
                        onChange={(event, newValue) => {
                            // Extract usernames from the selected values and update the state
                            const selectedUsernames = newValue.map(option => option);
                            props.setannotators(selectedUsernames);
                        }}

                        style={{width: 500}}
                        renderInput={(params) => (
                            <TextField {...params} label="Members" placeholder="Members"/>
                        )}
                    />}


                {props.loading ? <div>
                    <div className='loading'><CircularProgress /></div>
                </div>: <div></div>}

            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>No</Button>
                 <Button onClick={props.confirm} autoFocus>
                    Confirm
                </Button>
            </DialogActions>
        </Dialog>
    );

}
export default NewReviewerDialog