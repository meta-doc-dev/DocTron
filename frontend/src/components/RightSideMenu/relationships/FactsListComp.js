import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';

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
import axios from "axios";
import { cloneDeep } from 'lodash';
const checkedIcon = <CheckBoxIcon fontSize="small" />;

import {AppContext} from "../../../App";
import IconButton from "@mui/material/IconButton";
import Chip from "@mui/material/Chip";
import {CircularProgress} from "@mui/material";
import RightSideConcept from "../associations/RightSideConcept";
import RightSideRelation from "./RightSideRelation";
import SearchIcon from "@material-ui/icons/Search";
import SearchRelationComponent from "./SearchRelationComponent";
import {ConceptContext} from "../../../BaseIndex";
import {RelSearchContext} from "../../../BaseIndex";
import EditIcon from '@mui/icons-material/Edit';
import {ClickOnBaseIndex, updateRelMentionColor, waitForElm} from "../../HelperFunctions/HelperFunctions";
import RelationshipComponent from "./RelationshipComponent";
// import * as URL from "url";
import AddIcon from '@mui/icons-material/Add';
import CommentModal from "../../Annotations/mentions/modals/CommentModal";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import TextField from "@mui/material/TextField";
import DialogActions from "@mui/material/DialogActions";

export default function FactsListComp(props){
    const { modality,inarel,allrels,document_id,openall,sourceall,view,predicateall,targetall,username,curannotator,snackmessage,opensnack,mentions,showrelspannel,readonlyrelation,modifyrel,targettext,predicatetext,sourcetext,targetconcepts,predicateconcepts,predicate,target,source,relationship,relationshipslist,sourceconcepts } = useContext(AppContext);
    const [Modality,SetModality] = modality
    const [DocumentID,SetDocumentID] = document_id
    const [MentionsList, SetMentionsList] = mentions
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Username,SetUsername] = username
    const [ShowComment,SetShowComment] = useState(false)
    const [OpenComment,SetOpenComment] = useState(false)
    const [OpenAll,SetOpenAll] = useState(0)
    const [Open,SetOpen]=openall
    const [RelationshipsList, SetRelationshipsList] = relationshipslist
    const [RelationshipsListFiltered, SetRelationshipsListFiltered] = useState(false)
    const [LoadingRel,SetLoadingRel] = useState(false)
    // const [RelationshipsList, SetRelationshipsList] = useState(false)
    const [OpenSubject,SetOpenSubject] = useState(false)
    const [OpenPredicate,SetOpenPredicate] = useState(false)
    const [OpenObject,SetOpenObject] = useState(false)
    const [OpenOther,SetOpenOther] = useState(false)
    const {areaSearch,urlSearch,nameSearch,areasSearch,searchsubject,searchpredicate,searchobject} =  useContext(ConceptContext);
    const [ShowList,SetShowList] = useState(false)
    const [OpenRelation,SetOpenRelation] = useState(false)
    // const {searchsubj,searchobj,searchpredicate} =  useContext(RelSearchContext);
    const [SearchSubject, SetSearchSubject] = searchsubject
    const [SearchPredicate, SetSearchPredicate] = searchpredicate
    const [SearchObject, SetSearchObject] = searchobject
    // const [SearchSubject, SetSearchSubject] = useState(false)
    // const [SearchPredicate, SetSearchPredicate] = useState(false)
    // const [SearchObject, SetSearchObject] = useState(false)
    const [InARel,SetInARel] = inarel
    const [Source,SetSource] = source;
    const [SourceConcepts,SetSourceConcepts] = sourceconcepts
    const [PredicateConcepts,SetPredicateConcepts] = predicateconcepts
    const [TargetConcepts,SetTargetConcepts] = targetconcepts
    const [SourceText,SetSourceText] = sourcetext
    const [PredicateText,SetPredicateText] = predicatetext
    const [TargetText,SetTargetText] =targettext
    const [Target,SetTarget] = target;
    const [Predicate,SetPredicate] = predicate;
    const [SnackMessage,SetSnackMessage] = snackmessage;
    const [OpenSnack,SetOpenSnack] = opensnack
    const {area,url,name,urlname,description,areas,conceptslist} =  useContext(ConceptContext);
    const [Areas,SetAreas] = areas
    const [RelCount,SetRelCount] = useState(0)
    const [ConceptsList,SetConceptsList] = conceptslist
    const [Relationship,SetRelationship] = relationship
    const [SourceFilteredRelations,SetSourceFilteredRelations] = useState(false)
    const [PredicateFilteredRelations,SetPredicateFilteredRelations] = useState(false)
    const [TargetFilteredRelations,SetTargetFilteredRelations] = useState(false)
    const [OtherFilteredRelations,SetOtherFilteredRelations] = useState(false)
    const [ShowRels,SetShowRels] = showrelspannel
    const [SourceAll,SetSourceAll] = sourceall;
    const [PredicateAll,SetPredicateAll] = predicateall;
    const [TargetAll,SetTargetAll] = targetall;
    const [AddArea,SetAddArea] = useState(false)
    const [AddConcept,SetAddConcept] = useState(false)
    const [Options,SetOptions] = useState(false)
    const [View,SetView] = view
    const [Comment,SetComment] = useState(false)
    const [AreaToFilter,SetAreaToFilter] = useState(false)
    const [UrlToFilter,SetUrlToFIlter] = useState(false)
    const [ConceptToFilter,SetConceptToFIlter] = useState(false)
    const [ShowReadOnlyRelation,SetShowReadOnlyRelation] = readonlyrelation
    const [Modify,SetModify] = modifyrel
   /* let names = []
    ConceptsList.map(x=>{
        names.push(x.name)
    })
    let urls = []
    ConceptsList.map(x=>{
        urls.push(x.url)
    })*/
    // const [AreaValue,SetAreaValue] = area
    // const [ConceptValue,SetConceptValue] =  name
    // const [UrlValue,SetUrlValue] = url
    const [AllRels,SetAllRels] = allrels
    const [AreaValue,SetAreaValue] = areaSearch
    const [ConceptValue,SetConceptValue] = nameSearch
    const [UrlValue,SetUrlValue] = urlSearch
    const [Value,SetValue] = useState(null)
    // const sorted_mentions = RelationshipsList.sort(function(a, b) { return a.start - b.start; })
    // const sorted_mentions_10 = sorted_mentions.slice(0,5)


/*    useEffect(()=>{
        async function fetchRelationships(){
            const response = await axios.get('relationships',{params:{user:CurAnnotator}});
            console.log('request',response)
            SetRelationshipsList(response.data)
            return response
        }
        fetchRelationships()

    },[])*/








    function copyRelation(e,relation){
        e.preventDefault();
        e.stopPropagation();
        let source = relation['subject']
        let predicate = relation['predicate']
        let target = relation['object']
        if(Modality === 2){
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Saving...'})

            axios.post('relationships/copy', {
                subject: source,
                predicate: predicate,
                object: target,
                user: CurAnnotator
            }).then(response => {
                console.log(response)
                SetSnackMessage({'message': 'Saved'})
            }).catch(error => {
                SetSnackMessage({'message': 'ERROR'})

                console.log(source, predicate, target)
            })

        }
    }

    function deleteRelation(e,relation){
        e.preventDefault();
        e.stopPropagation();
        let source = relation['subject']
        let predicate = relation['predicate']
        let target = relation['object']
        if(Modality === 2){
            console.log('ecco')
            SetOpenSnack(true)
            SetSnackMessage({'message':'You cannot annotate this document'})
        }else {
            SetOpenSnack(true)
            SetSnackMessage({'message': 'Deleting...'})
            axios.delete('relationships', {
                data: {
                    source: source,
                    predicate: predicate,
                    target: target
                }
            }).then(response => {
                SetRelationshipsList(response.data)
                reset_lists()
                SetSource(false)
                SetPredicate(false)
                SetTarget(false)
                SetTargetText(false)
                SetPredicateText(false)
                SetSourceText(false)
                SetTargetConcepts(false)
                SetPredicateConcepts(false)
                SetSourceConcepts(false)
                SetLoadingRel(false)
                SetOpenRelation(false)
                SetShowReadOnlyRelation(false)
                SetInARel(false)
                SetSnackMessage({'message': 'Deleted'})

            }).catch(error =>
                console.log(source, predicate, target))
        }
    }


    useEffect(()=>{
        if(RelationshipsList){
            var rels = []
            rels = RelationshipsList.filter(x=>x['start'] === -1)
            SetRelationshipsList(rels)

            if(!Modify){
                SetRelCount(RelationshipsList['counttotal'])
            }
        }


    },[RelationshipsList])


    function removeAllChildren(nodetype){
        let target = document.getElementById(nodetype)
        // let target ='';
        let sources = Array.from(document.getElementsByClassName(nodetype))
        if(target !== null){
            let els =Array.from(document.querySelectorAll('div[class^="bulls"]'))
            sources.map(el=>{
                el.classList.remove(nodetype)
            })

            if(target.childNodes){
                console.log('node',target.childNodes)
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
    useEffect(() => {
        if(!ShowComment){
            SetComment(false)
            SetOpenComment(false)
        }
    }, [ShowComment]);

    useEffect(() => {
        if(OpenComment){
            var rel = {}
            rel['subject_concept_url'] = OpenComment.subject.concept.concept_url
            rel['object_concept_url'] = OpenComment.object.concept.concept_url
            rel['predicate_concept_url'] = OpenComment.predicate.concept.concept_url
            rel['subject_concept_area'] = OpenComment.subject.concept.concept_area
            rel['object_concept_area'] = OpenComment.object.concept.concept_area
            rel['predicate_concept_area'] = OpenComment.predicate.concept.concept_area

            axios.get('relationships/assertion_comment',{params:{relationship:rel}})
                .then(response=>{

                    SetComment(response.data['comment'] === '' ? false : response.data['comment'])
                })
        }else{
            SetComment(false)
            SetShowComment(false)
        }




    }, [OpenComment]);

    function uploadComment(){
        if(OpenComment){
            var rel = {}
            rel['object_area'] = OpenComment.object.concept.concept_area
            rel['subject_area'] = OpenComment.subject.concept.concept_area
            rel['predicate_area'] = OpenComment.predicate.concept.concept_area
            rel['object_url'] = OpenComment.object.concept.concept_url
            rel['subject_url'] = OpenComment.subject.concept.concept_url
            rel['predicate_url'] = OpenComment.predicate.concept.concept_url
            var comment = document.getElementById("comment").value
            axios.post('relationships/assertion_comment',{relationship:rel,comment:comment})
                .then(response=>{

                    SetShowComment(false)
                    SetComment(false)
                    SetOpenComment(false)
                })
        }
    }

    useEffect(()=>{
        console.log('relationship',Relationship)
        // let mentions = props.mention.mentions.split(' ')
        removeAllChildren('source')
        removeAllChildren('predicate')
        removeAllChildren('target')
        if(Relationship){
            let source = Relationship['subject']
            if(Object.keys(source['mention']).length > 0) {
                let start_source = source['mention']['start']
                let stop_source = source['mention']['stop']
                let mention_source = MentionsList.find(x=>x['start'] === start_source && x['stop'] === stop_source)
                if(mention_source){
                    let mentions_source = mention_source.mentions
                    console.log(mention_source,mentions_source)
                    SetSource(mentions_source)
                    updateRelMentionColor('source',mentions_source)
                }


                // waitForElm(".source").then(r=>{
                //     r.scrollIntoView({ behavior: "smooth"})
                // })

            }else if (Object.keys(source['concept']).length > 0){
                SetSourceConcepts([source['concept']])
                SetSource(false)
                SetSourceText(source['concept']['concept_name'])
            }


            let predicate = Relationship['predicate']
            console.log(predicate['mention'])
            if(Object.keys(predicate['mention']).length > 0) {
                let start_predicate = predicate['mention']['start']
                let stop_predicate = predicate['mention']['stop']
                let mention_predciate = MentionsList.find(x => x['start'] === start_predicate && x['stop'] === stop_predicate)
                if(mention_predciate){
                    let mentions_predciate = mention_predciate.mentions
                    console.log(mention_predciate,mentions_predciate)
                    SetPredicate(mentions_predciate)
                    updateRelMentionColor('predicate',mentions_predciate)

                }

                // if(mentions.indexOf(mentions_predciate) !== -1){
                //     // questa è la source
                //     changeRole('Predicate')
                // }
            }else if (Object.keys(predicate['concept']).length > 0){
                SetPredicateConcepts([predicate['concept']])
                SetPredicate(false)
                SetPredicateText(source['concept']['concept_name'])
            }

            let target = Relationship['object']
            if(Object.keys(target['mention']).length > 0) {
                let start_target = target['mention']['start']
                let stop_target = target['mention']['stop']
                let mention_target = MentionsList.find(x=>x['start'] === start_target && x['stop'] === stop_target)
                if(mention_target){
                    let mentions_target = mention_target.mentions
                    console.log(mention_target,mentions_target)
                    SetTarget(mentions_target)

                    updateRelMentionColor('target',mentions_target)
                }


            }else if (Object.keys(target['concept']).length > 0){
                SetTargetConcepts([target['concept']])
                SetTarget(false)
                SetTargetText(source['concept']['concept_name'])
            }

        }
    },[Relationship])


    useEffect(() => {
        if(OpenRelation && !InARel){
            SetOpenRelation(false)
        }
    }, [InARel]);


    function reset_lists(){
        if(RelationshipsList && MentionsList){
            var all_rels = []
            var sources_all = []
            var predicates_all = []
            var targets_all = []
            RelationshipsList.map(rel=>{
                var cur_rel = []
                var rels = rel.subject.mention
                var concs = rel.subject.concept
                if(rels.start){
                    var start = rels.start
                    var end = rels.stop
                    var mention = MentionsList.find(x=>x['start'] === start && x['stop'] === end)
                    if (mention){
                        cur_rel.push(mention.mentions)
                    }
                    if(mention && sources_all.indexOf(mention.mentions) === -1){
                        sources_all.push(mention.mentions)
                    }
                }else{
                    cur_rel.push(concs.concept_name)
                }
                var relp = rel.object.mention
                var conp = rel.object.concept
                if(relp.start){
                    var start = relp.start
                    var end = relp.stop
                    var mention = MentionsList.find(x=>x['start'] === start && x['stop'] === end)
                    if (mention){
                        cur_rel.push(mention.mentions)
                    }
                    if(mention && targets_all.indexOf(mention.mentions) === -1){
                        targets_all.push(mention.mentions)

                    }
                }else{
                    cur_rel.push(conp.concept_name)
                }
                var relt = rel.predicate.mention
                var conct = rel.predicate.concept
                if(relt.start){
                    var start = relt.start
                    var end = relt.stop
                    var mention = MentionsList.find(x=>x['start'] === start && x['stop'] === end)
                    if(mention){
                        cur_rel.push(mention.mentions)
                    }
                    if(mention && predicates_all.indexOf(mention.mentions) === -1){
                        predicates_all.push(mention.mentions)


                    }
                }else{
                    cur_rel.push(conct.concept_name)
                }
                all_rels.push(cur_rel)
            })
            SetSourceAll(sources_all)
            SetPredicateAll(predicates_all)
            SetTargetAll(targets_all)
            SetAllRels(all_rels)

        }
    }


    useEffect(() => {
        if(Relationship){
            SetShowReadOnlyRelation(true)
            SetOpenRelation('predicate' + '_' + RelationshipsList.indexOf(Relationship).toString())
        }
    }, [Relationship]);


    useEffect(() => {
        if(OpenRelation){
            SetShowReadOnlyRelation(true)
        }
        if(OpenAll === true) {

            if (RelationshipsList && MentionsList ) {
                SetOpen(true)
                reset_lists()
                SetInARel(false)
            }
        }else if(OpenAll === false){
            SetOpen(false)
            SetInARel(true)
            SetRelationship(false)
            SetSourceAll(false)
            SetPredicateAll(false)
            SetAllRels([])
            SetTargetAll(false)


        }
    }, [OpenAll]);

    useEffect(()=>{
        if(DocumentID){
            SetOpen(false)
            SetOpenAll(0)

        }
    },[DocumentID])


    useEffect(() => {
        if(InARel){
            SetShowList(true)
        }
    }, [InARel]);

    return(
        <div id='rightsiderelationshipsclass'>
            {ShowComment &&   <Dialog
                open={ShowComment}
                onClose={(e)=> {
                    e.preventDefault()
                    SetShowComment(false)
                    SetComment(false)
                    SetOpenComment(false)
                }}
                maxWidth={'lg'}
                sx={{width:'100%'}}


            >
                <DialogTitle>Leave a comment about your annotation</DialogTitle>
                <DialogContent>
                    <DialogContentText>

                    </DialogContentText>
                    <div>
                        <TextField           multiline
                                             rows={4} id="comment" sx={{margin:'10px 0',width:'100%'}} label="Comment" variant="outlined" />

                        {Comment && <><h5>Your comment:</h5>
                            <div>{Comment}</div>
                        </>}
                    </div>
                </DialogContent>
                <DialogActions>
                    <Button        onClick={(e)=> {
                        e.preventDefault()
                        SetShowComment(false)
                        SetComment(false)
                        SetOpenComment(false)
                    }}>Cancel</Button>
                    <Button onClick={uploadComment}>Confirm</Button>
                </DialogActions>
            </Dialog>}


            {(Modify && InARel) ? <RelationshipComponent /> :
            <div>
                {(RelationshipsList) ? <>
                        <div>
                            <Button disabled={View === 4} onClick={()=> {
                                SetShowList(prev => !prev);

                            }} variant="text">Facts <i>({RelationshipsList.length})</i></Button>
                        </div>




                        <Collapse in={ShowList}>
                        <div style={{marginTop:'15px',paddingLeft:'5%'}}>

                                {RelationshipsList.map((rel,i)=>
                                    <>
                                        <div ><span className={'areas_header_instance'}><span onClick={(e)=> {
                                            e.preventDefault()
                                            e.stopPropagation()
                                            if(OpenRelation === false || OpenRelation !== 'predicate' + '_' + i.toString()){
                                                SetShowReadOnlyRelation(true)
                                                SetSource(false)
                                                SetPredicate(false)
                                                SetTarget(false)
                                                SetSourceText(false)
                                                SetPredicateText(false)
                                                SetTargetText(false)
                                                SetSourceConcepts(false)
                                                SetPredicateConcepts(false)
                                                SetTargetConcepts(false)
                                                SetOpenRelation('predicate' + '_' + i.toString())
                                                SetInARel(false)
                                                SetRelationship(rel)

                                            }else{
                                                SetOpenRelation(false)
                                                SetShowReadOnlyRelation(false)
                                                SetModify(false)
                                                SetRelationship(false)
                                                SetSource(false)
                                                SetPredicate(false)
                                                SetTarget(false)
                                                SetSourceText(false)
                                                SetPredicateText(false)
                                                SetTargetText(false)
                                                SetSourceConcepts(false)
                                                SetPredicateConcepts(false)
                                                SetTargetConcepts(false)
                                                SetInARel(false)

                                            }
                                        }} className={OpenRelation === 'predicate_' + i.toString() ? 'selected_item':''}>{rel['text'] !== '' ? rel['text'] : 'Relation ' + i.toString()}</span></span>
                                            &nbsp;&nbsp;<span><Button variant={'outlined'} size={'small'} onClick={(e)=>{
                                                e.preventDefault()
                                                e.stopPropagation()
                                                SetShowComment(true)
                                                SetOpenComment(rel)


                                            }}>Comment</Button></span>

                                            {CurAnnotator === Username ? <><div style={{display:"inline-block",marginLeft:'10px'}}>
                                                {OpenRelation === 'predicate' + '_' + i.toString() &&
                                                <div style={{display:"inline-block"}}>
                                                    <IconButton onClick={(e)=> {
                                                    e.preventDefault()
                                                    e.stopPropagation()

                                                    SetShowReadOnlyRelation(false);
                                                    SetModify(true)
                                                }}>
                                                    <EditIcon />
                                                </IconButton>
                                                    <IconButton onClick={(e)=>deleteRelation(e,rel)}>
                                                    <DeleteIcon />
                                                    </IconButton>

                                                    </div>

                                                }

                                            </div>
                                            </> : <>
                                            <div style={{display:"inline-block"}}>
                                                <IconButton onClick={(e)=>copyRelation(e,rel)}>
                                                    <AddIcon />
                                                </IconButton>

                                            </div>

                                            </>}
                                        </div>
                                        {OpenRelation === 'predicate'+'_'+i.toString() && <Collapse in={OpenRelation === 'predicate'+'_'+i.toString()}><RightSideRelation time={rel.time} count={rel.count}/>
                                        </Collapse> }

                                    </>)}




                            </div>

                    </Collapse>









                    </>
                    : <CircularProgress />}
            </div>}


        </div>
    );
}