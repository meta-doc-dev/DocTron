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

function ValueLabelComponent(props) {
    const { children, value } = props;

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

const IOSSlider = styled(Slider)(({ theme }) => ({
    color: '#007bff',
    height: 5,
    padding: '15px 0',
    '& .MuiSlider-thumb': {
        height: 20,
        width: 20,
        backgroundColor: '#fff',
        boxShadow: '0 0 2px 0px rgba(0, 0, 0, 0.1)',
        '&:focus, &:hover, &.Mui-active': {
            boxShadow: '0px 0px 3px 1px rgba(0, 0, 0, 0.1)',
            // Reset on touch devices, it doesn't add specificity
            '@media (hover: none)': {
                boxShadow: iOSBoxShadow,
            },
        },
        '&:before': {
            boxShadow:
                '0px 0px 1px 0px rgba(0,0,0,0.2), 0px 0px 0px 0px rgba(0,0,0,0.14), 0px 0px 1px 0px rgba(0,0,0,0.12)',
        },
    },
    '& .MuiSlider-valueLabel': {
        fontSize: 12,
        fontWeight: 'normal',
        top: -6,
        backgroundColor: 'unset',
        color: theme.palette.text.primary,
        '&::before': {
            display: 'none',
        },
        '& *': {
            background: 'transparent',
            color: '#000',
            ...theme.applyStyles('dark', {
                color: '#fff',
            }),
        },
    },
    '& .MuiSlider-track': {
        border: 'none',
        height: 5,
    },
    '& .MuiSlider-rail': {
        opacity: 0.5,
        boxShadow: 'inset 0px 0px 4px -2px #000',
        backgroundColor: '#d0d0d0',
    },
    ...theme.applyStyles('dark', {
        color: '#0a84ff',
    }),
}));

const PrettoSlider = styled(Slider)({
    color: '#52af77',
    height: 8,
    '& .MuiSlider-track': {
        border: 'none',
    },
    '& .MuiSlider-thumb': {
        height: 24,
        width: 24,
        backgroundColor: '#fff',
        border: '2px solid currentColor',
        '&:focus, &:hover, &.Mui-active, &.Mui-focusVisible': {
            boxShadow: 'inherit',
        },
        '&::before': {
            display: 'none',
        },
    },
    '& .MuiSlider-valueLabel': {
        lineHeight: 1.2,
        fontSize: 12,
        background: 'unset',
        padding: 0,
        width: 32,
        height: 32,
        borderRadius: '50% 50% 50% 0',
        backgroundColor: '#52af77',
        transformOrigin: 'bottom left',
        transform: 'translate(50%, -100%) rotate(-45deg) scale(0)',
        '&::before': { display: 'none' },
        '&.MuiSlider-valueLabelOpen': {
            transform: 'translate(50%, -100%) rotate(-45deg) scale(1)',
        },
        '& > *': {
            transform: 'rotate(45deg)',
        },
    },
});

const AirbnbSlider = styled(Slider)(({ theme }) => ({
    color: '#3a8589',
    height: 3,
    padding: '13px 0',
    '& .MuiSlider-thumb': {
        height: 27,
        width: 27,
        backgroundColor: '#fff',
        border: '1px solid currentColor',
        '&:hover': {
            boxShadow: '0 0 0 8px rgba(58, 133, 137, 0.16)',
        },
        '& .airbnb-bar': {
            height: 9,
            width: 1,
            backgroundColor: 'currentColor',
            marginLeft: 1,
            marginRight: 1,
        },
    },
    '& .MuiSlider-track': {
        height: 3,
    },
    '& .MuiSlider-rail': {
        color: '#d8d8d8',
        opacity: 1,
        height: 3,
        ...theme.applyStyles('dark', {
            color: '#bfbfbf',
            opacity: undefined,
        }),
    },
}));

function AirbnbThumbComponent(props) {
    const { children, ...other } = props;
    return (
        <SliderThumb {...other}>
            {children}
            <span className="airbnb-bar" />
            <span className="airbnb-bar" />
            <span className="airbnb-bar" />
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

    const handleChange = (event, newValue) => {
        setValue(newValue); // Aggiorna lo stato
        AdddeleteLabel(event,props.label,newValue)

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
        <Box sx={{marginTop:'5%'}}>
            <Typography gutterBottom><span>{props.label}: {value !== null ? value : 'not set'}    </span>        <span> <Button size={'small'} sx={{textAlign:'right'}} onClick={()=>setValue(null)}>Reset</Button>

            </span>
            </Typography>
            <div onClick={(e)=> {
                e.preventDefault()
                if (value === null) {
                    setValue(props.min)
                    AdddeleteLabel(e,props.label,1)
                }
            }}>
                <Slider                 marks={marks}
                                        sx={value === null  ? {
                                            width:'70%',
                                            '& .MuiSlider-thumb': {
                                                backgroundColor: 'blue', // Colore del thumb
                                                border: '0px solid red', // Bordo del thumb
                                                width: 0, // Dimensioni del thumb
                                                height: 0,
                                                '&:hover': {
                                                    boxShadow: '0px 0px 10px blue', // Effetto hover
                                                },
                                            },
                                        } : {width:'70%'}}
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