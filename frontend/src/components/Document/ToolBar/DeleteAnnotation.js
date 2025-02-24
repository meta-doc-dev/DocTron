import {Col, Row} from "react-bootstrap";

import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import DeleteIcon from '@mui/icons-material/Delete';

import axios from "axios";
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import {AppContext} from "../../../App";
import {DeleteRange} from "../../HelperFunctions/HelperFunctions";


function DeleteAnnotation(){
    const { concepts,expand,annotatedlabels,inarel,documentdescription,showupload,showstats,showview,showcollections,showfilter,showbar,showdocs,showmembers,showsettings,
        showdownload,relationship,relationshipslist,showfactspannel,currentdiv,firstsel,newfact,secondsel,showlabelspannel,showmentionsspannel,showconceptspannel,showrelspannel,showautomaticannotation,mentions,startrange,endrange,fields,fieldsToAnn } = useContext(AppContext);
    const [InARel,SetInARel] = inarel
    const [RelationshipsList, SetRelationshipsList] = relationshipslist

    const [DocumentDesc,SetDocumentDesc] = documentdescription

    const [MentionsList,SetMentionsList] = mentions
    const [ConceptsList,SetConceptsList] = concepts
    const [ShowFacts,SetShowFacts] = showfactspannel

    const [ShowLabels,SetShowLabels] = showlabelspannel
    const [ShowMentions,SetShowMentions] = showmentionsspannel
    const [ShowConcepts,SetShowConcepts] = showconceptspannel
    const [ShowRels,SetShowRels] = showrelspannel
    const [ShowAutoAnno,SetShowAutoAnno] = showautomaticannotation;
    const [NewFact,SetNewFact] = newfact;
    const [Start,SetStart] = startrange
    const [End,SetEnd] = endrange
    const [CurrentDiv,SetCurrentDiv] = currentdiv
    const [Expand,SetExpand] = expand
    const [FirstSelected,SetFirstSelected] = firstsel
    const [SecondSelected,SetSecondSelected] = secondsel
    const [Relationship,SetRelationship] = relationship

    const [ShowDeleteAnnotationModal,SetShowDeleteAnnotationModal] = useState(false)
    const [ShowDownload,SetShowDownload] = showdownload
    const [ShowUpload,SetShowUpload] = showupload
    const [ShowStats,SetShowStats] = showstats
    const [ShowView,SetShowView] = showview
    const [ShowCollections,SetShowCollections] = showcollections
    const [ShowFilter,SetShowFilter] = showfilter
    const [ShowBar, SetShowBar] = showbar;
    const [ShowDocs,SetShowDocs] = showdocs
    const [ShowMembers,SetShowMembers] =showmembers
    const [ShowSettings,SetShowSettings] =showsettings
    const [AnnotatedLabels,SetAnnotatedLabels] =annotatedlabels

    function deleteAnnotation(e){
        e.preventDefault()
        e.stopPropagation()
        //axios.get('compute_stats')
        axios.post('delete_annotation_all')
            .then(r=>{
                SetShowDeleteAnnotationModal(false);
                SetMentionsList([])
                SetRelationshipsList([])
                SetRelationship(false)
                SetConceptsList([])
                SetDocumentDesc(r.data['document'])
                SetNewFact(false)
                SetShowRels(false)
                SetShowLabels(false)
                SetShowConcepts(false)
                SetShowMentions(false)
                SetExpand(false)
                SetShowFacts(false)

                SetShowStats(false)
                SetAnnotatedLabels(false)
                SetShowDocs(false)
                SetShowCollections(false)
                SetShowView(false)
                SetShowMembers(false)
                SetShowFilter(false)
                SetShowSettings(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)

                DeleteRange(SetStart,SetEnd,SetFirstSelected,SetSecondSelected,SetCurrentDiv)

            })
            .catch(error=>console.log('error',error))
    }



    return(
        <div className='inline'>

               <>
                   <Tooltip title="Delete Annotation">

                       <Button variant="outlined" color={'error'} disabled = {InARel} size="small" className={'bt'} onClick={()=>SetShowDeleteAnnotationModal(true)}>
                           <DeleteIcon />
                       </Button>

                </Tooltip>
               </>


            {ShowDeleteAnnotationModal &&
            <Dialog
                open={ShowDeleteAnnotationModal}
                onClose={()=>SetShowDeleteAnnotationModal(false)}

                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Delete annotation
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Are you sure you want to remove your annotations for this document?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={()=> {
                        SetShowDeleteAnnotationModal(false);
                    }} color={'error'}>No</Button>
                    <Button onClick={deleteAnnotation}  autoFocus>
                        Yes
                    </Button>
                </DialogActions>
            </Dialog>
            }
        </div>


    );

}
export default DeleteAnnotation

// {/*{ShowDeleteAnnotationModal &&*/}
// {/*<Dialog*/}
// {/*    open={ShowDeleteAnnotationModal}*/}
// {/*    onClose={()=>SetShowDeleteAnnotationModal(false)}*/}
//
// {/*    aria-labelledby="alert-dialog-title"*/}
// {/*    aria-describedby="alert-dialog-description"*/}
// {/*>*/}
// {/*    <DialogTitle id="alert-dialog-title">*/}
// {/*        Delete concept*/}
// {/*    </DialogTitle>*/}
// {/*    <DialogContent>*/}
// {/*        <DialogContentText id="alert-dialog-description">*/}
// {/*            Are you sure you want to remove all the annotations for this document?*/}
// {/*        </DialogContentText>*/}
// {/*    </DialogContent>*/}
// {/*    <DialogActions>*/}
// {/*        <Button onClick={()=> {*/}
// {/*            SetShowDeleteAnnotationModal(false);*/}
// {/*        }}>Disagree</Button>*/}
// {/*        <Button onClick={deleteAnnotation} autoFocus>*/}
// {/*            Delete*/}
// {/*        </Button>*/}
// {/*    </DialogActions>*/}
// {/*</Dialog>*/}
// {/*}*/}