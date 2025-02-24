import React, {useContext, useEffect, useState} from 'react'
import Nav from "react-bootstrap/Nav";
import Figure from "react-bootstrap/Figure";
import './sidebar.css';
import {AppContext} from "../../App";
import SmartToySharpIcon from '@mui/icons-material/SmartToySharp';
import NotStartedIcon from '@mui/icons-material/NotStarted';

import EmailIcon from '@mui/icons-material/Email';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import SettingsIcon from '@mui/icons-material/Settings';
import UploadIcon from '@mui/icons-material/Upload';
import ArticleIcon from '@mui/icons-material/Article';
import CreateIcon from '@mui/icons-material/Create';
import DownloadIcon from '@mui/icons-material/Download';
import IconButton from '@mui/material/IconButton';
import StackedBarChartIcon from '@mui/icons-material/StackedBarChart';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import GroupIcon from '@mui/icons-material/Group';
import {createTheme, ThemeProvider} from "@mui/material/styles";
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import {Tooltip} from "@mui/material";
import axios from "axios";
import TopicIcon from "@mui/icons-material/Topic";
import FlagIcon from "@mui/icons-material/Flag";
function SideBar(props){

    const { showbar,inarel,showview,showtopics,profile,showtasks,collection,showroles,username,showtypes,showupload,document_id,showautomaticannotation,collectiondocuments,showdocs,expand,showdownload,showmembers,showstats,showcollections,showfilter,showsettings,modality } = useContext(AppContext);
    const [CollectionDocuments,SetCollectionDocuments] = collectiondocuments
    const [Redir,SetRedir] = useState(false)
    const [RedirCredits,SetRedirCredits] = useState(false)
    const [ShowBar, SetShowBar] = showbar;
    const [Modality,SetModality] = modality
    const [ShowDocs,SetShowDocs] = showdocs
    const [ShowTopics,SetShowTopics] = showtopics
    const [Username,SetUsername] = username
    const [ShowMembers,SetShowMembers] =showmembers
    const [ShowSettings,SetShowSettings] =showsettings
    const [Expand,SetExpand] = expand
    const [ShowRoles,SetShowRoles] = showroles
    const [ShowStats,SetShowStats] = showstats
    const [ShowView,SetShowView] = showview
    const [ShowCollections,SetShowCollections] = showcollections
    const [ShowFilter,SetShowFilter] = showfilter
    const [Collection,SetCollection] = collection
    const [Reviewers,SetReviewers] = useState([])
    const [Admins,SetAdmins] = useState([])
    const [InARel, SetInARel] = inarel;
    const [Profile, SetProfile] = profile;
    const [DocumentID, SetDocumentID] = document_id;
    const [ShowDownload,SetShowDownload] = showdownload
    const [ShowUpload,SetShowUpload] = showupload
    const [ShowTasks,SetShowTasks] = showtasks
    const [ShowAutoAnno,SetShowAutoAnno] = showautomaticannotation
    const [ShowAnnoTypes,SetShowAnnoTypes] = showtypes
    const height = document.documentElement.scrollHeight

    useEffect(()=>{
        const height = document.documentElement.scrollHeight
        console.log('height',height)
        // console.log('height123',ShowBar)

        if(document.getElementById('sidenav') !== null){
            document.getElementById('sidenav').style.height = height.toString() + 'px'

        }
    },[ShowBar])

    useEffect(()=>{

        SetExpand(false);
        SetShowStats(false)
        SetShowDocs(false)
        SetShowTopics(false)
        SetShowCollections(false)
        SetShowMembers(false)
        SetShowSettings(false)
        SetShowFilter(false)
        SetShowView(false)
        SetShowDownload(false)
        SetShowUpload(false)
        SetShowAutoAnno(false)
        SetShowRoles(false)
        SetShowTasks(false)


    },[InARel])

    useEffect(()=>{
        if(!ShowDocs){
            SetExpand(false);
            SetShowAnnoTypes(true)

        }
        SetShowStats(false)
        SetShowCollections(false)
        SetShowMembers(false)
        SetShowSettings(false)
        SetShowFilter(false)
        SetShowRoles(false)
        SetShowView(false)
        SetShowDownload(false)
        SetShowUpload(false)
        SetShowAutoAnno(false)
        SetShowTasks(false)



    },[DocumentID])




    const bottoni = createTheme({
        palette: {
            buttons: {
                main: '#fff',
                contrastText: '#fff',
            },


        },
    });
    function Clear(){
        // e.preventDefault()
        SetExpand(false);
        SetShowStats(false)
        SetShowDocs(false)
        SetShowTopics(false)
        SetShowCollections(false)
        SetShowRoles(false)
        SetShowView(false)
        SetShowMembers(false)
        SetShowFilter(false)
        SetShowSettings(false)
        SetShowDownload(false)
        SetShowUpload(false)
        SetShowAutoAnno(false)
        SetShowAnnoTypes(true)
        SetShowRoles(false)
        SetShowTasks(false)

    }


    function OpenMenu(e,string){
        e.preventDefault()
        e.stopPropagation()



        if(string === 's' ) {
            if( ShowStats){
                Clear()

            }else{
                SetShowStats(true)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowRoles(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowView(false)
                SetExpand(true);
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowDownload(false)
                SetShowAnnoTypes(false)
                SetShowFilter(false)
                SetShowTasks(false)

            }
        }
        if(string === 'r' ) {
            if( ShowRoles){
                Clear()

            }else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowView(false)
                SetExpand(true);
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowDownload(false)
                SetShowAnnoTypes(false)
                SetShowFilter(false)
                SetShowRoles(true)
                SetShowTasks(false)

            }
        }
        else if(string === 'd') {
            if(ShowDocs){
                Clear()
            }else{
                SetShowDocs(true)
                SetShowDownload(false)
                SetShowTopics(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetShowStats(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowFilter(false)
                SetShowSettings(false)
                SetShowView(false)
                SetExpand(true);

            }

        }
        else if(string === 'c') {
            if(ShowCollections){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(true)
                SetShowMembers(false)
                SetShowFilter(false)
                SetShowSettings(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);

            }
        }
        else if(string === 'm' ) {
            if(ShowMembers){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(true)
                SetShowFilter(false)
                SetShowSettings(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);

            }

        }else if(string === 'f' ) {
            if(ShowFilter){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowFilter(true)
                SetShowSettings(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }else if(string === 'color' ) {
            if(ShowSettings){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(true)
                SetShowFilter(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }else if(string === 'view' ) {
            if(ShowView){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(true)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }else if(string === 'download' ) {
            if(ShowDownload){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(true)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }else if(string === 'upload' ) {
            if(ShowUpload){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(true)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }else if(string === 'auto' ) {
            if(ShowAutoAnno){
                Clear()
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(true)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }
        else if(string === 'ty' ) {
            if(ShowAnnoTypes){
                Clear()
                SetShowAnnoTypes(false)
            }
            else{
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(true)
                SetShowRoles(false)
                SetShowTasks(false)

                SetExpand(true);
            }

        }
        else if(string === 'to' ) {
            if (ShowTopics) {
                Clear()
            } else {
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(true)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowTasks(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetExpand(true);
            }
        }
        else if(string === 'task' ) {
            if (ShowTasks) {
                Clear()
            } else {
                SetShowStats(false)
                SetShowDocs(false)
                SetShowTopics(false)
                SetShowTasks(true)
                SetShowCollections(false)
                SetShowMembers(false)
                SetShowSettings(false)
                SetShowFilter(false)
                SetShowDownload(false)
                SetShowView(false)
                SetShowDownload(false)
                SetShowUpload(false)
                SetShowAutoAnno(false)
                SetShowAnnoTypes(false)
                SetShowRoles(false)
                SetExpand(true);
            }
        }


    }

    useEffect(()=>{
        if(Collection){
            var reviewers=[]
            var admins = []
            var members = []
            axios.get('collections/users',{params:{collection:Collection}}).then(response=>{
                members = response.data['members']
                members.map(member=>{
                    if(member.reviewer){
                        reviewers.push(member.username)
                    }
                    if(member.admin){
                        admins.push(member.username)
                    }
                })
                SetAdmins(admins)
                SetReviewers(reviewers)
            })

        }
    },[Collection])

    return (

        <div className="sidenav" id='sidenav' >
            {/*{Redir && <Redirect to={"/instructions"}/>}*/}
            {/*{RedirCredits && <Redirect to={"/credits"}/>}*/}

            {/*<div style={{'text-align':'center'}}>*/}
            <ThemeProvider theme={bottoni}>
                <Tooltip placement="right" title={'Roles'}>
                    <IconButton color="buttons" disabled={InARel}
                                component="div" onClick={(e) => {
                        OpenMenu(e, 'r')
                    }}>
                        <CreateIcon sx={{fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>
                <Tooltip placement="right" title={'Documents'}>
                    <IconButton  color="buttons" disabled={InARel  || !Collection || !CollectionDocuments || CollectionDocuments.length === 0} component="div" onClick={(e)=> {OpenMenu(e,'d')}} >
                        <ArticleIcon sx={{ fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>
                <Tooltip placement="right" title={'Topics'}>
                    <IconButton  color="buttons" disabled={InARel  || !Collection || !CollectionDocuments || CollectionDocuments.length === 0} component="div" onClick={(e)=> {OpenMenu(e,'to')}} >
                        <TopicIcon sx={{ fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>
                {/*<Tooltip placement="right" title={'Tasks'}>
                    <IconButton  color="buttons" disabled={InARel  || !Collection || !CollectionDocuments || CollectionDocuments.length === 0} component="div" onClick={(e)=> {OpenMenu(e,'task')}} >
                        <FlagIcon sx={{ fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>*/}
                <Tooltip placement="right" title={'Collections'}>
                <IconButton color="buttons"  disabled={InARel  || !Collection}  aria-label="Collections" component="div" onClick={(e)=> {OpenMenu(e,'c')}} >
                    <CollectionsBookmarkIcon sx={{ fontSize: '1.5rem'}} />
                </IconButton></Tooltip>
                <Tooltip placement="right" title={'Members'}>
                <IconButton color="buttons"  disabled={InARel || Modality === 1 || !Collection} aria-label="Members" component="div" onClick={(e)=> {OpenMenu(e,'m')}} >
                    <GroupIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>
                <Tooltip placement="right" title={'Statistics'}>
                <IconButton color="buttons"  disabled aria-label="Stats" component="div" onClick={(e)=> {OpenMenu(e,'s')}}>
                    <StackedBarChartIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>

                <Tooltip placement="right" title={'Settings'}>
                <IconButton color="buttons"  aria-label="Settings" disabled={InARel  || !Collection} component="div" onClick={(e)=> {OpenMenu(e,'color')}}>
                    <SettingsIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>
                <Tooltip placement="right" title={'Download'}>

                <IconButton color="buttons"  aria-label="Download" disabled={InARel || !Collection} component="div" onClick={(e)=> {OpenMenu(e,'download')}}>
                    <DownloadIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>
                <Tooltip placement="right" title={'Upload'}>
{/*
                <IconButton color="buttons"   aria-label="Upload" disabled={InARel || !CollectionDocuments || CollectionDocuments.length === 0} component="div" onClick={(e)=> {OpenMenu(e,'upload')}}>
                    <UploadIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>
                <Tooltip placement="right" title={'View'}>*/}

                <IconButton color="buttons" aria-label="View"  disabled={ InARel  || !Collection} component="div" onClick={(e)=> {OpenMenu(e,'view')}}>
                    <RemoveRedEyeIcon sx={{ fontSize: '1.5rem'}}/>
                </IconButton></Tooltip>

                <br/><br/>
                {/*<Tooltip placement="right" title={'Instructions'}>*/}
                {/*    <IconButton className={'bottombutt'} color="buttons" aria-label="Auto"  component="a" target={'_blank'} href={'/instructions'}>*/}

                {/*    /!*<IconButton color="buttons" aria-label="Auto"  component="div" onClick={()=>SetRedir(curval => !curval)}>*!/*/}
                {/*        <HelpOutlineIcon sx={{ fontSize: '1.5rem'}}/>*/}
                {/*    </IconButton>*/}
                {/*</Tooltip>*/}
                <Tooltip placement="right" title={'Demo'}>
                    <IconButton className={'bottombutt'} color="buttons" aria-label="Auto"  component="a" target={'_blank'} href={'/demo'}>

                        <NotStartedIcon sx={{ fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>
                <Tooltip placement="right" title={'Credits'}>
                    <IconButton className={'bottombutt'} color="buttons" aria-label="Auto"  component="a" target={'_blank'} href={'/credits'}>
                        <EmailIcon sx={{ fontSize: '1.5rem'}}/>
                    </IconButton>
                </Tooltip>
            </ThemeProvider>
            </div>

    );
}

export default SideBar
