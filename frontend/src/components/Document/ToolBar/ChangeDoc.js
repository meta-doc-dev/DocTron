import {Col, Row} from "react-bootstrap";

import React, {useState, useEffect, useContext, createContext, useRef, useCallback} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import {
    faChevronLeft, faPalette,
    faChevronRight, faExclamationTriangle,
    faGlasses,
    faInfoCircle,
    faList, faPlusCircle,
    faProjectDiagram, faArrowLeft, faArrowRight, faTrash, faSave, faFileInvoice
} from "@fortawesome/free-solid-svg-icons";
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import ActualPosition from "../../BaseComponents/ActualPosition";
import {AppContext} from "../../../App";
import axios from "axios";
import {ClickOnBaseIndex} from "../../HelperFunctions/HelperFunctions";



function ChangeDoc(props){
    const { username,collection,documentlist,users,relationship,collectionslist,collectiondocuments,annotatedlabels,fieldsToAnn,fields,showmembers,showfilter,showstats,showcollections,expand,inarel,labels,addconceptmodal,annotation,mentions,document_id,concepts } = useContext(AppContext);
    const [DocumentID,SetDocumentID] = document_id
    const [Relationship,SetRelationship] = relationship

    const [InARel,SetInARel] = inarel


    const ToPrev = (event) => {
        event.preventDefault();
        event.stopPropagation()
        // console.log(props.documentList)
        var cur_ind = props.documentList.map(x=>x.hashed_id)
        cur_ind = cur_ind.indexOf(DocumentID)
        console.log(cur_ind)
        // SetDocumentID(false)
        let ind_to_set;
        if(cur_ind === 0){
            ind_to_set = props.documentList.length - 1;
        }
        else{
            ind_to_set =  cur_ind - 1
        }
        console.log(ind_to_set,props.documentList[ind_to_set])

        axios.post('update_document_id',{'document':props.documentList[ind_to_set]['hashed_id']})
            .then(resp=>{
                SetDocumentID(props.documentList[ind_to_set]['hashed_id'])
                SetRelationship(false)
            })

    }

    const ToNext = (event) => {
        event.preventDefault();
        event.stopPropagation()
        console.log(props.documentList)
        console.log(DocumentID)

        var cur_ind = props.documentList.map(x=>x.hashed_id)
        cur_ind = cur_ind.indexOf(DocumentID)
        console.log(cur_ind)

        let ind_to_set;
        if(cur_ind === props.documentList.length - 1){
            ind_to_set = 0;
        }
        else{
            ind_to_set =  cur_ind + 1
        }
        console.log(ind_to_set,props.documentList[ind_to_set])

        axios.post('update_document_id',{'document':props.documentList[ind_to_set]['hashed_id']})
                    .then(resp=>{
                        SetDocumentID(props.documentList[ind_to_set]['hashed_id'])
                        SetRelationship(false)

                    })
    }




    const changeDocumentArrow = useCallback((event) => {
        // console.log('chiave',event.key)
        if (event.keyCode === 39 && event.shiftKey) {
            ToNext(event)

        }else if(event.keyCode === 37 && event.shiftKey){
            ToPrev(event)
        }
    }, [DocumentID]);

    useEffect(() => {
        if(! (props.documentList.length <2  || InARel)){
            document.addEventListener("keydown", changeDocumentArrow, false);

            return () => {
                document.removeEventListener("keydown", changeDocumentArrow, false);
            };
        }

    }, [DocumentID]);


    return(
        <div className='inline'>
            <span>

                <IconButton size="small" variant="contained" className={'bt'} disabled={props.documentList.length <2 } onClick={ToPrev}>
                    <ArrowBackIosIcon />
                </IconButton>
            </span>
            <span style={{marginLeft:'1vw'}}>
            <IconButton  size="small" variant="contained" className={'bt'} disabled={props.documentList.length <2  } onClick={ToNext}>
                <ArrowForwardIosIcon />
            </IconButton></span>
        </div>
    );

}
export default ChangeDoc