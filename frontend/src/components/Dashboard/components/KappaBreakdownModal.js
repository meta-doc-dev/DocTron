import React from "react";

const KappaBreakdownModal = ({ isOpen, onClose, documentId, breakdownData }) => {
  if (!isOpen || !breakdownData) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h2>Annotation Breakdown for Document {documentId}</h2>
        <button style={styles.closeButton} onClick={onClose}>✖</button>

        {breakdownData.length === 0 ? (
          <p>No annotation data available.</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Annotator</th>
                <th style={styles.th}>Annotation Type</th>
                <th style={styles.th}>Count</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(breakdownData).map(([annotator, annotations]) =>
                Object.entries(annotations).map(([type, count], index) => (
                  <tr key={`${annotator}-${type}-${index}`}>
                    <td style={styles.td}>{annotator}</td>
                    <td style={styles.td}>{type}</td>
                    <td style={{ ...styles.td, ...styles.count }}>{count}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default KappaBreakdownModal;

  // Inline Styles
  const styles = {
    overlay: {
      position: "fixed",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      background: "rgba(0, 0, 0, 0.6)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000
    },
    modal: {
      background: "white",
      padding: "20px",
      borderRadius: "10px",
      width: "50%",
      textAlign: "center",
      boxShadow: "0px 0px 10px rgba(0, 0, 0, 0.2)",
      position: "relative"
    },
    closeButton: {
      background: "none",
      border: "none",
      fontSize: "20px",
      position: "absolute",
      top: "10px",
      right: "15px",
      cursor: "pointer"
    },
    table: {
      width: "100%",
      borderCollapse: "collapse",
      marginTop: "10px"
    },
    th: {
      background: "#f4f4f4",
      padding: "10px",
      borderBottom: "1px solid #ddd",
      textAlign: "left"
    },
    td: {
      padding: "10px",
      borderBottom: "1px solid #ddd",
      textAlign: "left"
    },
    count: {
      fontWeight: "bold"
    }
  };