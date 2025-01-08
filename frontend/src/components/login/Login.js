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
import './login.css'

// import '../General/first_row.css';
import AccountCircle from '@mui/icons-material/AccountCircle';

import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import axios from "axios";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import {Redirect} from "react-router-dom";
import Chip from "@mui/material/Chip";


function Login() {


    const { showbar,username,task,reports,languageList,curannotator,redir } = useContext(AppContext);

    const [Task,SetTask] = task
    const [Username,SetUsername] = useState('')
    const [User,SetUser] = username
    const [Password,SetPassword] = useState('')
    const [CurAnnotator,SetCurAnnotator] = curannotator
    const [Error,SetError] = useState('')
    const [Redir,SetRedir] = redir
    const [Login,SetLogin] = useState(false)
    const [Orcid,SetOrcid] = useState(false)
    console.log('login')
    const signup_url = "http://localhost:8000/signup"


    const orcid_error = window.error;
    useEffect(()=>{
        if(orcid_error !== null && orcid_error !== false && orcid_error !== undefined && orcid_error !== ''){
            SetError('The user does not exist, or has not linked the account to the ORCID ID yet')
        }
    },[orcid_error])

    const handleSubmit1 = (event) =>{
        console.log('us')
        event.preventDefault();
        event.stopPropagation();
        const data = new FormData(event.currentTarget);
        // console.log({
        //     username: data.get('username'),
        //     password: data.get('password'),
        // });
        data.append('task', Task);
        var username = data.get('username')
        // SetUser(username)
        if (data.get('username','') !== '' && data.get('password','') !== '' && Task){
            axios({
                method: "post",
                url: "login",
                data: data,
                headers: { "Content-Type": "multipart/form-data" },
            })
                .then((response) =>{
                    //handle success
                    console.log('resp',response)

                    SetUser(username)
                    SetCurAnnotator(username)

                    // return <Redirect to='/index'/>
                        // SetUser(username)
                    SetRedir(true)
                    // }

                })
                .catch((response) =>{
                    //handle error
                    console.log(response);
                    SetError('The password or the username are not valid')
                    SetRedir(0)
                    SetUsername('')
                    SetPassword('')
                });
        }
        else {
            SetError('The email, the username, the password, and a task are mandatory')
        }

    }




    useEffect(()=>{
        if(Login && Orcid){
            const formData = new FormData();
            formData.append('orcid', Orcid);

            axios({
                method: "post",
                url: "login",
                data: formData,
                headers: { "Content-Type": "multipart/form-data" },
            })
                .then((response) =>{
                    //handle success
                    console.log('resp',response)

                    SetUser(username)
                    SetCurAnnotator(username)

                    // return <Redirect to='/index'/>
                    // SetUser(username)
                    SetRedir(true)
                    // }

                })
                .catch((response) =>{
                    //handle error
                    console.log(response);
                    SetError('An error occurred')
                    SetRedir(0)
                    SetUsername('')
                    SetPassword('')
                });
        }
    },[Login,Orcid])




    return (
        <div className="App">




            <div >
                <Container fluid>
                    {(Redir === true  && (User && User !== '' && User !== undefined)) && <Redirect to='/index'/>}
                <div>
                    <div>


                    </div>
                    <div className={'reglog'}>

                        <div><img className={'login'} src={"http://localhost:8000/static/img/doctron.png"} /></div>

                        {Error !== '' && <div style={{width:'30vw',display:"inline-block"}}><Alert severity="error">{Error}</Alert></div>}
                        <Box component="form" onSubmit={(e)=>{handleSubmit1(e)}} noValidate sx={{ mt: 1 }}>
                            <FormControl>
                                <div style={{marginTop:'3vh'}}>
                                    <TextField sx={{ width:'350px'}}   size="small"
                                               name="username" required id="standard-basic" label="Username" variant="outlined" />
                                </div>
                                <div style={{marginTop:'3vh'}}>
                                    <TextField
                                        // onChange={(e)=>{handleChangePsw(e)}}
                                        required
                                        sx={{ width:'350px' }}
                                        id="standard-password-input"
                                        label="Password"
                                        type="password"
                                        name="password"
                                        size="small"
                                        autoComplete="current-password"
                                        variant="outlined"
                                    />
                                    <div style={{fontSize:'0.65rem',margin:0,textAlign:'right'}}><a href={window.location.origin+'/password_reset'}>I forgot my password</a> </div>
                                </div>
                                <div style={{width:'350px'}}>
                                    <h6>Tasks</h6>
                                    <div>
                                        {['Deep learning','Ad hoc','Passage retrieval','Question answering','Conversational','Entity retrieval'].map(el=><span><Chip sx={{margin:'1%'}} label={el} variant={Task === el ? 'filled':"outlined"} color={'info'} onClick={(e)=>{
                                            if(Task === el){
                                                SetTask(false)
                                            }else{
                                                SetTask(el)
                                            }
                                        }} /></span>)}
                                    </div>


                                </div>
                                <Button type="submit"  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgba(34,193,195,1) 0%, rgba(255,185,33,1) 100%);" }} size={'large'}
                                        variant="contained" style={{marginTop:'5vh',width:'350px'}}>Log In</Button>
                            </FormControl>
                        {/*    {window.location.hostname === "doctron.dei.unipd.it" &&<div style={{marginTop: '2vh'}}><a href={'https://doctron.dei.unipd.it/login_with_orcid'}>
                                <img className={'orcid'} height='4vh'
                                     src="https://doctron.dei.unipd.it/static/img/ORCID.png" alt="ORCID ID logo"/> Log
                                in with ORCID ID
                            </a>
                            </div>}*/}

                        </Box>

                        <br/>
                        <div style={{marginTop:'2vh'}}>
                            <Link href={signup_url} variant="body2">
                                {"Don't have an account? Sign Up"}
                            </Link>
                        </div>

                    </div>
                </div>
                </Container>
            </div>

        </div>
    );
}


export default Login;
