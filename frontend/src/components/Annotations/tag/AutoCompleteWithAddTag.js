import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import React, {useContext, useEffect, useState} from "react";
import {Col, Row} from "react-bootstrap";
import Button from "@mui/material/Button";
import Mention from "../mentions/Mention";

import axios from "axios";
import {ButtonGroup} from "@mui/material";

import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

import '../annotation.css'
import {CircularProgress} from "@mui/material";
import {AppContext} from "../../../App";

import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';
import {RelationConceptContext} from "../concepts/RelationshipConceptModal";
import {ConceptContext, RelSearchContext} from "../../../BaseIndex";
import {isElementOfType} from "react-dom/test-utils";

export default function AutoCompleteWithAddTag(props) {
    const {inarel, tags, newfact, newfactin} = useContext(AppContext);

    const [InARel, SetInARel] = inarel
    const [NewFact, SetNewFact] = newfact
    const [NewFactInterno, SetNewFactInterno] = newfactin


    const {
        area,
        url,
        name,
        areas,
        conceptslist,
        areaSearch,
        searchsubject,
        searchpredicate,
        searchobject
    } = useContext(ConceptContext);
    const {area1, url1, name1, urlname1, description1, areas1, conceptslist1} = useContext(RelationConceptContext);

    const [SearchSubject, SetSearchSubject] = searchsubject
    const [SearchPredicate, SetSearchPredicate] = searchpredicate
    const [SearchObject, SetSearchObject] = searchobject


    const [ConceptsList, SetConceptsList] = conceptslist
    const [Tags, SetTags] = tags

    const [AreaValue, SetAreaValue] = area

    const [AreaValueRel, SetAreaValueRel] = (InARel || NewFact || NewFactInterno) ? area1 : useState(null)


    const [AreaValueSearch, SetAreaValueSearch] = (SearchObject || SearchPredicate || SearchSubject) ? areaSearch : useState(null)


    const [AddArea, SetAddArea] = useState(false)
    const [AreaOptions, SetAreaOptions] = useState(false)
    const [AreaValueFinal, SetAreaValueFinal] = useState(null)

    const [NewConcept,SetNewConcept] = useState(false)


    let areas_list = []
    Tags.map(x => {
        areas_list.push(x)
    })



    function resetOptions() {
        let options = []
        Tags.map(x => {
            let obj = {}
            obj['area'] = x
            // console.log('opt1', obj, options, options.indexOf(obj))
            const filtered = options.filter(ele => ele.area === x['area']);
            if (filtered.length === 0) {
                options.push(obj)
            }

        })
        SetAreaOptions(options)

        SetNewConcept(false)
    }


    function updateConceptsListsArea(newValue) {
        let options_c = []
        // SetValue(AreaValue)
        Tags.map(x => {
            let obj = {}
            if (x.trim() === newValue.area.trim()) {

                obj['area'] = x
                let filtered = [];

                // escludo concetti con stesso nome per non avere duplicati nella lista
                filtered = options_c.filter(ele => ele.name === x['name']);
                if (filtered.length === 0) {
                    options_c.push(obj)

                }

            }


        })



    }

    /*function updateoptions(type) {
        if(!NewConcept){
            let filtered = []
            let filtered_area = []
            let filtered_name = []
            let filtered_urls = []
            ConceptsList.map(x => {
                filtered.push(x)
            })

            if (AreaValueFinal !== null && type !== 'area') {
                ConceptsList.map((x, i) => {
                    if (x.area !== AreaValueFinal.area) {
                        filtered.splice(i, 1)
                    }
                })

            }
            if (UrlValueFinal !== null && type !== 'url') {
                ConceptsList.map(x => {
                    if (x.url !== UrlValueFinal.url) {
                        // let fil = filtered.filter(c=>c['url'] === x.url)[0]
                        let index = -1
                        filtered.map((j, i) => {
                            if (j['url'] === x.url) {
                                index = i
                            }

                        })
                        // let index = filtered.indexOf(fil)
                        filtered.splice(index, 1)
                    }
                })
            }
            if (ConceptValueFinal !== null && type !== 'name') {
                ConceptsList.map(x => {
                    if (x.name !== ConceptValueFinal.name) {
                        let index = []
                        filtered.map((j, i) => {
                            if (j['name'] === x.name) {
                                index.push(i)
                            }

                        })
                        index.map(c => filtered.splice(c, 1))
                        // let fil = filtered.filter(c=>c['name'] === x.name)[0]
                        // let index = filtered.indexOf(fil)
                        // filtered.splice(index,1)
                    }
                })
            }

            let areas = []
            let names = []
            let urls = []
            filtered.map(x => {
                // if(areas.indexOf(x['area'])){
                let json = {}
                json['area'] = x['area']
                let fil = areas.map(c => c['area'] === x['area'])
                if (fil.length === 0) {
                    areas.push(json)

                }
                // }
                // if(names.indexOf(x['name'])){
                json = {}
                json['name'] = x['name']
                fil = names.map(c => c['name'] === x['name'])
                if (fil.length === 0) {
                    names.push(json)

                }
                // }
                // if(urls.indexOf(x['url'])){
                json = {}
                json['url'] = x['url']
                fil = urls.map(c => c['url'] === x['url'])
                if (fil.length === 0) {
                    urls.push(json)

                }
                // }

            })

            if (type !== 'area') {
                SetAreaOptions(areas)

            }
            if (type !== 'name') {
                SetNameOptions(names)

            }
            if (type !== 'url') {
                if (urls.length === 1) {
                    SetUrlValueFinal(urls[0])

                    if (props.type === 'concept') {
                        SetUrlValue(urls[0])
                    } else if (props.type === 'relationship') {
                        SetUrlValueRel(urls[0])
                    } else if (props.type === 'search') {
                        SetUrlValueSearch(urls[0])
                    }

                } else {
                    SetUrlValueFinal(null)
                    SetUrlValueSearch(null)
                    SetUrlValueRel(null)
                    SetUrlValue(null)
                }
                SetUrlOptions(urls)

            }
        }



    }*/

    // useEffect(()=>{
    //
    //     resetOptions()
    //
    // },[ConceptsList])


    /*function updateconceptslistsconcepts(newvalue) {
        let options_area = []
        conceptslist.map(x => {
            let obj = {}
            if (x.name.trim() === newvalue.name.trim()) {

                // if (x.name.tolowercase().trim() === newvalue.name.tolowercase().trim()) {
                obj['area'] = x['area']
                let filtered = [];

                filtered = options_area.filter(ele => ele.area === x['area']);
                if (filtered.length === 0) {
                    options_area.push(obj)
                }

            }


        })
        if (options_area.length === 1) {
            setareavaluefinal(options_area[0])

            if (props.type === 'search') {
                setareavaluesearch(options_area[0])
            } else if (props.type === 'concept') {
                setareavalue(options_area[0])

            } else if (props.type === 'relationship') {
                setareavaluerel(options_area[0])

            }

        }else if(options_area.length === 0){
            conceptslist.map(x => {
                let obj = {}
                obj['area'] = x['area']
                // console.log('opt1', obj, options, options.indexof(obj))
                const filtered = options_area.filter(ele => ele.area === x['area']);
                if (filtered.length === 0) {
                    options_area.push(obj)
                }

            })
        }

        setareaoptions(options_area)




    }
*/

    useEffect(() => {
        if (Tags) {
            resetOptions()

        }
    }, [Tags])

    return (
        <div>
            <Autocomplete
                value={AreaValueFinal}
                sx={{width: '100%'}}
                size={props.no_add_new_concept === true ? "small" : "medium"}
                onChange={(event, newValue) => {

                    if (newValue && newValue.inputValue) {
                        SetAddArea(true)
                        SetNewConcept(true)
                        SetAreaValueFinal({
                            area: newValue.inputValue,
                        })

                        // Create a new value from the user input

                        if (props.type === 'search') {
                            SetAreaValueSearch({
                                area: newValue.inputValue,
                            });
                        } else if (props.type === 'concept') {
                            SetAreaValue({
                                area: newValue.inputValue,
                            });

                        } else if (props.type === 'relationship') {
                            SetAreaValueRel({
                                area: newValue.inputValue,
                            });


                        }
                        updateConceptsListsArea({area: newValue.inputValue})

                        // SetAreaValue({
                        //     area: newValue.inputValue,
                        // });
                    } else if (newValue !== null) {
                        SetAddArea(true)
                        SetAreaValueFinal(newValue)

                        if (props.type === 'search') {
                            SetAreaValueSearch(newValue);


                        } else if (props.type === 'concept') {
                            SetAreaValue(newValue);


                        } else if (props.type === 'relationship') {
                            SetAreaValueRel(newValue);


                        }
                        // SetAreaValue(newValue);
                        if(newValue.area !== undefined){
                            updateConceptsListsArea(newValue)

                        }
                        // else{
                        //     updateConceptsListsArea({area:newValue})
                        //
                        // }
                    } else if (newValue === null) {

                        SetAreaValueFinal(newValue)

                        // SetAreaValue(newValue)
                        if (props.type === 'search') {
                            SetAreaValueSearch(newValue);


                        } else if (props.type === 'concept') {
                            SetAreaValue(newValue);



                        } else if (props.type === 'relationship') {
                            SetAreaValueRel(newValue);


                        }

                        resetOptions()


                    }


                }}

                filterOptions={(options, params) => {
                    // const filtered = filter(options, params);
                    // console.log('add',props.to_add,Options)
                    let filtered = []
                    const {inputValue} = params;

                    AreaOptions.map((opt) => {
                        // console.log('add',opt,AreaValue)
                        filtered.push(opt)


                    })
                    // console.log('filtered', filtered)

                    if (inputValue !== '') {
                        const {inputValue} = params;
                        // Suggest the creation of a new value

                        // const isExisting = areas_list.some((option) => inputValue.toLowerCase().trim() === option.toLowerCase().trim())
                        const isExisting = areas_list.some((option) => inputValue.trim() === option.trim())
                        // filtered = filtered.filter(x => x.area.toLowerCase().trim().includes(inputValue.toLowerCase().trim()))
                        filtered = filtered.filter(x => x.area.trim().includes(inputValue.trim()))

                        if (inputValue !== '' && !isExisting && !props.no_add_new_concept) {
                            filtered.push({
                                inputValue,
                                area: `Add "${inputValue}"`,
                            });
                        }


                    }
                    // console.log('filtered', filtered)
                    return filtered;
                }}
                selectOnFocus
                clearOnBlur
                handleHomeEndKeys
                id="free-solo-with-text-demo"
                options={AreaOptions}

                getOptionLabel={(option) => {
                    // Value selected with enter, right from the input
                    if (typeof option === 'string') {
                        return option;
                    }
                    // Add "xxx" option created dynamically
                    if (option.inputValue) {
                        return option.inputValue;
                    }
                    // Regular option
                    return option.area;


                }}

                renderOption={(props1, option, {inputValue}) => {

                    let parts = []

                    const matches_area = match(option.area, inputValue, {insideWords: true});
                    let parts_area = parse(option.area, matches_area);
                    parts = parts_area

                    return (
                        <li {...props1}>
                            <div>
                                {parts.map((part, index) => (
                                    <span
                                        key={index}
                                        style={{
                                            fontWeight: part.highlight ? 700 : 400,
                                            color: part.highlight ? 'royalblue' : 'black',
                                        }}
                                    >
                                              {part.text}
                                            </span>
                                ))}
                            </div>
                        </li>
                    );


                }}

                // freeSolo
                renderInput={(params) => (
                    <TextField {...params} label={"Tag"}/>
                )}
            />




        </div>


    )
}



