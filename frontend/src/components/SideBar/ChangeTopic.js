import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';
import RemoveIcon from '@mui/icons-material/Remove';
import axios from "axios";
import {ButtonGroup} from "@mui/material";
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

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import AddIcon from '@mui/icons-material/Add';
import Paper from "@mui/material/Paper";
import {styled} from '@mui/material/styles';
import {createTheme, ThemeProvider} from '@mui/material/styles';
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


export default function ChangeTopic(props) {
    const {collection, topic, topics} = useContext(AppContext);
    const [TopicsList, SetTopicsList] = topics
    const [Topic, SetTopic] = topic


    const changeTopic = (e) => {
        e.preventDefault()
        e.stopPropagation()
        axios.post('topic', {'topic': e.target.id})
            .then(r => {
                SetTopic(e.target.id)
            })
    }


    return (
        <div>
            <h5 className='inline_block'>
                Topics {' '}
            </h5>


            {TopicsList ?
                <div className={'documents'}>
                    <div className='coll_docs' style={{fontSize: '0.9rem'}}>

                        {TopicsList && TopicsList.length > 0 && <div>{TopicsList.map(topic => <div className={'doc_id_link'}>
                            {topic.query_id === Topic.toString() ?
                                <span id={topic.query_id} style={{fontWeight: 'bold'}}
                                      onClick={changeTopic}>{topic.query_id}</span> :
                                <span onClick={changeTopic} id={topic.query_id}>{topic.query_id}</span>}


                        </div>)}</div>}


                    </div>
                </div>


                : <div className='loading'>
                    <CircularProgress/>
                </div>}


        </div>
    );
}