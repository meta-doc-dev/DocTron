import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';
import RemoveIcon from '@mui/icons-material/Remove';
import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import AddIcon from '@mui/icons-material/Add';
import Paper from "@mui/material/Paper";
import { styled } from '@mui/material/styles';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import {AppContext} from "../../App";
import IconButton from "@mui/material/IconButton";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
import TuneSharpIcon from "@mui/icons-material/TuneSharp";
import FilterAltIcon from '@mui/icons-material/FilterAlt';

import FilterDocumentComponent from "./FilterDocumentComponent";
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import {CSSTransition} from "react-transition-group";
import './sidebar.css'


export default function ChangeDocumentComppnent({displayDocs,setDisplayDocs}){
    const { collection,document_id,labels, role,modality,collectiondocuments,mentions,concepts,relationshipslist,annotatedlabels } = useContext(AppContext);
    const [Collection,SetCollection] = collection
    const [DocumentID,SetDocumentID] = document_id
    const [Modality,SetModality] = modality
    const [ShowSearch,SetShowSearch] = useState(false)
    const [Role,SetRole] = role



    useEffect(()=>{
        // change role returns a list of documents accordine to role
        if(Role){
            axios.get('change_role',{params:{role:Role}})
                .then(response=>{
                    let docs = response.data['documents']
                    setDisplayDocs(docs)
                })
        }

    },[])


    const changeDoc = (e) =>{
        e.preventDefault()
        e.stopPropagation()
        axios.post('update_document_id',{'document':e.target.id})
            .then(r=>{
                SetDocumentID(e.target.id)
            })
    }



    const handleSearch = (e) => {
        e.preventDefault()
        e.stopPropagation()

        SetShowSearch(prev => !prev)
    }

    return(
        <div>
            <h5 className='inline_block'>
                Documents {' '}
            </h5>
            {displayDocs && <div style={{float:'right', marginRight:'20px'}}>
                <IconButton sx={{padding:0}}  onClick={handleSearch} component="span" >
                    <FilterAltIcon />
                </IconButton>{' '}

            </div>}

            <CSSTransition in={ShowSearch} timeout={500} classNames="filterclass" appear >
                <div>{ ShowSearch && <FilterDocumentComponent displayDocs = {displayDocs} setDisplayDocs={setDisplayDocs} />}</div>
            </CSSTransition>


            {displayDocs ?
                <div className={'documents'}>
                <div className='coll_docs' style={{fontSize:'0.9rem'}}>
                    Found: <i style={{fontSize:'0.9rem'}}>{displayDocs.filter(d => (d['split'] === 'yes' || d['split'] === 'all')).length} documents</i>
                <div><hr/>The documents assigned to you are the following:
                    <div>
                        {displayDocs.filter(d => (d['split'] === 'yes' || d['split'] === 'all')).map(doc =>
                            <div className={doc.annotated ? 'doc_id_link colored' : 'doc_id_link'}>
                                {doc.hashed_id === DocumentID ? <span id={doc.hashed_id} style={{fontWeight: 'bold'}}
                                                                      onClick={changeDoc}>{doc.id}</span> :
                                    <span onClick={changeDoc} id={doc.hashed_id}>{doc.id}</span>}

                            </div>
                        )}
                        <hr/>
                        <hr/><div>Documents assigned to other annotators:</div>
                    </div>

                </div>



                {Modality === 0 && displayDocs.filter(d=>d['split'] === 'no').map(doc=>
                    <div  className={doc.annotated ? 'doc_id_link colored' : 'doc_id_link'}>
                        {doc.hashed_id === DocumentID ? <span id={doc.hashed_id} style={{fontWeight:'bold'}}  onClick={changeDoc}>{doc.id}</span> : <span  onClick={changeDoc} id={doc.hashed_id}>{doc.id}</span>}

                        </div>
                )}</div>
                </div>
                : <div className='loading'>
                <CircularProgress />
            </div>}



        </div>
    );
}