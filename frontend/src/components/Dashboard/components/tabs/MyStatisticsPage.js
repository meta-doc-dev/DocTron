import React, {useContext, useEffect, useMemo, useState} from "react";
import {useNavigate} from "react-router-dom";
import axios from "axios";
import {AlertCircle} from "lucide-react";
import {AppContext} from "../../../../App";
import {useStatistics} from "../hooks/useStatistics";
import SortableTable from "../sortableTable/SortableTable";
import {COLUMN_TYPES} from "../sortableTable/types";
import StatCard from "../statCard/StatCard";
import StatsTabs from "../statTab/StatTab";
import AnnotationTableGrid from "../sortableTable/DocTable";
import DocumentAnnotationGrid from "../sortableTable/DocumentAnnotationGrid";
import "./styles.css";
import {IconArrowBack} from "@tabler/icons-react";

const MyStatisticsPage = () => {
    const navigate = useNavigate();

    const {
        dashboardCollections: [collectionsList],
        collection: [collectionID, SetCollection],
        role: [role, SetRole],
        document_id: [documentID, setDocumentID],
        username: [username]
    } = useContext(AppContext);

    /* 📌 Select the currently active collection */
    const selectedCollection = useMemo(() => {
        if (!collectionsList?.length) return null;
        return collectionsList.find((c) => c.collection_id === collectionID) || collectionsList[0];
    }, [collectionID, collectionsList]);

    const [selectedUser, setSelectedUser] = useState(username);

    /* 📌 Fetch user-specific statistics */
    const {indStatistics, globalStatistics, labelRange, error, loading} = useStatistics(
        collectionID || "",
        selectedCollection?.annotation_type_name || "",
        selectedUser
    );

    const [users, SetUsers] = useState([])

    useEffect(() => {
        if (!collectionID) return;
        setSelectedTopic(null);
        axios
            .get(`/collection-users`, {params: {collection_id: collectionID}})
            .then((response) => {
                SetUsers(response.data)
            })
            .catch((error) => console.error("Error fetching user statistics:", error));
    }, [collectionID])

    const [selectedTopic, setSelectedTopic] = useState(null)
    const [actualSelectedTopic, setActualSelectedTopic] = useState(null)

    /** 📌 User-specific statistics */
    const [userStats, setUserStats] = useState([]);
    const [statsActiveTab, setStatsActiveTab] = useState("individual");

    useEffect(() => {
        if (!collectionID || !username) return;

        axios
            .get(`/user-statistic-cards`, {
                params: {
                    collection_id: collectionID,
                    user: username,
                    active_tab: statsActiveTab || "individual",
                    selected_topic: selectedTopic || null,
                }
            })
            .then((response) => {
                const data = response.data;
                setUserStats(data);
            })
            .catch((error) => console.error("Error fetching user statistics:", error));
    }, [collectionID, username, statsActiveTab, selectedTopic]);

    const [documentStats, setDocumentStats] = useState(null);

    useEffect(() => {
        if (!collectionID || !username || !selectedTopic || statsActiveTab === "inter-agreement") return;
        axios.get(`document-wise${statsActiveTab === 'global' ? '-global' : ''}`, {
            params: {
                collection_id: collectionID,
                topic_id: selectedTopic,
                username: selectedUser,
                annotation_type: selectedCollection?.annotation_type_name
            }
        }).then((response) => {
            setDocumentStats(response.data);
        }).catch((error) => {
            console.error("Error fetching user statistics:", error);
        });
    }, [selectedTopic, username, collectionID, statsActiveTab]);


    const handleTabChange = (tab) => {
        setSelectedTopic(null);
        setDocumentStats(null);
        setStatsActiveTab(tab);
    }

    // Define table columns for individual statistics configuration once
    const individualTableColumns = [
        {key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID},
        {key: "topic_title", label: "Topic", type: COLUMN_TYPES.TOPIC_TITLE},
        {key: "number_of_annotated_documents", label: "Annotated Documents", type: COLUMN_TYPES.ANNOTATED},
        {key: "number_of_missing_documents", label: "Missing Documents", type: COLUMN_TYPES.MISSING}
    ];

    // Define table columns for global statistics configuration once
    const globalTableColumns = [
        {key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID},
        {key: "topic_title", label: "Topic", type: COLUMN_TYPES.TOPIC_TITLE},
        {key: "total_annotators", label: "Total Annotators", type: COLUMN_TYPES.ANNOTATORS},
        {key: "total_documents", label: "Annotated Documents", type: COLUMN_TYPES.ANNOTATED},
        {key: "total_documents_unique", label: "Annotated Documents (Unique)", type: COLUMN_TYPES.UNIQUE_ANNOTATED},
        {key: "number_of_missing_documents", label: "Missing Documents", type: COLUMN_TYPES.MISSING},
        {key: "avg_annotators_per_document", label: "Avg Annotators", type: COLUMN_TYPES.AVG_ANNOTATORS},
    ];

    const renderStatisticsTable = (data, statType = "individual", withModals = true) => {
        return (
            <SortableTable
                data={data}
                columns={statType === "individual" ? individualTableColumns : globalTableColumns}
                labelRange={labelRange}
                annotationType={selectedCollection?.annotation_type_name}
                onNavigate={handleNavigate}
                setSelectedTopic={setSelectedTopic}
                setActualSelectedTopic={setActualSelectedTopic}
                withModals={withModals}
            />
        );
    }

    const onBack = () => {
        setSelectedTopic(null);
        setDocumentStats(null);
    }

    const renderDocumentStatisticsTable = (data, statType = "individual") => {
        if (statType === "global") return (
            <AnnotationTableGrid
                data={data}
                onBack={onBack}
                selectedTopicId={actualSelectedTopic}
            />
        )
        return (
            <DocumentAnnotationGrid
                data={data}
                onBack={onBack}
                selectedTopicId={actualSelectedTopic}
            />
        )
    }


    /* 📌 Handles document navigation */
    const handleNavigate = (docId, topicId) => {
        try {
            axios.post("/jump-to-document", {
                document: docId,
                topic: topicId,
                collection: collectionID
            }).then(() => {
                setDocumentID(docId);
                SetCollection(collectionID);
                SetRole("Annotator")
                window.location.assign("/index");
            });

        } catch (error) {
            console.error("Navigation failed:", error);
        }
    };

    return (
        <section className="main__content my-stats">
            <div className="main__cards">
                {userStats && userStats.map((stat, index) => (
                    <StatCard key={index} title={stat.title} value={stat.value}/>
                ))}
            </div>

            <StatsTabs
                activeTab={statsActiveTab}
                onTabChange={handleTabChange}
            />

            {statsActiveTab === "individual" && users && (
                <select
                    value={selectedUser}
                    onChange={(e) => {
                        setSelectedTopic(null);
                        setDocumentStats(null);
                        setSelectedUser(e.target.value);
                    }}
                    disabled={users.length === 1}
                    className="user-select"
                >
                    {users.map((u) => (
                        <option key={u} value={u}>
                            {u}
                        </option>
                    ))}
                </select>
            )}

            {loading && (
                <div className="loading-container">
                    <div className="loading-spinner"/>
                </div>
            )}

            {error && (
                <div className="error-message">
                    <AlertCircle className="error-icon" size={20}/>
                    <p>{error}</p>
                </div>
            )}

            {selectedTopic && (
                <header className="topic-details">
                    <h4>Selected Topic: {selectedTopic}</h4>

                    <button
                        className="details-btn"
                        onClick={onBack}
                    >
                        <IconArrowBack/>
                        <span>Back</span>
                    </button>
                </header>
            )}

            {/* Individual Stats Panel */}
            {statsActiveTab === "individual" && !loading && !error && indStatistics && (
                selectedTopic && documentStats ? (
                    renderDocumentStatisticsTable(documentStats)
                ) : (
                    renderStatisticsTable(indStatistics)
                )
            )}

            {/* Global Stats Panel */}
            {statsActiveTab === "global" && !loading && !error && indStatistics && (
                selectedTopic && documentStats ? (
                    renderDocumentStatisticsTable(documentStats, "global")
                ) : (
                    renderStatisticsTable(globalStatistics, "global")
                )
            )}


            {/* Inter-Agreement Panel */}
            {statsActiveTab === "inter-agreement" && (
                <div className="text-center text-gray-500 py-8">
                    Inter-agreement statistics coming soon
                </div>
            )}
        </section>
    );
};

export default MyStatisticsPage;