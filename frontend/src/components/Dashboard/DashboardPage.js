import React, { useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import axios from "axios";
import "./style.css";
import DashboardLayout from "./DashboardLayout";

const DashboardPage = () => {
    useEffect(() => {
        axios.defaults.baseURL = window.baseurl ? window.baseurl.replace(/\/dashboard\/$/, "/") : "http://localhost:8000/";
        axios.defaults.withCredentials = true; 
      }, []);

  return (
    <DashboardLayout>
        <Outlet />
    </DashboardLayout>
    );
};

export default DashboardPage;
