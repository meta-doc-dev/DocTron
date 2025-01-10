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
import InfoIcon from "@material-ui/icons/Info";
import IconButton from "@mui/material/IconButton";
import CommentDialog from "./CommentDialog";
import DetailsDialog from "./DetailsDialog";

function ValueLabelComponent(props) {
    const {children, value} = props;

    return (
        <Tooltip enterTouchDelay={0} placement="top" title={value}>
            {children}
        </Tooltip>
    );
}

ValueLabelComponent.propTypes = {
    children: PropTypes.element.isRequired,
    value: PropTypes.node,
};

const iOSBoxShadow =
    '0 3px 1px rgba(0,0,0,0.1),0 4px 8px rgba(0,0,0,0.13),0 0 0 1px rgba(0,0,0,0.02)';


function AirbnbThumbComponent(props) {
    const {children, ...other} = props;
    return (
        <SliderThumb {...other}>
            {children}
            <span className="airbnb-bar"/>
            <span className="airbnb-bar"/>
            <span className="airbnb-bar"/>
        </SliderThumb>
    );
}

AirbnbThumbComponent.propTypes = {
    children: PropTypes.node,
};


export default function LabelSlider(props) {
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
    const [ShowCommentDialog,SetShowCommentDialog] = useState(false)
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
    const [value, setValue] = useState(null); // Stato locale
    const [OpenDetails,SetOpenDetails] = useState(false)

    useEffect(() => {
        setValue(props.value)
    }, [props.value]);
    const handleChange = (event, newValue) => {
        setValue(newValue); // Aggiorna lo stato
        AdddeleteLabel(event, props.label, newValue)

    };

    function AdddeleteLabel(e, label, score) {
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
                    if (props.type_lab === 'label'){
                        axios.post('labels/insert', {label: label, score: score})
                            .then(response => {


                            })
                    }else if(props.type_lab === 'passage'){
                      console.log('passage')
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


    const marks = [

        {
            value: props.min,
            label: props.min,
        },
        {
            value: props.max,
            label: props.max,
        }
    ];


    return (
        <Box sx={{marginTop: '5%'}}>
            <CommentDialog open={ShowCommentDialog} setopen={SetShowCommentDialog} label={props.label}/>
            <DetailsDialog open={OpenDetails} setopen={SetOpenDetails} label={props.label} details={props.details} />

            <Typography gutterBottom><span>{props.label} <IconButton size={'small'} onClick={()=> {
                if (props.details !== null) {
                    SetOpenDetails(prev => !prev)
                }
            }


                } aria-label="info">
  <InfoIcon fontSize="inherit"/>
</IconButton>: {value !== null ? value : 'not set'}    </span> <span> <Button size={'small'} sx={{textAlign: 'right'}}
                                                                              onClick={() => {
                                                                                  SetShowCommentDialog(prev=>!prev)
                                                                              }}>Comment</Button> </span>


                <span> <Button size={'small'} sx={{textAlign: 'right'}}
                               onClick={() => {
                                   setValue(null)
                                   axios.delete('labels', {data: {label: props.label}})
                                       .then(response => {
                                           SetNotAdded([...NotAdded, props.label])
                                           var labels = Object.entries(AnnotatedLabels).map(([key]) => key).filter(x => x === props.label)
                                           //var labels = AnnotatedLabels.filter(o => o !== props.label)
                                           SetAnnotatedLabels(labels)
                                           SetLoading(false)

                                       })
                               }}>Reset</Button>

            </span>
            </Typography>
            <div onClick={(e) => {
                e.preventDefault()
                if (value === null) {
                    setValue(props.min)
                    AdddeleteLabel(e, props.label, 1)
                }
            }}>
                <Slider marks={marks}
                        sx={value === null ? {
                            width: '70%',
                            '& .MuiSlider-thumb': {
                                backgroundColor: 'blue', // Colore del thumb
                                border: '0px solid red', // Bordo del thumb
                                width: 0, // Dimensioni del thumb
                                height: 0,
                                '&:hover': {
                                    boxShadow: '0px 0px 10px blue', // Effetto hover
                                },
                            },
                        } : {width: '70%'}}
                        valueLabelDisplay="auto"
                        aria-label={props.label}
                        value={value === null ? props.min : value} // Default a props.min per evitare errori
                        max={props.max}
                        min={props.min}
                        onChange={handleChange}

                />
            </div>


        </Box>
    );
}