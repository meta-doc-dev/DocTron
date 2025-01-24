import axios from "axios";
import {ButtonGroup, Collapse} from "@material-ui/core";
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
import {AppContext} from "../../../App";
import {createTheme, ThemeProvider} from "@mui/material/styles";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
import Button from "@mui/material/Button";
import LabelSlider from "./LabelSlider";
import LabelsRadio from "./LabelsRadio";

const checkedIcon = <CheckBoxIcon fontSize="small"/>;


export default function LabelsClass(props) {
    const {
        view,
        document_id,
        labels,
        modality,
        annotationtype,
        snackmessage,
        opensnack,
        curannotator,
        username,
        inarel,
        labelstosave,
        annotatedlabels
    } = useContext(AppContext);
    const [Labels, SetLabels] = labels
    const [NotAdded, SetNotAdded] = useState([])
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [Username, SetUsername] = username
    const [Loading, SetLoading] = useState(false)
    const [SnackMessage, SetSnackMessage] = snackmessage;
    const [OpenSnack, SetOpenSnack] = opensnack
    const [Modality, SetModality] = modality
    const [View, SetView] = view
    const [InARel, SetInARel] = inarel
    const [AnnotationType, SetAnnotationType] = annotationtype
    const [ShowList, SetShowList] = useState(AnnotationType === 'Graded labeling')




    useEffect(() => {
        if (AnnotatedLabels) {
            const labs = Object.entries(AnnotatedLabels).map(([key]) => key);
            var notadded = Labels['labels'].filter(o => labs.indexOf(o) === -1)
            SetNotAdded(notadded)
        }


    }, [AnnotatedLabels])


    const labelstheme = createTheme({
        palette: {
            added: {
                main: 'rgb(103, 148, 54)',
                contrastText: '#fff',
            },
            not_added: {
                main: 'rgb(66, 122, 161)',
                contrastText: '#fff',
            },

        },
    });

    return (
        <div>

            <Button disabled={View === 4 || InARel} onClick={() => SetShowList(prev => !prev)} variant="text">Labels</Button>
            <Collapse in={ShowList && !InARel}>
                <div>Click on the slider to set the grade for each label</div>
                <div style={{fontSize:'1rem'}}>
                    {AnnotatedLabels ? <ThemeProvider theme={labelstheme}>
                        {Labels['labels'].map((o, i) =>
                                <div>
                                    {parseInt(Labels['values'][i][1]) - parseInt(Labels['values'][i][0]) + 1 > 5 ? <LabelSlider label={o} details = {Labels['details'][i]} value={AnnotatedLabels[o] !== undefined ? AnnotatedLabels[o] : null} min={Labels['values'][i][0]} max={Labels['values'][i][1]} type_lab={'label'}/> :
                                        <LabelsRadio  label={o} details = {Labels['details'][i]}  value={AnnotatedLabels[o] !== undefined ? AnnotatedLabels[o] : null} min={Labels['values'][i][0]} max={Labels['values'][i][1]} type_lab={'label'}/> }

                                </div>

                        )}

                    </ThemeProvider> : <div className='loading'>
                        <CircularProgress/>
                    </div>}


                </div>
            </Collapse>


        </div>
    );
}