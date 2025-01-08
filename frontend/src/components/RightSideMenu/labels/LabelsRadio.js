import * as React from 'react';
import PropTypes from 'prop-types';
import Slider, { SliderThumb } from '@mui/material/Slider';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import Box from '@mui/material/Box';
import {useContext, useEffect, useState} from "react";
import Button from "@mui/material/Button";
import {AppContext} from "../../../App";
import axios from "axios";
import FormControlLabel from "@mui/material/FormControlLabel";
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";




export default function LabelsRadio(props) {
    const {
        view,
        document_id,
        labels,
        modality,
        annotationtypes,
        snackmessage,
        opensnack,
        curannotator,
        username,
        inarel,
        labelstosave,
        annotatedlabels
    } = useContext(AppContext);
    const [ShowList, SetShowList] = useState(true)
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
    const [AnnotationTypes, SetAnnotationTypes] = annotationtypes
    const [value, setValue] = useState(props.value); // Stato locale

    const handleChange = (event) => {
        var val = event.target.value
        setValue(val);
        if (val === 'true'){
            val = 0
        }else if(val === 'false'){
            val = 1
        }else{
            val = parseInt(val)
        }
         // Aggiorna lo stato
        AdddeleteLabel(event,props.label,val)

    };
    function AdddeleteLabel(e,label,score) {
        e.preventDefault()
        if (Modality === 2 || View === 4) {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'You cannot annotate this document'})
        } else if (AnnotationTypes.indexOf('Labels annotation') === -1) {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Labels annotation is not allowed here'})
        } else {
            if (CurAnnotator === Username) {
                if (score !== null) {

                    axios.post('labels/insert', {label: label,score: score})
                        .then(response => {


                        })

                } else {
                    axios.delete('labels', {data: {label: label}})
                        .then(response => {


                        })

                }
            } else {
                if (score !== null) {
                    axios.post('labels/copy', {label: label}).then(res => console.log(res)).catch(error => console.log(error))
                    SetLoading(false)

                }

            }
        }


    }

    function creaArray(min, max) {
        let array = [];
        for (let i = parseInt(min); i <= parseInt(max); i++) {
            array.push(i);
        }
        if(parseInt(min) === 0 && parseInt(max) === 1 ) {
            return ['true','false']
        }
        return array;
    }


    return (
        <Box sx={{marginTop:'5%'}}>
            <div><span>{props.label}: {value !== null ? value : 'not set'}    </span>  <span> <Button size={'small'} sx={{textAlign:'right'}} onClick={()=>setValue(null)}>Reset</Button>
            </span></div>
            <FormControl>

                <RadioGroup
                    row
                    onChange={handleChange}
                    aria-labelledby={props.label}
                    name={props.label}
                >

                    {creaArray(props.min, props.max).map(el=><FormControlLabel value={el} control={<Radio size="small"/>} label={el}/>)}


                </RadioGroup>
            </FormControl>



        </Box>
    );
}