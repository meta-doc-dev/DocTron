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
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
if (window.baseurl !== ''){
    axios.defaults.baseURL = window.baseurl

}else{
    axios.defaults.baseURL = 'http://localhost:8000/';

}
// import '../General/first_row.css';
import AccountCircle from '@mui/icons-material/AccountCircle';

import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import axios from "axios";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import {Redirect, useParams} from "react-router-dom";
import validator from "email-validator";


function ResetForm() {





    const [Redir,SetRedir] = useState(false)


    const [PasswordVal,SetPasswordVal] = useState('')
    const [PasswordValUp,SetPasswordValUp] = useState('')
    const [Name,SetName] = useState('')
    const [Surname,SetSurname] = useState('')
    const [Badge,SetBadge] = useState('')
    const [Email,SetEmail] = useState('')
    const [Password,SetPassword] = useState('')
    const [Error,SetError] = useState('')
    const [PswCompliant,SetPswCompliant] = useState(true)
    const [PswEqual,SetPswEqual] = useState(true)

    const [data,SetFormData] = useState(false)
    const [Message,SetMessage] = useState('')
    const { token } = useParams();
    const orcid_error = window.error;
    const handlePasswordChange = (event) => {
        const passwordValue = event.target.value;
        SetPasswordVal(passwordValue);
        SetError("")
        SetPswCompliant(true)
        SetPswEqual(true)
        var regex = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;
        var special = regex.test(passwordValue);
        var len = passwordValue.length >= 8
        var number = /[0-9]/.test(passwordValue)
        var upper = /[A-Z]/.test(passwordValue)

        var div_length = document.getElementById('length-psw')
        if (len){
            div_length.setAttribute('class','satisfied')
        }
        else{
            div_length.setAttribute('class','not-satisfied')
        }

        var div_length = document.getElementById('number-psw')
        if (number){
            div_length.setAttribute('class','satisfied')
        }else{
            div_length.setAttribute('class','not-satisfied')
        }

        var div_length = document.getElementById('upper-psw')
        if (upper){
            div_length.setAttribute('class','satisfied')
        }else{
            div_length.setAttribute('class','not-satisfied')
        }

        var div_length = document.getElementById('special-psw')
        if (special){
            div_length.setAttribute('class','satisfied')
        }else{
            div_length.setAttribute('class','not-satisfied')
        }




    };

    const handlePasswordUpChange = (event) => {
        SetError("")
        const passwordValue = event.target.value;
        SetPasswordValUp(passwordValue)

    };




    function handleSubmit(event){
        event.preventDefault();
        var foormdata = null
        foormdata = new FormData(event.currentTarget);
        SetFormData(foormdata)

        console.log({
            email: foormdata.get('email'),
            name: foormdata.get('name'),
            surname: foormdata.get('surname'),
            badge: foormdata.get('badge'),
            password: foormdata.get('password'),
            password_check: foormdata.get('password_check'),

        });



        if(PasswordVal !== PasswordValUp){
            SetPswEqual(false)
        }
        var regex = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;

        var psw_comp = false
        var special = regex.test(PasswordVal);
        var len = PasswordVal.length >= 8
        var number = /[0-9]/.test(PasswordVal)
        var upper = /[A-Z]/.test(PasswordVal)
        if ((special && upper && number && len)){

            psw_comp = true
        }

        var psw_equal = false
        if(foormdata.get('password','') === foormdata.get('password_check','')){
            psw_equal = true
        }


        if(psw_comp && psw_equal  && foormdata.get('password','') !== '' && foormdata.get('password_check','') !== '' ){
            var data_to_send = data ? data : foormdata
            axios({
                method: "post",
                url: `${window.location.origin}/password_reset/${token}`, // Corretto
                data: data_to_send,
                headers: { "Content-Type": "multipart/foncbirm-data" },
            })
                .then(function (response) {
                    //handle success
                    SetRedir(true)
                })
                .catch(function (response) {

                    SetError('Something went wrong')
                    SetPassword('')
                    SetPasswordVal('')
                    SetPasswordValUp('')
                    SetRedir(false)
                    var div_length = document.getElementById('length-psw')
                    div_length.setAttribute('class','not-satisfied')

                    var div_length = document.getElementById('number-psw')
                    div_length.setAttribute('class','not-satisfied')

                    var div_length = document.getElementById('upper-psw')
                    div_length.setAttribute('class','not-satisfied')
                    var div_length = document.getElementById('special-psw')
                    div_length.setAttribute('class','not-satisfied')


                });
        }else{
            SetPassword('')
            SetPasswordVal('')
            SetPasswordValUp('')
            SetFormData(false)
            var div_length = document.getElementById('length-psw')
            div_length.setAttribute('class','not-satisfied')

            var div_length = document.getElementById('number-psw')
            div_length.setAttribute('class','not-satisfied')

            var div_length = document.getElementById('upper-psw')
            div_length.setAttribute('class','not-satisfied')
            var div_length = document.getElementById('special-psw')
            div_length.setAttribute('class','not-satisfied')
        }




    }






    return (
        <div className="App">

            {Redir === true && <Redirect to='/login'/>}



            <div >
                <Container fluid>
                    <div>

                        <div className={'reglog'}>
                            {window.errorMessage.length > 0 ?  <div style={{width:'400px',display:"inline-block"}}><Alert severity="error">{window.errorMessage}</Alert>

                                    <div style={{margin: '3vh 1vh'}}>
                                        <a href={window.location.origin+"/login"}>Back to login</a></div>
                                </div>:
                                <Box component="form" onSubmit={(e)=>{handleSubmit(e)}} noValidate sx={{ mt: 1 }}>
                                    <FormControl>
                                        <div style={{marginTop:'3vh',width:'20vw'}}>

                                            <TextField
                                                id="password"
                                                name="password"
                                                label="Password"
                                                value={PasswordVal}
                                                required
                                                type="password"
                                                size={'small'}
                                                sx={{ width:'400px' }}
                                                onChange={handlePasswordChange}
                                                error={PswCompliant === false}
                                                helperText={PswCompliant === false && "The password does not comply with the requirements"}
                                            />
                                            <div style={{textAlign:'left'}}>
                                                <div id={'length-psw'} className={'not-satisfied'}>8 characters</div>
                                                <div id={'upper-psw'} className={'not-satisfied'}>1 upper case letter</div>
                                                <div id={'special-psw'} className={'not-satisfied'}>1 special character</div>
                                                <div id={'number-psw'} className={'not-satisfied'}>1 number</div>

                                            </div>
                                            <br/>
                                            <TextField
                                                id="password_check"
                                                name="password_check"
                                                required
                                                value={PasswordValUp}
                                                label="Insert password again"
                                                type="password"
                                                size={'small'}
                                                sx={{ width:'400px' }}
                                                onChange={handlePasswordUpChange}
                                                error={PswEqual === false}
                                                helperText={PswEqual === false && "The passwords are not equal"}
                                            />


                                        </div>






                                        <Button type="submit"   sx={{ '& > :not(style)': { m: 1 },background:"linear-gradient(90deg, rgb(126 42 148) 0%, rgb(45 83 141) 100%)" }} size={'large'}
                                                variant="contained" style={{marginTop:'5vh',width:'400px'}}>Reset</Button>
                                        {Error !== '' && <div style={{width:'400px',display:"inline-block"}}><Alert severity="error">{Error}</Alert></div>}

                                        {Message !== '' && <div style={{width:'400px',display:"inline-block"}}><Alert severity="success">{Message}</Alert></div>}

                                    </FormControl>


                                </Box>}



                        </div>
                    </div>
                </Container>
            </div>

        </div>
    );
}


export default ResetForm;
