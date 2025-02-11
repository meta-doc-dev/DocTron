import React, { useContext, useEffect, useMemo, useState } from "react";
import { AppContext } from "../../../../App";
import StatCard from "../statCard/StatCard";
import "../../style.css";
import axios from "axios";
import SortableTable from "../sortableTable/SortableTable";

const GlobalStatisticsPage = () => {
  const { collectionslist: [collectionslist],
    collection: [collectionID],
    usersListAnnotations: [usersListAnnotations],
    collectiondocuments: [collectionDocuments, setCollectionDocuments],
    documentlist: [documentList, setDocumentList],
    document_id: [documentID, setDocumentID],
    showdocs: [showDocs, setShowDocs],
    topics: [topicsList, setTopicsList],
    topic: [topicID, setTopicID],
  } = useContext(AppContext);

  return (
    <section className="main__content global-stats">
      <h3>Global Statistics</h3>
    </section>
  );
};

export default GlobalStatisticsPage;
