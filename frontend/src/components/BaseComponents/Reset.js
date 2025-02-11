import '../../App.css';
import {AppContext} from '../../App';
import React, {useState, useEffect, useContext, createContext} from "react";

import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import {Container,Row,Col} from "react-bootstrap";
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import Alert from '@mui/material/Alert'

// import '../General/first_row.css';

import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import axios from "axios";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";


function Reset() {


    const { email, } = useContext(AppContext);



    const [Error,SetError] = useState('')

    const [Message,SetMessage] = useState('')
    console.log('login')
    const orcid_error = window.error;


    const handleSubmit = (event) =>{
        event.preventDefault();
        event.stopPropagation();
        SetError('')
        const data = new FormData(event.currentTarget);
        // console.log({
        //     username: data.get('username'),
        //     password: data.get('password'),
        // });
        var username = data.get('username')
        // SetUser(username)
        if (data.get('email','') !== ''  ){
            axios({
                method: "post",
                url: "password_reset",
                data: data,
                headers: { "Content-Type": "multipart/form-data" },
            })
                .then((response) =>{
                    //handle success
                    if (response.data['error']){
                        SetError("The email is not existing")
                    }
                    else{
                        SetMessage("An email to reset your password has been sent to your account")
                    }

                })
                .catch((response) =>{
                    //handle error
                    SetError("An error occurred")
                });
        }
        else {
            SetError('The email is missing')
        }

    }






    return (
        <div className="App">




            <div >
                <Container fluid>
                    <div>

                        <div className={'reglog'}>

                            <Box component="form" onSubmit={(e)=>{handleSubmit(e)}} noValidate sx={{ mt: 1 }}>
                                <FormControl>
                                    <div style={{marginTop: '3vh'}}>
                                        <TextField sx={{width: '400px', margin: '1vh 0'}} size="small"

                                            // value={Username}
                                            // onChange={(e)=>{handleChangeUsername(e)}}
                                                   name="email" required id="standard-basic" label="Email"
                                                   variant="outlined"/>
                                    </div>
                                    {/*<div style={{marginTop: '3vh'}}>*/}
                                    {/*    <TextField sx={{width: '400px', margin: '1vh 0'}} size="small"*/}

                                    {/*        // value={Username}*/}
                                    {/*        // onChange={(e)=>{handleChangeUsername(e)}}*/}
                                    {/*               name="username" required id="standard-basic" label="Username"*/}
                                    {/*               variant="outlined"/>*/}
                                    {/*</div>*/}


                                    <Button type="submit"  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgba(34,193,195,1) 0%, rgba(255,185,33,1) 100%)" }} size={'large'}
                                            variant="contained" style={{marginTop:'5vh',width:'400px'}}

                                            >Reset</Button>


                                </FormControl>


                            </Box>
                            {Error !== '' &&
                                <div style={{width: '400px', margin: '3vh 0', display: "inline-block"}}><Alert
                                    severity="error">{Error}</Alert></div>}

                            {Message !== '' &&
                                <div style={{width: '400px', margin: '3vh 0', display: "inline-block"}}><Alert
                                    severity="success">{Message}</Alert></div>}


                        </div>
                    </div>
                </Container>
            </div>

        </div>
    );
}


export default Reset;
