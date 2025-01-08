import {Col, ProgressBar, Row} from "react-bootstrap";

import axios from "axios";
import {ButtonGroup} from "@material-ui/core";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;

// import '../annotation.css'
// import '../documents.css'
import '../concepts/conceptmodal.css'
import {CircularProgress} from "@mui/material";
import KeyboardBackspaceIcon from '@mui/icons-material/KeyboardBackspace';
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, styled} from "@mui/material/styles";
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import Alert from '@mui/material/Alert';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Draggable from 'react-draggable';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import DialogContent from "@mui/material/DialogContent";
import {updateMentionColor} from "../../HelperFunctions/HelperFunctions";
import {ConceptContext} from "../../../BaseIndex";
import SelectTag from "./SelectTag";
import Paper from "@mui/material/Paper";
// export const ConceptContext = createContext('')

function PaperComponent(props) {
    return (
        <Draggable
            handle="#draggable-dialog-title"
            cancel={'[class*="MuiDialogContent-root"]'}
        >
            <Paper {...props} />
        </Draggable>
    );
}
export default function DraggableModalTag(props) {
    const {
        relationshipslist,
        concepts,
        tags,collectionconcepts,
        tags_split,
        curmention,
        endrange,areascolors
    } = useContext(AppContext);

    const {
        areas,
        name,area,
        url,
        urlname,
        conceptslist,
        description
    } = useContext(ConceptContext);

    const [ConceptsList,SetConceptsList] = collectionconcepts
    const [RelationshipsList,SetRelationshipsList] = relationshipslist

    const [Area,SetArea] = area
    const [Concepts,SetConcepts] = concepts;
    const [ShowAlert, SetShowAlert] = useState(false)
    const [CurMention,SetCurMention] = curmention;
    const [Areas,SetAreas] = areas
    const [ShowAlertWarningArea,SetShowAlertWarningArea] = useState(false)
    const [SelectedMention, SetSelectedMention] = useState(false)
    const [Tags, SetTags] = tags
    const [TagsSplitted,SetTagsSplitted] = tags_split
    const [value,SetValue] = useState(0)

    function handleChangeRadio(e){
        e.preventDefault()
        e.stopPropagation()
        let v = e.target.value
        SetValue(parseInt(v))

        let selected = CurMention[v]

        SetSelectedMention(selected)
    }


    function handleClose(){
        props.setshowtagmodal(false)

        SetArea(null)
        SetAreas(false)
        SetShowAlertWarningArea(false)
        SetShowAlert(false)
    }

    useEffect(()=>{

        if(Tags){
            var aa = []
            Tags.map(elemento=>{
                var area = elemento
                if(aa.indexOf(area) === -1){
                    aa.push(area)
                }
            })
            SetAreas(aa)
        }


    },[Tags])



    useEffect(()=>{
        SetArea(null)
    },[])


    function submitNewConcept(e){
        e.preventDefault();
        e.stopPropagation();

        if(Area === null){
            SetShowAlert(true)
        }else{
            let area = 'Default'
            if(Area !== null && Area){
                area = Area.area
            }

            axios.post('tag/insert',{mention:CurMention[0],area:area})
                .then(response=>{
                    SetConcepts(response.data['concepts'])
                    SetConceptsList(response.data['concepts_list'])
                    SetTags(response.data['tags_list'])
                    SetTagsSplitted(response.data['tags'])
                    SetRelationshipsList(response.data['relationships'])


                    // updateMentionColor(CurMention[0].mentions,CurMention[0].start,CurMention[0].stop,response.data['concepts'],AreasColors)
                    handleClose()

                })
                .catch(error =>{
                    console.log('error',error)
                })

        }


    }
    useEffect(()=>{
        if(Tags){
            if((Area === null) ){
                SetShowAlertWarningArea(false)
            }


        }

    },[Area])


    return (
    <Dialog
        open={props.showtagmodal}
        onClose={handleClose}

        // hideBackdrop={true}
        // disableEnforceFocus={true}

        PaperComponent={PaperComponent}
        aria-labelledby="draggable-dialog-title"
    >

            <div style={{padding:'2%',width:'500px'}}>
                {(Areas && CurMention) ? <>
                    {CurMention.length === 1 && <SelectTag type={'concept'} handleclose ={handleClose}   />}
                    {CurMention.length > 1 && <div style={{padding:'3%'}}>
                        <DialogTitle style={{cursor: 'move'}} id="draggable-dialog-title">
                            Select the mention
                        </DialogTitle>
                        <DialogContent>
                            <DialogContentText id="alert-dialog-description">
                                Select the mention you want to associate a concept to
                                <div>
                                    {CurMention.map((m,i)=><div>
                                        <Radio
                                            checked={value === i}
                                            onClick={handleChangeRadio}
                                            value={i}
                                            aria-label={m.mention_text}
                                        />{' '}{m.mention_text}
                                    </div>)}
                                </div>
                            </DialogContentText>

                        </DialogContent>




                    </div>}
                    <div style={{margin:'3%'}}>
                        {ShowAlert && <Alert sx={{marginBottom: '3%'}} severity="error">Please, set a type, then, confirm.</Alert>}
                    </div>
                </> :<div className='loading'>
                    <CircularProgress />
                </div>
                    }


            </div>


            <DialogActions>


                <Button autoFocus onClick={handleClose}>
                    Cancel
                </Button>
                {CurMention.length === 1 && <Button disabled={Area === '' || Area === false} onClick={submitNewConcept}>Confirm</Button>}
                {CurMention.length > 1 && <Button onClick={()=>SetCurMention([CurMention[value]])}>Confirm</Button>}
            </DialogActions>

        {/*</ConceptContext.Provider>*/}

    </Dialog>
);
}