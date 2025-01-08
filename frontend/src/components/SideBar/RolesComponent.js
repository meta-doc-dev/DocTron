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

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';

const checkedIcon = <CheckBoxIcon fontSize="small"/>;
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import AddIcon from '@mui/icons-material/Add';
import Paper from "@mui/material/Paper";
import {styled} from '@mui/material/styles';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import Box from '@mui/material/Box';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import {AppContext} from "../../App";
import IconButton from "@mui/material/IconButton";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";

import './sidebar.css'


export default function RolesComponent(props) {
    const {
        collection,
        document_id,
        role,
        username,
        modality,
        collectiondocuments,
        mentions,
        concepts,
        relationshipslist,
        annotatedlabels
    } = useContext(AppContext);
    const [Collection, SetCollection] = collection
    const [DocumentID, SetDocumentID] = document_id
    const [Username, SetUsername] = username
    const [ShowSearch, SetShowSearch] = useState(false)
    const [CollectionDocuments, SetCollectionDocuments] = collectiondocuments
    const [Roles, SetRoles] = useState(["Annotator"]);
    const [Role, SetRole] = role

    useEffect(() => {
        if (Collection) {
            var members = []
            var roles = ["Annotator"]
            axios.get('collections/users', {params: {collection: Collection}}).then(response => {
                members = response.data['members']
                members.map(member => {
                    if (member.admin && member.username === Username) {
                        roles.push("Admin")
                    }
                    if (member.reviewer && member.username === Username) {
                        roles.push("Reviewer")
                    }
                })
                SetRoles(roles)
            })


        }
    }, [Collection])


    function handleClick(e, role) {
        e.preventDefault()
        SetDocumentID(false)
        SetRole(role)

    }

    /*    useEffect(()=>{
            axios.get('collections/documents')
                .then(response=>{


                        let docs = response.data
                        setDisplayDocs(docs)
                })
        },[])*/


    return (
        <div>
            <h5>
                Change role
            </h5>

            <div>
                {Roles && Roles.length > 0 ?
                    <div style={{paddingTop: '2%'}}>

                        {Roles.map(c =>
                            <div style={{marginTop: '10px'}}>
                                <div id={c.id}><Chip color={"primary"} variant={c === Role ? 'filled' : 'outlined'}
                                                     label={c} onClick={(e) => handleClick(e, c)}/></div>

                            </div>
                        )}
                    </div>


                    : <div className='loading'>
                        <CircularProgress/>
                    </div>}


            </div>
        </div>
    );
}