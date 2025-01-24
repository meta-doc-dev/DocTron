import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";

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

// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import DraggableModal from "../concepts/DraggableConceptModal";
import {DeleteRange} from "../../HelperFunctions/HelperFunctions";
import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";
import ReplayCircleFilledIcon from '@mui/icons-material/ReplayCircleFilled';
import {ArrowContext} from "../../Document/DocumentFinal_2";
import RelationshipModal from "../concepts/RelationshipConceptModal";
import {ConceptContext} from "../../../BaseIndex";
import DescriptionDialog from "../concepts/DescriptionDialog";
export default function OverlayRelComponent(props){
    const { username,inarel,predicate,source,relationshipslist,sourcetext,sourceconcepts,targettext,targetconcepts,predicatetext,predicateconcepts,firstsel,secondsel,collection,mentions,addconceptmodal,mentiontohighlight,startrange,endrange } = useContext(AppContext);

    const [InARel,SetInARel] = inarel;

    const [RelationshipsList,SetRelationshipsList] = relationshipslist


    return (
        <>{InARel &&
            <div>


                    <Chip label={props.label} size="small" color="info" onClick={(e) => {
                        e.preventDefault()
                        SetRelationship(RelationshipsList[props.index])
                    }} variant="contained"/>





            </div>
        }</>
    )
}