import React, { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { AlertCircle } from "lucide-react";
import { AppContext } from "../../../../App";
import { useStatistics } from "../hooks/useStatistics";
import SortableTable from "../sortableTable/SortableTable";
import { COLUMN_TYPES } from "../sortableTable/types";
import StatCard from "../statCard/StatCard";
import StatsTabs from "../statTab/StatTab";
import "./styles.css";

const MyStatisticsPage = () => {
  const navigate = useNavigate();

  const {
    dashboardCollections: [collectionsList],
    collection: [collectionID],
    document_id: [documentID, setDocumentID],
    username: [username]
  } = useContext(AppContext);

  /* 📌 Select the currently active collection */
  const selectedCollection = useMemo(() => {
    if (!collectionsList?.length) return null;
    return collectionsList.find((c) => c.collection_id === collectionID) || collectionsList[0];
  }, [collectionID, collectionsList]);

  /* 📌 Fetch user-specific statistics */
  const { indStatistics, globalStatistics, labelRange, error, loading } = useStatistics(
    collectionID || "",
    selectedCollection?.annotation_type_name || "",
    // username
  );

  /** 📌 TODO: CHANGE WITH THE ACTUAL DATA */
  /** 📌 User-specific statistics */
  const [userStats, setUserStats] = useState({
    totalMentions: 0,
    totalConcepts: 0,
    totalLabels: 0,
    totalRelationships: 0,
    totalAssertions: 0,
    annotatedDocs: 0
  });

  const [statsActiveTab, setStatsActiveTab] = useState("individual");

  useEffect(() => {
    if (!collectionID || !username) return;

    axios
      .get(`/user-statistics`, { params: { collection: collectionID, user: username } })
      .then((response) => {
        const data = response.data;

        setUserStats({
          totalMentions: data.mentions || 0,
          totalConcepts: data.concepts || 0,
          totalLabels: data.labels || 0,
          totalRelationships: data.relationships || 0,
          totalAssertions: data.assertions || 0,
          annotatedDocs: data.annotated_documents || 0
        });
      })
      .catch((error) => console.error("Error fetching user statistics:", error));
  }, [collectionID, username]);


  const handleTabChange = (tab) => {
    setStatsActiveTab(tab);
  }

  // Define table columns for individual statistics configuration once
  const individualTableColumns = [
    { key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID },
    { key: "topic_title", label: "Topic Name", type: COLUMN_TYPES.TOPIC_TITLE },
    { key: "number_of_annotated_documents", label: "Annotated Documents", type: COLUMN_TYPES.ANNOTATED },
    { key: "number_of_missing_documents", label: "Missing Documents", type: COLUMN_TYPES.MISSING }
  ];

  // Define table columns for global statistics configuration once
  const globalTableColumns = [
    { key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID },
    { key: "topic_title", label: "Topic Name", type: COLUMN_TYPES.TOPIC_TITLE },
    { key: "total_annotators", label: "Total Annotators", type: COLUMN_TYPES.ANNOTATORS },
    { key: "number_of_annotated_documents", label: "Annotated Documents", type: COLUMN_TYPES.ANNOTATED },
    { key: "number_of_missing_documents", label: "Missing Documents", type: COLUMN_TYPES.MISSING }
  ];

  const renderStatisticsTable = (data, statType = "individual", withModals = true) => (
    <SortableTable
      data={data}
      columns={statType === "individual" ? individualTableColumns : globalTableColumns}
      labelRange={labelRange}
      annotationType={selectedCollection?.annotation_type_name}
      onNavigate={handleNavigate}
      withModals={withModals}
    />
  );

  /* 📌 Handles document navigation */
  const handleNavigate = async (docId, topicId) => {
    try {
      await axios.post("/jump-to-document", {
        document: docId,
        topic: topicId,
        collection: collectionID
      });
      setDocumentID(docId);
      navigate("/index");
    } catch (error) {
      console.error("Navigation failed:", error);
    }
  };

  return (
    <section className="main__content my-stats">
      {/* 📌 USER-SPECIFIC COLLECTION STATISTICS */}
      {/* TODO: REMOVED FOR NOW */}
      {/*<h4 className="section-title">User Statistics for Collection</h4>*/}

      <div className="main__cards">
        <StatCard title="User Annotations" value={selectedCollection?.user_annotations_count || 0} />
        <StatCard title="User Annotation %" value={`${selectedCollection?.perc_annotations_user || 0}%`} />
        <StatCard title="Documents Annotated" value={userStats.annotatedDocs} />
        <StatCard title="Mentions" value={userStats.totalMentions} />
      </div>

      {/** 📌 SORTABLE TABLE: USER'S INDIVIDUAL TOPIC STATISTICS */}
      {/*<h4 className="section-title">My Individual Annotations</h4>*/}

      <StatsTabs
        activeTab={statsActiveTab}
        onTabChange={handleTabChange}
      />

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner" />
        </div>
      )}

      {error && (
        <div className="error-message">
          <AlertCircle className="error-icon" size={20} />
          <p>{error}</p>
        </div>
      )}


      {/* Individual Stats Panel */}
      {statsActiveTab === "individual" &&
        !loading &&
        !error &&
        indStatistics &&
        renderStatisticsTable(indStatistics)
      }

      {/* Global Stats Panel */}
      {statsActiveTab === "global" &&
        !loading &&
        !error &&
        globalStatistics &&
        renderStatisticsTable(globalStatistics, "global")
      }

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