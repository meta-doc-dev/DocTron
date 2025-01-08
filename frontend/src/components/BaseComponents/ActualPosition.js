import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import TopicIcon from '@mui/icons-material/Topic';
import ArticleIcon from '@mui/icons-material/Article';
import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
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

function handleClick(event) {
    event.preventDefault();
    console.info('You clicked a breadcrumb.');
}

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
    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments
    const [Doc,SetDoc] = useState(null)
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

    return(
        <div className='inline'>
            {CollectionDescription && Doc && DocumentID && Topic&& <div role="presentation">
                <div role="presentation" onClick={handleClick}>
                    <Breadcrumbs aria-label="breadcrumb">
                         <StyledBreadcrumb
                            ccomponent="div"
                            label={`Task: ${Task}`}
                            icon={<FlagIcon fontSize="small"/>}/>
                        <StyledBreadcrumb
                            component="div"
                            label={`Collection: ${CollectionDescription}`}
                            icon={<CollectionsIcon fontSize="small"/>}
                        />
                        <StyledBreadcrumb
                            ccomponent="div"
                              onClick={()=>console.log('topic')}
                              label={`Topic: ${Topic}`}
                              icon={<TopicIcon fontSize="small"/>}/>
                        <StyledBreadcrumb
                            component="div"
                            label={`Doc: ${Doc}`}
                            icon={<ArticleIcon fontSize="small"/>}
                            onClick={()=>SetShowDocs(prev=>!prev)}
                        />
                    </Breadcrumbs>
                </div>


            </div>}


            {/*<span style={{display:'inline-block'}}><h3>{props.collection_name}</h3></span >&nbsp;&nbsp;{bull}&nbsp;&nbsp;<span style={{display:'inline-block'}}><h4>{props.document_id}</h4></span>*/}
            {/*<span style={{display:'inline-block'}}><h3>Collection name</h3></span >&nbsp;&nbsp;/&nbsp;&nbsp;<span style={{display:'inline-block'}}><h4>Doc id</h4></span>*/}
        </div>
    );
}