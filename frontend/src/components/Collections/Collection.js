import {Col, Row} from "react-bootstrap";
import {Redirect} from "react-router-dom";
import React, {useState, useEffect, useContext, createContext, useRef} from "react";
import Badge from 'react-bootstrap/Badge'
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import 'bootstrap/dist/css/bootstrap.min.css';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import LockIcon from '@mui/icons-material/Lock';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import DialogTitle from '@mui/material/DialogTitle';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import DeleteMemberDialog from "./dialogs/DeleteMemberDialog";
import {SliderPicker} from 'react-color';

import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import QueryStatsIcon from '@mui/icons-material/QueryStats';

import Collapse from "@material-ui/core/Collapse";
import {
    faChevronLeft, faPalette,
    faChevronRight, faExclamationTriangle,
    faGlasses,
    faInfoCircle,
    faList, faPlusCircle,
    faProjectDiagram, faArrowLeft, faArrowRight, faTrash, faSave, faFileInvoice
} from "@fortawesome/free-solid-svg-icons";
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import {AppContext} from "../../App";
import axios from "axios";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import {keyboard} from "@testing-library/user-event/dist/keyboard";
import Alert from "@mui/material/Alert";
import AddMemberDialog from "./dialogs/AddMemberDialog";
import AddLabelsDialog from "./dialogs/AddLabelsDialog";
import DeleteCollectionDialog from "./dialogs/DeleteCollectionDialog";
import TransferAnnotationDialog from "./dialogs/TransferAnnotationDialog";
import {dom} from "@fortawesome/fontawesome-svg-core";
import NewRoundDialog from "./dialogs/NewRoundDialog";
import {responsiveProperty} from "@mui/material/styles/cssUtils";
import SplitDialog from "./dialogs/SplitDialog";
import HoneyPotDialog from "./dialogs/HoneyPotDialog";
import ColorTagsAreas from "./ColorTagsAreas";
import ReviseDialog from "./dialogs/ReviseDialog";
import NewReviewerDialog from "./dialogs/NewReviewerDialog";

export default function Collection(props) {
    const {
        username,
        profile,
        users,
        collectionslist,
        collection,
        document_id,
        labels,
        areascolors,
        modality
    } = useContext(AppContext);
    const [ShowTransfer, SetShowTransfer] = useState(false)
    const [ShowCollectionDetails, SetShowCollectionDetails] = useState(false)
    const [Username, SetUsername] = username
    const [Revise, SetRevise] = useState(false)
    const [Collection, SetCollection] = collection
    const [LoadingRound, SetLoadingRound] = useState(false)
    const [DocumentID, SetDocumentID] = document_id
    const [OpenNewRoundDialog, SetOpenNewRoundDialog] = useState(false)
    const [OpenSplitCollection, SetOpenSplitCollection] = useState(false)
    const [Users, SetUsers] = users
    const [Profile, SetProfile] = profile
    const [MemberFrom, SetMemberFrom] = useState(false)
    const [MemberTo, SetMemberTo] = useState(false)
    const [Profiles, SetProfiles] = useState([])
    const [LabelsToAdd, SetLabelsToAdd] = useState(false)
    const [TagsToAdd, SetTagsToAdd] = useState(false)
    const [OpenDeleteCollDialog, SetOpenDeleteCollDialog] = useState(false)
    const [OpenMemberDialog, SetOpenMemberDialog] = useState(false)
    const [OpenAddMemberDialog, SetOpenAddMemberDialog] = useState(false)
    const [OpenAddLabelsDialog, SetOpenAddLabelsDialog] = useState(false)
    const [Members, SetMembers] = useState(props.collection.members)
    const [Labels, SetLabels] = useState(props.collection.labels)
    const [LabelsAll, SetLabelsAll] = labels
    const [CollectionDocuments, SetCollectionDocuments] = useState([])
    const [MembersToAdd, SetMembersToAdd] = useState([])
    const [MemberToDel, SetMemberToDel] = useState(false)
    const [options, SetOptions] = useState([])
    const [AllOptions, SetAllOptions] = useState([])
    const [UpdateMembers, SetUpdateMembers] = useState(false)
    const [UpdateLabels, SetUpdateLabels] = useState(false)
    const [UpdateTags, SetUpdateTags] = useState(false)
    const [OpenAddTagsDialog, SetOpenAddTagsDialog] = useState(false)
    const [Beginner, SetBeginner] = useState([])
    const [Expert, SetExpert] = useState([])
    const [Admin, SetAdmin] = useState([])
    const [Tech, SetTech] = useState([])
    const [Modality, SetModality] = useState(0)
    const [AreasColorsCollection, SetAreasColorsCollection] = areascolors
    const [CollectionsList, SetCollectionsList] = collectionslist
    const [Redir, SetRedir] = useState(false)
    const [OverWrite, SetOverWrite] = useState(false)
    const [OpenHoneyPot, SetOpenHoneyPot] = useState(false)
    const [LoadColl, SetLoadColl] = useState(false)
    const [Revisor, SetRevisor] = useState(false)
    const [OpenQrelsDialog, SetOpenQrelsDialog] = useState(false)
    const [HoneyPot, SetHoneyPot] = useState([])
    const [Reviewers, SetReviewers] = useState([])
    const [Admins, SetAdmins] = useState([])
    const [ShowNew, SetShowNew] = useState({
        'Professor': false,
        'Expert': false,
        'Beginner': false,
        'Tech': false,
        'Student': false,
        'Admin': false
    })
    const [AddLabel, SetAddLabel] = useState(false)
    const [Color, SetColor] = useState(props.color)
    const [AreasColors, SetAreasColors] = useState(false)
    const [Student, SetStudent] = useState([])
    const [Professor, SetProfessor] = useState([])
    const [JsonMembers, SetJsonMembers] = useState({})
    const [Error, SetError] = useState(false)
    const [Languages, SetLanguages] = useState([])
    const [Invitation, SetInvitation] = useState(false)
    const [NewRev, SetNewRev] = useState(false)
    const [NewAd, SetNewAd] = useState(false)
    const [CollectionTags, SetCollectionTags] = useState([])
    const [CollectionAreas, SetCollectionAreas] = useState([])
    const [MembersToSplit, SetMembersToSplit] = useState([])
    const [AnnotationTypes, SetAnnotationTypes] = useState([])
    const [TopicsSplit,SetTopicsSplit] = useState(false);
    const [DocsSplit,SetDocsSplit] = useState(false);

    useEffect(() => {
        if (LoadColl) {
            axios.get('collections/list').then(response => {
                SetCollectionsList(response.data['collections'])
            })
                .catch(error => {
                    console.log('error', error)
                })
        }
    }, [LoadColl])


    useEffect(() => {
        SetInvitation(props.collection.status)

        if (props.collection) {

            var reviewers = []
            var admins = []
            SetAnnotationTypes(props.collection.types)
            props.collection.members.map(member => {
                if (member.reviewer) {
                    reviewers.push(member.username)
                }
                if (member.admin) {
                    admins.push(member.username)
                }
            })
            SetAdmins(admins)
            SetReviewers(reviewers)
            axios.get('collection_options', {params: {collection: props.collection.id}}).then(response => {
                SetAreasColors(response.data)
            }).catch(error => {
                console.log(error)
            })
            axios.get('collections/modality', {params: {collection: props.collection.id}}).then(response => {
                SetModality(response.data['modality'])
            }).catch(error => {
                console.log(error)
            })
            axios.get('get_tags', {params: {collection: props.collection.id}}).then(response => SetCollectionTags(response.data['areas'])).catch(error => console.log(error))
            axios.get('get_collection_areas', {params: {collection: props.collection.id}}).then(response => SetCollectionAreas(response.data['areas'])).catch(error => console.log(error))
            axios.get('collections/documents', {params: {collection: props.collection.id}}).then(response => SetCollectionDocuments(response.data)).catch(error => console.log(error))
        }
    }, [props.collection])

    useEffect(() => {

        if (Users) {
            var opt = Users.filter(a => a.username !== Username)
            var profiles = []
            for (let ind = 0; ind < Users.length; ind++) {
                if (profiles.indexOf(Users[ind].profile) === -1) {
                    profiles.push(Users[ind].profile)
                    // var str_name = 'All' +' '+ Users[ind].profile
                    // opt.push({'username':str_name,'profile':Users[ind].profile})
                }
            }
            for (let i = 0; i < profiles.length; i++) {
                var count_p = 0
                for (let ind = 0; ind < opt.length; ind++) {
                    if (opt[ind].profile === profiles[i]) {
                        count_p = count_p + 1

                    }
                }
                if (count_p <= 1) {
                    opt = opt.filter(o => o.profile !== profiles[i])
                }

            }
            var members_usernames = []
            for (let i = 0; i < props.collection.members.length; i++) {
                members_usernames.push(props.collection.members[i].username)
            }
            SetAllOptions(opt)
            opt = opt.filter(o => members_usernames.indexOf(o.username) === -1)
            console.log('opt', opt)
            SetOptions(opt)
            var profiles = get_profiles()
            SetProfiles(profiles)
        }

    }, [Users])


    useEffect(() => {
        // if (Members.length > 0){
        var profiles = get_profiles()
        SetProfiles(profiles)

        var beg = Members.filter(u => u.profile === 'Beginner')
        /*var bep = []
        if(beg.length > 10){
            bep = beg.slice(10, beg.length)
            beg = beg.slice(0, 10);
        }*/
        var exp = Members.filter(u => u.profile === 'Expert')
        /*var exp_p = []
        if(exp.length > 10){
            exp_p = exp.slice(10, exp.length)
            exp = exp.slice(0, 10);
        }*/
        var tec = Members.filter(u => u.profile === 'Tech')
        /*var tec_p = []
        if(tec.length > 10){
            tec_p = tec.slice(10, tec.length)
            tec = tec.slice(0, 10);
        }*/
        var stud = Members.filter(u => u.profile === 'Student')
        /* var stud_p = []
         if(stud.length > 10){
             stud_p = stud.slice(10, stud.length)
             stud = stud.slice(0, 10);
         }*/

        var prof = Members.filter(u => u.profile === 'Professor')
        /*var prof_p = []
        if(prof.length > 10){
            prof_p = prof.slice(10, prof.length)
            prof = prof.slice(0, 10);
        }*/
        var ad = Members.filter(u => u.admin === true)
        var rev = Members.filter(u => u.reviewer === true)
        /*var ad_p = []
        if(ad.length > 10){
            ad_p = ad.slice(10, ad.length)
            ad = ad.slice(0, 10);
        }*/
        SetAdmin(ad)
        var mem = {
            'Professor': prof,
            'Student': stud,
            'Beginner': beg,
            'Expert': exp,
            'Admin': ad,
            'Reviewer': rev,
            'Tech': tec
        }
        /* var memplus = {
             'Professor':prof_p,
             'Student': stud_p,
             'Beginner':bep,
             'Expert':exp_p,
             'Admin': ad_p,
             'Tech':tec_p
         }*/
        SetJsonMembers(mem)
        // SetJsonMembersPlus10(memplus)


        // }
        // else{
        //     SetJsonMembers({})
        //     SetJsonMembersPlus10({})
        // }

    }, [Members])


    function deleteMember(e) {
        var coll = Members.filter(e => e !== MemberToDel)

        if (MemberToDel !== Username) {
            axios.delete('collections/delete_member',
                {
                    data: {
                        member: MemberToDel,
                        collection: props.collection.id
                    }
                }
            )
                .then(response => {
                    console.log(response.data)
                    SetMembers(coll)
                    SetUpdateMembers(true)
                    handleCloseMemberDialog()
                })
                .catch(error => {
                    SetError(true)
                    console.log(error)
                })
        }


    }

    function get_profiles() {
        var profiles = []
        Members.map((u, i) => {
            if (profiles.indexOf(u.profile) === -1) {
                profiles.push(u.profile)
            }
        })
        return profiles
    }


    function deleteCollection(e) {
        var coll = Members.filter(e => e !== MemberToDel)


        axios.delete('collections', {data: {collection: props.collection['id']}})

            .then(response => {
                console.log(response.data)
                let collections = CollectionsList.map(x => x)
                collections = collections.filter(x => x.id !== props.collection['id'])
                SetCollectionsList(collections)
                handleCloseCollectionDialog()
            })
            .catch(error => {
                SetError(true)
                console.log(error)
            })
        axios.get("get_session_params").then(response => {
            console.log('params', response.data)
            SetCollection(response.data['collection']);
            SetDocumentID(response.data['document']);

        })

    }

    function AddMember(e) {
        axios.post('collections/add_member',
            {
                members: MembersToAdd,
                collection: props.collection.id
            }
        )
            .then(response => {
                console.log(response.data)
                SetUpdateMembers(true)
                handleCloseAddMemberDialog()

            })
            .catch(error => {
                SetError(true)
                console.log(error)
            })

    }

    function reviseCollection(e) {
        SetLoadingRound(true)
        if (Revisor === Username) {
            axios.post('revise_collection', {collection: props.collection.id}
            )
                .then(response => {
                    console.log(response.data)
                    SetLoadingRound(false)
                    SetLoadColl(true)
                    handleCloseRoundDialog()

                })
                .catch(error => {
                    SetError(true)
                    SetLoadingRound(false)
                    console.log(error)
                })
        }


    }

    function addReviewer(e) {
        SetLoadingRound(true)
        if (Reviewers.length > 0) {
            axios.post('add_reviewer', {reviewers: Reviewers, collection: props.collection.id}
            )
                .then(response => {
                    console.log(response.data)
                    SetLoadingRound(false)
                    SetLoadColl(true)
                    handleCloseRoundDialog()

                })
                .catch(error => {
                    SetError(true)
                    SetLoadingRound(false)
                    console.log(error)
                })
        }


    }

    function addAdmin(e) {
        SetLoadingRound(true)
        if (Admins.length > 0) {
            axios.post('add_admin', {admin: Admins, collection: props.collection.id}
            )
                .then(response => {
                    console.log(response.data)
                    SetLoadingRound(false)
                    SetLoadColl(true)
                    handleCloseRoundDialog()

                })
                .catch(error => {
                    SetError(true)
                    SetLoadingRound(false)
                    console.log(error)
                })
        }


    }

    function createRound(e) {
        SetLoadingRound(true)
        axios.post('create_new_round',
            {
                collection: props.collection.id.split('_round_')[0],
            }
        )
            .then(response => {
                console.log(response.data)
                SetLoadingRound(false)
                SetLoadColl(true)
                handleCloseRoundDialog()

            })
            .catch(error => {
                SetError(true)
                SetLoadingRound(false)

                console.log(error)
            })

    }

    function splitUsers(e) {
        e.preventDefault()
        SetLoadingRound(true)
        axios.post('split_users',
            {
                collection: props.collection.id,
                topic: TopicsSplit,
                document: DocsSplit
            }
        )
            .then(response => {
                console.log(response.data)
                SetLoadingRound(false)
                SetLoadColl(true)
                handleCloseSplitDialog()

            })
            .catch(error => {
                SetError(true)
                SetLoadingRound(false)
                console.log(error)
            })

    }

    function createhoneypot(e) {
        e.preventDefault()
        SetLoadingRound(true)
        axios.post('honeypot',
            {
                collection: props.collection.id,
                documents: HoneyPot
            }
        )
            .then(response => {
                console.log(response.data)
                SetLoadingRound(false)
                SetLoadColl(true)
                handleCloseHP()

            })
            .catch(error => {
                SetError(true)
                SetLoadingRound(false)
                console.log(error)
            })

    }

    function TransferAnnotations(e) {
        if (MemberFrom) {
            axios.post('transfer_annotations',
                {
                    member: MemberFrom,
                    collection: props.collection.id,
                    overwrite: OverWrite
                }
            )
                .then(response => {
                    console.log(response.data)
                    handleCloseTransferDialog()

                })
                .catch(error => {
                    SetError(true)
                    console.log(error)
                })
        }

    }

    function AddLabels(e) {
        axios.post('collections/add_labels',
            {
                labels: LabelsToAdd,
                collection: props.collection.id
            }
        )
            .then(response => {
                console.log(response.data)
                handleCloseAddlabelsDialog()
                SetUpdateLabels(true)

            })
            .catch(error => {
                SetError(true)
                console.log(error)
            })

    }

    function AddTags(e) {
        axios.post('collections/add_tags',
            {
                tags: TagsToAdd,
                collection: props.collection.id
            }
        )
            .then(response => {
                console.log(response.data)
                handleCloseAddTagsDialog()
                SetUpdateTags(true)

            })
            .catch(error => {
                SetError(true)
                console.log(error)
            })

    }

    useEffect(() => {
        if (UpdateLabels) {
            axios.get('collections/labels', {params: {collection: props.collection.id}})
                .then(response => {
                    SetLabels(response.data['labels'])
                    // SetLabelsAll(response.data['labels'])
                })
                .catch(error => {
                    console.log('error', error)

                })
        }
        SetUpdateLabels(false)
    }, [UpdateLabels])

    useEffect(() => {
        if (UpdateTags) {
            axios.get('get_tags', {params: {collection: props.collection.id}}).then(response => SetCollectionTags(response.data['areas'])).catch(error => console.log(error))

        }
        SetUpdateTags(false)
    }, [UpdateTags])

    useEffect(() => {
        if (UpdateMembers) {
            axios.get('collections/users', {params: {collection: props.collection.id}})
                .then(response => {
                    SetMembers(response.data['members'])
                })
                .catch(error => {
                    console.log('error', error)

                })
        }
        SetUpdateMembers(false)
    }, [UpdateMembers])


    const handleCloseCollectionDialog = () => {
        SetError(false)
        SetOpenDeleteCollDialog(false);

    }
    const handleCloseTransferDialog = () => {
        SetError(false)
        SetShowTransfer(false);
        SetMemberFrom(false)
        SetMemberTo(false)

    }
    const handleCloseAddlabelsDialog = () => {
        SetError(false)
        SetOpenAddLabelsDialog(false);
        SetLabelsToAdd(false)
        SetUpdateLabels(false)

    }
    const handleCloseSplitDialog = () => {
        SetError(false)
        SetOpenSplitCollection(false);

    }
    const handleCloseHP = () => {
        SetError(false)
        SetOpenHoneyPot(false);

    }
    const handleCloseAddTagsDialog = () => {
        SetError(false)
        SetOpenAddTagsDialog(false);
        SetTagsToAdd(false)
        SetUpdateTags(false)

    }
    const handleCloseMemberDialog = () => {
        SetError(false)
        SetOpenMemberDialog(false);
        SetMemberToDel(false)
        SetUpdateMembers(false)
    }
    const handleCloseRoundDialog = () => {
        SetError(false)
        SetOpenNewRoundDialog(false);
        SetRevise(false)
        SetNewRev(false)
        SetNewAd(false)

    }
    const handleCloseAddMemberDialog = () => {
        SetError(false)
        SetOpenAddMemberDialog(false);
        SetMembersToAdd([])
        SetUpdateMembers(false)
    }
    const handleChangeLabels = (event) => {
        SetError(false)
        SetLabelsToAdd(event.target.value);

    };

    useEffect(() => {
        if (OpenMemberDialog || OpenAddMemberDialog || OpenAddLabelsDialog || OpenDeleteCollDialog) {
            SetError(false)
        }
    }, [OpenAddLabelsDialog, OpenDeleteCollDialog, OpenMemberDialog, OpenAddMemberDialog])

    const theme = createTheme({

        palette: {
            Professor: {
                main: '#1976d2',
                contrastText: '#fff',
            },
            Admin: {
                main: '#28a745',
                contrastText: '#fff',
            },
            Reviewer: {
                main: '#d3792f',
                contrastText: '#fff',
            },
            Expert: {
                main: '#1976d2',
                contrastText: '#fff',

            },
            Student: {
                main: '#1976d2',
                contrastText: '#fff',

            },
            Beginner: {
                main: '#1976d2',
                contrastText: '#fff',

            },
            Tech: {
                main: '#1976d2',
                contrastText: '#fff',

            },
            Label: {
                main: '#17a2b8',
                contrastText: '#fff',
            },
        },
    });

    function ShowNew10UsersFunc(e, profile) {
        e.preventDefault()
        var json_o = {}
        console.log('k', ShowNew)

        Object.keys(ShowNew).map((p) => {
            json_o[p] = ShowNew[p]
        })
        json_o[profile] = !ShowNew[profile]
        SetShowNew(json_o)


    }

    function acceptInvitation(e, id) {
        e.preventDefault()
        e.stopPropagation()
        axios.post('accept_invitation', {collection: id})
            .then(r => SetInvitation('Accepted'))
            .catch(error => console.log(error))
    }

    function redirToAnnotation(e) {
        e.preventDefault()
        e.stopPropagation()

        axios.get("change_collection_id", {params: {collection: props.collection.id}})
            .then(rs => {
                SetCollection(props.collection.id);
                SetAreasColorsCollection(AreasColors)
                SetDocumentID(rs.data['document_id'])
                SetRedir(true)

            })

    }

    function updateArea(color, tag) {
        let areas = {}

        Object.keys(AreasColors).map(a => areas[a] = AreasColors[a])
        areas[tag] = color
        console.log('areas', areas)
        SetAreasColors(areas)
        SetColor(color)
        return areas

    }

    const updateColor = (tag, color) => {
        let color_str_0 = null
        if (color.rgb) {
            color_str_0 = 'rgba(' + color.rgb.r + ',' + color.rgb.g + ',' + color.rgb.b + ', 1)'
        } else {
            color_str_0 = hexToRgb(color)
        }

        var areas = updateArea(color_str_0, tag)
        axios.post('collection_options', {
            collection: props.collection.id,
            options: areas
        }).catch(error => SetError(true))
    }

    function reset_colors(e, type) {
        e.preventDefault()
        axios.delete('collection_options', {data: {collection: props.collection.id, type: type}}).then(response => {
            console.log(response.data)
            SetAreasColors(response.data)

        })
            .catch(error => SetError(true))
    }

    function rgbToHex(rgb) {
        // Estrai i valori di r, g, b dalla stringa "rgb(r, g, b)"
        if (rgb) {
            const rgbArray = rgb.match(/\d+/g); // Estrai solo i numeri (r, g, b)

            // Converti ogni valore a esadecimale e assicurati che abbia 2 cifre
            const red = parseInt(rgbArray[0]).toString(16).padStart(2, '0');
            const green = parseInt(rgbArray[1]).toString(16).padStart(2, '0');
            const blue = parseInt(rgbArray[2]).toString(16).padStart(2, '0');

            // Restituisci la stringa esadecimale completa
            return `#${red}${green}${blue}`;
        }

    }

    function hexToRgb(hex) {
        // Estrai i valori di r, g, b dalla stringa "rgb(r, g, b)"
        if (hex) {
            hex = hex.replace(/^#/, '');

            // Se il formato è corretto (6 caratteri esadecimali)
            if (hex.length === 6) {
                // Estrai i componenti RGB come coppie di caratteri
                const r = parseInt(hex.slice(0, 2), 16);
                const g = parseInt(hex.slice(2, 4), 16);
                const b = parseInt(hex.slice(4, 6), 16);

                // Restituisci il risultato in formato RGB
                return `rgb(${r}, ${g}, ${b})`;
            } else {
                throw new Error('Formato esadecimale non valido');
            }
        }

    }

    return (
        <div style={{marginBottom: '30px'}}>
            {Redir && <Redirect to={"/index"}/>}
            <TransferAnnotationDialog setoverwrite={SetOverWrite} options={AllOptions} collection={props.collection}
                                      memberfrom={MemberFrom} memberto={MemberTo} setmemberfrom={SetMemberFrom}
                                      setmemebeto={SetMemberTo} transfer={TransferAnnotations} open={ShowTransfer}
                                      handleClose={handleCloseTransferDialog} error={Error}/>
            <DeleteMemberDialog todel={MemberToDel} open={OpenMemberDialog} deleteMember={deleteMember} error={Error}
                                handleClose={handleCloseMemberDialog}/>
            <AddMemberDialog addMember={AddMember} setmembers={SetMembersToAdd} members={MembersToAdd} options={options}
                             error={Error} name={props.collection.name} open={OpenAddMemberDialog}
                             handleClose={handleCloseAddMemberDialog}/>
            <AddLabelsDialog type={'labels'} addlabels={AddLabels} error={Error} setlabelstoadd={SetLabelsToAdd}
                             open={OpenAddLabelsDialog} handleClose={handleCloseAddlabelsDialog}/>
            <AddLabelsDialog type={'tags'} addlabels={AddTags} error={Error} setlabelstoadd={SetTagsToAdd}
                             open={OpenAddTagsDialog} handleClose={handleCloseAddTagsDialog}/>
            <DeleteCollectionDialog open={OpenDeleteCollDialog} handleClose={handleCloseCollectionDialog}
                                    name={props.collection.name} error={Error} deletecollection={deleteCollection}/>
            <NewRoundDialog loading={LoadingRound} open={OpenNewRoundDialog} handleClose={handleCloseRoundDialog}
                            name={props.collection.name} error={Error} createRound={createRound}/>
            {/*
            <ReviseDialog collection={props.collection} members={props.collection.members} setrevisor={SetRevisor} revisor={Revisor} loading={LoadingRound} open={Revise} handleClose={handleCloseRoundDialog} name={props.collection.name} error={Error} revise={reviseCollection}/>
*/}
            <NewReviewerDialog collection={props.collection} members={props.collection.members} type={'reviewer'}
                               annotators={Reviewers} setannotators={SetReviewers} loading={LoadingRound} open={NewRev}
                               handleClose={handleCloseRoundDialog} name={props.collection.name} error={Error}
                               confirm={addReviewer}/>
            <NewReviewerDialog collection={props.collection} members={props.collection.members} type={'admin'}
                               annotators={Admins} setannotators={SetAdmins} loading={LoadingRound} open={NewAd}
                               handleClose={handleCloseRoundDialog} name={props.collection.name} error={Error}
                               confirm={addAdmin}/>
            <SplitDialog open={OpenSplitCollection} handleClose={handleCloseSplitDialog} name={props.collection.name}
                         collection={props.collection} error={Error} members={MembersToSplit} set_topic={SetTopicsSplit}
                         set_doc={SetDocsSplit} setmembers={SetMembersToSplit} split={splitUsers} loading={LoadingRound} />
            <HoneyPotDialog open={OpenHoneyPot} handleClose={handleCloseHP} name={props.collection.name}
                            collection={props.collection} error={Error} honeypot={HoneyPot} sethoneypot={SetHoneyPot}
                            documents={CollectionDocuments} createpot={createhoneypot}/>


            <Card sx={{minWidth: 275, maxHeight: '30%', backgroundColor: '#dddddd40'}} elevation={3}>

                <CardContent>
                    <Typography sx={{fontSize: 14}} color="text.secondary" gutterBottom>
                        <div>
                            Creator: {props.collection.creator}
                        </div>

                    </Typography>
                    <Typography variant="h5" component="div">
                        {props.collection.name}&nbsp;&nbsp;
                        {/*<Chip size="small" label="Private" icon={<LockIcon/>} color='error'/>*/}
                    </Typography>
                    <Typography sx={{mb: 1.5}} color="text.secondary">
                        Date of creation: {props.collection.date}
                        <br/>

                        {/*{props.documents_count}*/}
                    </Typography>
                    <hr/>
                    <Typography variant="body2">
                        <h6>Task: {props.collection.task}</h6>
                        <h6>Documents: {props.collection.documents_count}</h6>
                        <h6>Documents annotated: {props.collection.annotations_count}</h6>
                        {props.collection.batch.length > 0 && <>
                            {props.collection.batch.map((b, i) =>
                                <>
                                    <p>{Object.keys(b)[0]}: {b[Object.keys(b)[0]]} documents</p>
                                </>
                            )}
                        </>}
                        <br/>


                        <h6 style={{marginBottom: '1%'}}>Description:</h6>
                        <div>{props.collection.description}</div>
                        <hr/>
                        <h6 style={{marginBottom: '1%'}}>Modality:</h6>
                        <div>The modality determine how the users access and the modify the documents. In the <b>collaborative
                            open</b> modality, the users can annotate all the documents of the collection. In the <b>collaborative
                            restricted</b> modality, the users can annotate exclusively the documents assigned to them;
                            if no document is assigned, then no document can be modified. Finally, the
                            in <b>competitive</b> modality, the annotators cannot see each other annotations.
                        </div>
                        <div>
                            <Chip sx={{margin: '5px'}} variant={Modality === 0 ? 'filled' : 'outlined'}
                                  disabeld={Username !== props.collection.creator}
                                  label={'Collaborative open'} color={'success'} size="small" onClick={(e) => {
                                if (Username === props.collection.creator) {
                                    axios.post('collections/modality', {
                                        collection: props.collection.id,
                                        modality: 'Collaborative open'
                                    }).then(response => {
                                        SetModality(0);

                                    })
                                }

                            }}/>
                            <Chip sx={{margin: '5px'}} variant={Modality === 2 ? 'filled' : 'outlined'}
                                  disabeld={Username !== props.collection.creator}
                                  label={'Collaborative restricted'} color={'success'} size="small" onClick={(e) => {
                                if (Username === props.collection.creator) {
                                    axios.post('collections/modality', {
                                        collection: props.collection.id,
                                        modality: 'Collaborative restricted'
                                    }).then(response => {
                                        SetModality(2);

                                    })
                                }
                            }}/>
                            <Chip sx={{margin: '5px'}} variant={Modality === 1 ? 'filled' : 'outlined'}
                                  disabeld={Username !== props.collection.creator}
                                  label={'Competitive'} color={'success'} size="small" onClick={(e) => {
                                if (Username === props.collection.creator) {
                                    axios.post('collections/modality', {
                                        collection: props.collection.id,
                                        modality: 'Competitive'
                                    }).then(response => {
                                        SetModality(1);

                                    })
                                }
                            }}/>


                        </div>

                    </Typography>
                    <Collapse in={ShowCollectionDetails && AreasColors}>
                        <Typography variant="body2">
                            <hr/>
                            <h6 style={{marginBottom: '1%', marginTop: '1%'}}>Annotation types: </h6>
                            <div>
                                {['Labels annotation', 'Passages annotation', 'Entity linking', 'Entity tagging', 'Relationships annotation', 'Facts annotation'].map(annotation =>
                                    <Chip label={annotation} sx={{margin: '1%'}}
                                          disabled={props.collection.creator !== Username} onClick={(e) => {
                                        var types = props.collection.types.map(x => x)
                                        types.push(annotation)
                                        axios.post("collections/add_type", {
                                            collection_id: props.collection.id,
                                            type: annotation
                                        })
                                            .then(response => {
                                                SetAnnotationTypes(types)
                                            })
                                    }} variant={AnnotationTypes.indexOf(annotation) !== -1 ? 'filled' : "outlined"}
                                          color={'info'}/>
                                )}

                            </div>

                            <h6 style={{marginBottom: '1%', marginTop: '1%'}}>Members: </h6>
                            <div>
                                {JsonMembers !== {} && <div>
                                    {Object.keys(JsonMembers).map((k, o) =>
                                        <div>
                                            {JsonMembers[k].length > 0 &&
                                                <div style={{marginTop: '10px', marginBottom: '10px'}}>
                                                     <span style={{marginRight: '2%'}}>
                                                        <i>{k}:</i>
                                                    </span>
                                                    <ThemeProvider theme={theme}>
                                                    <span>
                                                        {JsonMembers[k].map((m, i) =>
                                                            <>{(m.profile === k || (m.admin && k === 'Admin') || (m.reviewer && k === 'Reviewer')) &&
                                                                <span
                                                                    style={{margin: '1%'}}>{Username === props.collection.creator ?
                                                                    <Chip
                                                                        variant={m.status === 'Invited' ? 'outlined' : 'filled'}
                                                                        label={m.username} color={k} size="small"
                                                                        onDelete={(e) => {
                                                                            if (Admins.indexOf(m.username) === -1 && Reviewers.indexOf(m.username) === -1) {
                                                                                SetMemberToDel(m.username);
                                                                                SetOpenMemberDialog(true)
                                                                            }

                                                                        }}/>
                                                                    : <Chip
                                                                        variant={m.status === 'Invited' ? 'outlined' : 'filled'}
                                                                        color={k} label={m.username} size='small'/>}
                                                                    </span>}


                                                            </>
                                                        )}
                                                    </span>


                                                    </ThemeProvider>

                                                </div>}
                                        </div>
                                    )}
                                    <div>
                                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) && Reviewers.length === 0 && <>

                                            <Tooltip title="Add members" placement="top">
                                                <>Add new reviewer
                                                    <IconButton color="primary" aria-label="upload picture"
                                                                component="span" onClick={() => SetNewRev(true)}>
                                                        <AddCircleOutlineIcon/>
                                                    </IconButton></>
                                            </Tooltip>
                                            <div style={{fontSize: '0.8rem'}}>If the member is found it will be
                                                displayed in the list above.
                                            </div>
                                        </>
                                        }
                                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) && <>

                                            <Tooltip title="Add members" placement="top">
                                                <>Add new admin
                                                    <IconButton color="primary" aria-label="upload picture"
                                                                component="span" onClick={() => SetNewAd(true)}>
                                                        <AddCircleOutlineIcon/>
                                                    </IconButton></>
                                            </Tooltip>
                                            <div style={{fontSize: '0.8rem'}}>If the member is found it will be
                                                displayed in the list above.
                                            </div>
                                        </>
                                        }
                                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) && <>

                                            <Tooltip title="Add members" placement="top">
                                                <>Add new annotators
                                                    <IconButton color="primary" aria-label="upload picture"
                                                                component="span"
                                                                onClick={() => SetOpenAddMemberDialog(true)}>
                                                        <AddCircleOutlineIcon/>
                                                    </IconButton></>
                                            </Tooltip>
                                            <div style={{fontSize: '0.8rem'}}>If the member is found it will be
                                                displayed in the list above.
                                            </div>
                                        </>
                                        }
                                    </div>
                                </div>}
                            </div>

                            <hr/>
                            <ThemeProvider theme={theme}>
                                <h6 style={{marginBottom: '1%'}}>Labels </h6>
                                <Button size={'small'} onClick={() => SetAddLabel(prev => !prev)}>Add label</Button>
                                {AddLabel && <div>
                                    add

                                </div>}
                            </ThemeProvider>
                            <hr/>
                            {AnnotationTypes.indexOf() !== -1 && <ThemeProvider theme={theme}>
                                <h6 style={{marginBottom: '1%'}}>Tags: </h6>
                                <div>
                                    {CollectionTags.map((m, i) =>
                                        <div style={{margin: '10px', display: "inline-block"}}><Chip label={m}
                                                                                                     size='small'
                                                                                                     color='Label'/>
                                        </div>
                                    )}
                                    {Username === props.collection.creator &&
                                        <Tooltip title="Add labels" placement="top">
                                            <IconButton color="primary" aria-label="upload picture" component="span"
                                                        onClick={() => SetOpenAddTagsDialog(true)}>
                                                <AddCircleOutlineIcon/>
                                            </IconButton></Tooltip>}
                                </div>
                                <hr/>
                            </ThemeProvider>}
                            <ThemeProvider theme={theme}>
                                {CollectionTags.length > 0 && <><h6 style={{marginBottom: '1%'}}>Change tags
                                    colors </h6>
                                    For each tag (entity tagging)
                                    select a color. If no color is selected, the default one will be applied.
                                    <div>
                                        <div><br/>
                                            {CollectionTags.map(tag => <div style={{margin: '25px 0'}}>

                                                <ColorTagsAreas setcolors={SetAreasColors} colors={AreasColors}
                                                                collection={props.collection} tag={tag}/>


                                            </div>)}
                                        </div>
                                        <Button variant="text" onClick={(e) => reset_colors(e, 'tags')}
                                                color={'error'}>Reset</Button>

                                        <hr/>

                                    </div></>}

                                {CollectionAreas.length > 0 &&
                                    <div><h6 style={{marginBottom: '1%'}}>Change concept type colors </h6>
                                        For each concept type (the category each concept belongs to)
                                        select a color. If no color is selected, the default one will be applied.
                                        <div><br/>
                                            {CollectionAreas.map(tag => <div style={{margin: '25px 0'}}>
                                                <ColorTagsAreas setcolors={SetAreasColors} colors={AreasColors}
                                                                collection={props.collection} tag={tag}/>


                                            </div>)}
                                        </div>
                                        <Button variant="text" onClick={(e) => reset_colors(e, 'areas')}
                                                color={'error'}>Reset</Button>

                                    </div>}
                            </ThemeProvider>


                        </Typography>
                    </Collapse>
                </CardContent>
                <CardActions>
                    {Invitation !== 'Invited' ? <>
                        <Button size="small" style={{marginRight: '1%'}}
                                onClick={() => SetShowCollectionDetails(prev => !prev)}>More</Button>
                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) &&
                            <Button size="small" style={{marginRight: '1%'}}
                                    onClick={() => SetOpenQrelsDialog(prev => !prev)}>Qrels schema</Button>}
                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) &&
                            <Button size="small" style={{marginRight: '1%'}}
                                    onClick={() => SetOpenNewRoundDialog(prev => !prev)}>New Iteration</Button>}
                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) &&
                            <Button size="small" style={{marginRight: '1%'}}
                                    onClick={() => SetOpenSplitCollection(prev => !prev)}>Split</Button>}
                        {(Username === props.collection.creator || Admins.indexOf(Username) !== -1) &&
                            <Button size="small" style={{marginRight: '1%'}}
                                    onClick={() => SetOpenHoneyPot(prev => !prev)}>HoneyPot</Button>}

                        {/*
                        {Reviewers.indexOf(Username) !== -1 &&  <Button size="small" style={{marginRight:'1%'}} onClick={()=>SetRevise(prev=>!prev)}>Review</Button>}
*/}


                        {/*
                        <Button disabled={Modality === 1} href={'collections/'+props.collection.id} size="small" style={{marginRight:'1%'}}>Documents</Button>
*/}
                        <Button onClick={redirToAnnotation} size="small" style={{marginRight: '1%'}}>Annotate</Button>
                        {/*<Button size="small" style={{marginRight:'1%'}}>Download</Button>*/}
                        {/*<Button size="small" style={{marginRight:'1%'}}>Stats</Button>*/}
                        {/*<Button onClick={()=>SetShowTransfer(prev=>!prev)} size="small" style={{marginRight:'1%'}}>Transfer</Button>*/}
                        {Username === props.collection.creator && <>
                            {/*<Button size="small" style={{marginRight:'1%'}}>Add documents</Button>*/}
                            <Button color="error" onClick={() => SetOpenDeleteCollDialog(true)} size="small"
                                    style={{marginRight: '1%'}}>Delete</Button></>}
                    </> : <>
                        <Button variant='contained' color={'error'} size="small" style={{marginRight: '1%'}}
                                onClick={(e) => {
                                    acceptInvitation(e, props.collection.id)
                                }}>Accept Invitation</Button>

                    </>
                    }


                </CardActions>
            </Card>
        </div>
    );
}