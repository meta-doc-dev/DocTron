import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';
import RemoveIcon from '@mui/icons-material/Remove';
import axios from "axios";
import {ButtonGroup} from "@mui/material";
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
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;


export default function SearchComponent(props){
    const { collection,document_id,labels, inarel,labelstosave,annotatedlabels } = useContext(AppContext);
    const [Collection,SetCollection] = collection
    const [DocumentID,SetDocumentID] = document_id
    const [Labels,SetLabels] = labels
    const [NotAdded,SetNotAdded] = useState([])
    const [ShowSelect,SetShowSelect] = useState(false)
    // const [AnnotatedLabels, SetAnnotatedLabels] = useState(false)
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [LabelsToSave, SetLabelsToSave] = labelstosave
    const [InARel,SetInARel] = inarel

    // function changeLabelList(changeListEl){
    //     var labels = NotAdded.filter(o => o !== changeListEl)
    //     SetAnnotatedLabels([...AnnotatedLabels,changeListEl])
    //     SetLabelsToSave([...LabelsToSave,changeListEl])
    //     SetNotAdded(labels)
    // }


    function deleteLabel(toDel){
        var labels = AnnotatedLabels.filter(o => o !== toDel)
        // AnnotatedLabels.map((o,i)=>{
        //     if(o !== toDel){
        //         labels.push(o)
        //     }
        // })
        SetNotAdded([...NotAdded,toDel])
        SetAnnotatedLabels(labels)

    }
    function AdddeleteLabel(label){
        if(Modality === 2 || View === 4) {

        }else if(AnnotationTypes.indexOf('Passages annotation') === -1) {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Passages annotation is not allowed here'})
        }else{
            if(AnnotatedLabels.indexOf(label) === -1) {
                // AnnotatedLabels.push(label)
                var labels = NotAdded.filter(o => o !== label)
                SetNotAdded(labels)
                SetAnnotatedLabels([...AnnotatedLabels,label])
                axios.post('annotate_label',{label:label})
                    .then(response=>{
                        var labels = NotAdded.filter(o => o !== label)
                        SetNotAdded(labels)
                        SetAnnotatedLabels([...AnnotatedLabels,label])
                    })

            }
            else{
                axios.post('delete_label',{label:label})
                    .then(response=>{
                        SetNotAdded([...NotAdded,label])
                        var labels = AnnotatedLabels.filter(o => o !== label)
                        SetAnnotatedLabels(labels)
                    })

            }
            // var labels = AnnotatedLabels.filter(o => o !== label)
            // // AnnotatedLabels.map((o,i)=>{
            // //     if(o !== toDel){
            // //         labels.push(o)
            // //     }
            // // })
            // SetNotAdded([...NotAdded,label])
            // SetAnnotatedLabels(labels)

        }

    }

    useEffect(()=>{
        if(AnnotatedLabels){
            var notadded = Labels.filter(o => (AnnotatedLabels).indexOf(o) === -1)
            SetNotAdded(notadded)

        }


    },[AnnotatedLabels])

    // useEffect(()=>{
    //     console.log('collection',Collection)
    //     if(Collection && Labels){
    //         axios.get('get_annotated_labels')
    //             .then(response=>{
    //                 SetAnnotatedLabels(response.data)
    //                 var notadded = Labels.filter(o => (response.data).indexOf(o) === -1)
    //                 SetNotAdded(notadded)
    //             })
    //     }
    // },[Collection,Labels])

    const labelstheme = createTheme({
        palette: {
            added: {
                main: 'rgb(103, 148, 54)',
                contrastText: '#fff',
            },
            not_added: {
                main: 'rgb(66, 122, 161)',
                contrastText: '#fff',
            },

        },
    });

    return(
        <div>
            <h5>
                Labels <i>({AnnotatedLabels.length})</i>
            </h5>
            <div>
                {AnnotatedLabels ? <ThemeProvider theme={labelstheme}>
                    {Labels['labels'].map(o=>
                        <span><Chip color={'not_added'} variant={NotAdded.indexOf(o) !== -1 ? "outlined": "filled"} label={o} size="small" onClick={()=>AdddeleteLabel(o)}/>{' '}</span>

                    )}

                </ThemeProvider>:<div className='loading'>
                    <CircularProgress />
                </div>}


            </div>
        </div>
    );
}