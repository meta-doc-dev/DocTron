import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import BorderColorIcon from "@mui/icons-material/BorderColor";
import BarChartIcon from "@mui/icons-material/BarChart";
import DownloadIcon from "@mui/icons-material/Download";
import {CollectionsBookmarkOutlined} from "@material-ui/icons";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Alert from "@mui/material/Alert";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import axios from "axios";
import {CircularProgress,Table, TableBody, TableContainer, TableHead, TableRow} from "@mui/material";
import TableCell from "@material-ui/core/TableCell";
import {InputLabel, Select, TextField} from "@material-ui/core";
import MenuItem from "@mui/material/MenuItem";
import {AppContext} from "../../../App";
import FormControl from "@mui/material/FormControl";
import Autocomplete from "@mui/material/Autocomplete";
// import {Table} from "@devexpress/dx-react-grid-material-ui";
import Paper from "@mui/material/Paper";


function DeleteMemberDialog(props){
    const { annotators,collectiondocuments  } = useContext(AppContext);
    const [docOptions,SetdocOptions] = useState([])

    const [Loading,SetLoading]= useState(false)
    const [Fleiss,SetFleiss] = useState(false)
    const [Document,SetDocument] = useState("")
    const [Rows,SetRows] = useState([])

    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments

    useEffect(()=>{
        var options = [{'label': 'All','value':''}]
        if(CollectionDocuments){
            CollectionDocuments.map(c=>{
                options.push({'label':c.id,'value':c.hashed_id})
            })
        }
        SetdocOptions(options)
    },[CollectionDocuments])

    useEffect(()=>{
        if(Document || Document === ""){
            SetLoading(true)
            let rows = []
            axios.get('create_fleiss_overview',{params:{collection: props.collection,document:Document}})
                .then(response=>{
                    const keys = Object.keys(response.data);

                    SetLoading(false)
                    keys.map(key=>{
                        rows.push(createData(response.data[key]['round'], response.data[key]['mentions'], response.data[key]['concepts'], response.data[key]['relationships'], response.data[key]['assertions'],response.data[key]['labels']),)
                    })

                    SetRows(rows)



                })
                .catch(error=>{
                    SetLoading(false);
                })
        }

    },[Document])

    function createData(
        round,
        mentions,
        concepts,
        relationships,
        assertions,
        labels,
    ) {
        return { round, mentions, concepts, relationships, assertions, labels };
    }



    return(
        <Dialog
            open={props.open}
            fullWidth
            maxWidth='lg'
            onClose={props.handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                Rounds overview
            </DialogTitle>
            <DialogContent>
                <div style={{padding: '2%'}}>
                    {docOptions && <Autocomplete

                        id="doc"
                        onChange={(event, newValue) => {
                            SetDocument(newValue.value)
                        }
                        }
                        getOptionLabel={(option) => option.label}

                        options={docOptions}
                        sx={{width: '100%'}}
                        renderInput={(params) => <TextField {...params} label="Document"/>}
                    />}
                </div>
                {Loading === true && <div className='loading'><CircularProgress /></div>}

                {Rows.length > 0 && Loading === false && <div style={{padding: '2%'}}>
                    <TableContainer component={Paper}>
                        <Table sx={{minWidth: 650}} aria-label="simple table">
                            <TableHead>
                                <TableRow>
                                    <TableCell align="right"><b>Round</b></TableCell>
                                    <TableCell align="right"><b>Mentions</b></TableCell>
                                    <TableCell align="right"><b>Concepts</b></TableCell>
                                    <TableCell align="right"><b>Relationships</b></TableCell>
                                    <TableCell align="right"><b>Assertions</b></TableCell>
                                    <TableCell align="right"><b>Labels</b></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {Rows.map((row) => (
                                    <TableRow
                                        key={row.round}
                                        sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                    >

                                        <TableCell align="right">{row.round}</TableCell>
                                        <TableCell align="right">{row.mentions}</TableCell>
                                        <TableCell align="right">{row.concepts}</TableCell>
                                        <TableCell align="right">{row.relationships}</TableCell>
                                        <TableCell align="right">{row.assertions}</TableCell>
                                        <TableCell align="right">{row.labels}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>

                </div>
                }
            </DialogContent>
            <DialogActions>
                <Button color='error' onClick={props.handleClose}>Close</Button>

            </DialogActions>
        </Dialog>
    );

}
export default DeleteMemberDialog