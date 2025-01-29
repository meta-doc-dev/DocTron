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
import '../rightsidestyles.css'
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
import Paper from "@mui/material/Paper";
import {styled} from '@mui/material/styles';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import Box from '@mui/material/Box';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import {AppContext} from "../../../App";
import IconButton from "@mui/material/IconButton";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
import RightSideMention from "./RightSideMention";
import {RemovehighlightMention} from "../../HelperFunctions/HelperFunctions";
import LabelsRadio from "../labels/LabelsRadio";
import LabelSlider from "../labels/LabelSlider";
import GitHubIcon from "@mui/icons-material/GitHub";
import CommentIcon from "@mui/icons-material/Comment";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";

export default function PointsListClass(props) {
    const {view, labels, mentions,inarel,pointhigh,points, concepts,annotationtypes, tags_split, documentdescription} = useContext(AppContext);
    const [ShowComment,SetShowComment] = useState(false)
    const [OpenComment,SetOpenComment] = useState(false)
    const [MentionsList, SetMentionsList] = mentions
    const [Points, SetPoints] = points
    const [Labels, SetLabels] = labels
    const [Comment,SetComment] = useState(false)
    const [ConceptsList, SetConceptsList] = concepts
    const [DocumentDesc, SetDocumentDesc] = documentdescription
    const [PointHigh,SetPointHigh] = pointhigh
    const [TagsSplitted, SetTagsSplitted] = tags_split

    const sorted_mentions = MentionsList.sort(function (a, b) {
        return a.start - b.start;
    })

    const [View, SetView] = view
    const [InARel, SetInARel] = inarel
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes

    const [ShowList, SetShowList] = useState(AnnotationTypes.includes('Object detection'))

    const [MentionsListHigh, SetMentionsListHigh] = useState([])

    useEffect(() => {
        var elements = document.getElementsByClassName(`points_class`)
        for(var i = elements.length - 1; i >= 0; i--){
            elements[i].classList.remove('selected_point');
        }
        if(PointHigh) {
            var idx = Points['points'].indexOf(PointHigh)
            var div_sel = document.getElementById(`points_${idx}`)
            div_sel.classList.add('selected_point');
        }
    }, [PointHigh,Points]);

    function uploadComment(){
        if(OpenComment){
            var rel = {}

            var comment = document.getElementById("comment").value
            axios.post('object_detection/comment',{points:OpenComment,comment:comment})
                .then(response=>{

                    SetShowComment(false)
                    SetComment(false)
                    SetOpenComment(false)
                })
        }
    }

    useEffect(() => {
        if(OpenComment){
            axios.get('object_detection/comment',{params:{points:OpenComment}})
                .then(response=>{

                    SetComment(response.data['comment'] === '' ? false : response.data['comment'])
                })
        }else{
            SetComment(false)
            SetShowComment(false)
        }




    }, [OpenComment]);

    return (
        <div id='rightsidementionsclass'>

            {ShowComment &&   <Dialog
                open={ShowComment}
                onClose={(e)=> {
                    e.preventDefault()
                    SetShowComment(false)
                    SetComment(false)
                    SetOpenComment(false)
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
                        SetOpenComment(false)
                    }}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>}







            <Button disabled={View === 4} onClick={() => SetShowList(prev => !prev)}
                    variant="text">Objects <i>({Points['points'].length})</i></Button>

            <Collapse in={ShowList}>
                <div>
                    {Points ? <>

                            {Points['points'].map((point, index) =>
                                <div>

                                    <div onClick={()=> {
                                        if(PointHigh === point) {
                                            SetPointHigh(false)
                                        }else {
                                            SetPointHigh(point)
                                        }
                                    }} className={'points_class'} id={`points_${index}`}   style={{margin: "5% 0"}}>Object  {index +1}</div>
                                    <div style={{display:"inline-block"}}>
                                        <IconButton fontSize={'large'} aria-label="comment" onClick={() => {
                                            SetOpenComment(point)
                                            SetShowComment(true)
                                            console.log('comment object')
                                        }}>
                                            <CommentIcon /></IconButton>
                                        <IconButton fontSize={'large'} aria-label="remove" onClick={() => {
                                            axios.delete('object_detection',{data:{points:point}})
                                                .then(response => SetPoints(response.data))
                                                .catch(error => console.log(error))
                                        }}>
                                            <DeleteIcon />
                                        </IconButton>


                                    </div>
                                    <Collapse in={PointHigh === point}>
                                        <div>

                                            {Labels['labels_passage'].map((o, i) =>
                                                <div>
                                                    {parseInt(Labels['values_passage'][i][1]) - parseInt(Labels['values_passage'][i][0]) + 1 > 5 ?
                                                        <LabelSlider label={o}
                                                                     points={point}
                                                                     value={Points['values'][index][o]}
                                                                     details={Labels['details_passage'][i]}
                                                                     min={Labels['values_passage'][i][0]}
                                                                     max={Labels['values_passage'][i][1]}
                                                                     type_lab={'obj'}/> :
                                                        <LabelsRadio label={o}
                                                                     points={point}
                                                                     value={Points['values'][index][o]}
                                                                     details={Labels['details_passage'][i]}
                                                                     min={Labels['values_passage'][i][0]}
                                                                     max={Labels['values_passage'][i][1]}
                                                                     type_lab={'obj'}/>}

                                                </div>
                                            )}

                                            <hr/>
                                        </div>
                                    </Collapse>


                                </div>
                            )}

                        </>
                        : <CircularProgress/>}
                </div>
            </Collapse>


        </div>
    );
}