import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';
import RemoveIcon from '@mui/icons-material/Remove';
import axios from "axios";
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
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

import UploadFileIcon from '@mui/icons-material/UploadFile';
import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {
    faChevronLeft, faPalette,
    faChevronRight, faExclamationTriangle,
    faGlasses,
    faInfoCircle,
    faList, faPlusCircle,
    faProjectDiagram, faArrowLeft, faArrowRight, faTrash, faSave, faFileInvoice
} from "@fortawesome/free-solid-svg-icons";
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import DocumentToolBar from "../Document/ToolBar/DocumentToolBar";
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
// const label = { inputProps: { 'aria-label': 'Checkbox demo' } };
import CircleOutlinedIcon from '@mui/icons-material/CircleOutlined';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
export default function DownloadDocument(props){
    const { collection,document_id,users,username, annotationtype,topic,showfilter,fields,fieldsToAnn,expand } = useContext(AppContext);
    const [Collection,SetCollection] = collection
    const [DocumentID,SetDocumentID] = document_id
    const [Username,SetUsername] = username
    const [Topic,SetTopic] = topic
    const [Batch,SetBatch] = useState(false)
    const [FormatValue,SetFormatValue] = useState('json')
    const [AnnotatorValue,SetAnnotatorValue] = useState(Username)
    const [AnnotationType, SetAnnotationType] = annotationtype
    const [AnnotationValue,SetAnnotationValue] = useState(AnnotationType)
    const [DocumentsValue,SetDocumentsValue] = useState(DocumentID)
    const [TopicValue,SetTopicValue] = useState(Topic)
    const [BatchValue,SetBatchValue] = useState(1)
    const [UsersList,SetUsersList] = users
    const [Admins,SetAdmins] = useState([])
    var FileDownload = require('js-file-download');

    useEffect(()=>{

        let max_batch = 0
        axios.get('get_batches')
            .then(response=> {
                console.log('response',response.data['max_batch'])
                max_batch = response.data['max_batch']
                SetBatch(max_batch)
            })
            .catch(e=>console.log(e))
        axios.get('collections/users',{params:{collection:Collection}})
            .then(response=>{
                SetUsersList(response.data['members'])
                SetAdmins(response.data['admins'])
            })
            .catch(error=>{
                console.log('error',error)

            })


    },[])

    useEffect(()=>{
        if(Username){
            SetAnnotatorValue(Username)
        }
        if(DocumentID){
            SetDocumentsValue(DocumentID)
        }
    },[Username,DocumentID])


    function downloadAnnotations(e){
        e.preventDefault()
        e.stopPropagation()
        axios.get('download_annotations', {
            params: {
                format: FormatValue,
                annotators: AnnotatorValue,
                annotation: AnnotationValue,
                document: DocumentsValue,
                topic: TopicValue,
                batch:BatchValue,
            }
        })
            .then(function (response) {
                console.log('message', response.data);
                let filename = AnnotationValue + '.'+FormatValue.toLowerCase()
                if(FormatValue.toLowerCase() === 'trec'){
                    filename = AnnotationValue + '.qrels'
                }
                if(FormatValue === 'json'){
                    FileDownload(JSON.stringify(response.data,null,4), filename);

                }else{
                    FileDownload((response.data), filename);

                }


            })
            .catch(function (error) {

                console.log('error message', error);
            });


    }

    return(
        <div className='download'>


            <h5>Download</h5>
            <div className='selectclass'>
                <FormControl fullWidth>
                    <InputLabel id="format">Format</InputLabel>
                    <Select
                        labelId="format"
                        id="format"
                        value={FormatValue}
                        variant={'outlined'}
                        sx={{width: '100%'}}
                        label="Format"
                        size={'small'}

                        onChange={(e) => {
                            SetFormatValue(e.target.value)
                        }}
                    >

                        <MenuItem value={'json'}>JSON</MenuItem>
                        <MenuItem value={'csv'}>CSV</MenuItem>
                        {['Graded labeling', 'Passage annotation'].indexOf(AnnotationType) !== -1 &&
                            <MenuItem value={'trec'}>TREC-like</MenuItem>}

                    </Select></FormControl>
            </div>
            <div className='selectclass'>
                <FormControl fullWidth>
                    <InputLabel id="format">Topic</InputLabel>
                    <Select
                        labelId="topic"
                        id="topic"
                        value={TopicValue}
                        variant={'outlined'}
                        sx={{width: '100%'}}
                        label="Topic"
                        size={'small'}

                        onChange={(e) => {
                            SetTopicValue(e.target.value)
                        }}
                    >

                        <MenuItem value={Topic}>This topic</MenuItem>
                        <MenuItem value={'all'}>All topics</MenuItem>


                    </Select></FormControl>
            </div>
            <div className='selectclass'><FormControl fullWidth>
                <InputLabel id="doc">Documents</InputLabel>
                <Select
                    labelId="doc"
                    id="format_select"
                    size={'small'}
                    variant={'outlined'}

                    value={DocumentsValue}
                    sx={{width: '100%'}}
                    label="Documents"
                    onChange={(e) => {
                        SetDocumentsValue(e.target.value)
                    }}
                >

                    <MenuItem value={DocumentID}>This document</MenuItem>
                    <MenuItem value={'all'}>All collection</MenuItem>

                </Select></FormControl>
            </div>

            {DocumentsValue === 1 && Batch > 0 && <div className='selectclass'><FormControl fullWidth>
                <InputLabel id="doc">Batch</InputLabel>
                <Select
                    labelId="doc"
                    id="format_select"
                    value={BatchValue}
                    sx={{width: '100%'}}
                    size={'small'}

                    label="Batch"
                    onChange={(e) => {
                        SetBatchValue(e.target.value)
                    }}
                    variant={'outlines'}>

                    {Array.from({length: parseInt(Batch)}, (v, k) => k + 1).map(batch =>
                        <MenuItem value={parseInt(batch)}>{batch.toString()}</MenuItem>)}
                    <MenuItem value={'all'}>All batches</MenuItem>

                </Select></FormControl>
            </div>}


            {UsersList && Admins && Admins.indexOf(Username) !== -1 &&
                <div className='selectclass'><FormControl fullWidth>
                    <InputLabel id="annotator">Annotator</InputLabel>
                    <Select
                        labelId="annotator"
                        id="format_select"
                        value={AnnotatorValue}
                        sx={{width: '100%'}}
                        label="Annotator"
                        size={'small'}
                        onChange={(e) => {
                            SetAnnotatorValue(e.target.value)
                        }}
                        variant={'outlined'}>

                        <MenuItem value={Username}>{Username}</MenuItem>
                        {UsersList.map(u => <MenuItem value={u.username}>{u.username}</MenuItem>)}


                        <MenuItem value={'IAA-Inter Annotator Agreement'}>IAA-Inter Annotator Agreement</MenuItem>
                        <MenuItem value={'all'}>All</MenuItem>

                    </Select></FormControl>
                </div>}
            <Button className='selectclass' onClick={downloadAnnotations} variant="contained">Download</Button>


        </div>
    );
}