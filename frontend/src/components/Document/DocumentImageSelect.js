import React, {useContext, useEffect, useState} from "react";

import { ReactLassoSelect } from "react-lasso-select";
import axios from "axios";
import {AppContext} from "../../App";
import {ConceptContext} from "../../BaseIndex";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";



function pointsToString(points) {
    return points.map(({ x, y }) => `${x},${y}`).join(" ");
}

export default function DocumentImageSelect() {
    const [width, setWidth] = useState(800);
    const [Image, SetImage] = useState(null);
    const init = "172,173 509,99 458,263"
        .split(" ")
        .map((c) => c.split(",").map(Number))
        .map(([x, y]) => ({ x, y }));

    const {
        autoannotation,
        saving,
        modality,
        loadingann,
        newmention,
        annotatedlabels,
        username,
        modifyrel,
        curannotator, factslist,
        documentdescription,
        document_id,
        topic,pointhigh,
        fields,
        fieldsToAnn,points
    } = useContext(AppContext);
    const [LoadingNewAnn, SetLoadingNewAnn] = loadingann
    const [Topic, SetTopic] = topic
    const [Clicked,SetClicked] = useState(false);
    const [Points, setPoints] = points;
    const [curPoints, setCurPoints] = useState([]);
    const [AutoAnnotate, SetAutoAnnotate] = autoannotation
    const [DocumentID, SetDocumentID] = document_id

    const [FactsList, SetFactsList] = factslist

    const [DocumentDescEmpty, SetDocumentDescEmpty] = useState(false)

    const [CurAnnotator, SetCurAnnotator] = curannotator
    const [AnnotatedLabels, SetAnnotatedLabels] = annotatedlabels
    const [PointHigh,SetPointHigh] = pointhigh


    const [LoadLab, SetLoadLab] = useState(false)


    useEffect(()=>{
        if(PointHigh){
             setCurPoints(PointHigh.split(" ")
                        .map((c) => c.split(",").map(Number))
                        .map(([x, y]) => ({ x, y }))
                    );
        }else{
            setCurPoints([])
        }
    },[PointHigh])

    useEffect(() => {
        if ((DocumentID && CurAnnotator) || LoadingNewAnn) {
            axios.get('object_detection', {params: {document_id: DocumentID, user: CurAnnotator}})
                .then(response => {

                    if (response.data['points'].length > 0) {

                        setPoints(response.data['points']);
                       /* setCurPoints(response.data['points'][0].split(" ")
                            .map((c) => c.split(",").map(Number))
                            .map(([x, y]) => ({ x, y }))
                        );*/
                    }
                })

            axios.get('get_document_content', {params: {document_id: DocumentID, user: CurAnnotator}})
                .then(response => {

                    console.log('response',response.data)
                    SetDocumentDescEmpty(response.data['empty'])
                    if (response.data['image']) {
                        SetImage(`data:image/png;base64,${response.data['image']}`);
                    }
                    //SetImage(response.data['image'])
                })
            // GET FIELDS OF A DOCUMENT


        }
    }, [DocumentID, CurAnnotator, AutoAnnotate, LoadingNewAnn, Topic])


    function uploadPoints(path){
        if(path !== '' && path !== undefined && path !== null && path !== PointHigh){
            if(PointHigh === false){
                axios.post("object_detection/insert",{points:path})
                    .then(response=>{console.log(response);
                        SetClicked(false)
                        setPoints(response.data['points'])
                        SetPointHigh(path)
                    })
                    .catch(error => console.log(error))
            }else{
                axios.post("object_detection/update",{points:path,points_prev:PointHigh})
                    .then(response=>{console.log(response);
                        SetClicked(false)
                        setPoints(response.data['points'])

                    })
                    .catch(error => console.log(error))
            }


        }

    }

    return (
        <div>
            <Paper elevation={2}>

                <div style={{margin:'10px 0px',textAlign:'center'}}>
                    <div>
                        <span><b>Doc ID: </b></span><span>{DocumentDescEmpty['doc_id']}</span>
                    </div>
                    <div>
                        {Image && <ReactLassoSelect
                            value={curPoints}
                            src={Image}
                            onChange={(path) => {
                                setCurPoints(path);

                            }}
                            onComplete={(path)=>uploadPoints(pointsToString(path))}
                            imageStyle={{ width: `${width}px` }}

                        />}
                        <br />
              {/*          Image width:{" "}
                        <input
                            type="range"
                            min='0'
                            max="1000"
                            value={width}
                            onChange={(e) => setWidth(e.target.value)}
                        />
                        <br />*/}
                        <div>
                            {/*      <span>
                               Points: {pointsToString(points)}
                           </span>*/}
                            <span>
                                <Button variant={'contained'} color={'error'} size={'small'}
                                        onClick={()=>{

                                /*    axios.delete('object_detection',{data:{points:curPoints}})
                                        .then(response => setPoints([]))
                                        .catch(error => console.log(error))*/

                                }}
                                >Clear</Button>
                            </span>
                        </div>
                        <br/>

                    </div>

                </div>

            </Paper>

        </div>
    );
}