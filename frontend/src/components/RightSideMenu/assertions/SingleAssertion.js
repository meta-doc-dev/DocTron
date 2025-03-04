import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";

import axios from "axios";
import {ButtonGroup, Collapse} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import EditIcon from '@mui/icons-material/Edit';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, styled} from "@mui/material/styles";
import '../rightsidestyles.css'
import {
    clearMentionsFromBorder,
    DeleteRange,
    highlightMention,
    recomputeColor, RemovehighlightMention
} from "../../HelperFunctions/HelperFunctions";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";

import 'bootstrap/dist/css/bootstrap.min.css';
import '../rightsidestyles.css'

import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Snackbar from '@mui/material/Snackbar';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import Chip from "@mui/material/Chip";

import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import {createTheme, ThemeProvider} from "@mui/material/styles";

import ClearIcon from '@mui/icons-material/Clear';
import MuiAlert from '@mui/material/Alert';
import {ArrowContext} from "../../Document/DocumentFinal_2";
import {ConceptContext} from "../../../BaseIndex";

export default function SingleAssertion(props){
    const { username,showmentionsspannel,relationship,source,sourcetext,sourceconcepts,targettext,targetconcepts,predicatetext,predicateconcepts,target,inarel,firstsel,currentdiv,secondsel,mentiontohighlight,startrange,endrange } = useContext(AppContext);
    const [Relationship,SetRelationship] = relationship
    const [SourceDescription,SetSourceDescription] = useState(false)
    const [PredicateDescription,SetPredicateDescription] = useState(false)
    const [ObjectDescription,SetObjectDescription] = useState(false)

    const roletheme = createTheme({
        palette: {
            Source: {
                main: 'rgb(214, 28, 78)',
                contrastText: '#fff',
            },
            Predicate: {
                main: 'rgb(55, 125, 113)',
                contrastText: '#fff',
            },
            Target: {
                main: 'rgb(241, 136, 103)',
                contrastText: '#fff',
            },
            neutro: {
                main: props.color,
                contrastText: '#fff',
            },
        },
    });

    // RENDERE RELATION DOPO CHIAMATA GET

    return (
        <div>
            <Collapse in={props.open}>
                <div  style={{fontSize:'small'}}>
                    {Relationship ? <>
                        <ThemeProvider theme={roletheme}>
                            <div style={{marginTop:'5px',marginBottom:'5px'}}>

                        <span><Chip size='small' variant={'filled'} color={'Source'} label={'Subject'}
                                    onClick={() => SetSourceDescription(prev => !prev)}/></span>{'  '}
                                <span>{Relationship['subject']['concept']['concept_name']}</span>


                            </div>
                            {SourceDescription && <div>
                                <a href={Relationship['subject']['concept']['concept_name']}>{Relationship['subject']['concept']['concept_name']}</a>
                            </div>}
                            <div style={{marginTop:'5px',marginBottom:'5px'}}>
                    <span><Chip size='small'  variant={'filled'} color={'Predicate'} label={'Predicate'}
                                onClick={() => SetPredicateDescription(prev => !prev)}/></span>{'  '}
                                <span>{Relationship['predicate']['concept']['concept_name']}</span>

                            </div>
                            {PredicateDescription && <div>
                                <a href={Relationship['predicate']['concept']['concept_url']}>{Relationship['predicate']['concept']['concept_url']}</a>
                            </div>}
                            <div style={{marginTop:'5px',marginBottom:'5px'}}>
                    <span><Chip size='small'  variant={'filled'} color={'Target'} label={'Object'}
                                onClick={() => SetObjectDescription(prev => !prev)}/></span>{'  '}
                                <span>{Relationship['object']['concept']['concept_name']}</span>

                            </div>
                            {ObjectDescription && <div>
                                <a href={Relationship['object']['concept']['concept_url']}>{Relationship['object']['concept']['concept_url']}</a>
                            </div>}
                            <hr/>
                            <div>
                                <span><b>Insertion datetime:{' '}</b></span>
                                <span>{props.time}</span>
                            </div>
                            <div>
                                <span><b>Annotators:{' '}</b></span>
                                <span>{props.count}</span>
                            </div>
                            <hr/></ThemeProvider>
                    </>: <CircularProgress />}



                </div>
            </Collapse>
        </div>


    )
}