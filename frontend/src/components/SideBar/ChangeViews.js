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
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import './sidebar.css'
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

import Paper from "@mui/material/Paper";
import { styled } from '@mui/material/styles';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import {AppContext} from "../../App";
import IconButton from "@mui/material/IconButton";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
import { HuePicker,SliderPicker   } from 'react-color';
import {waitForElm} from "../HelperFunctions/HelperFunctions";
import Radio from "@mui/material/Radio";
import DialogContentText from "@mui/material/DialogContentText";
// "react-color": "^3.0.0-beta.3",

export default function ChangeViews(props){
    const { collection,document_id,labels, areascolors,labelstosave,concepts,view } = useContext(AppContext);

    const [value,setValue] = useState(4)
    const [View,SetView] = view

    useEffect(() => {
        setValue(View)
    }, [View]);

    function handleChangeRadio(e){
        e.preventDefault();
        e.stopPropagation()
        console.log(e.target.value)
        let val = parseInt(e.target.value)
        setValue(val)
        SetView(val)
    }







    return(
        <div>

            <h5>Document annotations view</h5>

            <div>
                {['Mentions','Concepts','Tags','All','Empty'].map((m,i)=>
                    <div>

                        <Radio
                            //defaultChecked={i === 3}
                            checked={value === i}
                            onClick={handleChangeRadio}
                            value={i}
                            aria-label={m}
                        />{' '}{m}</div>
                )
                }

            </div>



        </div>

    );
}
