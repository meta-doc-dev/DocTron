import Button from "@mui/material/Button";
import TopicIcon from '@mui/icons-material/Topic';
import ArticleIcon from '@mui/icons-material/Article';
import axios from "axios";
import {ButtonGroup, Dialog, DialogActions, DialogContent} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import Breadcrumbs from "@mui/material/Breadcrumbs";
import Link from "@mui/material/Link";
import {emphasize} from "@mui/material";
import {styled} from "@mui/material/styles";
import Chip from "@mui/material/Chip";
import * as PropTypes from "prop-types";
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import FlagIcon from '@mui/icons-material/Flag';
import CollectionsIcon from '@mui/icons-material/Collections';
import DialogTitle from "@mui/material/DialogTitle";
import DialogContentText from "@mui/material/DialogContentText";
import EditIcon from "@mui/icons-material/Edit";
import {AppContext} from "../../../App";



const StyledBreadcrumb = styled(Chip)(({ theme }) => {
    const backgroundColor =
        theme.palette.mode === 'light'
            ? theme.palette.grey[100]
            : theme.palette.grey[800];
    return {
        backgroundColor,
        height: theme.spacing(3),
        color: theme.palette.text.primary,
        fontWeight: theme.typography.fontWeightRegular,
        '&:hover, &:focus': {
            backgroundColor: emphasize(backgroundColor, 0.06),
        },
        '&:active': {
            boxShadow: theme.shadows[1],
            backgroundColor: emphasize(backgroundColor, 0.12),
        },
    };
}); // TypeScript only: need a type cast here because https://github.com/Microsoft/TypeScript/issues/26591


function HomeIcon(props) {
    return null;
}

HomeIcon.propTypes = {fontSize: PropTypes.string};
export default function CommentDialog(props){
    const { collection,document_id,collectiondocuments,topic,showdocs,task } = useContext(AppContext);

    const [Comment,SetComment] = useState(null)



    const handleClose = () => {
        props.setopen(false)
    };

    useEffect(() => {
        if (props.mention && props.mention.mention_text) {
            delete props.mention.mention_text;
        }
        axios.get('labels/comment',{params:{label:props.label,mention:props.mention,points:props.points}})
            .then(response=>{

                SetComment(response.data['comment'])
            })



    }, [props.label]);


    function uploadComment(){
        var comment = document.getElementById("comment").value
        if (props.type === 'label'){
            axios.post('labels/comment',{label:props.label,comment:comment,type:'label'})
                .then(response=>{

                    props.setopen(false)
                })
        }else if(props.type === 'passage'){
            axios.post('labels/comment',{label:props.label,comment:comment,mention:props.mention,type:'passage'})
            .then(response=>{

                props.setopen(false)
            })
        }
        else if(props.type === 'obj'){
            axios.post('labels/comment',{label:props.label,comment:comment,points:props.points,type:'object'})
                .then(response=>{

                    props.setopen(false)
                })
        }

    }

    return(

            <Dialog
                open={props.open}
                onClose={handleClose}
                maxWidth={'lg'}
                sx={{width:'100%'}}


            >
               <DialogTitle>Leave a comment about your annotation</DialogTitle>
                <DialogContent>
                    <DialogContentText>

                    </DialogContentText>
                    <div>
                        <TextField           multiline
                                             rows={4} id="comment" sx={{margin:'10px 0',width:'100%'}} label="Comment" variant="outlined" />

                        {Comment && <><h5>Your comment:</h5>
                            <div>{Comment}</div>
                        </>}
                        </div>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>




    );
}