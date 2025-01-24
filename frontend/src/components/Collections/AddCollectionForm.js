import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";

import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import Chip from '@mui/material/Chip';

import './collection.css'

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import UploadIcon from '@mui/icons-material/Upload';

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Fade from '@mui/material/Fade';

import IconButton from '@mui/material/IconButton';
import Collapse from "@material-ui/core/Collapse";
import Checkbox from '@mui/material/Checkbox';
import Paper from "@mui/material/Paper";
import {styled} from '@mui/material/styles';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {CollectionContext} from "./CollectionsList";
import {AppContext} from "../../App";
import {forEach} from "react-bootstrap/ElementChildren";
import {CircularProgress} from "@mui/material";
import FileDownload from "js-file-download";
import FormControlLabel from "@mui/material/FormControlLabel";

export default function AddCollectionForm() {
    const {addcollection, updatecollection} = useContext(CollectionContext);
    const {users, annotationtypes,annotationtype, username, snackmessage, opensnack} = useContext(AppContext);
    const [SnackMessage, SetSnackMessage] = snackmessage;
    const [OpenSnack, SetOpenSnack] = opensnack
    const [AddCollection, SetAddCollection] = addcollection
    const [Description, SetDescription] = useState('')
    const [Title, SetTitle] = useState('')
    const [PubmedId, SetPubmedId] = useState('')
    const [SemanticID, SetSemanticID] = useState('')
    const [OpenAIREId, SetOpenAIREId] = useState('')
    const [ShowAreaPubmed, SetShowAreaPubmed] = useState(false)
    const [Topics, SetTopics] = useState([])
    const [Qrels, SetQrels] = useState([])
    const [Users, SetUsers] = users
    const [TagsToAdd, SetTagsToAdd] = useState([])
    const [Username, SetUsername] = username
    const [SelectedMembers, SetSelectedMembers] = useState([])
    const [UpdateCollection, SetUpdateCollection] = updatecollection
    const [ShowDocumentsUpload, SetShowDocumentsUpload] = useState(true)
    const [ShowError, SetShowError] = useState(false)
    const [Files, SetFiles] = useState([])
    const [OpenAIREFiles, SetOpenAIREFiles] = useState([])
    const [PubmedFiles, SetPubmedFiles] = useState([])
    const [SemanticFiles, SetSemanticFiles] = useState([])
    const [ConceptsFiles, SetConceptsFiles] = useState([])
    const [options, SetOptions] = useState([])
    var FileDownload = require('js-file-download');
    const [Loading, SetLoading] = useState(false)
    const [AddLabel, SetAddLabel] = useState([1, 2, 3])
    const [AddLabelPassage, SetAddLabelPassage] = useState([1, 2, 3])
    const [AddTag, SetAddTag] = useState([1, 2, 3])
    const [AddMember, SetAddMember] = useState([1, 2, 3])
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [AnnotationType, SetAnnotationType] = annotationtype

    //const [Task, SetTask] = task
    const [isChecked, SetisChecked] = useState(false)
    const [isCheckedQ, SetisCheckedQ] = useState(false)
    const [IRDataset, SetIRDataset] = useState("")
    //const [AllTypes] = useState(['Entity tagging', 'Labels annotation', 'Passages annotation', 'Entity linking', 'Relationships annotation', 'Facts annotation'])

/*    useEffect(() => {
        var types = []
        if (Task === 'Deep learning') {
            types = ['Labels annotation']

        } else if (Task === 'Ad hoc') {
            types = ['Labels annotation']

        } else if (Task === 'Question answering') {
            types = ['Passages annotation', 'Labels annotation', 'Entity tagging, Entity linking']

        } else if (Task === 'Conversational') {
            types = ['Passages annotation', 'Labels annotation']
        } else if (Task === 'Passages retrieval') {
            types = ['Passages annotation']
        } else if (Task === 'Entity retrieval') {
            types = ['Entity tagging, Entity linking']
        }
        SetAnnotationTypes(types)

    }, [Task])*/


    const handleChangeDesc = (event) => {
        SetDescription(event.target.value);
    };
    const handleChangeTitle = (event) => {
        SetTitle(event.target.value);
    };
    const handleChangePubmedId = (event) => {
        SetPubmedId(event.target.value);
    };
    const handleChangeIRDataset = (event) => {
        SetIRDataset(event.target.value);
    };

    useEffect(() => {
        if (!AddCollection) {
            clearFields()
        }
    }, [AddCollection])

    const clearFields = () => {
        SetDescription('')
        SetTitle('')
        SetSelectedMembers([])
        SetPubmedId('')
        // delete files
        DeleteFiles()


    }


    const theme = createTheme({
        palette: {
            neutral: {
                main: '#64748B',
                contrastText: '#fff',
            },
            neutral_pubmed: {
                main: '#0e2f44',
                contrastText: '#fff',
            },
            neutral_updload: {
                main: '#daa520',
                contrastText: '#fff',
            },
        },
    });
    const Input = styled('input')({
        display: 'none',
    });

    function AddFiles(type) {
        SetShowError(false)
        if (type === 'documents') {
            var input = document.getElementById('files_to_upload');
            // SetInpuLength(input.files.length)
            var files = []
            if (input.files[0] !== undefined || input.files[0] !== null) {
                for (let ind = 0; ind < input.files.length; ind++) {
                    if (input.files[ind].name.endsWith('csv') || input.files[ind].name.endsWith('json') || input.files[ind].name.endsWith('txt') || input.files[ind].name.endsWith('pdf') || input.files[ind].name.toLowerCase().endsWith('jpg') || input.files[ind].name.toLowerCase().endsWith('jpeg') || input.files[ind].name.toLowerCase().endsWith('png') || input.files[ind].name.toLowerCase().endsWith('pdf')) {
                        files.push(input.files[ind])
                    }
                }
            }
            SetFiles(files)
        } else if (type === 'topics') {
            var input = document.getElementById('topics_to_upload');
            // SetInpuLength(input.files.length)
            var files = []
            if (input.files[0] !== undefined || input.files[0] !== null) {
                for (let ind = 0; ind < input.files.length; ind++) {
                    if (input.files[ind].name.endsWith('json') || input.files[ind].name.toLowerCase().endsWith('jpg') || input.files[ind].name.toLowerCase().endsWith('jpeg')|| input.files[ind].name.toLowerCase().endsWith('png')|| input.files[ind].name.toLowerCase().endsWith('pdf')) {
                        files.push(input.files[ind])

                    }
                }

            }

            SetTopics(files)
        } else if (type === 'qrels') {
            var input = document.getElementById('qrels_to_upload');
            // SetInpuLength(input.files.length)
            var files = []
            if (input.files[0] !== undefined || input.files[0] !== null) {
                for (let ind = 0; ind < input.files.length; ind++) {
                    if (input.files[ind].name.endsWith('json')) {
                        files.push(input.files[ind])

                    }
                }

            }

            SetQrels(files)
        } else if (type === 'concepts') {
            SetShowError(false)
            var input = document.getElementById('concepts_to_upload');
            // SetInpuLength(input.files.length)
            var files = []
            if (input.files[0] !== undefined || input.files[0] !== null) {
                for (let ind = 0; ind < input.files.length; ind++) {
                    if (input.files[ind].name.endsWith('csv') || input.files[ind].name.endsWith('json')) {
                        files.push(input.files[ind])

                    }
                }
            }

            SetConceptsFiles(files)
        }

    }


    function DeleteFiles() {
        var input = document.getElementById('files_to_upload');
        if (input !== undefined && input !== null) {
            input.value = null

        }
        // SetInpuLength(false)
        SetFiles([])
        SetConceptsFiles([])
        SetPubmedFiles([])
        SetOpenAIREFiles([])
        SetSemanticFiles([])

    }

    function GetFiles(type) {
        var formData = new FormData();
        var files = []
        var type_coll = 'Textual'
        var type_topic = 'Textual'
        if (Files && (type === 'documents' || type === 'all')) {

            for (let ind = 0; ind < Files.length; ind++) {
                formData.append('document_' + ind.toString(), Files[ind]);
                if(Files[ind].name.toLowerCase().endsWith('pdf') ||Files[ind].name.toLowerCase().endsWith('jpeg') || Files[ind].name.toLowerCase().endsWith('jpg') || Files[ind].name.toLowerCase().endsWith('png')) {
                    type_coll = "Image"
                }
            }

        }
        formData.append('type_collection', type_coll);
        if (ConceptsFiles && (type === 'concepts' || type === 'all')) {

            for (let ind = 0; ind < ConceptsFiles.length; ind++) {
                formData.append('concepts_' + ind.toString(), ConceptsFiles[ind]);
            }
        }
        if (Topics && (type === 'topics' || type === 'all')) {

            for (let ind = 0; ind < Topics.length; ind++) {
                formData.append('topics_' + ind.toString(), Topics[ind]);
                if(Topics[ind].name.toLowerCase().endsWith('pdf') || Topics[ind].name.toLowerCase().endsWith('jpeg') || Topics[ind].name.toLowerCase().endsWith('jpg') || Topics[ind].name.toLowerCase().endsWith('png')) {
                    type_topic = "Image"
                }
            }
        }
        formData.append('topic_type', type_topic);

        if (Qrels && (type === 'qrels' || type === 'all')) {

            for (let ind = 0; ind < Qrels.length; ind++) {
                formData.append('qrels' + ind.toString(), Qrels[ind]);
            }
        }
        return formData

    }


    function uploadData() {
        //SetLoading(true)
        SetShowError(false)
        var upload = true

        var lab = []
        var max_lab = []
        var min_lab = []
        var all_lab = []
        var all_max_lab = []
        var all_min_lab = []
        var tags = []
        if (AnnotationType === 'Entity tagging'){
            AddTag.map(el => {
                var inputl = document.getElementById(`tag_${el}`);
                if (inputl.value !== '') {
                    tags.push(inputl.value)
                }
            })
        }
        if (['Graded labeling','Object detection'].indexOf(AnnotationType) !== -1) {

            AddLabel.map(el => {
                var inputl = document.getElementById(`label_${el}`);
                lab.push(inputl.value)
                if (inputl.value !== '') {
                    all_lab.push(inputl.value)
                }
                var inputmin = document.getElementById(`min_${el}`);
                if (inputmin.value !== '') {
                    all_min_lab.push(inputmin.value)
                }
                var inputmax = document.getElementById(`max_${el}`);
                if (inputmax.value !== '') {
                    all_max_lab.push(inputmax.value)
                }
                if (parseInt(inputmax.value) >= parseInt(inputmin.value)) {
                    max_lab.push(inputmax.value)
                    min_lab.push(inputmin.value)
                }
            })
        }
        if (all_lab.length !== all_min_lab.length || all_lab.length !== all_max_lab.length || all_max_lab.length !== all_min_lab.length) {
            SetShowError('You have to provide label, min and max values for all the labels provided. Max maust be greater or equal than min.')
            SetLoading(false)
            upload = false
        }

        var lab = []
        var max_lab = []
        var min_lab = []
        var all_lab = []
        var all_max_lab = []
        var all_min_lab = []
        if(AnnotationType === "Passages annotation"){
            AddLabelPassage.map(el => {
                var inputl = document.getElementById(`label_p_${el}`);
                lab.push(inputl.value)
                if (inputl.value !== '') {
                    all_lab.push(inputl.value)
                }
                var inputmin = document.getElementById(`min_p_${el}`);
                if (inputmin.value !== '') {
                    all_min_lab.push(inputmin.value)
                }
                var inputmax = document.getElementById(`max_p_${el}`);
                if (inputmax.value !== '') {
                    all_max_lab.push(inputmax.value)
                }
                if (parseInt(inputmax.value) >= parseInt(inputmin.value)) {
                    max_lab.push(inputmax.value)
                    min_lab.push(inputmin.value)
                }
            })
        }

        if (all_lab.length !== all_min_lab.length || all_lab.length !== all_max_lab.length || all_max_lab.length !== all_min_lab.length) {
            SetShowError('You have to provide label, min and max values for all the labels provided. Max maust be greater or equal than min.')
            SetLoading(false)
            upload = false
        }

       /* if (Task === '' || !Task) {
            SetShowError('Please, set the task on the left.')
            SetLoading(false)
            upload = false
        }*/
        if (AnnotationTypes.length === 0) {
            SetShowError('Please, add at least one annotation type')
            SetLoading(false)
            upload = false
        }
        if (PubmedId === '' && Files.length === 0 && IRDataset === '') {
            SetShowError('Please, add at least a document (or its pubmed ID) before confirm.')
            SetLoading(false)
            upload = false
        }
        if (all_lab.length !== all_min_lab.length || all_lab.length !== all_max_lab.length || all_max_lab.length !== all_min_lab.length) {
            SetShowError('You have to provide label, min and max values for all the labels provided. Max maust be greater or equal than min.')
            SetLoading(false)
            upload = false
        }
        if ((AnnotationTypes.indexOf('Passages retrieval') !== -1 && AnnotationTypes.indexOf('Passages retrieval') !== -1) && labels.length === 0) {
            SetShowError('You have to provide at least one label, with min and max values. Max maust be greater or equal than min.')
            SetLoading(false)
            upload = false
        }
        if (upload) {
            var input = ''
            // var formData = new FormData();
            let formData = GetFiles('all')

            input = document.getElementById('pubmed_ids');
            var pubmed = input.value
            formData.append('pubmed_ids', pubmed);
            console.log(pubmed)

            input = document.getElementById('collection_name');
            var name1 = input.value
            console.log(name1)


            input = document.getElementById('ir_dataset');
            var ir_dataset = input.value

            var ir_preanno = isChecked;
            var ir_queries = isCheckedQ;

            input = document.getElementById('collection_description');
            var desc = input.value

            var labels = []
            var min_labels = []
            var max_labels = []
            var labels_p = []
            var min_labels_p = []
            var max_labels_p = []
            var tags = []
            var members = []
            if(AnnotationType === "Graded labeling" || AnnotationType === 'Object detection') {

                AddLabel.map((el, index) => {
                    input = document.getElementById(`label_${el}`);
                    if (input.value !== '') {
                        labels.push(input.value)
                        input = document.getElementById(`min_${el}`);
                        if (input.value === '') {
                            min_labels.push(0)
                            max_labels.push(1)
                        } else {
                            min_labels.push(input.value)
                        }

                        input = document.getElementById(`max_${el}`);
                        if (input.value === '') {
                            max_labels.push(1)
                            min_labels[index] = 0
                        } else {
                            max_labels.push(input.value)
                        }
                    }

                })
            }
            if(AnnotationType === "Passages annotation" ) {

                AddLabelPassage.map((el, index) => {
                    input = document.getElementById(`label_p_${el}`);
                    if (input.value !== '') {
                        labels_p.push(input.value)
                        input = document.getElementById(`min_p_${el}`);
                        if (input.value === '') {
                            min_labels_p.push(0)
                            max_labels_p.push(1)
                        } else {
                            min_labels_p.push(input.value)
                        }

                        input = document.getElementById(`max_p_${el}`);
                        if (input.value === '') {
                            max_labels_p.push(1)
                            min_labels_p[index] = 0
                        } else {
                            max_labels_p.push(input.value)
                        }
                    }

                })
            }
            if(AnnotationType === "Entity tagging"){
                AddTag.map(el => {
                    input = document.getElementById(`tag_${el}`);
                    tags.push(input.value)

                })
            }

            AddMember.map(el => {
                input = document.getElementById(`member_${el}`);
                members.push(input.value)

            })
            //formData.append('task', Task);
            formData.append('name', name1);
            formData.append('description', desc)
            formData.append('annotation_type', AnnotationType)
            //AnnotationTypes.forEach(item => formData.append('annotationtypes[]', item));
            tags.filter(x => x !== '').forEach(item => formData.append('tags[]', item));
            labels.forEach(item => formData.append('labels[]', item));
            max_labels.forEach(item => formData.append('max_labels[]', item));
            min_labels.forEach(item => formData.append('min_labels[]', item));

            labels_p.forEach(item => formData.append('labels_p[]', item));
            max_labels_p.forEach(item => formData.append('max_labels_p[]', item));
            min_labels_p.forEach(item => formData.append('min_labels_p[]', item));

            members = members.filter(x => x !== '')
            formData.append('members[]', members)
            formData.append('ir_dataset', ir_dataset)
            formData.append('ir_preanno', ir_preanno)
            formData.append('ir_queries', ir_queries)


            axios({
                method: "post",
                url: "collections",
                data: formData,
                headers: {"Content-Type": "multipart/form-data"},
            })

                .then(function (response) {
                    //handle success
                    SetOpenSnack(true)
                    SetSnackMessage({'message': response.data['msg']})
                    SetAddCollection(false) // close window
                    SetUpdateCollection(true) // reload collection list
                    SetLoading(false)
                })
                .catch(function (response) {
                    //handle error
                    console.log(response);
                    SetShowError('An error occurred.')
                    SetLoading(false)

                });
        }


    }
    const handleChangeTags = (event)=>{
        SetTagsToAdd(event.target.value)
    }

    function DownloadTemplate(type) {
        axios.get('download_template_concepts', {params: {type: type}})
            .then(response => {
                if (type === 'json') {
                    FileDownload(JSON.stringify(response.data, null, 4), 'template_concepts.json');

                } else if (type === 'doc_json') {
                    FileDownload(JSON.stringify(response.data, null, 4), 'template_documents.json');

                } else if (type === 'topic_json') {
                    FileDownload(JSON.stringify(response.data, null, 4), 'template_topics.json');

                } else {
                    FileDownload((response.data), 'template_concepts.csv');

                }
            })
    }


    return (
        <div className='addcontainer'>
            <h3>Add a new collection for <i>{AnnotationType}</i></h3>
            <div><i>In order to create a new collection you need to set the name and to add at least a document.</i>
            </div>
            {Loading === false ? <div>


                <Row className='addcollectionclass'>
                    <Col md={1}></Col>
                    {/*<Col md={2}>Name:</Col>*/}
                    <Col md={10}><TextField id="collection_name" sx={{width: '100%'}} style={{marginTop: '1%'}}
                                            placeholder="Collection name"
                                            label="Name"
                                            value={Title}

                                            onChange={(e) => handleChangeTitle(e)}
                                            required variant="outlined"/></Col>
                    <Col md={1}></Col>
                </Row>
                <Row className='addcollectionclass'>
                    <Col md={1}></Col>
                    {/*<Col md={2}>Description</Col>*/}
                    <Col md={10}><TextField
                        id="collection_description"
                        placeholder="Collection description"
                        label="Description"
                        value={Description}
                        onChange={(e) => handleChangeDesc(e)}
                        multiline
                        sx={{width: '100%'}}
                        rows={2}
                    /></Col>
                    <Col md={1}></Col>
                </Row>
                <Row className='addcollectionclass'>
                    <Col md={1}></Col>
                    {/*<Col md={2}>Shared with:</Col>*/}
                    <Col md={10}>
                        <div>
                            <h6>Members <i>(Optional)</i></h6>
                            <div>Members share the collection with you. Add one or members allowed to annotate your
                                documents.
                            </div>
                        </div>


                        <div>
                            {AddMember.map(el =>
                                <TextField
                                    placeholder="Select a member"
                                    variant='outlined'
                                    id={`member_${el}`}
                                    label="Member"
                                    rows={1}
                                    sx={{width: '100%', marginTop: '15px'}}
                                />
                            )
                            }
                            <Button onClick={() => SetAddMember((prev) => [...prev, (prev[prev.length - 1] || 0) + 1])}>Add
                                Member</Button>


                        </div>
                    </Col>
                    <Col md={1}></Col>
                </Row>

                <hr/>
                {/*<div style={{marginTop: '15px'}}>
                    <div><h5>Select the annotation types</h5></div>
                    <div>The already selected types are related to the selected task. If you want to add some extra
                        types, click on the related button.
                    </div>

                    <div>
                        {AnnotationTypes.map(el =>
                            <span><Chip sx={{margin: '1%'}} label={el}
                                        variant={AnnotationTypes.indexOf(el) !== -1 ? 'filled' : "outlined"}
                                        color={'info'} onClick={(e) => {
                                if (AnnotationType === el) {
                                    var types = AnnotationTypes.map(t => t)
                                    types.push(el)
                                    SetAnnotationTypes(types)
                                } else {
                                    var types = AnnotationTypes.filter(t => t !== el)
                                    SetAnnotationTypes(types)
                                }
                            }}/></span>)}
                    </div>


                </div>*/}
                <hr/>
                {AnnotationType && <div>
                    <div><h5>Customize annotation</h5></div>


                    {(["Graded labeling","Object detection"].indexOf(AnnotationType) !== -1) &&
                        <div>
                            <div>
                                <h6>Labels <i></i></h6>
                                <div>Provide a set of labels with the ranges of values that can be assigned; if you want
                                    binary labels, place 0 for MIN and 1 for MAX.
                                </div>
                            </div>
                            <div>
                                {AddLabel.map(el => <Row>
                                    <Col md={8}>
                                        <TextField
                                            placeholder="Label"
                                            variant='outlined'
                                            id={`label_${el}`}
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}

                                        />
                                    </Col>
                                    <Col md={2}>
                                        <TextField
                                            placeholder="Min"
                                            variant='outlined'
                                            id={`min_${el}`}
                                            type="number"
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}

                                        />
                                    </Col>
                                    <Col md={2}>
                                        <TextField
                                            placeholder="Max"
                                            variant='outlined'
                                            id={`max_${el}`}
                                            type="number"
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}
                                        />
                                    </Col>
                                </Row>)}


                                <Button
                                    onClick={() => SetAddLabel((prev) => [...prev, (prev[prev.length - 1] || 0) + 1])}>Add
                                    label</Button>


                            </div>
                        </div>}
                    {(['Passages annotation'].indexOf(AnnotationType) !== -1) &&
                        <div>
                            <div>
                                <h6>Labels for passage annotation<i></i></h6>
                                <div>Provide a set of labels with the ranges of values that can be assigned; if you want
                                    binary labels, place 0 for MIN and 1 for MAX.
                                </div>
                            </div>
                            <div>
                                {AddLabelPassage.map(el => <Row>
                                    <Col md={8}>
                                        <TextField
                                            placeholder="Label"
                                            variant='outlined'
                                            id={`label_p_${el}`}
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}

                                        />
                                    </Col>
                                    <Col md={2}>
                                        <TextField
                                            placeholder="Min"
                                            variant='outlined'
                                            id={`min_p_${el}`}
                                            type="number"
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}

                                        />
                                    </Col>
                                    <Col md={2}>
                                        <TextField
                                            placeholder="Max"
                                            variant='outlined'
                                            id={`max_p_${el}`}
                                            type="number"
                                            rows={1}
                                            sx={{width: '100%', marginTop: '15px'}}
                                        />
                                    </Col>
                                </Row>)}


                                <Button
                                    onClick={() => SetAddLabelPassage((prev) => [...prev, (prev[prev.length - 1] || 0) + 1])}>Add
                                    label</Button>


                            </div>
                        </div>}
                    {AnnotationType === 'Entity tagging'  && <div>
                        <div>
                            <h6>Tags </h6>
                            <div>Provide a set of tags; one or more of these tags can be associated to each mention to
                                perform entity tagging.
                            </div>
                        </div>
                        <div>
                            {AddTag.map(el =>
                                <TextField
                                    placeholder="Select a list of tags"
                                    variant='outlined'
                                    id={`tag_${el}`}
                                    onChange={handleChangeTags}
                                    label="Tag"
                                    rows={2}
                                    sx={{width: '100%', marginTop: '15px'}}
                                />
                            )
                            }
                            <Button onClick={() => SetAddTag((prev) => [...prev, (prev[prev.length - 1] || 0) + 1])}>Add
                                Tag</Button>


                        </div>
                    </div>}

                    {AnnotationType === 'Entity linking' && <div style={{marginTop: '15px'}}>
                        <h6>Concepts</h6>
                        <div>Add one or more files containing the concepts used to perform <b>entity linking</b>. Files
                            can be CSV, or json.
                        </div>
                        <div style={{fontSize: '0.8rem'}}>
                            <div>Download <span className={'buttontem'}
                                                onClick={() => DownloadTemplate('csv')}>here</span>{' '}
                                the csv template.
                            </div>
                            <div>Download <span className={'buttontem'}
                                                onClick={() => DownloadTemplate('json')}>here</span>{' '}
                                the json template.
                            </div>
                        </div>

                        <div className='uploadfiles'>
                        <span className='collectionButt'>
                            <label htmlFor="concepts_to_upload">
                                <input hidden accept="*" id="concepts_to_upload" onChange={() => {
                                    AddFiles('concepts')
                                }} multiple type="file"/>
                                {/*<Button variant="contained" size={'small'} sx={{margin:'10px',display:"inline-block"}} onChange={()=>GetFiles('concepts')} component="span" startIcon={<UploadFileIcon/>}>*/}
                                <Button variant="contained" size={'small'}
                                        sx={{margin: '10px', display: "inline-block"}} component="span"
                                        startIcon={<UploadFileIcon/>}>
                                        Upload
                                </Button>
                            </label>

                        </span>

                        </div>
                        <div>
                            {ConceptsFiles &&
                                <>
                                    {ConceptsFiles.length > 0 && <b>Uploaded concepts:</b>
                                    }
                                    {ConceptsFiles.map(file =>
                                        <div>
                                            <span>{file.name}</span>{' '}<span><IconButton onClick={() => {
                                            let conc = ConceptsFiles.map(x => x)
                                            conc = conc.filter(x => x.name !== file.name)
                                            SetConceptsFiles(conc)
                                        }}><DeleteIcon/></IconButton></span>
                                        </div>
                                    )}
                                </>}


                        </div>
                    </div>}


                </div>}


                <hr/>
                <div>
                    <div><h5>Upload from ir_datasets</h5>
                        <div>Doctron allows you to upload a collection from <a
                            href={"https://ir-datasets.com/"}>ir_datasets</a>. Provide the URL of the dataset as it is
                            provided in the guidelines (e.g., "aquaint/trec-robust-2005").
                            <>{window.location.hostname === "doctron.dei.unipd.it" &&
                                <i>(Max 10 documents will be uploaded)</i>}</></div>

                        <TextField
                            placeholder="IR_dataset URL"
                            variant='outlined'
                            id={"ir_dataset"}
                            onChange={handleChangeIRDataset}
                            rows={1}
                            sx={{width: '100%', marginTop: '15px'}}

                        />
                        <FormControlLabel onChange={(e) => {
                            SetisCheckedQ(prev => !prev)
                        }} id="preannotation" control={<Checkbox/>}
                                          label="Add also original collection's queries."/>
                     {/*   <FormControlLabel onChange={(e) => {
                            SetisChecked(prev => !prev)
                        }} id="preannotation" control={<Checkbox/>}
                                          label="Add relevance judgements preannotations. In this case, the label Relevance will be added by default with the range of values provided in the original collection."/>
*/}
                    </div>

                </div>
                <hr/>
                <div style={{marginTop: '10px'}}>
                    <div className={'clickable clickBelow'} onClick={() => SetShowDocumentsUpload(prev => !prev)}>
                        {/*
                        <h5>Upload custom collection</h5>
*/}
                    </div>
                    <Collapse in={ShowDocumentsUpload}>

                        <>
                            <div><h6>Upload custom documents</h6></div>
                            <div>
                                <i>Textual documents can be uploaded in CSV, JSON, TXT, PDF
                                    formats. Images instead, can be uploaded in JPG or PNG.
                                    This is optional if you provided a URL of a
                                    ir-dataset. <>{window.location.hostname === "doctron.dei.unipd.it" &&
                                        <i>(Max 10 documents allowed)</i>}</></i>


                                <div style={{fontSize: '0.8rem'}}>
                                    <div>If you plan to associate an ID to your documents, provide them as csv or json
                                        files,
                                        and, for each document, provide a key (for json), or the column (for the csv)
                                        with <i>document_id</i> name.
                                        If your documents have a title, put it in the <i>title</i> key (column). TXT
                                        files will
                                        be treated as unique annotable text, hence it will not be split into sections.
                                    </div>
                                    <div>Download <span className={'buttontem'}
                                                        onClick={() => DownloadTemplate('doc_json')}>here</span>{' '}
                                        the json template.
                                    </div>

                                </div>
                                <Row className='addcollectionclass'>

                                    <Col md={1}></Col>
                                    <Col md={10}>

                                        <div className='uploadfiles'>
                        <span className='collectionButt'>
                            <label htmlFor="files_to_upload">
                                <Input accept="*" id="files_to_upload" onChange={() => {
                                    AddFiles('documents')
                                }} multiple type="file"/>
                                <ThemeProvider theme={theme}>
                                    {/*<Button variant="contained"  onChange={()=>GetFiles('documents')} color='neutral_updload' component="span" startIcon={<UploadFileIcon/>}>*/}
                                    <Button sx={{marginTop: '15px'}} variant="contained" color='neutral_updload'
                                            component="span" startIcon={<UploadFileIcon/>}>
                                        Upload documents
                                    </Button></ThemeProvider>
                            </label>
                        </span>


                                        </div>
                                        {Files &&
                                            <>
                                                {Files.length > 0 && <b>Uploaded documents files:</b>
                                                }
                                                {Files.map(file =>
                                                    <div>
                                                        <span>{file.name}</span>{' '}<span><IconButton onClick={() => {
                                                        let conc = Files.map(x => x)
                                                        conc = conc.filter(x => x.name !== file.name)
                                                        SetFiles(conc)
                                                    }}><DeleteIcon/></IconButton></span>
                                                    </div>
                                                )}
                                            </>}
                                        <div>
                                            <hr/>
                                            <div>
                                                <b>Upload PubMed abstracts <i>(Optional)</i></b>
                                            </div>
                                            <div>
                                                <i>Upload a list of at most 10 Pubmed IDs <b>single-space separated</b>.
                                                </i>
                                                <div>Note: the requests are based on the Pubmed API, and there is a
                                                    limited
                                                    number of
                                                    requests that can be performed per second.
                                                </div>

                                                <Row className='addcollectionclass'>

                                                    <Col md={1}></Col>
                                                    <Col md={10}>
                                                        {/*<Collapse in={ShowAreaPubmed}>*/}
                                                        <TextField
                                                            id="pubmed_ids"
                                                            // placeholder="PubMed IDs commma separated: 1234,12,456"
                                                            label="PubMed IDs"
                                                            multiline
                                                            onChange={(e) => handleChangePubmedId(e)}
                                                            value={PubmedId}
                                                            sx={{width: '100%', marginTop: '15px'}}
                                                            helperText="PubMed IDs must be single space separated: 123 12 456"
                                                            rows={3}
                                                        />

                                                    </Col>
                                                    <Col md={1}></Col>
                                                </Row>
                                            </div>
                                        </div>
                                        <hr/>
                                    </Col>
                                    <Col md={1}></Col>
                                </Row>
                            </div>

                            <hr/>
                            <div>
                                <div><h5>Upload custom topics</h5></div>
                                <div>
                                        <i>Textual topics can be uploaded in JSON format. Image topics can be a PNG, JPG or JPEG file..</i> :


                                    <div style={{fontSize: '0.8rem'}}>

                                        <div>Download <span className={'buttontem'}
                                                            onClick={() => DownloadTemplate('topic_json')}>here</span>{' '}
                                            the json template.
                                        </div>

                                    </div>
                                    <Row className='addcollectionclass'>

                                        <Col md={1}></Col>
                                        <Col md={10}>

                                            <div className='uploadfiles'>
                        <span className='collectionButt'>
                            <label htmlFor="topics_to_upload">
                                <Input accept="*" id="topics_to_upload" onChange={() => {
                                    AddFiles('topics')
                                }} multiple type="file"/>
                                <ThemeProvider theme={theme}>
                                    <Button sx={{marginTop: '15px'}} variant="contained" color='neutral_updload'
                                            component="span" startIcon={<UploadFileIcon/>}>
                                        Upload topics
                                    </Button></ThemeProvider>
                            </label>
                        </span>


                                            </div>
                                            {Topics &&
                                                <>
                                                    {Topics.length > 0 && <b>Uploaded topic files:</b>
                                                    }
                                                    {Topics.map(file =>
                                                        <div>
                                                            <span>{file.name}</span>{' '}<span><IconButton
                                                            onClick={() => {
                                                                let conc = Topics.map(x => x)
                                                                conc = conc.filter(x => x.name !== file.name)
                                                                SetTopics(conc)
                                                            }}><DeleteIcon/></IconButton></span>
                                                        </div>
                                                    )}
                                                </>}

                                        </Col>
                                        <Col md={1}></Col>
                                    </Row>
                                </div>
                            </div>
                            <hr/>
                            <div>
                       {/*         <div><h5>Upload relevance judgements <i>(Optional)</i></h5></div>
                                <div>
                                    <i>QRELS can be uploaded in JSON format. Qrels are needed to be provided with a set
                                        of preannotations. </i>

                                    <div style={{fontSize: '0.8rem'}}>

                                        <div>Download <span className={'buttontem'}
                                                            onClick={() => DownloadTemplate('qrels_json')}>here</span>{' '}
                                            the json template.
                                        </div>

                                    </div>*/}
    {/*                                <Row className='addcollectionclass'>

                                        <Col md={1}></Col>
                                        <Col md={10}>

                                            <div className='uploadfiles'>*/}
                     {/*   <span className='collectionButt'>
                            <label htmlFor="qrels_to_upload">
                                <Input accept="*" id="qrels_to_upload" onChange={() => {
                                    AddFiles('qrels')
                                }} multiple type="file"/>
                                <ThemeProvider theme={theme}>
                                    <Button sx={{marginTop: '15px'}} variant="contained" color='neutral_updload'
                                            component="span" startIcon={<UploadFileIcon/>}>
                                        Upload qrels
                                    </Button></ThemeProvider>
                            </label>
                        </span>*/}


                                           {/* </div>
                                            {Qrels &&
                                                <>
                                                    {Qrels.length > 0 && <b>Uploaded qrels files:</b>
                                                    }
                                                    {Qrels.map(file =>
                                                        <div>
                                                            <span>{file.name}</span>{' '}<span><IconButton
                                                            onClick={() => {
                                                                let conc = Qrels.map(x => x)
                                                                conc = conc.filter(x => x.name !== file.name)
                                                                SetTopics(conc)
                                                            }}><DeleteIcon/></IconButton></span>
                                                        </div>
                                                    )}
                                                </>}

                                        </Col>
                                        <Col md={1}></Col>
                                    </Row>*/}
{/*
                                </div>
*/}
                            </div>
                            <hr/>
                        </>
                    </Collapse>
                </div>


                {ShowError && <Alert severity="error">Error - {ShowError}</Alert>}
                <Row>
                    <Col md={1}></Col>
                    <Col md={10}>
                        <div style={{textAlign: "center"}}>
                            <ThemeProvider theme={theme}>
                                <Button color="neutral" onClick={() => {
                                    SetAddCollection(false);
                                    SetShowError(false)
                                }} className='collectionButt' variant="contained">
                                    Clear
                                </Button>
                            </ThemeProvider>
                            <div className='confirmButt'><Button variant="contained"
                                                                 onClick={() => uploadData()}>Confirm</Button></div>
                        </div>

                    </Col>
                    <Col md={1}></Col>
                </Row>
            </div> : <div className='loading'><CircularProgress/>
            </div>}
        </div>

    );
}