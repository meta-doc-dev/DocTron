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
import {AppContext} from "../../../App";
import {InputLabel, Select, TextField} from "@material-ui/core";
import MenuItem from "@mui/material/MenuItem";
import axios from "axios";
import {CircularProgress} from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Autocomplete from "@mui/material/Autocomplete";

function CoehnsDialog(props){
    const { annotators,collectiondocuments  } = useContext(AppContext);

    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments
    const [Document,SetDocument] = useState("")
    const [Annotators,SetAnnotators] = annotators
    const [FirstMember,SetFirstMember] = useState('')
    const [SecondMember,SetSecondMember] = useState('')
    const [Loading,SetLoading] = useState(false)
    const [Coehns,SetCoehns] = useState(false)
    const [docOptions,SetdocOptions] = useState([])
    const [Members,SetMembers] = useState([])

    useEffect(()=>{
        if(FirstMember && SecondMember ){
            SetLoading(true)
            axios.get('create_coehns',{params:{user1:FirstMember,user2:SecondMember,document:Document,collection:props.collection}})
                .then(response=>{
                    SetLoading(false)
                    SetCoehns(response.data)

                })
                .catch(error=> {
                    console.log('error', error);
                    SetLoading(false)
                })
        }

    },[FirstMember,SecondMember,Document])

    useEffect(()=>{
        var options = [{'label': 'All','value':''}]
        if(CollectionDocuments){
            CollectionDocuments.map(c=>{
                options.push({'label':c.id,'value':c.hashed_id})
            })
        }
        SetdocOptions(options)
    },[CollectionDocuments])

    useEffect(()=> {
        var options = []
        if(Annotators){
            Annotators.map(c=>{
                options.push({'label':c,'value':c})
            })
        }
        SetMembers(options)
    },[Annotators])

    useEffect(()=>{

        async function fetchAnnotators(){
            const response = await axios.get('get_annotators');
            // console.log('request',response)
            SetAnnotators(response.data)

            return response
        }
        fetchAnnotators()


    },[])

    const handleChangeDoc = (event) => {
        console.log('doc',event.target.value)
        SetDocument(event.target.value);
    };

    const handleChangeFirst = (event) => {
        SetFirstMember(event.target.value);
    };

    const handleChangeSecond = (event) => {
        SetSecondMember(event.target.value);
    };
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
                Coehn's Kappa between two annotators
            </DialogTitle>
            <DialogContent>
                <div>
                    <div style={{padding: '2%'}}>
                        {docOptions && <Autocomplete

                            id="doc"
                            onChange={(event, newValue) => {
                                SetDocument(newValue.value)
                                }
                            }
                            getOptionLabel={(option) => option.label}

                            options={docOptions}
                            sx={{width: '100%'}}
                            renderInput={(params) => <TextField {...params} label="Document"/>}
                        />}
                    </div>
                    <div style={{padding: '2%'}}>
                        {Members && <Autocomplete

                            id="first"
                            onChange={(event, newValue) => {
                                SetFirstMember(newValue.value)
                            }
                            }

                            getOptionDisabled={(option) =>
                                option.label === SecondMember
                            }
                            getOptionLabel={(option) => option.label}

                            options={Members}
                            sx={{width: '100%'}}
                            renderInput={(params) => <TextField {...params} label="First Member"/>}
                        />}
                    </div>
                    <div style={{padding: '2%'}}>
                        {Members && <Autocomplete
                            getOptionLabel={(option) => option.label}
                            onChange={(event, newValue) => {
                                SetSecondMember(newValue.value)
                            }
                            }
                            id="second"
                            getOptionDisabled={(option) =>
                                option.label === FirstMember
                            }
                            options={Members}
                            sx={{width: '100%'}}
                            renderInput={(params) => <TextField {...params} label="Second Member"/>}
                        />}
                    </div>
                    {/*    <FormControl sx={{ m: 1, minWidth: 120 }}>*/}
                    {/*        <InputLabel id="demo-simple-select-helper-label">Document</InputLabel>*/}
                    {/*        <Select*/}
                    {/*            labelId="demo-simple-select-helper-label"*/}
                    {/*            id="demo-simple-select-helper"*/}
                    {/*            value={Document}*/}
                    {/*            label="document"*/}
                    {/*            onChange={handleChangeDoc}*/}
                    {/*        >*/}
                    {/*            <MenuItem value="">*/}
                    {/*                All*/}
                    {/*            </MenuItem>*/}
                    {/*            {CollectionDocuments && CollectionDocuments.map(document=>*/}
                    {/*                <MenuItem value={document.hashed_id}>{document.id}</MenuItem>*/}


                    {/*            )}*/}
                    {/*        </Select></FormControl>*/}
                    {/*</div>*/}
                    {/*<div style={{padding: '2%'}}>*/}


                    {/*<FormControl sx={{ width: '100%' }}>*/}
                    {/*    <InputLabel id="demo-select-small-label">Document</InputLabel>*/}
                    {/*    <Select*/}
                    {/*        labelId="demo-select-small-label"*/}
                    {/*        id="demo-select-small"*/}
                    {/*        value={Document}*/}
                    {/*        label="First Member"*/}

                    {/*        onChange={handleChangeDoc}*/}
                    {/*    >*/}


                    {/*    </Select></FormControl>*/}
                    {/*</div>*/}
                    {/*<div style={{padding: '2%'}}>*/}
                    {/*    <FormControl sx={{ width: '100%' }}>*/}

                    {/*<InputLabel id="demo-select-small-label">First Member</InputLabel>*/}
                    {/*<Select*/}
                    {/*    labelId="demo-select-small-label"*/}
                    {/*    id="demo-select-small"*/}
                    {/*    value={FirstMember}*/}

                    {/*    label="First Member"*/}
                    {/*    onChange={handleChangeFirst}*/}
                    {/*>*/}
                    {/*    <MenuItem value="">*/}
                    {/*        First Member*/}
                    {/*    </MenuItem>*/}
                    {/*    {Annotators && Annotators.map(annotator=>*/}
                    {/*        <MenuItem disabled={annotator === SecondMember} value={annotator}>{annotator}</MenuItem>*/}


                    {/*    )}*/}

                    {/*</Select></FormControl>*/}
                    {/*</div>*/}
                    {/*<div style={{padding: '2%'}}>*/}
                    {/*    <FormControl sx={{ width: '100%' }}>*/}

                    {/*<InputLabel id="demo-select-small-label">Second Member</InputLabel>*/}
                    {/*<Select*/}
                    {/*    labelId="demo-select-small-label"*/}
                    {/*    id="demo-select-small"*/}
                    {/*    value={SecondMember}*/}

                    {/*    label="Second Member"*/}


                    {/*    onChange={handleChangeSecond}*/}
                    {/*>*/}
                    {/*    <MenuItem value="">*/}
                    {/*        Second Member*/}
                    {/*    </MenuItem>*/}
                    {/*    {Annotators && Annotators.map(annotator=>*/}

                    {/*        <MenuItem disabled={annotator === FirstMember} value={annotator}>{annotator}</MenuItem>*/}

                    {/*    )}*/}

                    {/*</Select></FormControl></div>*/}
                    {Loading === true && <div className='loading'><CircularProgress /></div>}
                    {Coehns && !Loading && <div>
                        The agreement between {FirstMember} and {SecondMember} is:<br/>
                        <Row>
                            <Col md={2}><b>Mentions</b></Col>
                            <Col md={10}>{Coehns['mentions']}</Col>
                        </Row>
                        <Row>
                            <Col md={2}><b>Concepts</b></Col>
                            <Col md={10}>{Coehns['concepts']}</Col>
                        </Row>
                        <Row>
                            <Col md={2}><b>Relationships</b></Col>
                            <Col md={10}>{Coehns['relations']}</Col>
                        </Row>
                        <Row>
                            <Col md={2}><b>Assertions</b></Col>
                            <Col md={10}>{Coehns['assertions']}</Col>
                        </Row>
                        <Row>
                            <Col md={2}><b>Labels</b></Col>
                            <Col md={10}>{Coehns['labels']}</Col>
                        </Row>



                    </div>}



                </div>
            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>Close</Button>

            </DialogActions>
        </Dialog>
    );

}
export default CoehnsDialog