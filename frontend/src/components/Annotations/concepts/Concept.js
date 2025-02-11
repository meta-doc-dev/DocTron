import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Draggable from 'react-draggable';

import axios from "axios";
import {ButtonGroup} from "@mui/material";
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
import EditIcon from '@mui/icons-material/Edit';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';
import '../annotation.css'

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
import DocumentToolBar from "../../Document/ToolBar/DocumentToolBar";
import AddIcon from '@mui/icons-material/Add';
import Collapse from "@mui/material/Collapse";
import Paper from "@mui/material/Paper";
import '../annotation.css'
// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import DraggableModal from "./DraggableConceptModal";
import {DeleteRange, updateMentionColor, waitForElm} from "../../HelperFunctions/HelperFunctions";
import DeleteMentionModal from "../mentions/modals/DeleteMentionModal";
import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";
import IconButton from '@mui/material/IconButton';

import {type} from "@testing-library/user-event/dist/type";
import Tooltip from '@mui/material/Tooltip';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import ChipRel from "../relationship/ChipRelationship";
import DescriptionDialog from "./DescriptionDialog";



export default function Concept(props){
    const { username,concepts,modality,inarel,documentdescription,areascolors,curannotator,mentions,relationshipslist,mentiontohighlight,startrange,endrange } = useContext(AppContext);
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [Concept,SetConcept] = useState(false)
    const [Comment,SetComment] = useState(false)
    const [ShowComment,SetShowComment] = useState(false)

    const [ConceptsList,SetConceptsList] = concepts
    const [ShowDelete,SetShowDelete] = useState(false)
    const [ShowDescription,SetShowDescription] = useState(false)
    const [ShowMultiple,SetShowMultiple] = useState(false)
    const [Modality,SetModality] = modality
    const [InARel,SetInARel] = inarel
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Username,SetUsername] = username
    const [AreasColors,SetAreasColors] = areascolors
    const Colors = ['red','orange','green','blue','purple','pink','black']
    const [Color,SetColor] = useState('rgba(65,105,225,1)')
    const [ColorOver,SetColorOver] = useState('rgba(65,105,225,0.7)')
    const [DocumentDesc,SetDocumentDesc] = documentdescription


    useEffect(() => {
        if(Concept){
            if (props.mention && props.mention.mention_text) {
                delete props.mention.mention_text;
            }
            axios.get('concepts/comment',{params:{concept:Concept,mention:props.mention}})
                .then(response=>{

                    SetComment(response.data['comment'] === '' ? false : response.data['comment'])
                })
        }else{
            SetComment(false)
            SetShowComment(false)
        }




    }, [Concept]);


    function uploadComment(){
        if(Concept){
            var comment = document.getElementById("comment").value
            axios.post('concepts/comment',{concept:Concept,comment:comment,mention:props.mention})
                .then(response=>{

                    SetShowComment(false)
                    SetComment(false)
                    SetConcept(false)
                })
        }


    }


    const handleDelete = (event,i) => {
        event.preventDefault();
        event.stopPropagation();
        if(Modality === 2){
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            axios.delete('concepts/delete', {
                data: {
                    mention: props.mention,
                    url: props.concepts[i]['concept'].concept_url,
                    area: props.concepts[i]['concept'].area
                }
            })
                .then(response => {
                    // props.setconcepts(false)
                    let concepts = []
                    ConceptsList.map(c => {
                        if (!(c['concept']['concept_url'] === props.concepts[i]['concept'].concept_url && props.concepts[i].start === c.start && props.concepts[i].stop === c.stop)) {
                            concepts.push(c)
                        }
                    })
                    if (i === 0) {
                        SetShowDelete(false)

                    }
                    SetConceptsList(concepts)
                    SetRelationshipsList(response.data['relationships'])
                    // updateMentionColor(props.mention.mentions, props.mention.start, props.mention.stop, concepts,AreasColors)
                    // console.log('cocnepts',concepts)


                })
                .catch(error => {
                    console.log('error', error)
                })
        }

    }

    useEffect(()=>{
        // console.log('color update')
        // if(!InARel){
            if(props.concepts.length===1){
                let area = props.concepts[0]['concept']['area']
                //let color_0 = window.localStorage.getItem(area)
                let color_0 = null
                if(AreasColors[area]){
                    color_0 = AreasColors[area]
                }


                if(color_0 === null) {
                    color_0 = 'rgba(65,105,225,1)'
                    //window.localStorage.setItem(area, color_0)
                }

                // waitForElm('#'+props.mention_id).then((mention) => {
                //     mention.style.color = color_0
                //     mention.style.backgroundColor = color_0.replace('1)','0.1)')
                // })
                let color_1 = color_0.replace('1)', '0.7)')

                SetColor(color_0)
                SetColorOver(color_1)
            }
            else if(props.concepts.length > 1){
                let color_0 = 'rgba(50,50,50,1)'
                // waitForElm('#'+props.mention_id).then((mention) => {
                //     mention.style.color = color_0
                //     mention.style.backgroundColor = color_0.replace('1)','0.1)')
                // })
                let color_1 = color_0.replace('1)', '0.7)')

                SetColor(color_0)
                SetColorOver(color_1)
            }
        // }


    },[AreasColors,props.concepts])


    const CustomChip = styled(Chip)({
        fontSize:12,
        height:22,
        maxWidth:200,
        backgroundColor: Color,
        color:'white',
        "&:hover": {
            backgroundColor: ColorOver,
            color:'white',
            "& .MuiChip-deleteIcon": {
                height:20,
                color:'white',
                backgroundColor: ColorOver,
            },
        },
        "& .MuiChip-deleteIcon": {
            height:20,
            color:'white',
            backgroundColor: Color,
        },
    });



    return (
        <div style={{textAlign:'center'}}>
            {((props.concepts && props.concepts.length >= 1 && Color && ColorOver && !InARel)) &&
                <>{props.concepts.map(concept =>
                    <span>

                     {CurAnnotator === Username ?<CustomChip label={concept['concept'].concept_name}
                                                             onDelete={(e)=>handleDelete(e,0)} onClick={(e) => {
                             e.preventDefault()
                             SetConcept(concept['concept'].concept_url)
                             SetShowComment(prev => !prev)
                         }}  /> :
                         <CustomChip label={concept['concept'].concept_name}
                                     onClick={(e) => {
                                         e.preventDefault()
                                         SetConcept(concept['concept'].concpet_url)
                                         SetShowComment(prev => !prev)
                                     }}  />}
                    </span>
                )
                }</>}





              {/*  <div style={{textAlign:'center'}}>

                    {CurAnnotator === Username ?<CustomChip label={props.concepts[0]['concept'].concept_name}
                            onDelete={()=>SetShowDelete(prev=>!prev)} onClick={()=>SetShowDescription(prev=>!prev)}  /> :
                    <CustomChip label={props.concepts[0]['concept'].concept_name}
                                 onClick={()=>SetShowDescription(prev=>!prev)}  />}
            </div>}*/}

            {((props.concepts && props.concepts.length >= 1 && Color && ColorOver && InARel)) &&
            <div style={{textAlign:'center'}}>
                <>{props.concepts.map(concept =>
                    <span>
                <ChipRel role={props.role} variant = {(props.role.toLowerCase() === 'source' || props.role.toLowerCase() === 'predicate' || props.role.toLowerCase() === 'target') ? "filled":"outlined"} color={Color} label={concept['concept'].concept_name} />
                    </span>)}</>
                    </div>}
          {/*  {props.concepts && props.concepts.length > 1 &&  Color && ColorOver && InARel &&
            <div className='concepts'>
                <ChipRel role={props.role} variant = {(props.role.toLowerCase() === 'source' || props.role.toLowerCase() === 'predicate' || props.role.toLowerCase() === 'target') ? "filled":"outlined"} color={Color} label={props.concepts.length}  />
            </div>}*/}


{/*
            {ShowDescription && <DescriptionDialog show={ShowDescription} setshow={SetShowDescription} area={props.concepts[0]['concept']['area']}  name={props.concepts[0]['concept']['concept_name']} url={props.concepts[0]['concept']['concept_url']} description={props.concepts[0]['concept']['concept_description']} />}
*/}


            {ShowComment &&   <Dialog
                open={ShowComment}
                onClose={(e)=> {
                    e.preventDefault()
                    SetShowComment(false)
                    SetComment(false)
                    SetConcept(false)
                }}
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
                    <Button        onClick={(e)=> {
                        e.preventDefault()
                        SetShowComment(false)
                        SetComment(false)
                        SetConcept(false)
                    }}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>}

  {/*          {ShowDelete &&
            <Dialog
                open={ShowDelete}
                onClose={()=>SetShowDelete(false)}

                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Delete concept
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Are you sure you want to delete the concept <b>{props.concepts[0]['concept'].concept_name}</b>?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={()=> {
                        SetShowDelete(false);
                    }}>No</Button>
                    <Button onClick={(e)=>handleDelete(e,0)} autoFocus>
                        Yes
                    </Button>
                </DialogActions>
            </Dialog>
            }*/}



        </div>

    )
}