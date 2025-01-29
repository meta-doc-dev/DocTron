import * as React from 'react';
import PropTypes from 'prop-types';
import Slider, {SliderThumb} from '@mui/material/Slider';
import {styled} from '@mui/material/styles';
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
import IconButton from "@mui/material/IconButton";
import InfoIcon from "@material-ui/icons/Info";
import CommentDialog from "./CommentDialog";
import DetailsDialog from "./DetailsDialog";


export default function LabelsRadio(props) {
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
    const [ShowList, SetShowList] = useState(true)
    const [ShowCommentDialog, SetShowCommentDialog] = useState(false)
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

    const [AnnotationType, SetAnnotationType] = annotationtype
    const [OpenDetails,SetOpenDetails] = useState(false)
    const [value, setValue] = useState(null); // Stato locale

    useEffect(() => {
        setValue(props.value)
    }, [props.value]);
    const handleChange = (event) => {
        var val = event.target.value
        setValue(val);
        if (val === 'true') {
            val = 0
        } else if (val === 'false') {
            val = 1
        } else {
            val = parseInt(val)
        }
        // Aggiorna lo stato
        AdddeleteLabel(event, props.label, val)

    };

    function mapKey(element) {
        if (props.min === 0 && props.max === 1) {
            if (element === 1) {
                return 'false'
            } else if (element === 0) {
                return 'true'
            }
        } else if (element === null) {
            return null
        } else {
            return parseInt(element)
        }
    }

    function AdddeleteLabel(e, label, score) {
        e.preventDefault()
        if (Modality === 2 || View === 4) {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'You cannot annotate this document'})
        } else if (AnnotationType !== 'Graded labeling' && AnnotationType !== 'Passages annotation' &&  AnnotationType !== 'Object detection') {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Labeling is not allowed here'})
        } else {
            if (CurAnnotator === Username) {
                if (score !== null) {
                    if (props.type_lab === 'label') {
                        axios.post('labels/insert', {label: label, score: score})
                            .then(response => {


                            })
                    } else if (props.type_lab === 'passage') {
                        console.log('passage')
                        axios.post('labels/insert', {label: label, score: score,mention:props.mention})
                            .then(response => {


                            })
                    }
                    else if (props.type_lab === 'obj') {
                        console.log('object detection')
                        axios.post('labels/insert', {label: label, score: score,points:props.points})
                            .then(response => {


                            })
                    }


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
        return array;
    }


    return (
        <Box sx={{marginTop: '5%'}}>
            {ShowCommentDialog && <CommentDialog open={ShowCommentDialog} setopen={SetShowCommentDialog} mention={props.mention ? props.mention : null} points={props.points ? props.points : null} label={props.label} type={'passage'}/>}
            <DetailsDialog open={OpenDetails} setopen={SetOpenDetails} label={props.label} details={props.details} />


            <div><span>{props.label} </span>
                {props.type_anno !== 'quick' && <><span> <IconButton size={'small'} onClick={()=> {
                if (props.details !== null) {
                    SetOpenDetails(prev => !prev)
                }
            }


            } aria-label="info">
  <InfoIcon fontSize="inherit"/>
</IconButton>: {mapKey(value) !== null ? mapKey(value) : 'not set'}    </span> <span> <Button size={'small'}
                                                                                              sx={{textAlign: 'right'}}
                                                                                              onClick={() => {
                                                                                                  SetShowCommentDialog(prev => !prev)
                                                                                              }}>Comment</Button> </span><span> <Button
                size={'small'}
                sx={{textAlign: 'right'}}
                onClick={() => {
                    setValue(null)
                    if(props.type_lab === 'passage') {
                        axios.delete('labels', {data: {label: props.label,start:props.mention.start,stop:props.mention.stop}})
                            .then(response => {
                                SetNotAdded([...NotAdded, props.label])
                                var labels = Object.entries(AnnotatedLabels).map(([key]) => key).filter(x => x === props.label)
                                SetAnnotatedLabels(labels)
                                SetLoading(false)

                            })
                    }else if(props.type_lab === 'obj') {
                        axios.delete('labels', {data: {label: props.label,points:props.points}})
                            .then(response => {
                                SetNotAdded([...NotAdded, props.label])
                                var labels = Object.entries(AnnotatedLabels).map(([key]) => key).filter(x => x === props.label)
                                SetAnnotatedLabels(labels)
                                SetLoading(false)

                            })
                    }else {
                        axios.delete('labels', {data: {label: props.label}})
                            .then(response => {
                                SetNotAdded([...NotAdded, props.label])
                                var labels = Object.entries(AnnotatedLabels).map(([key]) => key).filter(x => x === props.label)
                                SetAnnotatedLabels(labels)
                                SetLoading(false)

                            })
                    }


                }}>Reset</Button>
            </span></>}</div>
            <FormControl>

                <RadioGroup
                    row
                    onChange={handleChange}
                    aria-labelledby={props.label}
                    value={value}
                    name={props.label}
                >

                    {creaArray(props.min, props.max).map(el => <FormControlLabel value={el}
                                                                                 control={<Radio size="small"/>}
                                                                                 label={mapKey(el)}/>)}


                </RadioGroup>
            </FormControl>

        </Box>
    );
}