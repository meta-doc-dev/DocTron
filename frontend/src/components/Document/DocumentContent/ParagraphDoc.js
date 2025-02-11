import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
// import Draggable from 'react-draggable';

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

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import EditIcon from '@mui/icons-material/Edit';

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';

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

import AddIcon from '@mui/icons-material/Add';
import Collapse from "@mui/material/Collapse";
import Paper from "@mui/material/Paper";
import '../document.css'
// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";
import {type} from "@testing-library/user-event/dist/type";
import {waitForElm} from "../../HelperFunctions/HelperFunctions";

export default function ParagraphDoc(props) {

    useEffect(() => {

    }, [props.testo])

    return (
        <>
            {props.chiave.endsWith('_key') && props.chiave !== 'title_key' &&
                <span className='no_men key' id={props.id}>{props.testo}</span>}
            {props.chiave === 'title_value' && <span className='no_men title_value' id={props.id}>{props.testo}</span>}
            {props.chiave !== 'title_value' && props.chiave.endsWith('value') && props.chiave.endsWith('_value') &&
                <span className='no_men' id={props.id}>
                {props.testo.replace('<br>', '\n')}

                </span>}


        </>

    )

}
