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
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;

const checkedIcon = <CheckBoxIcon fontSize="small" />;

import { HuePicker,SliderPicker   } from 'react-color';
import {AppContext} from "../../App";

export default function ColorTagsAreas(props){
    const [Update,SetUpdate] = useState(false);
    const [Color,SetColor] = useState('')

    useEffect(()=>{
        if(props.colors[props.tag]){
            SetColor(rgbToHex(props.colors[props.tag]))
        }else{
            SetColor(rgbToHex('rgba(65,105,225,1)'))
        }
    },[])

    useEffect(() => {
        if (Update ) {
            updateColor(props.tag,Color);
        }
    }, [Update]);


    function updateArea(color,tag){
        let areas = {}

        Object.keys(props.colors).map(a=>areas[a] = props.colors[a])
        areas[tag] = color
        props.setcolors(areas)
        return areas

    }
    const updateColor = (tag,color) => {
        let color_str_0 = null
        if(color instanceof Object){
            color_str_0 = 'rgba('+color.rgb.r+','+color.rgb.g + ','+color.rgb.b+', 1)'
            SetColor(rgbToHex(color_str_0))
        }else{
            color_str_0 = hexToRgb(color)

        }

        var areas = updateArea(color_str_0,tag)
        axios.post('collection_options',{collection:props.collection.id,options:areas})
            .then(response => {SetUpdate(false)})
    }

    function rgbToHex(rgb) {
        // Estrai i valori di r, g, b dalla stringa "rgb(r, g, b)"
        if(rgb){
            const rgbArray = rgb.match(/\d+/g); // Estrai solo i numeri (r, g, b)

            // Converti ogni valore a esadecimale e assicurati che abbia 2 cifre
            const red = parseInt(rgbArray[0]).toString(16).padStart(2, '0');
            const green = parseInt(rgbArray[1]).toString(16).padStart(2, '0');
            const blue = parseInt(rgbArray[2]).toString(16).padStart(2, '0');

            // Restituisci la stringa esadecimale completa
            return `#${red}${green}${blue}`;
        }

    }
    function hexToRgb(hex) {
        // Estrai i valori di r, g, b dalla stringa "rgb(r, g, b)"
        if(hex){
            hex = hex.replace(/^#/, '');

            // Se il formato è corretto (6 caratteri esadecimali)
            if (hex.length === 6) {
                // Estrai i componenti RGB come coppie di caratteri
                const r = parseInt(hex.slice(0, 2), 16);
                const g = parseInt(hex.slice(2, 4), 16);
                const b = parseInt(hex.slice(4, 6), 16);

                // Restituisci il risultato in formato RGB
                return `rgba(${r}, ${g}, ${b}, 1)`;
            } else {
                throw new Error('Formato esadecimale non valido');
            }
        }

    }

    return(
        <div>
            <Row><Col
                md={3}>{props.tag}</Col> <Col md={6}>
                <SliderPicker onChangeComplete={(color) => {
                    SetColor(color)
                    SetUpdate(true)
                }}
                              color={props.colors[props.tag]}
                />
            </Col>
                <Col md={3}>
                    <TextField
                        id="hex_color"
                        label="HEX Color"
                        value={Color}
                        onChange={(event) => {

                            SetColor(event.target.value);
                            if(event.target.value.length === 7 && event.target.value.startsWith('#')){SetUpdate(true)}


                        }}
                    />

                </Col></Row>


        </div>

    );
}
