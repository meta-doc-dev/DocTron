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

export default function MentionsListClass(props) {
    const {view, labels, mentions,inarel, curannotator,username,concepts,annotationtypes, tags_split, documentdescription} = useContext(AppContext);

    const [MentionsList, SetMentionsList] = mentions
    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [Username, SetUsername] = username
    const [Labels, SetLabels] = labels
    const [ConceptsList, SetConceptsList] = concepts
    const [DocumentDesc, SetDocumentDesc] = documentdescription

    const [TagsSplitted, SetTagsSplitted] = tags_split

    const sorted_mentions = MentionsList.sort(function (a, b) {
        return a.start - b.start;
    })

    const [View, SetView] = view
    const [InARel, SetInARel] = inarel
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes

    const [ShowList, SetShowList] = useState(AnnotationTypes.includes('Passages annotation'))

    const [MentionsListHigh, SetMentionsListHigh] = useState([])




    return (
        <div id='rightsidementionsclass'>
            <Button disabled={View === 4 || InARel} onClick={() => SetShowList(prev => !prev)}
                    variant="text">Passages <i>({MentionsList.length})</i></Button>

            <Collapse in={ShowList && !InARel}>
                <div>
                    {MentionsList ? <>

                            {sorted_mentions.map((mention, index) =>
                                <div>

                                    <div id={mention.mentions} style={{margin: "5% 0"}}><RightSideMention
                                        testo={mention.mention_text} listhigh={MentionsListHigh}
                                        setlisthigh={SetMentionsListHigh}
                                        mention={mention} index={index}/></div>

                                    <Collapse in={MentionsListHigh.filter(x=> x[0] === mention.start && x[1] === mention.stop).length > 0}>
                                        <div>

                                            {Labels['labels_passage'].map((o, i) =>
                                                <div>
                                                    {parseInt(Labels['values_passage'][i][1]) - parseInt(Labels['values_passage'][i][0]) + 1 > 5 ?
                                                        <LabelSlider label={o}
                                                                     details={Labels['details_passage'][i]}
                                                                     value={mention['labels'][o]}                                                                     mention={mention}
                                                                     mention={mention}
                                                                     min={Labels['values_passage'][i][0]}
                                                                     max={Labels['values_passage'][i][1]}
                                                                     type_lab={'passage'}/> :
                                                        <LabelsRadio label={o}
                                                                     details={Labels['details_passage'][i]}
                                                                     value={mention['labels'][o]}
                                                                     mention={mention}
                                                                     min={Labels['values_passage'][i][0]}
                                                                     max={Labels['values_passage'][i][1]}
                                                                     type_lab={'passage'}/>}

                                                </div>
                                            )}
                                            {CurAnnotator === Username && <Button color={'error'} size={'small'} variant={'outlined'}
                                                     onClick={() => {
                                                         axios.delete('mentions/delete', {
                                                             data: {
                                                                 start: mention.start,
                                                                 stop: mention.stop,
                                                                 mention_text: mention.mention_text,
                                                                 position: mention.position
                                                             }
                                                         })
                                                             .then(response => {

                                                                 SetDocumentDesc(response.data['document'])
                                                                 SetMentionsList(response.data['mentions'])
                                                                 SetConceptsList(response.data['concepts'])
                                                                 SetTagsSplitted(response.data['tags'])
                                                                 var m = MentionsListHigh.filter(x => x[0] !== mention.start && x[1] !== mention.stop)
                                                                 SetMentionsListHigh(m)


                                                             })
                                                     }}>Delete passage</Button>}
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