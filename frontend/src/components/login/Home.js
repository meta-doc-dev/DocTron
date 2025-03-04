import '../../App.css';
import React, {useState, useEffect, useContext, createContext} from "react";

import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import {Container,Row,Col} from "react-bootstrap";
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import './login.css'

var login_url = window.baseurl + 'loginPage'
var signup_url =  window.baseurl + 'signup'
const logourl = window.baseurl + "static/img/doctron.png"

import GitHubIcon from '@mui/icons-material/GitHub';
import IconButton from "@mui/material/IconButton";
import login from "@components/login/Login";

function Home() {


    return (
        <div className="App">




            <div >
                <Container fluid>
                    <div>

                        <div className={'reglog'}>

                            <div><img className={'login'} src={logourl} /></div>
                            <div>
                                <div style={{fontSize:'1.2rem'}}>
                                    <div>Start the annotation</div>
                                    <div>
                                        <Button variant="text" href={login_url}  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgba(34,193,195,1) 0%, rgba(255,185,33,1) 100%);",color:"white",'&:hover': { color: 'white' // Change text color to white on hover
                                            } }}  size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>Login</Button>
                                        <Button variant="text" href={signup_url} disabled={window.baseurl === 'https://doctorn.dei.unipd.it/'}  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgba(34,193,195,1) 0%, rgba(255,185,33,1) 100%);",color:"white" ,'&:hover': {color: 'white' // Change text color to white on hover
                                            } }}  size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>Signup</Button>
                                    </div>
                                </div><hr/>
                       {/*         <div style={{fontSize:'1.2rem'}}>
                                    <div>Want to know more? Explore Doctron features with our tutorial</div>
                                    <div>
                                        <Button variant="text" href={"https://doctron.dei.unipd.it/demo"} target="_blank"  sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgba(34,193,195,1) 0%, rgba(255,185,33,1) 100%);",color:"white",'&:hover': {
                                                color: 'white' // Change text color to white on hover
                                            } }} size={'large'}
                                                style={{margin:'2vh 1vh',width:'100px'}}>TUTORIAL
                                        </Button>

                                    </div>
                                </div>*/}

                            </div>

                        </div>



                            <br/>
                            <div style={{marginTop:'2vh',textAlign:'center',fontSize:'1.25rem'}}>
                               <span><IconButton fontSize={'large'} aria-label="github">
                                    <GitHubIcon />
                                  </IconButton>
                               </span>
                                <span>Instructions and Docker-based version are available on </span>
                                <Link href="https://github.com/meta-doc-dev/DocTron"  target="_blank" variant="div">
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
