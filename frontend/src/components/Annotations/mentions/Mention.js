
import React, {useState, useEffect, useContext, useMemo, useRef} from "react";

import HubIcon from '@mui/icons-material/Hub';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';
import '../annotation.css'
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AddIcon from '@mui/icons-material/Add';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import '../annotation.css'
import {AppContext} from "../../../App";
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import {alpha, createTheme, styled, ThemeProvider} from "@mui/material/styles";
import {
    DeleteRange,
    updateMentionColor,
    updateRelMentionColor,
    waitForElm
} from "../../HelperFunctions/HelperFunctions";
import DeleteMentionModal from "./modals/DeleteMentionModal";
import AssistantIcon from '@mui/icons-material/Assistant';

import Concept from "../concepts/Concept";
import ChooseMentionModal from "./modals/ChooseMentionModal";
import InfoModal from "./modals/InfoModal";
import {RelationConceptContext} from "../concepts/RelationshipConceptModal";
import {ConceptContext} from "../../../BaseIndex";
import TextFieldsIcon from '@mui/icons-material/TextFields';
import ShareIcon from '@mui/icons-material/Share';
import axios from "axios";
import SuggestionModal from "./modals/SuggestionModal";
import AnnotateAllModal from "./modals/AnnotateAllModal";
import Tag from "../tag/Tag";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Chip from "@mui/material/Chip";
import {Col, Row} from "react-bootstrap";
import Checkbox from "@mui/material/Checkbox";
import {pink} from "@mui/material/colors";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import CheckIcon from "@mui/icons-material/Check";
import {Popover} from "@mui/material";
import Button from "@mui/material/Button";
import {TextField} from "@material-ui/core";
import SelectMentionToDelete from "./modals/SelectMentionToDelete";


export default function Mention(props){
    props.mention.position = props.loc
    const { areascolors,concepts,inarel,annotationtypes,modality,newmention,binaryrel,addtagmodal,relationshipslist,tags_split,curannotator,opensnack,sourcetext,predicatetext,targettext,targetconcepts,predicateconcepts,sourceconcepts,snackmessage,username,showrelspannel,predicate,target,newrelation,readonlyrelation,view,source,document_id,tags,currentdiv,firstsel,curmention,secondsel,documentdescription,mentions,addconceptmodal,mentiontohighlight,startrange,endrange } = useContext(AppContext);
    const [DocumentDesc,SetDocumentDesc] = documentdescription
    const [MentionsInvolved,SetMentionsInvolved] = useState([])

    const [MentionsList,SetMentionsList] = mentions
    const [View,SetView] = view
    const [AnnotationTypes,SetAnnotationTypes] = annotationtypes
    const [Start,SetStart] = startrange
    const [End,SetEnd] = endrange
    const [Source,SetSource] = source
    const [Predicate,SetPredicate] = predicate
    const [Target,SetTarget] = target
    const [NewMention,SetNewMention] = newmention
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts,SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] =targettext
    const [Modality,SetModality] = modality
    const [CurrentDiv,SetCurrentDiv] = currentdiv
    const [CurMention,SetCurMention] = curmention
    // const [CurConcept,SetCurConcept] = curconcept
    const [FirstSelected,SetFirstSelected] = firstsel
    const [SecondSelected,SetSecondSelected] = secondsel
    const [ShowRels,SetShowRels] = showrelspannel
    const [NewRelation,SetNewRelation] = newrelation
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Username,SetUsername] = username
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = useState(false)
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const [ShowChooseRelationshipModal,SetShowChooseRelationshipModal] = useState(false)
    const [BinaryRel,SetBinaryRel] = binaryrel
    let key = props.loc

    const [RelationshipsList,SetRelationshipsList] = relationshipslist

    //PARTE RELATIVA AI TAG
    const [anchorElTagAnno, setAnchorElTagAnno] = useState(null);

    const handleCloseTagAnno = () => {
        setAnchorElTagAnno(null);
    };

    const openTagAnno = Boolean(anchorElTagAnno);
    const id = openTagAnno ? "simple-popover" : undefined;
    // FINE TAG


    const [ShowAddConceptModal,SetShowAddConceptModal] = addconceptmodal
    const [ShowDeleteMetnionModal,SetShowDeleteMetnionModal] = useState(false)
    const [ShowInfoModal,SetShowInfoModal] = useState(false)
    const [contextMenu, setContextMenu] = useState(null);
    const inputEl = useRef(null);
    const [InARel,SetInARel] = inarel
    const [AreasColors,SetAreasColors] = areascolors
    const [ShowSuggestionModal,SetShowSuggestionModal] = useState(false)
    const [ShowAnnotateAllModal,SetShowAnnotateAllModal] = useState(false)
    const [ShowAddTagModal,SetShowAddTagModal] = addtagmodal
    const [ConceptsList,SetConceptsList] = concepts
    const [anchorEl, setAnchorEl] = useState(null);
    const [SelectedTags,SetSelectedTags] = useState([])

    const [ShowCopyModal,SetShowCopyModal] = useState(false)
    const [ShowCopyConceptModal,SetShowCopyConceptModal] = useState(false)
    const [TagsSplitted,SetTagsSplitted] = tags_split
    const open = Boolean(anchorEl)
    const [Tags, SetTags] = tags
    const [SelectedMention,SetSetSelectedMention] = useState(false)



    function setMentionCurFunction(){
        var ment = props.mention
        ment['id'] = props.id
        let classes = Array.from(document.getElementById(props.id).classList)
        classes = classes.filter(x=>x.startsWith('mention_'))
        if(classes.length === 1){
            let ment = []
            let men = MentionsList.find(x=>x.mentions === classes[0])
            ment.push(men)
            SetCurMention(ment)
            return ment
        }else if(classes.length > 1){
            let ment = []
            classes.map(c=>{
                ment.push(MentionsList.find(x=>x.mentions ===  c))
            })
            SetCurMention(ment)
            return ment

        }
    }
    useEffect(() => {
        if (props.mention.mentions.split(' ').indexOf(NewMention) !== -1) {

            const targetElement = document.getElementById(props.id); // Modifica con il tuo ID
            if (targetElement) {
                setAnchorElTagAnno(targetElement);
                SetNewMention(false)
            }
        } else {
            setAnchorElTagAnno(null); // Chiudi il popover se non corrisponde
        }
    }, [props.mention.mentions, NewMention]);


    const handleClick = (event) => {

        event.preventDefault()
        event.stopPropagation()
        if(CurAnnotator !== Username){
            setAnchorEl(event.currentTarget);

        }
        // setOpen(prev=>prev)
    };
    const handleClickTagAnno = (event) => {

        event.preventDefault()
        event.stopPropagation()
        if(CurAnnotator === Username){
            setAnchorElTagAnno(event.currentTarget);
            SetNewMention(false)

        }
        // setOpen(prev=>prev)
    };

    useEffect(() => {
        waitForElm('#' + props.id).then((mention) => {
            let isSelecting = false;

            const selectableElement = document.getElementById(props.id);

            // Inizio della selezione
            let isMouseDown = false; // Traccia se il mouse è premuto
            let mouseMoved = false; // Traccia se c'è stato un movimento


            // Inizio del clic
            selectableElement.addEventListener('mousedown', () => {
                isMouseDown = true; // Il mouse è premuto
                mouseMoved = false; // Resetta il movimento
            });

            // Movimento del mouse
            selectableElement.addEventListener('mousemove', () => {
                if (isMouseDown) {
                    mouseMoved = true; // Se il mouse è premuto e si muove
                }
            });

            // Evento clic
            selectableElement.addEventListener('click', (event) => {
                if (!mouseMoved) {
                    console.log('Hai cliccato sul div!'); // Esegui l'azione solo se non si sta selezionando
                    handleClickTagAnno(event)

                } else {
                    event.preventDefault(); // Previene l'azione di clic durante la selezione
                    console.log('Selezione in corso, clic ignorato.'); // Messaggio di debug
                }
            });

        })
    }, []);

    useEffect(()=>{
        if(Username !== CurAnnotator){
            document.getElementById(props.id).addEventListener('click',handleClick)
        }else{

            //document.getElementById(props.id).addEventListener('click',handleClickTagAnno)
        }
    },[CurAnnotator,Username])


    const handleCloseMenu = () => {
        setAnchorEl(null);
    };

    function copyMention(e){
        e.stopPropagation()
        e.preventDefault()
        if(Modality === 2){
            console.log('ecco')
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            let mentions = props.mention.mentions.split(' ')
            if (mentions.length > 1) {
                SetShowCopyModal(true)
            } else {
                SetOpenSnack(true)
                let m = MentionsList.filter(x => x.mentions === props.mention.mentions)[0]
                m['id'] = props.id
                SetSnackMessage({'message': 'Saving...'})
                axios.post('mentions/copy', {mention: m}).then(response => SetSnackMessage({'message': 'Saved'})).catch(error => SetSnackMessage({'message': 'ERROR'}))
            }
        }
        handleCloseMenu()

    }
    function copyMentionConcept(e){
        e.stopPropagation()
        e.preventDefault()
        if(Modality === 2){
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else{
            let mentions = props.mention.mentions.split(' ')
            if(mentions.length > 1){
                SetShowCopyConceptModal(true)
            }else{
                SetOpenSnack(true)
                let m = MentionsList.filter(x=>x.mentions === props.mention.mentions)[0]
                m['id'] = props.id
                SetSnackMessage({'message':'Saving...'})

                axios.post('concepts/copy',{mention:m,user:CurAnnotator}).then(response=>SetSnackMessage({'message':'Saved'})).catch(error=>SetSnackMessage({'message':'ERROR'}))

            }
        }

        handleCloseMenu()
    }

    function copyMentionTag(e){
        e.stopPropagation()
        e.preventDefault()
        if(Modality === 2){
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            let mentions = props.mention.mentions.split(' ')
            if (mentions.length > 1) {
                SetShowCopyConceptModal(true)
            } else {
                SetOpenSnack(true)
                let m = MentionsList.filter(x => x.mentions === props.mention.mentions)[0]
                m['id'] = props.id
                SetSnackMessage({'message': 'Saving...'})

                axios.post('tag/copy', {
                    mention: m,
                    user: CurAnnotator
                }).then(response => SetSnackMessage({'message': 'Saved'})).catch(error => SetSnackMessage({'message': 'ERROR'}))

            }
        }
        handleCloseMenu()
    }

    function updateClassesStandard(mention){
        let classes = props.mention.mentions.split(' ')
        mention.className = "";
        mention.classList.add(...classes)
        // console.log('classes',classes,classes.length>1,props.mention.mentions)
        if(classes.length>1){
            mention.classList.add('underlined')
        }
        // console.log('class',classes)
        if(classes.indexOf('men') ===-1){
            mention.classList.add('men')

        }

        // let element = document.getElementById(props.id)
        if (props.loc !== 'title_key' && props.loc.endsWith('key')){
            mention.classList.add('key')
        }else if (props.loc === 'title_value' ){
            mention.classList.add('title_value')

        }
        if(CurAnnotator !== Username){
            mention.classList.add('annotatorhover')
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


    //LOCALSTORAGE
    /*useEffect(()=>{
        // console.log('entro in concepts')

        // QUESTO FUNZIONA ALL'INIZIO!!!!!
        //         console.log(ConceptsList,props.mention)
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
                    color_0 = window.localStorage.getItem(area)
                    if (color_0 === null) {
                        color_0 = 'rgba(65,105,225,1)'
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
                    color_0 = window.localStorage.getItem(area)
                    if (color_0 === null) {
                        color_0 = 'rgba(65,105,225,1)'
                    }
                }

            })
            if(tags_filtered.length > 1){
                color_0 = 'rgba(50,50,50,1)'
            }
        }


        waitForElm('#' + props.id).then((mention) => {
            updateClasses(mention)
            mention.style.color = color_0
            mention.style.backgroundColor = color_0.replace('1)', '0.1)')
        })


    },[props.mention,ConceptsList,MentionsList,AreasColors,TagsSplitted])*/

    useEffect(()=>{
        // console.log('entro in concepts')

        // QUESTO FUNZIONA ALL'INIZIO!!!!!
        //         console.log(ConceptsList,props.mention)
        var mention = props.mention
        mention['id'] = props.id
        // console.log('curmentoon',props.mention)
        let classes = props.mention.mentions.split(' ')
        let concepts_filtered = ConceptsList.filter(c=>c['mentions'].split(' ').some(item => classes.includes(item)))
        let tags_filtered = TagsSplitted.filter(c=>c['mentions'].split(' ').some(item => classes.includes(item)))
        var tags = props.tagsList.map(el=>el.tag.area)
        SetSelectedTags(tags)
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
                    color_0 = null
                    if(AreasColors[area]){
                        color_0 = AreasColors[area]
                    }else{
                        color_0 = 'rgba(65,105,225,1)'
                    }
                }

            })
            if(tags_filtered.length > 1){
                color_0 = 'rgba(50,50,50,1)'
            }
        }


        waitForElm('#' + props.id).then((mention) => {
            updateClasses(mention)
            if(View !== 4){
                mention.style.color = color_0
                mention.style.backgroundColor = color_0.replace('1)', '0.1)')
            }else{
                mention.style.color = 'black'
                mention.style.backgroundColor = 'white'
            }

        })


    },[props.mention,ConceptsList,MentionsList,AreasColors,TagsSplitted,View])

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
        if(!InARel){
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
        }

    };


    function selectTag(e,tag){
        e.preventDefault()
        e.stopPropagation()
        if(Modality === 2 || View === 4) {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'You cannot annotate this document'})
        }else if(AnnotationTypes.indexOf('Entity tagging') === -1){
                SetOpenSnack(true)
                SetSnackMessage({'message': 'Entity tagging is not allowed here'})
        }else {


            console.log(AreasColors)
            console.log(CurMention)
            var m = props.mention
            let ment = []
            m['id'] = props.id


            var tags = SelectedTags.map(e => e)

            if (tags.indexOf(tag) === -1) {
                console.log(tags)
                axios.post('tag/insert', {mention: props.mention, area: tag})
                    .then(response => {
                        tags.push(tag)
                        SetSelectedTags(tags)
                        SetConceptsList(response.data['concepts'])
                        SetTags(response.data['tags_list'])
                        SetTagsSplitted(response.data['tags'])
                        SetRelationshipsList(response.data['relationships'])


                    })
                    .catch(error => {
                        console.log('error', error)
                    })
            } else {
                console.log(tags)

                axios.delete('tag/delete', {data: {mention: props.mention, area: tag}})
                    .then(response => {
                        tags = tags.filter(c => c !== tag)
                        SetSelectedTags(tags)
                        SetTagsSplitted(response.data['tags'])
                        SetRelationshipsList(response.data['relationships'])

                    })
                    .catch(error => {
                        console.log('error', error)
                    })
            }
        }
        setContextMenu(null);
        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv)
        handleCloseTagAnno()
    }



    const handleClose = () => {
        setContextMenu(null);
    };


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
            minWidth: 200,
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






    function handleInfo(e){
        e.stopPropagation();
        e.preventDefault();
        setContextMenu(null);
        SetShowInfoModal(true)
        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv)
    }

    function handleSuggestion(e){
        e.stopPropagation();
        e.preventDefault();

        SetShowSuggestionModal(true)

        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv);
        setContextMenu(null);


    }

    function handleAnnotateAll(e){
        e.stopPropagation();
        e.preventDefault();

        SetShowAnnotateAllModal(true)

        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv);
        setContextMenu(null);


    }


    function handleConcept(e,tag=false){
        e.stopPropagation();
        e.preventDefault();
        if(tag === true){
            SetShowAddTagModal(prev => !prev);
        }else{
            SetShowAddConceptModal(prev => !prev);
        }
        setContextMenu(null);
        var ment = setMentionCurFunction()


        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv)
    }

    function handleRelationship(e,binary=false){
        e.stopPropagation();
        e.preventDefault();
        SetShowRels(false)
        SetShowReadOnlyRelation(false)
        // SetNewRelation(true)
        SetSource(false)
        SetPredicate(false)
        SetTarget(false)
        SetPredicateText(false)
        SetSourceText(false)
        SetTargetText(false)
        SetPredicateConcepts(false)
        SetSourceConcepts(false)
        SetTargetConcepts(false)
        if(props.mention.mentions.split(' ').length>1){
            SetShowChooseRelationshipModal(true)
            setContextMenu(null);
            // DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv);

        }else{
            SetInARel(true)
            if(binary){
                SetBinaryRel(true)
            }
            SetSource(props.mention.mentions)
            updateRelMentionColor('source',props.mention.mentions)

            DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv);
            setContextMenu(null);
        }

    }

    function handleDelete(e){
        e.stopPropagation();
        e.preventDefault();
        DeleteMention(e,props.mention,props.loc);

        //SetShowDeleteMetnionModal(true)
        setContextMenu(null);
        DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv);
    }

    /*    useEffect(()=>{
            if(NewMention.toString() === props.mention.mentions.split('_')[1]){
                console.log('TROVATO',NewMention)
            }
        },[MentionsList,NewMention])*/

    const handleKeyDownTag = (event) => {
        if (event.key === 'Enter') {
            // Your action here
            console.log('Tag confirmed:', event.target.value);
            selectTag(event,event.target.value);
            handleCloseTagAnno()



        }
    };


    function DeleteMention(e,mention,position){
        e.preventDefault()
        e.stopPropagation()
        let mentions = []
        mention.mentions.split(' ').map(m=>{
            mentions.push(MentionsList.filter(x=>x['mentions'] === m)[0])
        })
        if(mentions.length === 1){
            axios.delete('mentions/delete',{data:{start:mention.start,stop:mention.stop,mention_text:mention.mention_text,position:position}})
                .then(response=>{

                    SetDocumentDesc(response.data['document'])
                    SetMentionsList(response.data['mentions'])
                    SetConceptsList(response.data['concepts'])
                    SetTagsSplitted(response.data['tags'])

                })
        }
        else{
            SetShowDeleteMetnionModal(true)
        }

    }


    return (
        <div className={'mentionpart'}>
            {ShowDeleteMetnionModal && <SelectMentionToDelete show={ShowDeleteMetnionModal} setshow={SetShowDeleteMetnionModal} mention={props.mention}
                                                           position={props.loc}/>}
            {ShowInfoModal && <InfoModal show={ShowInfoModal} setshow={SetShowInfoModal} mention={props.mention}
            />}
            {ShowChooseRelationshipModal && <ChooseMentionModal type={'relationship'} show={ShowChooseRelationshipModal} setshow={SetShowChooseRelationshipModal} mention={props.mention} mention_id={props.id}
            />}
            {ShowCopyModal && <ChooseMentionModal type={'mention'} show={ShowCopyModal} setshow={SetShowCopyModal} mention={props.mention} mention_id={props.id}
            />}
            {ShowCopyConceptModal && <ChooseMentionModal type={'concept'} show={ShowCopyConceptModal} setshow={SetShowCopyConceptModal} mention={props.mention} mention_id={props.id}
            />}

            {ShowSuggestionModal && <SuggestionModal  show={ShowSuggestionModal} setshow={SetShowSuggestionModal} mention={props.mention} mention_id={props.id}
            />}
            {ShowAnnotateAllModal && <AnnotateAllModal  show={ShowAnnotateAllModal} setshow={SetShowAnnotateAllModal} mention={props.mention} mention_id={props.id} position={props.loc}
            />}



            {TagsSplitted && (View === 2 || View === 3) && !InARel && TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc)).length > 0 &&
                <>
                    <Tag tags={TagsSplitted.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id}/>
                </>
            }
            {ConceptsList && (View === 1 || View === 3) && !InARel && ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc)).length > 0 &&
                <>
                    <Concept concepts={ConceptsList.filter(x=>(x.start === props.mention.start && x.stop === props.mention.stop && x.position === props.loc))} mention={props.mention} mention_id = {props.id}/>
                </>
            }


            {CurAnnotator !== Username ? <div onClick={(e)=>{
                    if((e.altKey)) {
                        handleDelete(e)
                    }else if((e.shiftKey)){
                        console.log('relationships')
                        handleRelationship(e)
                    }else if (e.ctrlKey ) {
                        handleConcept(e)
                    }

                }
                }>
                    <div id={props.id} ref={inputEl} >
                        {props.mention_text.startsWith(' ') && !props.mention_text.endsWith(' ') && <>&nbsp;{props.mention_text.trim()}</>}
                        {props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text.trim()}&nbsp;</>}
                        {props.mention_text.endsWith(' ') && props.mention_text.startsWith(' ') && props.mention_text !== ' ' && <>&nbsp;{props.mention_text.trim()}&nbsp;</>}
                        {!props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text}</>}
                        {props.mention_text === (' ') && <>&nbsp;</>}
                    </div>
                </div> :
                <div onContextMenu={handleContextMenu} onClick={(e)=>{
                    if((e.altKey)) {
                        handleDelete(e)
                    }else if((e.shiftKey)){
                        console.log('relationships')
                        handleRelationship(e)
                    }else if (e.ctrlKey ) {
                        handleConcept(e)
                    }
                }
                }>

                    <div id={props.id} ref={inputEl} >

                        {props.mention_text.startsWith(' ') && !props.mention_text.endsWith(' ') && <>&nbsp;{props.mention_text.trim()}</>}
                        {props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text.trim()}&nbsp;</>}
                        {props.mention_text.endsWith(' ') && props.mention_text.startsWith(' ') && props.mention_text !== ' ' && <>&nbsp;{props.mention_text.trim()}&nbsp;</>}
                        {!props.mention_text.endsWith(' ') && !props.mention_text.startsWith(' ') && <>{props.mention_text}</>}
                        {props.mention_text === (' ') && <>&nbsp;</>}

                    </div>


                    <Menu
                        id={id}
                        open={openTagAnno && Tags && View !== 4}
                        anchorEl={anchorElTagAnno}
                        onClose={handleCloseTagAnno}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'center',
                        }}
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'center',
                        }}
                        sx={{ marginTop: '20px' }} // Sposta il menu di 20px sopra
                    >
                        <div></div>
                        <div style={{padding:'5%'}}>
                            <h6>Select tags</h6>
                            {Tags && Tags.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' })).map(tag => <MenuItem

                                sx={{
                                    '&:hover': {
                                        backgroundColor: AreasColors[tag], // Colore di sfondo on hover
                                        color: 'white', // Colore del font on hover

                                    },
                                    backgroundColor: 'white', // Colore di sfondo on hover
                                    color: AreasColors[tag], // Colore del font on hover

                                }}


                                autoFocus={false}
                                selected={SelectedTags.indexOf(tag) !== -1}
                                onClick={(e) => {
                                    selectTag(e, tag)
                                }}
                            >

                                {SelectedTags.indexOf(tag) !== -1 && <CheckIcon>
                                    <TextFieldsIcon fontSize="small"/>
                                </CheckIcon>}
                                {tag !== 'disease' ? tag : 'DDF'} </MenuItem>)}
                            <TextField onKeyDown={handleKeyDownTag} id="newTagField" label="Tag"
                                       style={{margin: '1vw', width: '80%', display: 'flex', justifyContent: 'left'}}
                                       variant="outlined"/>

                        </div>


                    </Menu>


                    {/*<Popover
                        id={id}
                        open={openTagAnno && Tags && Tags.length > 0}
                        anchorEl={anchorElTagAnno}
                        onClose={handleCloseTagAnno}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'center',
                        }}
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'center',
                        }}
                        sx={{ marginTop: '20px' }} // Sposta il menu di 20px sopra
                    >
                        <h5>Tags:</h5>
                        {Tags.map(tag=><div><Button onClick={handleCloseTagAnno}   sx={AreasColors ? {padding:'5px 5px',width:'100%',display:'flex',justifyContent:'left',color:AreasColors[tag]} : {padding:'5px 5px',width:'100%',display:'flex',justifyContent:'left',  color:'rgb(65, 105, 225)'}}>{tag}</Button></div>)}
                        <TextField onKeyDown={handleKeyDownTag} id="newTagField" label="Tag" style={{margin:'1vw',width:'80%',display:'flex',justifyContent:'left'}} variant="outlined" />


                    </Popover>*/}


                    <StyledMenu
                        open={contextMenu !== null && View !== 4}
                        onClose={handleClose}
                        // elevation={0}
                        anchorReference="anchorPosition"
                        anchorPosition={
                            contextMenu !== null
                                ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
                                : undefined
                        }
                    >
                        <div></div>
                        <div style={{display:'flex'}}>
                            <div >
                                {/* <MenuItem autoFocus={false}  onClick={(e)=>{
                                handleInfo(e)
                            }}>Ciao</MenuItem>*/}

                                <MenuItem autoFocus ={false} onClick={(e)=>{
                                    handleInfo(e)
                                }}>
                                    <ListItemIcon>
                                        <InfoIcon fontSize="small" />
                                    </ListItemIcon>
                                    Info
                                </MenuItem>
                                <MenuItem disabled={Modality === 1} onClick={(e)=>{
                                    handleSuggestion(e)
                                }}>
                                    <ListItemIcon>
                                        <AssistantIcon fontSize="small" />
                                    </ListItemIcon>
                                    Suggestion</MenuItem>
                                <MenuItem onClick={(e)=>{
                                    handleAnnotateAll(e)
                                }}>
                                    <ListItemIcon>
                                        <ContentCopyIcon fontSize="small" />
                                    </ListItemIcon>
                                    Annotate all</MenuItem>
                                <Divider />



                                <MenuItem onClick={(e)=> {
                                    handleConcept(e)
                                }}>
                                    <ListItemIcon>
                                        <AddIcon fontSize="small" />
                                    </ListItemIcon>
                                    Add Concept</MenuItem>

                                <MenuItem onClick={(e)=>{
                                    handleRelationship(e)
                                }}>
                                    <ListItemIcon>
                                        <HubIcon fontSize="small" />
                                    </ListItemIcon>
                                    Add Relationship</MenuItem>

                                <MenuItem onClick={(e)=>{
                                    handleRelationship(e,true)
                                }}>
                                    <ListItemIcon>
                                        <HubIcon fontSize="small" />
                                    </ListItemIcon>
                                    Add Binary Relationship</MenuItem>
                                <Divider />

                                <MenuItem style={{color:'#d00000'}} onClick={(e)=>{
                                    handleDelete(e)
                                }
                                }>
                                    <ListItemIcon >
                                        <DeleteIcon color='error' fontSize="small" />
                                    </ListItemIcon>
                                    Delete</MenuItem>




                            </div>



                        </div>

                    </StyledMenu>


                </div>}
            <Menu
                id="fade-menu"
                MenuListProps={{
                    'aria-labelledby': 'fade-button',
                }}
                anchorEl={anchorEl}
                open={open}
                onClose={handleCloseMenu}
            >
                <div></div>
                <MenuItem autoFocus ={false} onClick={(e)=>{
                    copyMention(e)
                }}>
                    <ListItemIcon>
                        <TextFieldsIcon fontSize="small" />
                    </ListItemIcon>
                    Copy mention
                </MenuItem>
                <MenuItem onClick={(e)=>{
                    copyMentionConcept(e)
                }}>
                    <ListItemIcon>
                        <ShareIcon fontSize="small" />
                    </ListItemIcon>
                    Copy mention and tag(s)</MenuItem>
                <MenuItem onClick={(e)=>{
                    copyMentionTag(e)
                }}>
                    <ListItemIcon>
                        <ShareIcon fontSize="small" />
                    </ListItemIcon>
                    Copy mention and tag(s)</MenuItem>
            </Menu>

        </div>
    )
}