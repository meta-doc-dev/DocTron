import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import axios from "axios";
import "./style.css";
import DashboardLayout from "./DashboardLayout";


const DashboardPage = () => {
    useEffect(() => {
        console.log('BASEURL DASHBOARD',window.baseurl)
        axios.defaults.baseURL = window.baseurl ? window.baseurl.replace(/\/dashboard\/$/, "/") : 'https://doctron.dei.unipd.it/';
        axios.defaults.withCredentials = true; 
      }, []);

  return (
    <DashboardLayout>
        <Outlet />
    </DashboardLayout>
    );
};

export default DashboardPage;
