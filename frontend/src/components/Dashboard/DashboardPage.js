import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import axios from "axios";
import "./style.css";
import DashboardLayout from "./DashboardLayout";


const DashboardPage = () => {
/*    useEffect(() => {
        axios.defaults.baseURL = window.baseurl ? window.baseurl.replace(/\/dashboard\/$/, "/") : {window.baseurl};
        axios.defaults.withCredentials = true; 
      }, []);*/

  return (
    <DashboardLayout>
        <Outlet />
    </DashboardLayout>
    );
};

export default DashboardPage;
