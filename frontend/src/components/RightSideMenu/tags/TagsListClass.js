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
import '../rightsidestyles.css'
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import UploadIcon from '@mui/icons-material/Upload';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import ArticleIcon from '@mui/icons-material/Article';
import {AppContext} from "../../../App";
import RightSideTag from "./RightSideTag";
import {waitForElm} from "../../HelperFunctions/HelperFunctions";
const checkedIcon = <CheckBoxIcon fontSize="small" />;


export default function TagsListClass(props){
    const { showtagspannel,concepts,view,tags_split,areascolors } = useContext(AppContext);
    const [Tags,SetTags] = useState([]);
    const [TagsSplitted,SetTagsSplitted] = tags_split
    const [ConceptsList,SetConceptsList] = concepts
    const [ShowArea,SetShowArea] = useState(null)
    const [AreasColors,SetAreasColors] = areascolors
    const [ShowTags,SetShowTags] = showtagspannel
    const [FullTagsList,SetFullTagsList] = useState([])
    const [ShowList,SetShowList] = useState(false)
    const [View,SetView] = view


    useEffect(()=>{
        if(AreasColors && ShowTags){
            let areas = {}
            Object.keys(AreasColors).map(k=>areas[k] = false)
            SetShowArea(areas)
            Object.keys(AreasColors).map(a=>{
                waitForElm('#'+a+'_id').then((element) => {
                    element.style.color = AreasColors[a]
                })
            })
        }

    },[AreasColors,ShowTags])




    useEffect(()=>{
        if(TagsSplitted){
            let tagslist = {}
            tagslist['total_list'] = []
            TagsSplitted.map(m=>{
                let c = m
                if(Array.from(Object.keys(tagslist)).indexOf(c.tag.area) === -1){
                    tagslist[c.tag.area] = 0
                }
                else{
                    tagslist[c.tag.area] = tagslist[c.tag.area] + 1
                }


            })

            SetTags(tagslist)

        }


    },[TagsSplitted])




    useEffect(()=>{

        axios.get('tag/full')
            .then(response=>{
                SetFullTagsList(response.data)

            })
            .catch(error=>{
                console.log(error)
            })
    },[])

    return(
        <div>
            <Button disabled={View === 4} onClick={()=>SetShowList(prev=>!prev)} variant="text">Tags <i>({TagsSplitted.length})</i></Button>

            <Collapse in={ShowList}>
                {Tags  && <div>
                    {(Object.keys(Tags)).filter(x=>x !== 'total_list').map(a =>
                        <>
                            <RightSideTag id ={a.toString()+'_id'} TagsList = {FullTagsList} c = {a} />




                        </>)}
                </div>}
            </Collapse>

            {/*{MentionsList && <div><i><b>{MentionsList.length}</b> mentions</i></div>}*/}



        </div>
    );
}