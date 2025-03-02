import React, { useContext, useEffect, useState } from "react";
import axios from "axios";
import SortableTable from "../sortableTable/SortableTable";
import { AppContext } from "../../../../App";
import KappaBreakdownModal from "../KappaBreakdownModal";
import "./styles.css";

const IAAPage = () => {
  const [fleissData, setFleissData] = useState([]);
  const [cohensData, setCohensData] = useState([]);
  const [annotators, setAnnotators] = useState([]);
  const [user1, setUser1] = useState("");
  const [user2, setUser2] = useState("");
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isModalOpen, setModalOpen] = useState(false);
  const [breakdownData, setBreakdownData] = useState([]);

  const { collection: [collectionID] } = useContext(AppContext);

  useEffect(() => {
    axios.get("/get_annotators")
      .then(res => {
        const filteredUsers = res.data.filter(user => user !== "IAA-Inter Annotator Agreement");
        setAnnotators(filteredUsers);
      })
      .catch(err => console.error("Error fetching annotators:", err));
  }, []);

  useEffect(() => {
    if (!collectionID) return;
    axios.get("/create_fleiss_overview", { params: { collection: collectionID } })
      .then(res => setFleissData(res.data))
      .catch(err => console.error("Error fetching Fleiss' Kappa:", err));
  }, [collectionID]);

  useEffect(() => {
    if (!collectionID || !user1 || !user2) return;
    axios.get('/create_coehns', {
      params: { collection: collectionID, user1, user2, document: '' }
    })
      .then(res => {
        setCohensData(res.data);
      })
      .catch(err => console.error("Error fetching Cohen's Kappa:", err));
  }, [collectionID, user1, user2]);

  const getDocumentBreakdown = (documentId) => {
    const documentInfo = fleissData?.find(doc => doc.document_id === documentId);
    return documentInfo ? documentInfo.annotation_details : [];
  };

  const openKappaModal = (documentId) => {
    setSelectedDocument(documentId);
    setBreakdownData(getDocumentBreakdown(documentId));
    setModalOpen(true);
  };

  const getKappaColorClass = (kappa) => {
    if (kappa >= 0.81) return "excellent";
    if (kappa >= 0.61) return "good";
    if (kappa >= 0.41) return "moderate";
    if (kappa >= 0.21) return "fair";
    return "poor";
  };

  return (
    <section className="main__content iaa-stats">
      <h3>Inter-Annotator Agreement</h3>

      <div className="annotator-selection">
        <div className="select-container">
          <label>Select Annotator 1:</label>
          <select onChange={e => setUser1(e.target.value)} value={user1}>
            <option value="">Select User</option>
            {annotators.map(user => (
              <option key={user} value={user}>{user}</option>
            ))}
          </select>
        </div>

        <div className="select-container">
          <label>Select Annotator 2:</label>
          <select onChange={e => setUser2(e.target.value)} value={user2}>
            <option value="">Select User</option>
            {annotators.map(user => (
              <option key={user} value={user}>{user}</option>
            ))}
          </select>
        </div>
      </div>

      <h4>Fleiss' Kappa</h4>
      {fleissData && Object.keys(fleissData).length > 0 ? (
        <SortableTable
          data={Object.keys(fleissData).map((iterationKey) => {
            const iteration = fleissData[iterationKey];
            return {
              iteration: <span className="row__title">{iteration.iteration}</span>,
              mentions: <span className={getKappaColorClass(iteration.mentions)}>{iteration.mentions.toFixed(2)}</span>,
              concepts: <span className={getKappaColorClass(iteration.concepts)}>{iteration.concepts.toFixed(2)}</span>,
              labels: <span className={getKappaColorClass(iteration.labels)}>{iteration.labels.toFixed(2)}</span>,
              relationships: <span className={getKappaColorClass(iteration.relationships)}>{iteration.relationships.toFixed(2)}</span>,
              assertions: <span className={getKappaColorClass(iteration.assertions)}>{iteration.assertions.toFixed(2)}</span>,
            };
          })}
          columns={["iteration", "mentions", "concepts", "labels", "relationships", "assertions"]}
        />
      ) : null}

      <h4>Cohen's Kappa (Pairwise Annotator Agreement)</h4>
      {(user1 && user2) ?

        (cohensData && Object.keys(cohensData).length > 0) ? (
          <SortableTable
            data={[{
              annotator1: user1,
              annotator2: user2,
              cohens_kappa: <span className={getKappaColorClass(cohensData.mentions)}>{cohensData.mentions.toFixed(2)}</span>,
              mentions: <span className={getKappaColorClass(cohensData.mentions)}>{cohensData.mentions.toFixed(2)}</span>,
              concepts: <span className={getKappaColorClass(cohensData.concepts)}>{cohensData.concepts.toFixed(2)}</span>,
              labels: <span className={getKappaColorClass(cohensData.labels)}>{cohensData.labels.toFixed(2)}</span>,
              assertions: <span className={getKappaColorClass(cohensData.assertions)}>{cohensData.assertions.toFixed(2)}</span>,
              relations: <span className={getKappaColorClass(cohensData.relations)}>{cohensData.relations.toFixed(2)}</span>,
            }]}
            columns={[
              "annotator1",
              "annotator2",
              "cohens_kappa",
              "mentions",
              "concepts",
              "labels",
              "assertions",
              "relations"
            ]}
          />
        ) : <p className="table__description">No Data to Display.</p>
        : <p className="table__description">Please Select Annotators First.</p>}

      <KappaBreakdownModal
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
        documentId={selectedDocument}
        breakdownData={breakdownData}
      />
    </section>
  );
};

export default IAAPage;
