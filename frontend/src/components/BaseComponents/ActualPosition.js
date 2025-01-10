import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import TopicIcon from '@mui/icons-material/Topic';
import ArticleIcon from '@mui/icons-material/Article';
import axios from "axios";
import {ButtonGroup, Dialog, DialogActions, DialogContent} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import {AppContext} from "../../App";
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
export default function ActualPosition(props){
    const { collection,document_id,collectiondocuments,topic,showdocs,task } = useContext(AppContext);
    const [Collection,SetCollection] = collection
    const [DocumentID,SetDocumentID] = document_id
    const [ShowDocs,SetShowDocs] = showdocs
    const [CollectionDescription,SetCollectionDescription] = useState(false)
    const [TopicComments,SetTopicComments] = useState([])
    const [DocumentsComments,SetDocumentsComments] = useState([])
    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments
    const [Doc,SetDoc] = useState(null)
    const [ShowCommentDoc,SetShowCommentDoc] = useState(null)
    const [ShowCommentTopic,SetShowCommentTopic] = useState(null)
    const [Topic,SetTopic] = topic
    const [Task,SetTask] = task

    useEffect(()=>{
        console.log('collection',Collection)
        if(Collection){
            axios.get('collections/name',{params:{collection:Collection}})
                .then(response=>{
                    SetCollectionDescription(response.data['name'])
                })
        }
    },[Collection])

    useEffect(()=>{
        if(CollectionDocuments && DocumentID){
            CollectionDocuments.map(doc=>{
                if(doc.hashed_id === DocumentID){
                    SetDoc(doc.id)
                }
            })
        }

    },[CollectionDocuments,DocumentID])


    const handleClose = () => {
        SetShowCommentDoc(false);
        SetShowCommentTopic(false);
    };

    useEffect(() => {

        axios.get('comment')
            .then(response=>{
                SetTopicComments(response.data['topic'])
                SetDocumentsComments(response.data['document'])
            })
    }, []);


    function uploadComment(){
        var commento = document.getElementById('commento').value
        var type = ''
        if(ShowCommentDoc){
            type = 'document'
        }else if(ShowCommentTopic){
            type = 'topic'
        }
        axios.post("comment",{comment:commento,type:type})
            .then(response=>{
                SetShowCommentDoc(false);
                SetShowCommentTopic(false);
            })
    }

    return(
        <div className='inline'>

            <Dialog
                open={ShowCommentDoc || ShowCommentTopic}
                onClose={handleClose}
                maxWidth={'lg'}
                sx={{width:'100%'}}


            >
                {ShowCommentTopic && <DialogTitle>Add a new comment for the topic: {Topic}</DialogTitle>}
                {ShowCommentDoc && <DialogTitle>Add a new comment for the document: {Doc}</DialogTitle>}
                <DialogContent>
                    <DialogContentText>
                        Write your comment below
                    </DialogContentText>
                    <div>


                        <TextField           multiline
                                             rows={4} id="commento" sx={{margin:'10px 0',width:'100%'}} label="Comment" variant="outlined" />

                        <h5>Other comments:</h5>
                        {ShowCommentTopic && TopicComments.map(comment=><div><b>{comment['username']}: </b><>{comment['comment']}</></div>)}
                        {ShowCommentDoc && DocumentsComments.map(comment=><div><b>{comment['username']}: </b><>{comment['comment']}</></div>)}
                    </div>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>

            {CollectionDescription && Doc && DocumentID && Topic&& <div role="presentation">
                <div role="presentation" >
                    <Breadcrumbs aria-label="breadcrumb">
               {/*          <StyledBreadcrumb
                            ccomponent="div"
                            label={`Task: ${Task}`}
                        />*/}
                        <StyledBreadcrumb
                            component="div"
                            label={`Collection: ${CollectionDescription}`}
                        />
                        <StyledBreadcrumb
                            ccomponent="div"
                            onClick={()=>SetShowCommentTopic(prev=>!prev)}
                            label={`Topic: ${Topic}`}
                            icon={<EditIcon fontSize="small"/>}
                        />
                        <StyledBreadcrumb
                            component="div"
                            label={`Doc: ${Doc}`}
                            onClick={()=>SetShowCommentDoc(prev=>!prev)}
                            icon={<EditIcon fontSize="small"/>}

                        />
                    </Breadcrumbs>
                </div>


            </div>}


          </div>
    );
}