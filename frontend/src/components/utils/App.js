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
import img from '../../logo/img_1.png'
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
import GitHubIcon from '@mui/icons-material/GitHub';
import IconButton from "@mui/material/IconButton";

function Home() {


    return (
        <div className="App">




            <div >
                <Container fluid>
                    <div>

                        <div className={'reglog'}>

                            <div><img className={'login'} src={"http://metatron.dei.unipd.it/static/img/logo.png"} /></div>
                            <div>
                                <div style={{fontSize:'1.2rem'}}>
                                    <div>Start the annotation</div>
                                    <div>
                                        <Button variant="text" href={"https://metatron.dei.unipd.it/loginPage"}  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgb(126 42 148) 0%, rgb(45 83 141) 100%)",color:"white",'&:hover': { color: 'white' // Change text color to white on hover
                                            } }}  size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>Login</Button>
                                        <Button variant="text" href={"https://metatron.dei.unipd.it/signup"}  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgb(126 42 148) 0%, rgb(45 83 141) 100%)",color:"white" ,'&:hover': {color: 'white' // Change text color to white on hover
                                            } }}  size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>Signup</Button>
                                    </div>
                                </div><hr/>
                                <div style={{fontSize:'1.2rem'}}>
                                    <div>Want to know more? Explore MetaTron features with our tutorial</div>
                                    <div>
                                        <Button variant="text" href={"https://metatron.dei.unipd.it/demo"} target="_blank"  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgb(126 42 148) 0%, rgb(45 83 141) 100%)",color:"white",'&:hover': {
                                                color: 'white' // Change text color to white on hover
                                            } }} size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>TUTORIAL
                                        </Button>

                                    </div>
                                </div>

                            </div>

                        </div>



                            <br/>
                            <div style={{marginTop:'2vh',textAlign:'center',fontSize:'1.25rem'}}>
                               <span><IconButton fontSize={'large'} aria-label="github">
                                    <GitHubIcon />
                                  </IconButton>
                               </span>
                                <span>Instructions and Docker-based version are available on </span>
                                <Link href="https://github.com/GDAMining/metatron"  target="_blank" variant="div">
                                    GitHub
                                </Link>
                            </div>
                    </div>


                </Container>
            </div>

        </div>
    );
}


export default Home;
