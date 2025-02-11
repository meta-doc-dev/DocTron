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
import CommentDialog from "../../RightSideMenu/labels/CommentDialog";
import CommentTag from "./CommentTag";



export default function Tag(props){
    const { username,concepts,inarel,modality,documentdescription,areascolors,curannotator,mentions,relationshipslist,tags_split,startrange,endrange } = useContext(AppContext);
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [Modality,SetModality] = modality
    const [ConceptsList,SetConceptsList] = concepts
    const [Comment,SetComment] = useState(false)
    const [ShowDelete,SetShowDelete] = useState(false)
    const [ShowComment,SetShowComment] = useState(false)
    const [ShowMultiple,SetShowMultiple] = useState(false)
    const [MentionsList,SetMentionsList] = mentions
    const [InARel,SetInARel] = inarel
    const [Tag,SetTag] = useState(false);
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Username,SetUsername] = username
    const [AreasColors,SetAreasColors] = areascolors
    const Colors = ['red','orange','green','blue','purple','pink','black']
    const [Color,SetColor] = useState('rgba(65,105,225,1)')
    const [ColorOver,SetColorOver] = useState('rgba(65,105,225,0.7)')
    const [DocumentDesc,SetDocumentDesc] = documentdescription
    const [TagsSplitted,SetTagsSplitted] = tags_split


    const handleDelete = (event,i) => {
        event.preventDefault();
        event.stopPropagation();
        if(Modality === 2){
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            axios.delete('tag/delete', {data: {mention: props.mention, area: props.tags[i]['tag'].area}})
                .then(response => {
                    // props.setconcepts(false)
                    let tags = []
                    response.data['tags'].map(c => {
                        if (!(c['tag']['area'] === props.tags[i]['tag'].area && props.tags[i].start === c.start && props.tags[i].stop === c.stop)) {
                            tags.push(c)
                        }
                    })
                    if (i === 0) {
                        SetShowDelete(false)

                    }
                    SetTagsSplitted(tags)
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
            if(props.tags.length===1){
                let area = props.tags[0]['tag']['area']
                let color_0 = null;
                if (AreasColors[area]){
                    color_0 = AreasColors[area]

                }


                if(color_0 === null) {
                    color_0 = 'rgba(65,105,225,1)'
                    //window.localStorage.setItem(area, color_0)
                }


                let color_1 = color_0.replace('1)', '0.7)')

                SetColor(color_0)
                SetColorOver(color_1)
            }
            else if(props.tags.length > 1){
                let color_0 = 'rgba(50,50,50,1)'

                let color_1 = color_0.replace('1)', '0.7)')

                SetColor(color_0)
                SetColorOver(color_1)
            }

        // }


    },[AreasColors,props.tags,TagsSplitted])


    const CustomChip = styled(Chip)({
        fontSize:12,
        height:22,
        maxWidth:200,
        backgroundColor: 'white',
        border:'solid 1px',
        color:Color,
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
            color:Color,
            backgroundColor: 'white',
        },
        "& .MuiChip-deleteIcon:hover": {
            height:20,
            color:'white',
            backgroundColor: Color,
        },
    });


    useEffect(() => {
        if(Tag){
            if (props.mention && props.mention.mention_text) {
                delete props.mention.mention_text;
            }
            axios.get('tag/comment',{params:{tag:Tag,mention:props.mention}})
                .then(response=>{

                    SetComment(response.data['comment'] === '' ? false : response.data['comment'])
                })
        }else{
            SetComment(false)
            SetShowComment(false)
        }




    }, [Tag]);

    useEffect(() => {
        if(!ShowComment){
            SetComment(false)
            SetTag(false)
        }
    }, [ShowComment]);

    function uploadComment(){
        if(Tag){
            var comment = document.getElementById("comment").value
            axios.post('tag/comment',{tag:Tag,comment:comment,mention:props.mention})
                .then(response=>{

                    SetShowComment(false)
                    SetComment(false)
                    SetTag(false)
                })
        }


    }


    return (
        <div style={{textAlign: 'center'}}>
{/*
            {ShowComment & Tag && <CommentTag tag={Tag} mention={props.mention} />}
*/}

            {((props.tags && props.tags.length >= 1 && Color && ColorOver && !InARel)) &&
                <>{props.tags.map(tag =>
                    <span>

                        {CurAnnotator === Username ?
                            <CustomChip
                                label={tag['tag'].area}
                                onDelete={(e) => handleDelete(e, 0)}
                                onClick={(e) => {
                                    e.preventDefault()
                                    SetTag(tag['tag'].area)
                                    SetShowComment(prev => !prev)
                                }}/> :
                            <CustomChip
                                label={tag['tag'].area }
                                onClick={(e) => {
                                    e.preventDefault()
                                    SetTag(tag['tag'].area)
                                    SetShowComment(prev => !prev)
                                }}/>}
                    </span>
                )
                }</>
            }
  {/*          {props.tags && props.tags.length > 1 && Color && ColorOver && !InARel &&
                <div style={{textAlign: 'center'}}>
                    <CustomChip label={props.tags.length} color="primary" onClick={() => SetShowMultiple(prev => !prev)}
                    />
                </div>}*/}
            {((props.tags && props.tags.length >= 1 && Color && ColorOver && InARel)) &&
                <div style={{textAlign: 'center'}}>
                    {props.tags.map(tag =>
                        <span>
                    <ChipRel role={props.role} variant = {(props.role.toLowerCase() === 'source' || props.role.toLowerCase() === 'predicate' || props.role.toLowerCase() === 'target') ? "filled":"outlined"} color={Color} label={tag['tag'].area } />
                        </span>)}
                </div>}
      {/*      {props.tags && props.tags.length > 1 &&  Color && ColorOver && InARel &&
            <div className='concepts'>
                <ChipRel role={props.role} variant = {(props.role.toLowerCase() === 'source' || props.role.toLowerCase() === 'predicate' || props.role.toLowerCase() === 'target') ? "filled":"outlined"} color={Color} label={props.tags.length}  />
            </div>}*/}


            {ShowDelete &&
            <Dialog
                open={ShowDelete}
                onClose={()=>SetShowDelete(false)}

                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Delete tag
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Are you sure you want to delete the tag <b>{props.tags[0]['tag'].area}</b>?
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
            }
            {ShowComment &&   <Dialog
                open={ShowComment}
                onClose={(e)=> {
                    e.preventDefault()
                    SetShowComment(false)
                    SetComment(false)
                    SetTag(false)
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
                        SetTag(false)
                    }}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>}

            {ShowMultiple &&
            <Dialog
                open={ShowMultiple}
                onClose={()=>SetShowMultiple(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
                maxWidth={'sm'}
                fullWidth={'sm'}
            >

                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        {props.tags.map((c,i)=><div>
                            <Tooltip title="Delete tag">
                            <span style={{display:"inline", float:'right'}}>
                                <IconButton aria-label="delete" color = 'error' onClick={(e)=>handleDelete(e,i)}>
                              <DeleteIcon />
                            </IconButton>

                            </span></Tooltip>
                            <div>

                                <div style={{marginBottom:'3%'}}>
                                    {c['tag'].area}
                                </div><hr/>
                            </div>

                        </div>)}
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={()=> {SetShowMultiple(false);}}>
                        Close
                    </Button>
                    {/*<Button onClick={(e)=>{handleDelete(e)}} autoFocus>*/}
                    {/*    Agree*/}
                    {/*</Button>*/}
                </DialogActions>
            </Dialog>
            }
        </div>

    )
}