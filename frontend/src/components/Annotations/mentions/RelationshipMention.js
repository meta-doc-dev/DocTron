import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";

import React, {useState, useEffect, useContext, useMemo, useRef} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
import EditIcon from '@mui/icons-material/Edit';
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';
import '../annotation.css'

import Fade from '@mui/material/Fade';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {
    faChevronLeft, faPalette,
    faChevronRight, faExclamationTriangle,
    faGlasses,
    faInfoCircle,
    faList, faPlusCircle,
    faProjectDiagram, faArrowLeft, faArrowRight, faTrash, faSave, faFileInvoice
} from "@fortawesome/free-solid-svg-icons";

import AddIcon from '@mui/icons-material/Add';
import Collapse from "@material-ui/core/Collapse";
import Paper from "@mui/material/Paper";
import '../annotation.css'
// import './documents.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";
import {ArrowContext} from "../../Document/DocumentFinal_2";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import DraggableModal from "../concepts/DraggableConceptModal";
import {
    DeleteRange,
    updateMentionColor,
    updateRelMentionColor,
    waitForElm
} from "../../HelperFunctions/HelperFunctions";
import DeleteMentionModal from "./modals/DeleteMentionModal";
import AssistantIcon from '@mui/icons-material/Assistant';
import CheckIcon from '@mui/icons-material/Check';
import Chip from "@mui/material/Chip";
import {type} from "@testing-library/user-event/dist/type";
import Concept from "../concepts/Concept";
import ChipRel from "../relationship/ChipRelationship";
import ChooseMentionModal from "./modals/ChooseMentionModal";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import Radio from "@mui/material/Radio";
import DialogActions from "@mui/material/DialogActions";
import {ConceptContext} from "../../../BaseIndex";
import Tag from "../tag/Tag";

export default function RelMention(props){
    const { view,concepts,inarel,sourceall,predicateall,targetall,relationship,tags_split,curannotator,binaryrel,username,predicateconcepts,predicatetext,targetconcepts,targettext,sourcetext,sourceconcepts,relationshipslist,areascolors,modifyrel,predicate,source,target,currentdiv,readonlyrelation,firstsel,curmention,secondsel,collection,mentions,addconceptmodal,mentiontohighlight,startrange,endrange } = useContext(AppContext);
    const { startanchorsp,startanchorpt,endanchorsp,endanchorpt,endanchorst,selectedarrow,startanchorst,overlappingpt,overlappingsp,overlappingst } = useContext(ArrowContext);
    const { sparrow,ptarrow,starrow } = useContext(ConceptContext);
    const [MentionToHighlight,SetMentionToHighlight] = mentiontohighlight
    const [Click,SetClick] = useState(false)
    const [Collection,SetCollection] = collection
    const [MentionsList,SetMentionsList] = mentions
    const [EndAnchorST,SetEndAnchorST] = endanchorst
    const [StartAnchorST,SetStartAnchorST] = startanchorst
    const [StartAnchorSP,SetStartAnchorSP] = startanchorsp
    const [StartAnchorPT,SetStartAnchorPT] = startanchorpt
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Username,SetUsername] = username
    const [AreasColors,SetAreasColors] = areascolors
    const [BinaryRel,SetBinaryRel] = binaryrel
    const [RelationshipsList,SetRelationshipsList] = relationshipslist
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts,SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] =targettext
    const [TagsSplitted,SetTagsSplitted] = tags_split

    const [EndAnchorSP,SetEndAnchorSP] = endanchorsp
    const [EndAnchorPT,SetEndAnchorPT] = endanchorpt
    const [View,SetView] = view
    const [SelectedMention,SetSelectedMention] = useState(false)
    const [Role,SetRole] = useState(false)
    const [Start,SetStart] = startrange
    const [End,SetEnd] = endrange
    const [Source,SetSource] = source
    const [Sources,SetSources] = sourceall
    const [Predicates,SetPredicates] = predicateall
    const [Targets,SetTargets] = targetall
    const [SourceAll,SetSourceAll] = sourceall
    const [PredicateAll,SetPredicateAll] = predicateall
    const [TargetAll,SetTargetAll] = targetall
    const [SelectedArrow,SetSelectedArrow] = selectedarrow
    const [Target,SetTarget] = target
    const [Predicate,SetPredicate] = predicate
    // const [SourceId,SetSourceId] = sourceid
    // const [TargetId,SetTargetId] = targetid
    // const [PredicateId,SetPredicateId] = predicateid
    const [SPArrow,SetSPArrow] = sparrow
    const [PTArrow,SetPTArrow] = ptarrow
    const [STArrow,SetSTArrow] = starrow
    const [CurrentDiv,SetCurrentDiv] = currentdiv
    const [CurMention,SetCurMention] = curmention
    const [FirstSelected,SetFirstSelected] = firstsel
    const [SecondSelected,SetSecondSelected] = secondsel
    const [Mentions,SetMentions] = useState(false)
    const [ShowSelectMentionModal,SetShowSelectMentionModal] = useState(false)
    const [value,SetValue] = useState(0)
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = readonlyrelation
    let key = props.loc
    const [ShowAddConceptModal,SetShowAddConceptModal] = addconceptmodal
    const [ShowDeleteMetnionModal,SetShowDeleteMetnionModal] = useState(false)
    const [contextMenu, setContextMenu] = useState(null);
    const inputEl = useRef(null);
    const [InARel,SetInARel] = inarel
    const [Relationship,SetRelationship] = relationship
    const [Concepts,SetConcepts] = useState(null)
    const [ConceptsList,SetConceptsList] = concepts
    // const [OverlappingPT,SetOverlappingPT] = overlappingpt
    // const [OverlappingST,SetOverlappingST] = overlappingst
    // const [OverlappingPS,SetOverlappingPS] = overlappingsp

    // useEffect(()=>{
    //     if(Sources){
    //         var sourcesall = Sources.filter(item => item !== Source)
    //         SetSourceAll(sourcesall)
    //
    //     }else{
    //         var sourcesall = Sources.map(item => item)
    //         SetSourceAll(sourcesall)
    //     }
    //     if(Predicates){
    //         var sourcesall = Predicates.filter(item => item !== Predicate)
    //         SetPredicateAll(sourcesall)
    //
    //     }else{
    //         var sourcesall = Predicates.map(item => item )
    //         SetPredicateAll(sourcesall)
    //     }
    //     if(Targets){
    //         var sourcesall = Sources.filter(item => item !== Target)
    //         SetTargetAll(sourcesall)
    //
    //     }else{
    //         var sourcesall = Sources.map(item => item)
    //         SetTargetAll(sourcesall)
    //     }
    //
    // },[Source,Predicate,Target])


    function updateClassesStandard(mention){

        let classes = props.mention.mentions.split(' ')
        if(classes.length>1){
            classes.push('underlined')
        }
        // console.log('class',classes)
        if(classes.indexOf('men') ===-1){
            classes.push('men')

        }

        // let element = document.getElementById(props.id)
        if (props.loc !== 'title_key' && props.loc.endsWith('key')){
            classes.push('key')
            mention.classList.add(...classes)
        }else if (props.loc === 'title_value' ){
            classes.push('title_value')

            mention.classList.add(...classes)
        }
        else if (props.loc.endsWith('_value' )){

            mention.classList.add(...classes)

        }
    }

    function updateClasses(mention){
        updateClassesStandard(mention)
        if(mention.classList.length>0){
            mention.classList.remove("source");
            mention.classList.remove("predicate");
            mention.classList.remove("target");
        }
        let color_0 = 'rgba(65,105,225,1)'
        mention.style.color = color_0
        mention.style.backgroundColor = color_0.replace('1)','0.1)')

    }

    function update(mention,color_0){
        // console.log('ATTENZIONE1',props.id)
        updateClasses(mention)
        mention.style.color = color_0
        mention.style.backgroundColor = color_0.replace('1)', '0.1)')


        let mentions = props.mention.mentions.split(' ')
        if (Source && mentions.indexOf(Source) !== -1) {
            // if(SourceAll.indexOf(Source) !== -1){
            //     let idx = 'source_all_' + SourceAll.filter(item => mentions.includes(item))[0].split('_')[1]
            //
            //     removeAllChildren(idx,'source_all')
            // }
            let found_source = true
            mention.classList.remove('source_all')
            mention.classList.add('source')
          /*  if (document.getElementById('source') === null) {
                var wrapper = document.createElement('div');
                wrapper.id = 'source'
                addChild('source')

            }*/

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (m === Source) {
                    found_source = true
                    mention.classList.add('source')

                    //addChild('source')


                }
            })


        }else if(SourceAll && SourceAll.filter(item => mentions.includes(item)).length > 0){
            //removeAllChildren('source')
            let found_source = true
            let idx = SourceAll.filter(item => mentions.includes(item))[0].split('_')[1]
            mention.classList.add('source_all')
            mention.classList.remove('source')
            mention.style.borderColor = color_0
            mention.style.border = '1px solid'

            let id_wrap = 'source_all_'+idx

            if (document.getElementById(id_wrap) === null) {
                var wrapper = document.createElement('div');
                wrapper.id = id_wrap
                wrapper.style.display = "inline-block";
                wrapper.style.position = "relative";
                wrapper.style.marginTop = "15px";

                //addChild(id_wrap)

            }

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (SourceAll.indexOf(m) !== -1) {
                    found_source = true
                    let idx = SourceAll.filter(item => mentions.includes(item))[0].split('_')[1]
                    mention.classList.add('source_all')
                    mention.classList.remove('source')
                    mention.style.borderColor = color_0
                    mention.style.border = '1px solid'
                    let id_wrap = 'source_all_'+idx
                    //addChild(id_wrap)


                }
            })
        }
        if (Predicate && mentions.indexOf(Predicate) !== -1) {
            let found_source = true
            mention.classList.add('predicate')
            mention.classList.remove('predicate_all')

            if (document.getElementById('predicate') === null) {
                var wrapper = document.createElement('div');
                wrapper.id = 'predicate'
                //addChild('predicate')

            }

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (m === Predicate) {
                    found_source = true
                    mention.classList.add('predicate')
                    mention.classList.remove('predicate_all')

                    //addChild('predicate')


                }
            })

        } else if(PredicateAll && PredicateAll.filter(item => mentions.includes(item)).length > 0){
            let found_source = true
            let idx = PredicateAll.filter(item => mentions.includes(item))[0].split('_')[1]
            mention.classList.add('predicate_all')
            mention.classList.remove('predicate')
            mention.style.borderColor = color_0
            mention.style.border = '1px solid'
            let id_wrap = 'predicate_all_'+idx

            if (document.getElementById(id_wrap) === null) {
                var wrapper = document.createElement('div');
                wrapper.id = id_wrap
                wrapper.style.display = "inline-block";
                wrapper.style.position = "relative";
                wrapper.style.marginTop = "15px";

                //addChild(id_wrap)

            }

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (PredicateAll.indexOf(m) !== -1) {
                    found_source = true
                    let idx = PredicateAll.filter(item => mentions.includes(item))[0].split('_')[1]
                    mention.classList.add('predicate_all')
                    mention.classList.remove('predicate')
                    mention.style.borderColor = color_0
                    mention.style.border = '1px solid'
                    let id_wrap = 'predicate_all_'+idx
                    //addChild(id_wrap)


                }
            })
        }

        if (Target && mentions.indexOf(Target) !== -1) {
            let found_source = true
            mention.classList.add('target')
            mention.classList.remove('target_all')

            if (document.getElementById('target') === null) {
                var wrapper = document.createElement('div');
                wrapper.id = 'target'
                //addChild('target')
            }

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (m === Target) {
                    found_source = true
                    mention.classList.add('target')
                    mention.classList.remove('target_all')

                    //addChild('target')

                }
            })
        }else if(TargetAll && TargetAll.filter(item => mentions.includes(item)).length > 0){
            let found_source = true
            let idx = TargetAll.filter(item => mentions.includes(item))[0].split('_')[1]
            mention.classList.add('target_all')
            mention.classList.remove('target')
            mention.style.borderColor = color_0
            mention.style.border = '1px solid'
            let id_wrap = 'target_all_'+idx

            if (document.getElementById(id_wrap) === null) {
                var wrapper = document.createElement('div');
                wrapper.id = id_wrap
                wrapper.style.display = "inline-block";
                wrapper.style.position = "relative";
                wrapper.style.marginTop = "15px";

                //addChild(id_wrap)

            }

            // questo è per colorare anche le overlapping ALL'INIZIO, APPENA PASSO DA NOT INAREL A INAREL
            mentions.map(m => {
                if (TargetAll.indexOf(m) !== -1) {
                    found_source = true
                    let idx = TargetAll.filter(item => mentions.includes(item))[0].split('_')[1]
                    mention.classList.add('target_all')
                    mention.classList.remove('target')
                    mention.style.borderColor = color_0
                    mention.style.border = '1px solid'
                    let id_wrap = 'target_all_'+idx
                    //addChild(id_wrap)


                }
            })
        }
    }


    function reset(){
        if(props.mention.mentions.split(' ').indexOf(Source) !== -1){
            Array.from(document.querySelectorAll('div[class^="source"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
            Array.from(document.querySelectorAll('[id^="source"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
        }
        if(props.mention.mentions.split(' ').indexOf(Predicate) !== -1){
            Array.from(document.querySelectorAll('div[class^="predicate"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
            Array.from(document.querySelectorAll('[id^="predicate"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
        }
        if(props.mention.mentions.split(' ').indexOf(Target) !== -1){
            Array.from(document.querySelectorAll('div[class^="target"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
            Array.from(document.querySelectorAll('[id^="target"]'))
                .forEach(div => {
                    // Sposta i figli del div nel suo genitore
                    while (div.firstChild) {
                        div.parentElement.insertBefore(div.firstChild, div);
                    }
                    // Rimuovi il div
                    div.remove();
                });
        }
    }


    useEffect(()=>{
        // console.log('entro in concepts')

        // QUESTO FUNZIONA ALL'INIZIO!!!!!
        // console.log('ATTENZIONE' ,props.id, Source,Predicate,Target)
        SetPTArrow(false)
        SetSPArrow(false)
        SetSTArrow(false)
        // console.log(ConceptsList,props.mention)
        var mention = props.mention
        mention['id'] = props.id
        // console.log('curmentoon',props.mention)
        let classes = props.mention.mentions.split(' ')
        let concepts_filtered = ConceptsList.filter(c=>c['mentions'].split(' ').some(item => classes.includes(item)))
        let tags_filtered = TagsSplitted.filter(c=>c['mentions'].split(' ').some(item => classes.includes(item)))

        let color_0 = 'rgba(65,105,225,1)'
        //     ora cerco se c'è qualche mention con concetto associato nella lista di concetti
        if(concepts_filtered.length > 0){
            concepts_filtered.map(c => {
                if (c['mentions'].split(' ').some(item => classes.includes(item))) {
                    let area = c['concept']['area']
                    color_0 = 'rgba(65,105,225,1)'
                    if(AreasColors[area]){
                        color_0 = AreasColors[area]
                    }
                }

            })
            if(concepts_filtered.length > 1){
                color_0 = 'rgba(50,50,50,1)'
            }
        }else if(tags_filtered.length > 0){
            tags_filtered.map(c => {
                if (c['mentions'].split(' ').some(item => classes.includes(item))) {
                    let area = c['tag']['area']
                    color_0 = 'rgba(65,105,225,1)'
                    if(AreasColors[area]){
                        color_0 = AreasColors[area]
                    }

                }

            })
            if(tags_filtered.length > 1){
                color_0 = 'rgba(50,50,50,1)'
            }
        }

        mention = document.getElementById(props.id)
        // console.log(mention)
        if (SourceAll && props.mention.mentions === Source && SourceAll.filter(item=>item === Source).length > 0){
            let idx = 'source_all_'+SourceAll.filter(item => props.mention.mentions.includes(item))[0].split('_')[1]
            removeAllChildren(idx,'source_all')
        }
        if (TargetAll && props.mention.mentions === Target && TargetAll.filter(item=>item === Target).length > 0){
            let idx = 'target_all_'+TargetAll.filter(item => props.mention.mentions.includes(item))[0].split('_')[1]
            removeAllChildren(idx,'target_all')
        }
        if (PredicateAll && props.mention.mentions === Predicate && PredicateAll.filter(item=>item === Predicate).length > 0){
            let idx = 'predicate_all_'+PredicateAll.filter(item => props.mention.mentions.includes(item))[0].split('_')[1]

            removeAllChildren(idx,'predicate_all')
        }
        if(mention!==undefined && mention !== null){
            update(mention,color_0)
        }else{
            waitForElm('#' + props.id).then((mention) => {
                update(mention,color_0)

            })
        }

    },[props.mention,Source,Predicate,Target])




    function removeAllChildren(nodetype,classname=null){
        if (classname === null){
            classname = nodetype
        }
        let target = document.getElementById(nodetype)
        // let target ='';
        let sources = Array.from(document.getElementsByClassName(classname))
        if(target !== null){
            let els =Array.from(document.querySelectorAll('div[class^="bulls"]'))
            sources.map(el=>{
                el.classList.remove(classname)
            })

            if(target.childNodes){
                els.map(el=>{
                    if(el.parentElement.id.toLowerCase() === nodetype){
                        target.removeChild(el)

                    }
                })
                target.replaceWith(...target.childNodes)
            }
            else{

                target.remove()
            }

        }
    }





    function findAncestor (el, cls) {

        // console.log('cls',cls)
        while(el.className !== cls){
            // console.log('el',el.id)
            el = el.parentElement
        }
        return el;
    }



    function addChild(nodetype){
        var wrapper = document.getElementById(nodetype)
        if(! wrapper) {
            // wrapper = Array.from(document.getElementsByClassName(nodetype))[0]
            wrapper = document.createElement('div');
            wrapper.style.display = "inline-block";
            wrapper.style.position = "relative";
            wrapper.style.marginTop = "15px";
            let color = ''
            if(nodetype.toLowerCase() === 'source' || nodetype.toLowerCase().includes('source_all')){
                color = 'rgb(214, 28, 78)'

            }else if(nodetype.toLowerCase() === 'target' || nodetype.toLowerCase().includes('target_all')){
                color = 'rgb(241, 136, 103)'

            }else if(nodetype.toLowerCase() === 'predicate' || nodetype.toLowerCase().includes('predicate_all')){
                color = 'rgb(55, 125, 113)'

            }


            // Credo le palle ai vertici del div
            var bulls_left = document.createElement('div');
            bulls_left.addEventListener("click", function(e) {
                const elementClicked = e.target;
                // if(elementClicked.getAttribute('listener') !== 'true'){

                // console.log(e.target.class,e.target.className,e.target.classList,SelectedArrow,Source,Target,Predicate)
                let position = e.target.className.split('_')
                position = position[position.length -1]

                SetClick([position,elementClicked.parentElement.id])
                // }

            });
            bulls_left.className = 'bulls_left'
            bulls_left.style.backgroundColor = color
            wrapper.appendChild(bulls_left);
            var bulls_right = document.createElement('div');
            bulls_right.addEventListener("click", function(e) {
                const elementClicked = e.target;
                // if(elementClicked.getAttribute('listener') !== 'true'){

                // console.log(e.target.class,e.target.className,e.target.classList,SelectedArrow,Source,Target,Predicate)
                let position = e.target.className.split('_')
                position = position[position.length -1]

                SetClick([position,elementClicked.parentElement.id])
                // }

            });
            bulls_right.className = 'bulls_right'
            bulls_right.style.backgroundColor =  color
            wrapper.appendChild(bulls_right);
            var bulls_top = document.createElement('div');
            bulls_top.addEventListener("click", function(e) {
                const elementClicked = e.target;
                // if(elementClicked.getAttribute('listener') !== 'true'){

                // console.log(e.target.class,e.target.className,e.target.classList,SelectedArrow,Source,Target,Predicate)
                let position = e.target.className.split('_')
                position = position[position.length -1]

                SetClick([position,elementClicked.parentElement.id])
                // }

            });
            bulls_top.className = 'bulls_top'

            bulls_top.style.backgroundColor = color
            wrapper.appendChild(bulls_top);
            var bulls_bottom = document.createElement('div');
            bulls_bottom.className = 'bulls_bottom'
            bulls_bottom.addEventListener("click", function(e) {
                const elementClicked = e.target;
                // if(elementClicked.getAttribute('listener') !== 'true'){

                // console.log(e.target.class,e.target.className,e.target.classList,SelectedArrow,Source,Target,Predicate)
                let position = e.target.className.split('_')
                position = position[position.length -1]

                SetClick([position,elementClicked.parentElement.id])
                // }

            });
            bulls_bottom.style.backgroundColor = color
            wrapper.appendChild(bulls_bottom);
            wrapper.id = nodetype


        }

        if(nodetype.includes('source_all')){
            nodetype = 'source_all'
        }
        if(nodetype.includes('target_all')){
            nodetype = 'target_all'
        }
        if(nodetype.includes('predicate_all')){
            nodetype = 'predicate_all'
        }

        var el = Array.from(document.getElementsByClassName(nodetype));

        el.map(e=>{
            let cur_el = e
            cur_el = findAncestor(cur_el,'mention_span')

            if(cur_el.parentElement.id !== nodetype && (['predicate','source','target'].indexOf(cur_el.parentElement.id) !== -1 || cur_el.parentElement.id.includes('source_all')|| cur_el.parentElement.id.includes('predicate_all')|| cur_el.parentElement.id.includes('target_all'))){
                e.classList.remove(nodetype)
                if(cur_el.parentElement.id === 'source'){
                    e.classList.add('source')

                }else if(cur_el.parentElement.id.includes('source_all')){
                    e.classList.add('source_all')
                }
                else if(cur_el.parentElement.id === 'predicate'){
                    e.classList.add('predicate')

                }else if(cur_el.parentElement.id.includes('predicate_all')){
                    e.classList.add('predicate_all')
                }
                else if(cur_el.parentElement.id === 'target'){
                    e.classList.add('target')

                }else if(cur_el.parentElement.id.includes('target_all')){
                    e.classList.add('target_all')
                }
            }
            else if(cur_el.parentElement.id !== nodetype){
                cur_el.parentNode.insertBefore(wrapper, cur_el);
                wrapper.appendChild(cur_el);
            }

        })

    }


    useEffect(()=>{

        // qui ci entro per spostare la freccia
        if(Click){
            let position = Click[0]
            if(Click[1] === 'source'){
                if(SelectedArrow === 'sp'){
                    SetStartAnchorSP(position)
                }
                else if(SelectedArrow === 'st'){
                    SetStartAnchorST(position)
                }

            }
            else if(Click[1] === 'target'){

                if(SelectedArrow === 'st'){
                    SetEndAnchorST(position)
                }
                else if(SelectedArrow === 'pt'){
                    SetEndAnchorPT(position)
                }
            }
            else if(Click[1] === 'predicate'){
                if(SelectedArrow === 'sp'){
                    SetEndAnchorSP(position)
                }

                else if(SelectedArrow === 'pt'){
                    SetStartAnchorPT(position)
                }
            }
        }

    },[Click])


    useEffect(()=>{
        let source = document.getElementById('source')
        let predicate = document.getElementById('predicate')
        let target = document.getElementById('target')
        if(!ShowReadOnlyRelation){
            if(!Source && source){
                removeAllChildren('source')
            }
            if(!Predicate && predicate){
                removeAllChildren('predicate')
            }
            if(!Target && target){
                removeAllChildren('target')
            }
        }

        // }

    },[Source,Predicate,Target])
    //
    //
    function changeRole(role=null) {




        let mention_cur_string = props.mention.mentions
        let splits = props.mention.mentions.split(' ')
        let dict_ment = {}
        // seleziono la mentions con lunghezza minore

        splits.map(split=>{
            dict_ment[split] = 0
            let mentions = MentionsList.filter(m => m.mentions.split(' ').indexOf(split) !== -1)
            mentions.map(m=>{
                dict_ment[split] = dict_ment[split] + (m.stop - m.start)
            })

        })
        const lowestEntry = Object.entries(dict_ment).reduce((prev, curr) => {
            return (curr[1] < prev[1]) ? curr : prev;
        });

// Output della chiave e del valore più basso
        mention_cur_string = lowestEntry[0]; // La chiave

        if (mention_cur_string.split(' ').length === 1) {
            if(role && role.toLowerCase() === 'source'){

                SetSource(mention_cur_string)
                updateRelMentionColor('source',mention_cur_string)

            }else if(role && role.toLowerCase() === 'predicate'){
                SetPredicate(mention_cur_string)
                updateRelMentionColor('predicate',mention_cur_string)


            }else if(role && role.toLowerCase() === 'target'){
                SetTarget(mention_cur_string)
                updateRelMentionColor('target',mention_cur_string)


            }

        }

    }


    useEffect(()=>{
        SetStart(false)
        SetEnd(false)
        SetFirstSelected(false)
        SetSecondSelected(false)
        SetCurrentDiv(false)


    },[contextMenu])



    const handleContextMenu = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setContextMenu(
            contextMenu === null
                ? {
                    mouseX: event.clientX + 2,
                    mouseY: event.clientY - 6,
                }
                : // repeated contextmenu when it is already open closes it with Chrome 84 on Ubuntu
                  // Other native context menus might behave different.
                  // With this behavior we prevent contextmenu from the backdrop to re-locale existing context menus.
                null,
        );
    };




    const handleClose = () => {
        setContextMenu(null);
    };

    function handleChangeRadio(e){
        e.preventDefault()
        e.stopPropagation()
        let v = e.target.value
        SetValue(parseInt(v))

        // let selected = MentionsInvolved[v]
        //
        // SetSetSelectedMention(selected)
    }

    const StyledMenu = styled((props) => (
        <Menu
            elevation={0}
            anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
            }}
            transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
            }}
            {...props}
        />
    ))(({ theme }) => ({
        '& .MuiPaper-root': {
            borderRadius: 6,
            marginTop: theme.spacing(1),
            minWidth: 180,
            fontSize: 10,
            color:
                theme.palette.mode === 'light' ? 'rgb(55, 65, 81)' : theme.palette.grey[300],
            boxShadow:
                'rgb(255, 255, 255) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 0px 0px 1px, rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.05) 0px 4px 6px -2px',
            '& .MuiMenu-list': {
                padding: '4px 0',

            },
            '& .MuiMenuItem-root': {
                fontSize:'0.8rem !important',
                padding: '2px 16px',
                '& .MuiSvgIcon-root': {
                    fontSize: 18,
                    // color: theme.palette.text.secondary,
                    marginRight: theme.spacing(1.5),
                },
                '&:active': {
                    backgroundColor: alpha(
                        theme.palette.primary.main,
                        theme.palette.action.selectedOpacity,
                    ),
                },
            },
        },
    }));



    return (
        <span className={'mentionpart_rel'}>
            {ShowSelectMentionModal &&

                <Dialog
                    open={ShowSelectMentionModal}
                    onClose={()=>{SetShowSelectMentionModal(false)}}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                    maxWidth={'sm'}
                    fullWidth={'sm'}
                >

                    {/*<div style={{padding:'2%',width:'500px'}}>*/}

                    <div style={{padding:'3%'}}>
                        <DialogTitle style={{cursor: 'move'}} >
                            Select the mention
                        </DialogTitle>
                        <DialogContent>
                            <DialogContentText id="alert-dialog-description">
                                Select the mention you want to associate a concept to
                                <div>
                                    {Mentions.map((m,i)=><div>
                                        <Radio
                                            checked={value === i}
                                            onClick={handleChangeRadio}
                                            value={i}
                                            aria-label={m.mention_text}
                                        />{' '}{m.mention_text}
                                    </div>)}
                                </div>
                            </DialogContentText>

                        </DialogContent>
                    </div>

                    <DialogActions>
                        <Button autoFocus onClick={()=>{SetShowSelectMentionModal(false)}}>
                            Cancel
                        </Button>
                        <Button onClick={()=>{
                            SetSelectedMention(Mentions[value]);
                            SetShowSelectMentionModal(false)}}>Confirm</Button>
                    </DialogActions>
                </Dialog>
            }

            {(View === 2 || View === 3)&& props.tagsList.length > 0 && props.mention.mentions.split(' ').indexOf(Source) === -1 && props.mention.mentions.split(' ').indexOf(Predicate) === -1 && props.mention.mentions.split(' ').indexOf(Target) === -1 && <><Tag role={'neutro'} tags={TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 2 || View === 3) && props.tagsList.length > 0 && props.mention.mentions.split(' ').indexOf(Source) !== -1 && <><Tag role={'Source'} tags={TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop &&  x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 2 || View === 3) && props.tagsList.length > 0 && props.mention.mentions.split(' ').indexOf(Predicate) !== -1 && <><Tag role={'Predicate'} tags={TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 2 || View === 3) && props.tagsList.length > 0 && props.mention.mentions.split(' ').indexOf(Target) !== -1 && <><Tag role={'Target'} tags={TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}


            {(View === 1|| View === 3) && props.concepts.length > 0 && props.mention.mentions.split(' ').indexOf(Source) === -1 && props.mention.mentions.split(' ').indexOf(Predicate) === -1  && props.mention.mentions.split(' ').indexOf(Target) === -1 && <><Concept role={'neutro'} concepts={ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 1|| View === 3) && props.concepts.length > 0 && props.mention.mentions.split(' ').indexOf(Source) !== -1 && <><Concept role={'Source'} concepts={ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop &&  x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 1|| View === 3) && props.concepts.length > 0 && props.mention.mentions.split(' ').indexOf(Predicate) !== -1 && <><Concept role={'Predicate'} concepts={ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}
            {(View === 1|| View === 3) && props.concepts.length > 0 && props.mention.mentions.split(' ').indexOf(Target) !== -1 && <><Concept role={'Target'} concepts={ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id} /></>}

            { <span  onContextMenu={handleContextMenu} >


                <span id={props.id} ref={inputEl}

                     onClick={(e)=>{
                         if(!ShowReadOnlyRelation && CurAnnotator === Username && View !== 4) {

                             e.preventDefault();
                             e.stopPropagation();



                             SetSPArrow(false)
                             SetSTArrow(false)
                             SetPTArrow(false)




                             if(!Source && !Predicate && !Target){
                                 removeAllChildren('source')
                                 changeRole('Source');
                                 // console.log('SOURCE')
                             }
                             else if(Source && Predicate && Target){
                                 if(props.mention.mentions.split(' ').indexOf(Source) !== -1){
                                     removeAllChildren('source')
                                     SetSource(false)
                                     SetSourceText(false)
                                     SetSourceConcepts(false)
                                 }else if(props.mention.mentions.split(' ').indexOf(Predicate) !== -1){
                                     removeAllChildren('predicate')
                                     SetPredicate(false)
                                     SetPredicateText(false)
                                     SetPredicateConcepts(false)
                                 }else if(props.mention.mentions.split(' ').indexOf(Target) !== -1){
                                     removeAllChildren('target')
                                     SetTarget(false)
                                     SetTargetText(false)
                                     SetTargetConcepts(false)
                                 }else{
                                     removeAllChildren('source')
                                     changeRole('Source');
                                     // console.log('SOURCE')
                                 }

                             }
                             else if(Source && !Predicate && !Target){
                                 // console.log('predicate')
                                 if(props.mention.mentions.split(' ').indexOf(Source) !== -1){
                                     removeAllChildren('source')
                                     SetSource(false)
                                     SetSourceText(false)
                                     SetSourceConcepts(false)
                                 }else{
                                     if (BinaryRel === false){
                                         removeAllChildren('target')
                                         changeRole('Target');
                                         // console.log('SOURCE')
                                     }else{
                                         /*removeAllChildren('target')
                                         changeRole('Target');*/
                                         removeAllChildren('target')
                                         changeRole('Target');
                                     }

                                 }

                             }
                             else if(!Source && Predicate && !Target){
                                 if(props.mention.mentions.split(' ').indexOf(Predicate) !== -1){
                                     removeAllChildren('predicate')
                                     SetPredicate(false)
                                     SetPredicateText(false)
                                     SetPredicateConcepts(false)
                                 }else{
                                     removeAllChildren('source')
                                     changeRole('Source');
                                     // console.log('SOURCE')
                                 }
                             }
                             else if(!Source && !Predicate && Target){
                                 if(props.mention.mentions.split(' ').indexOf(Target) !== -1){
                                     removeAllChildren('target')
                                     SetTarget(false)
                                     SetTargetText(false)
                                     SetTargetConcepts(false)
                                 }else{
                                     removeAllChildren('source')
                                     changeRole('Source');
                                     // console.log('SOURCE')
                                 }

                             }
                             else if(!Source && Predicate && Target){
                                 if(props.mention.mentions.split(' ').indexOf(Target) !== -1){
                                     removeAllChildren('target')
                                     SetTarget(false)
                                 }else if(props.mention.mentions.split(' ').indexOf(Predicate) !== -1){
                                     removeAllChildren('predicate')
                                     SetPredicate(false)

                                     SetPredicateText(false)
                                     SetPredicateConcepts(false)
                                 }
                                 else{
                                     removeAllChildren('source')
                                     changeRole('Source');
                                     // console.log('SOURCE')
                                 }

                             }
                             else if(Source && !Predicate && Target){
                                 if(props.mention.mentions.split(' ').indexOf(Target) !== -1){
                                     removeAllChildren('target')
                                     SetTarget(false)
                                     SetTargetText(false)
                                     SetTargetConcepts(false)
                                 }else if(props.mention.mentions.split(' ').indexOf(Source) !== -1){
                                     removeAllChildren('source')
                                     SetSource(false)
                                     SetSourceText(false)
                                     SetSourceConcepts(false)
                                 }
                                 else{
                                     removeAllChildren('predicate')
                                     changeRole('Predicate');
                                 }
                                 // console.log('predicate')
                             }
                             else if(Source && Predicate && !Target){
                                 // console.log('target')
                                 if(props.mention.mentions.split(' ').indexOf(Predicate) !== -1){
                                     removeAllChildren('predicate')
                                     SetPredicate(false)
                                     SetPredicateText(false)
                                     SetPredicateConcepts(false)
                                 }else if(props.mention.mentions.split(' ').indexOf(Source) !== -1){
                                     removeAllChildren('source')
                                     SetSource(false)
                                     SetSourceText(false)
                                     SetSourceConcepts(false)
                                 }
                                 else{
                                     removeAllChildren('target')
                                     changeRole('Target');
                                 }

                             }


                             // changeRole()
                             DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)
                         }
                     }

                     } >
                    {/*{props.mention.mentions === Source && <span><ChipRel role={'Source'} /></span>}*/}
                    {/*{props.mention.mentions === Target && <span><ChipRel role={'Target'} /></span>}*/}
                    {/*{props.mention.mentions === Predicate && <span><ChipRel role={'Predicate'} /></span>}*/}
                    <span>
                         {props.mention_text.startsWith(' ') && !props.mention_text.endsWith(' ') && <>&nbsp;{props.mention_text.trim()}</>}
                        {props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text.trim()}&nbsp;</>}
                        {props.mention_text.endsWith(' ') && props.mention_text.startsWith(' ') && props.mention_text !== ' ' && <>&nbsp;{props.mention_text.trim()}&nbsp;</>}
                        {!props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text}</>}
                        {props.mention_text === (' ') && <>&nbsp;</>}
                    </span>


                    {/*{!Source && SourceConcepts && (Predicate === props.mentions || Target === props.mentions) && <div className={'cover'}>ciao</div>}*/}
                    {/*{!Predicate && PredicateConcepts && (Source === props.mentions || Target === props.mentions) && <div className={'cover'}>ciao</div>}*/}
                    {/*{!Target && TargetConcepts && (Source === props.mentions || Predicate === props.mentions) && <div className={'cover'}>ciao</div>}*/}




                </span>

                {<StyledMenu
                    open={contextMenu !== null && ShowReadOnlyRelation === false && InARel && CurAnnotator === Username && View !== 4}
                    onClose={handleClose}

                    // elevation={0}
                    anchorReference="anchorPosition"
                    anchorPosition={
                        contextMenu !== null
                            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
                            : undefined
                    }
                >

                    <MenuItem autoFocus ={false} onClick={(e)=>{

                        e.preventDefault()
                        e.stopPropagation()
                        setContextMenu(null);
                        removeAllChildren('source')
                        SetSPArrow(false)
                        SetSTArrow(false)
                        SetPTArrow(false)
                        if(props.mention.mentions === Source){
                            removeAllChildren('source')
                            SetSourceText(false)
                            SetSourceConcepts(false)
                            SetSource(false)

                        }else if(props.mention.mentions === Predicate){
                            removeAllChildren('predicate')
                            SetPredicateText(false)
                            SetPredicateConcepts(false)
                            SetPredicate(false)

                            changeRole('Source');
                        }
                        else if(props.mention.mentions === Target){
                            removeAllChildren('target')
                            SetTargetText(false)
                            SetTargetConcepts(false)
                            SetTarget(false)

                            changeRole('Source');

                        }
                        else{
                            changeRole('Source');

                        }

                        DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)

                    }}>
                        <ListItemIcon >
                            {Source === props.mention.mentions ? <CheckIcon fontSize="small" /> : <></>}
                        </ListItemIcon>
                        Subject
                    </MenuItem>

                    {BinaryRel === false && <MenuItem autoFocus ={false} onClick={(e)=>{
                        if(!ShowReadOnlyRelation) {

                            e.preventDefault()
                            e.stopPropagation()
                            setContextMenu(null);
                            removeAllChildren('predicate')

                            if(props.mention.mentions === Predicate){
                                removeAllChildren('predicate')
                                SetPredicateText(false)
                                SetPredicateConcepts(false)
                                SetPredicate(false)



                            }else if(props.mention.mentions === Source){
                                removeAllChildren('source')
                                SetSourceConcepts(false)
                                SetSourceText(false)
                                SetSource(false)



                                changeRole('Predicate');
                            }
                            else if(props.mention.mentions === Target){
                                removeAllChildren('target')
                                SetTargetText(false)
                                SetTargetConcepts(false)
                                SetTarget(false)

                                changeRole('Predicate');

                            }
                            else{
                                changeRole('Predicate');

                            }

                            DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv);
                        }

                    }}>
                        <ListItemIcon >
                            {Predicate === props.mention.mentions ? <CheckIcon fontSize="small" /> : <></>}
                        </ListItemIcon>
                        Predicate
                    </MenuItem>}

                    <MenuItem autoFocus ={false} onClick={(e)=>{
                        if(!ShowReadOnlyRelation) {

                            e.preventDefault()
                            e.stopPropagation()
                            setContextMenu(null);
                            removeAllChildren('target')

                            if(props.mention.mentions === Target){
                                removeAllChildren('target')
                                SetTargetText(false)
                                SetTargetConcepts(false)
                                SetTarget(false)

                            }else if(props.mention.mentions === Source){
                                SetSourceText(false)
                                SetSourceConcepts(false)
                                SetSource(false)

                                removeAllChildren('source')

                                changeRole('Target');
                            }
                            else if(props.mention.mentions === Predicate){
                                removeAllChildren('target')
                                SetPredicateText(false)
                                SetPredicateConcepts(false)
                                SetPredicate(false)

                                changeRole('Target');

                            }
                            else{
                                changeRole('Target');

                            }

                            DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)
                        }
                    }}>
                        <ListItemIcon >
                            {Target === props.mention.mentions ? <CheckIcon fontSize="small" /> : <></>}
                        </ListItemIcon>
                        Object
                    </MenuItem>

                    <Divider />

                    <MenuItem style={{color:'#d00000'}} autoFocus ={false} onClick={(e)=>{
                        if(!ShowReadOnlyRelation) {
                            e.preventDefault()
                            e.stopPropagation()
                            setContextMenu(null);
                            // console.log('DELETE')
                            if (props.mention.mentions === Source){
                                removeAllChildren('source')
                                SetSourceText(false)
                                SetSourceConcepts(false)
                                SetSource(false)

                            }else if (props.mention.mentions === Predicate){
                                removeAllChildren('predicate')
                                SetSourceText(false)
                                SetSourceConcepts(false)
                                SetPredicate(false)

                            }else if (props.mention.mentions === Target){
                                removeAllChildren('target')
                                SetTargetText(false)
                                SetTargetConcepts(false)
                                SetTarget(false)

                            }
                            DeleteRange(SetStart, SetEnd, SetFirstSelected, SetSecondSelected, SetCurrentDiv)
                        }

                    }}>
                        <ListItemIcon >
                            <DeleteIcon color='error' fontSize="small" />
                        </ListItemIcon>
                        Delete

                    </MenuItem>

                </StyledMenu>}

            </span>}


        </span>
    )
}