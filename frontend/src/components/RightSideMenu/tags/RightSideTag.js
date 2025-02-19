
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import SaveIcon from '@mui/icons-material/Save';
import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import EditIcon from '@mui/icons-material/Edit';
const checkedIcon = <CheckBoxIcon fontSize="small" />;

// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, styled} from "@mui/material/styles";
import '../rightsidestyles.css'
import {
    clearMentionsFromBorder,
    DeleteRange, highlightMention,
    recomputeConceptColor,
    RemovehighlightMention
} from "../../HelperFunctions/HelperFunctions";

export default function RightSideTag(props){
    const { secondsel,currentdiv,firstsel,inarel,showtagspannel,tags_split,mentions,areascolors,startrange,endrange } = useContext(AppContext);
    const [TagToHighlight,SetTagToHighlight] = useState(false)
    const [MentionsList, SetMentionsList] = mentions
    const [TagsSplitted,SetTagsSplitted] = tags_split
    const [Start,SetStart] = startrange
    const [End,SetEnd] = endrange
    const [CurrentDiv,SetCurrentDiv] = currentdiv
    const [InARel,SetInARel] = inarel
    const [FirstSelected,SetFirstSelected] = firstsel
    const [SecondSelected,SetSecondSelected] = secondsel
    const [AreasColors,SetAreasColors] = areascolors
    const [ShowTags,SetShowTags] = showtagspannel


    function GetMentionsToBorder(c){
        let to_ret = []

        props.TagsList.map(mention=>{
            if(to_ret.indexOf(mention.mentions) === -1 && c === mention.tag.area){
                to_ret.push(mention)
            }
        })
        return to_ret
    }

    function clickOnConcept(e){
        e.preventDefault()
        e.stopPropagation()
        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv)
        let mentions_to_border = GetMentionsToBorder(props.c)
        let area = props.c
        let men_color = 'rgba(65,105,225,1)'
        if(AreasColors) {
            men_color = AreasColors[area]

        }
        console.log(men_color)
        if(TagToHighlight !== props.c){
            if(document.getElementById(props.id).style.fontWeight === 'bold'){

                SetTagToHighlight(props.id)
                // document.getElementById(props.mention.mentions).style.fontWeight = 'normal'
                document.getElementById(props.id).style.fontWeight = 'normal'
                document.getElementById(props.id).style.color = ''
                document.getElementById(props.id).style.backgroundColor = ''
                mentions_to_border.map(mention=>{
                    RemovehighlightMention(mention)
                })
            } else {
                // document.getElementById(props.mention.mentions).style.fontWeight = 'bold'
                SetTagToHighlight(props.c)
                document.getElementById(props.id).style.fontWeight = 'bold'
                document.getElementById(props.id).style.color = men_color
                document.getElementById(props.id).style.backgroundColor = men_color.replace('1)','0.1)')

                mentions_to_border.map(mention=>{
                    highlightMention(mention)
                })

                // recomputeColor(props.mention,true)

            }
        }else{
            document.getElementById(props.id).style.fontWeight = 'normal'
            document.getElementById(props.id).style.color = ''
            document.getElementById(props.id).style.backgroundColor = ''
            mentions_to_border.map(mention=>{
                RemovehighlightMention(mention)
            })
            SetTagToHighlight(false)
            // document.getElementById(props.mention.mentions).style.fontWeight = 'normal'

        }




    }
    useEffect(()=>{
        document.getElementById(props.id).style.fontWeight = ''
        document.getElementById(props.id).style.color = ''
        document.getElementById(props.id).style.backgroundColor = ''

    },[ShowTags])

    return (
        <div
            id={props.id}
            className='mentionButton'
            onClick={clickOnConcept}
        >{props.c} <i>({TagsSplitted.filter(x=>x['tag']['area'] === props.c).length})</i></div>

    )
}