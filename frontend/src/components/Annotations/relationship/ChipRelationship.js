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

import '../annotation.css'

import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import {DeleteRange,waitForElm} from "../../HelperFunctions/HelperFunctions";
import DeleteMentionModal from "../mentions/modals/DeleteMentionModal";
import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";




export default function ChipRel(props){

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

    const ChipRel = styled(Chip)({
        fontSize:12,
        height:22,
        maxWidth:200,


        // "&:hover": {
        //     // backgroundColor: ColorOver,
        //     color:'white',
        //     "& .MuiChip-deleteIcon": {
        //         height:20,
        //         // color:'white',
        //         // backgroundColor: ColorOver,
        //     },
        // },
        "& .MuiChip-outlined": {
            height:22,
            color:props.color,
            backgroundColor: "white",
        },
        "& .MuiChip-filled": {
            height:22,
            color:"white",
            backgroundColor: props.color,
        },
    });



    return (
        <ThemeProvider theme={roletheme}>
            {/*<ChipRel color={props.role} label={props.role[0]}   />*/}
            <ChipRel variant = {props.variant} color={props.role} label={props.label}   />
        </ThemeProvider>

    )
}