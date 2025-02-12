import React, { useContext, useEffect, useMemo, useState } from "react";
import ListComponent from "./components/listComponent/ListComponent";
import "./style.css";
import { AppContext } from "../../App";
import axios from "axios";
import Sidebar from "./components/sidebar/Sidebar";
import DashboardHeader from "./components/header/Header";

const DashboardLayout = ({ className = "", children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState("");

  const {
    dashboardCollections: [collectionslist],
    collection: [collectionID, setCollectionID],
    collectiondocuments: [collectionDocuments, setCollectionDocuments],
    documentdescription: [DocumentDescription, SetDocumentDescription],
    documentlist: [DocumentList, SetDocumentList],
    document_id: [documentID, detDocumentID],
    documentlist: [documentList, setDocumentList],
    topics: [topicsList, setTopicsList],
  } = useContext(AppContext);

  const groupedCollectionsByAnn = useMemo(() => {
    if (!Array.isArray(collectionslist)) return {};

    return collectionslist.reduce((acc, collection) => {
      const type = collection.annotation_type_name || "Unknown Type";
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(collection);
      return acc;
    }, {});
  }, [collectionslist]);

  const filteredGroups = useMemo(() => {
    if (!selectedGroup || selectedGroup === "All") {
      return groupedCollectionsByAnn;
    }
    return { [selectedGroup]: groupedCollectionsByAnn[selectedGroup] || [] };
  }, [groupedCollectionsByAnn, selectedGroup]);

  return (
      <section className={`layout dashboard ${className}`}>
        <DashboardHeader />
        <main className="main">
          <Sidebar
              // title="Dashboard"
              // isMenuOpen={isMenuOpen}
              // toggleMenu={() => setIsMenuOpen((state) => !state)}
          >
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

            <ListComponent
                items={filteredGroups}
                onClick={(id) => { setCollectionID(id); }}
                selectedItem={collectionID}
                itemKey="collection_id"
            />
          </Sidebar>
          {children}
        </main>
      </section>
  );
};

export default DashboardLayout;