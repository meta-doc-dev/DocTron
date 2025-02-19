import React, { useState, useRef, useEffect, useMemo, useContext } from 'react';
import "./style.css";
import { AppContext } from "../../../../App";
import { ChevronDown, ChevronRight, X } from "lucide-react";
import { IconCheck, IconLogout, IconUser } from "@tabler/icons-react";
import axios from "axios";

const annotationTypes = [
    { title: "Entity tagging", icon: "🏷️" },
    { title: "Entity linking", icon: "🔗" },
    { title: "Relationships annotation", icon: "🔄" },
    { title: "Facts annotation", icon: "📜" },
    { title: "Passages annotation", icon: "📖" },
    { title: "Graded labeling", icon: "✅" },
    { title: "Object detection", icon: "🖼️" },
];

const Sidebar = () => {
    const {
        dashboardCollections: [collectionsList],
        collection: [collectionID, setCollectionID],
        username: [username, setUsername],
        profile: [profile, setProfile],
        role: [role, setRole],
        openmodal: [openModal, setOpenModal]
    } = useContext(AppContext);

    const [openSection, setOpenSection] = useState(null);
    const [selectedGroup, setSelectedGroup] = useState("All");
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

    const userMenuRef = useRef(null);

    const groupedCollectionsByAnn = useMemo(() => {
        const grouped = annotationTypes.reduce((acc, { title }) => {
            acc[title] = [];
            return acc;
        }, {});

        if (Array.isArray(collectionsList)) {
            collectionsList.forEach((collection) => {
                const type = collection.annotation_type_name || "Unknown Type";
                if (!grouped[type]) {
                    grouped[type] = [];
                }
                grouped[type].push(collection);
            });
        }

        return grouped;
    }, [collectionsList]);

    const toggleSection = (type) => {
        setOpenSection((prev) => (prev === type ? null : type));
    };

    useEffect(() => {
        if (selectedGroup === "All") return;
        setOpenSection(selectedGroup);
    }, [selectedGroup]);

    useEffect(() => {
        if (!collectionID) return;

        const foundType = Object.entries(groupedCollectionsByAnn).find(([type, collections]) =>
            collections.some((collection) => collection.collection_id === collectionID)
        );

        if (foundType) {
            setOpenSection(foundType[0]);
        }
    }, [collectionID, groupedCollectionsByAnn]);

    const handleCloseModal = (e) => {
        e.preventDefault();
        setOpenModal(false);
    };

    const handleChangeProf = (e) => {
        e.preventDefault();
        setProfile(e.target.value);
    };

    const SubmitProfile = (e) => {
        e.preventDefault();
        axios.post("set_profile", { profile: Prof })
            .then(res => { SetValid(true); setProfile(Prof); })
            .catch(error => {
                // setErr(true);
                console.log('error', error);
            });
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
                setIsUserMenuOpen(false);
            }
        };

        if (isUserMenuOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        } else {
            document.removeEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isUserMenuOpen]);

    return (
        <div className={`sidebar ${isSidebarOpen ? "sidebar-open" : ""}`}>
            <div className="sidebar-header">
                <span>Dashboard</span>
                <button className="sidebar-toggle" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                    {isSidebarOpen ? <X size={20} /> : <ChevronRight size={20} />}
                </button>
            </div>
            <nav className="sidebar-nav">
                <h3>Collections By Annotation Type</h3>
                <select
                    value={selectedGroup}
                    onChange={(e) => setSelectedGroup(e.target.value)}
                    className="group-filter"
                >
                    <option value="All">All Annotation Types</option>
                    {Object.keys(groupedCollectionsByAnn).map((type) => (
                        <option key={type} value={type}>
                            {type}
                        </option>
                    ))}
                </select>
                <ul>
                    {annotationTypes.filter(type => selectedGroup === "All" || type.title === selectedGroup).map(({ title, icon }) => (
                        <li key={title}>
                            <div className="sidebar-item collapsible" onClick={() => toggleSection(title)}>
                                {icon}<span>{title}</span>
                                {openSection === title ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </div>
                            <div
                                className="submenu-container"
                                style={{
                                    maxHeight: openSection === title ? "500px" : "0px",
                                    opacity: openSection === title ? 1 : 0,
                                    overflow: "hidden",
                                    transition: "max-height 0.3s ease, opacity 0.3s ease",
                                }}
                            >
                                {groupedCollectionsByAnn[title] && groupedCollectionsByAnn[title].length > 0 ? (
                                    <ul className="submenu">
                                        {groupedCollectionsByAnn[title]?.map((collection) => (
                                            <li
                                                key={collection.collection_id}
                                                onClick={() => setCollectionID(collection.collection_id)}
                                                className={`sidebar-item ${collection.collection_id === collectionID ? "selected" : ""}`}
                                            >
                                                {collection.collection_id === collectionID ? <IconCheck className="sidebar-item-icon" /> : <></>}{collection.name}
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="empty-message">No collections available</p>
                                )}
                            </div>
                        </li>
                    ))}
                </ul>
            </nav>
            <div className="sidebar-footer">
                <div className="user-menu" onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}>
                    <p className='sidebar-user-name'><IconUser size={20} /> {username}</p>
                    <p className='sidebar-user-role'>{role}</p>
                </div>
                {isUserMenuOpen && (
                    <div className="user-dropdown" ref={userMenuRef}>
                        <button className="user-menu-item" onClick={() => console.log("Profile clicked")}>Profile</button>
                        <button className="user-menu-item" onClick={() => window.location.href = '/logout'}>Logout <IconLogout size={16} /></button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sidebar;