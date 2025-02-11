import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import {useParams} from "react-router-dom";

import axios from "axios";
import {ButtonGroup} from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from '@mui/material/TextField';
import React, {useState, useContext, createContext, useRef, useEffect} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';
import '../../App.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../App";
import PieCollection from "./utils/RadialChart";
import AddIcon from "@mui/icons-material/Add";
import {styled} from "@mui/material/styles";
import Chip from "@mui/material/Chip";
import GeneralStats from "./GeneralStats";
import MyStats from "./MyStats";
import SearchIcon from "@mui/icons-material/Search";
import NewRoundDialog from "../Collections/dialogs/NewRoundDialog";
import RoundDialog from "./utils/RoundDialog";
import CoehnsDialog from "./utils/CoehnsDialog";

export const CollectionContext = createContext('')

export default function StatisticsCollection(props){
    const { username,users,collectionslist,collectiondocuments,binaryrel,inarel } = useContext(AppContext);
    const [Username, SetUsername] = username
    const [CollectionsList,SetCollectionsList] = collectionslist
    const [CollectionToShow,SetCollectionToShow] = useState(false)
    const [AddCollection,SetAddCollection] = useState(false)
    const [UpdateCollection,SetUpdateCollection] = useState(false)
    const [Details,SetDetails] = useState(false)
    const [UsersList,SetUsersList] = users
    const {collection_id} = useParams()
    const [CollectionCur,SetCollectionCur] = useState(false)
    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments
    const [Type,SetType] = useState('my')
    const [DocumentPred,SetDocumentPred] = useState(false)
    const [Update,SetUpdate] = useState(false)
    const [options,SetOptions] = useState(false)
    const [Value,SetValue] = useState(false)

    const [OpenCoehnsModal,SetOpenCoehnsModal] = useState(false)
    const [OpenRoundsModal,SetOpenRoundsModal] = useState(false)
    const [BinaryRel,SetBinaryRel] = binaryrel
    const [InARel,SetInARel] = inarel
    useEffect(()=>{
        if(!InARel){
            SetBinaryRel(false)
        }
    },[InARel])

    useEffect(()=>{
        if(CollectionsList){
            let collection = CollectionsList.find(x=>x.id === collection_id)
            SetCollectionCur(collection)
        }
    },[CollectionsList])

    useEffect(()=>{
        if(CollectionDocuments){
            let options1 = [{id:'All documents',annotated:false}]
            CollectionDocuments.map(x=>options1.push(x))
            // options = options.splice(0,0,new_el)
            SetValue(options1[0])
            SetOptions(options1)
        }
    },[CollectionDocuments])


    useEffect(()=>{
        if(options){
            if(DocumentPred){
                SetValue(options.find(x=>x.id === DocumentPred))
            }else{
                SetValue(options.find(x=>x.id === 'All documents'))

            }
        }

    },[DocumentPred,options])
    useEffect(()=>{
        SetDocumentPred(false)
    },[Type])



    function ChangeType(e,type){
        e.preventDefault();
        e.stopPropagation();
        SetUpdate(false)
        let autocomplete = document.getElementById("combo-box-demo")
        autocomplete.value = options[0].id;
        SetDocumentPred(false)
        if(Type === 'my' && type === 'my'){
            SetType(false)
        }else if(type === 'my'){
            SetType('my')
        }else if(Type === 'all' && type === 'all'){
            SetType(false)
        }else{
            SetType('all')
        }

    }

    const handleCloseRoundDialog = () =>{
        SetOpenRoundsModal(false)
    }
    const handleCloseCoehnsDialog = () =>{

        SetOpenCoehnsModal(false);


    }

    return(
        <div className={'baseindex container-stats'}>
            <RoundDialog open={OpenRoundsModal} collection={collection_id} handleClose={handleCloseRoundDialog}  />
            <CoehnsDialog open={OpenCoehnsModal} collection={collection_id} handleClose={handleCloseCoehnsDialog} />



            {CollectionCur ? <div>
                <div className={'navbar'}>
                    <div ></div>
                    <div >
                    <Button sx={{margin:'0 5px'}} variant={Type==='my' ? 'contained' : 'outlined'} onClick={(e)=>ChangeType(e,'my')}>My Statistics</Button><Button sx={{margin:'0 5px'}} variant={Type==='all' ? 'contained' : 'outlined'} onClick={(e)=>ChangeType(e,'all')}>Global statistics</Button>
                    <Button sx={{margin:'0 5px'}} variant={Type==='all' ? 'contained' : 'outlined'} color='secondary' onClick={(e)=>SetOpenCoehnsModal(prev=>!prev)}>Coehns Agreement</Button>
                    <Button sx={{margin:'0 5px'}} variant={Type==='all' ? 'contained' : 'outlined'} color='success' onClick={(e)=>SetOpenRoundsModal(prev=>!prev)}>Rounds Agreement</Button>

                    </div>
                    <div >
                        <div className={'subcontainer'}>
                            <Autocomplete
                                disablePortal
                                id="combo-box-demo"
                                placeholder={'Insert a Document ID'}
                                getOptionLabel={(option) => option.id}
                                options={options}
                                value={Value}
                                // value={DocumentPred ? DocumentPred : ''}
                                onChange={(event, newInputValue) => {
                                    if (newInputValue === null || newInputValue.id === 'All documents'){
                                        SetDocumentPred(false);

                                    }else{
                                        SetDocumentPred(newInputValue.id);

                                    }
                                }}
                                sx={{ width: 300 }}
                                size={'small'}
                                renderInput={(params) => <TextField {...params} label="Document ID" />}
                                renderOption={(props, option, { inputValue }) => {
                                    const matches = match(option.id, inputValue, {insideWords: true});
                                    const parts = parse(option.id, matches);

                                    return (
                                        <li {...props}>
                                            <div>
                                                {parts.map((part, index) => (
                                                    <span
                                                        key={index}
                                                        style={{
                                                            fontWeight: part.highlight ? 700 : 400,
                                                        }}
                                                    >
                                              {part.text}
                                            </span>
                                                ))}
                                            </div>
                                        </li>
                                    );
                                }}
                            />
                        </div>



                    </div>
                    {/*<div ><Button onClick={()=>{*/}
                    {/*    SetUpdate(true)*/}
                    {/*}} endIcon={<SearchIcon/>}>Search</Button></div>*/}

                </div>
                <h2 style={{textAlign:"center"}}><i>{CollectionCur.name}</i> - {Type=== 'my' ? "Single User" : "Global"} Statistics - {DocumentPred ? DocumentPred : "All Documents"}</h2><hr/>
                {(Type === 'my' || (Type === 'my'  && DocumentPred)) && Username && <MyStats document={DocumentPred} />  }
                {(Type === 'all' || (Type === 'all'  && DocumentPred)) && Username &&  <GeneralStats document={DocumentPred} />  }

            </div> : <div className='loading'><CircularProgress /></div>}

        </div>
    );
}


