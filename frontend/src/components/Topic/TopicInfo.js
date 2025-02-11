import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import TopicIcon from '@mui/icons-material/Topic';
import ArticleIcon from '@mui/icons-material/Article';
import axios from "axios";
import {ButtonGroup} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import {AppContext} from "../../App";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import Link from "@mui/material/Link";
import {emphasize} from "@mui/material";
import {styled} from "@mui/material/styles";
import Chip from "@mui/material/Chip";
import * as PropTypes from "prop-types";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/Edit";

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;


export default function TopicInfo(props) {
    const {collection, document_id, collectiondocuments, topic} = useContext(AppContext);
    const [CollectionDocuments, SetCollectionDocuments] = collectiondocuments
    const [Info, SetInfo] = useState({})
    const [Topic, SetTopic] = topic


    useEffect(() => {
        if (Topic) {
            axios.get('topic', {params: {topic: Topic}})
                .then(response => {
                    SetInfo(response.data['topics'][0])
                })
        }

    }, [Topic])

    return (
        <div style={{padding:'2%',margin:'2%',backgroundColor:'#f5f5f5'}}>
            {Info && <div><h4>Topic </h4>

                {Object.keys(Info).map(key => <div>
                        <span>
                            <b>{key}: </b>
                        </span>
                        <span>
                            <>{Info[key]}</>
                        </span>
                        <br/>
                    </div>)}
            </div>}


        </div>
    );
}


