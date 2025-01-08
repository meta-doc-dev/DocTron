import * as React from 'react';
import Tooltip from '@mui/material/Tooltip';
import PersonAdd from '@mui/icons-material/PersonAdd';
import Settings from '@mui/icons-material/Settings';
import Logout from '@mui/icons-material/Logout';
import Link from '@mui/material/Link';
import { faUser } from '@fortawesome/free-solid-svg-icons'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import AdbIcon from '@mui/icons-material/Adb';
import './toolbar.css'
import {styled} from "@mui/material/styles";
import Stack from '@mui/material/Stack';
import Badge from '@mui/material/Badge';
import MailIcon from '@mui/icons-material/Mail';
import Chip from "@mui/material/Chip";
import {useContext, useEffect, useState} from "react";
import {AppContext} from "../../App";
import {Dialog, DialogActions, DialogContent, InputLabel, Select} from "@material-ui/core";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContentText from "@mui/material/DialogContentText";
import FormControl from "@mui/material/FormControl";
import axios from "axios";

const pages = ['Collection', 'Statistics'];
const settings = ['Profile',  'Logout'];

// const ResponsiveAppBar = () => {

function HeaderBar(props){
    const { username,profile,openmodal,role } = useContext(AppContext);
    const [Profile,SetProfile] = profile

    const [Counter,SetCounter] = useState(0)
    const [anchorEl, setAnchorEl] = React.useState(null);
    const [Username,SetUsername] = username
    const [Role,SetRole] = role
    const orcid = window.orcid
    const [Prof,SetProf] = useState("")
    const [Error,SetError] = useState(false)
    const [Valid,SetValid] = useState(false)
    const [OpenModal,SetOpenModal] = openmodal

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };
    const handleCloseModal = (e) =>{
        e.preventDefault()
        SetOpenModal(false)
    }
    const [anchorElNav, setAnchorElNav] = React.useState(null);
    const [anchorElUser, setAnchorElUser] = React.useState(null);

    const handleOpenNavMenu = (event) => {
        setAnchorElNav(event.currentTarget);
    };
    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };
    const handleOpenModalSettings = (e) => {
        e.preventDefault()
        SetOpenModal(true);
    };
    const handleChangeProf = (e) =>{
        e.preventDefault()
        SetProf(e.target.value)
    }
    const SubmitProfile = (e) =>{
        e.preventDefault()
        axios.post("set_profile",{profile:Prof}).then(res=>{SetValid(true);SetProfile(Prof)}).catch(error=>{
            SetError(true)
            console.log('error',error)
        })
    }

    return(

        <div className='header_bar'>

            <Button sx={{display:"inline-block",marginLeft:'5%'}}                             href="/index"
            >Home</Button>

                <Button
                    sx={{display:"inline-block",marginLeft:'5%'}}
                    href={'/collections'}
                    onClick={handleCloseNavMenu}
                >
                    Collections
                </Button>
                <Button
                    sx={{display:"inline-block",marginLeft:'5%'}}
                    href={'/statistics'}
                >
                    Statistics
                </Button>
            {window.location.hostname === "metatron.dei.unipd.it" && <Button
                sx={{display: "inline-block", marginLeft: '5%'}}
                onClick={() => SetOpenModal(prev => !prev)}
            >
                Settings
            </Button>}


            {/*<Button sx={{display:"inline-block"}}*/}
            {/*        variant={"text"}  endIcon={<AccountCircleIcon onClick={handleOpenUserMenu}/>}>*/}
            {/*    {Username}</Button>*/}
            <div style={{display:"inline-block",float:"right"}}>
                <Tooltip title={Username}><>
                    <div style={{display:"inline-block",fontWeight:"bold",color:"#1976d5"}}>
                        <div>{Username}</div><div style={{fontWeight:"normal",color:"#1976d5"}}><i>{Role}</i></div>
                    </div>
                    <Button
                        sx={{display:"inline-block"}}
                        variant={"text"}  endIcon={<AccountCircleIcon  />} onClick={handleOpenUserMenu}>
                    </Button>
                </>



                </Tooltip>
                <Menu
                    sx={{ mt: '45px' }}
                    id="menu-appbar"
                    anchorEl={anchorElUser}
                    anchorOrigin={{
                        vertical: 'top',
                        horizontal: 'right',
                    }}
                    keepMounted
                    transformOrigin={{
                        vertical: 'top',
                        horizontal: 'right',
                    }}
                    open={Boolean(anchorElUser)}
                    onClose={handleCloseUserMenu}
                >


                    <MenuItem onClick={handleCloseUserMenu} component="a" href="/logout">
                        <Typography  textAlign="center">Logout</Typography>
                    </MenuItem>


                </Menu>
            </div>






    </div>


    );

}


export default HeaderBar