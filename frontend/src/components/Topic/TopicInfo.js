import {Col, Row} from "react-bootstrap";

import axios from "axios";

import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import {AppContext} from "../../App";


const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;


export default function TopicInfo(props) {
    const {collection, document_id, collectiondocuments, topic} = useContext(AppContext);
    const [CollectionDocuments, SetCollectionDocuments] = collectiondocuments
    const [Info, SetInfo] = useState({})
    const [Topic, SetTopic] = topic


    useEffect(() => {
        if (Topic) {
            axios.get('topic', {params: {topic: Topic}})
                .then(response => {
                    SetInfo(response.data['topics'][0])
                })
        }

    }, [Topic])

    return (
        <div style={{padding:'2%',margin:'2%',backgroundColor:'#f5f5f5'}}>
            {Info && <div><h4>Topic </h4>

                {Object.keys(Info).map(key => <div>
                        <span>
                            <b>{key}: </b>
                        </span>
                        <span>
                            <>{Info[key]}</>
                        </span>
                        <br/>
                    </div>)}
            </div>}


        </div>
    );
}


