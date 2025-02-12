import React from 'react'
import { Link } from 'react-router-dom'
import "./style.css"
import { IconFolders, IconHexagonLetterDFilled, IconHome, IconLayoutDashboard } from '@tabler/icons-react'

const DashboardHeader = () => {
    return (
        <header className='dashboard-header'>
            <IconHexagonLetterDFilled size={32} className='header-logo' />

            <nav className='header-nav'>
                <Link to='/index'><IconHome stroke={1.5} /><span>Home</span></Link>
                <Link to='/collections'><IconFolders stroke={1.5} /><span>Collections</span></Link>
                <Link to='/dashboard'><IconLayoutDashboard stroke={1.5} /><span>Dashboard</span></Link>
            </nav>
        </header>
    )
}

export default DashboardHeader