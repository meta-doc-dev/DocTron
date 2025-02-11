import React, { useContext, useEffect, useMemo, useState } from "react";
import { AppContext } from "../../../../App";
import { useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import StatisticsTable from "../StatisticsTable";
import axios from "axios";
import "./styles.css"; // Extracted styles

const MyStatisticsPage = () => {
    const navigate = useNavigate();
    const {
        dashboardCollections: [collectionsList],
        collection: [collectionID],
        document_id: [DocumentID, SetDocumentID]
    } = useContext(AppContext);

    const [statistics, setStatistics] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // Select the collection based on the ID or fallback to the first one
    const selectedCollection = useMemo(() => {
        if (!Array.isArray(collectionsList) || collectionsList.length === 0) return null;
        return collectionsList.find(c => c.collection_id === collectionID) || collectionsList[0];
    }, [collectionID, collectionsList]);

    useEffect(() => {
        if (!selectedCollection) return;

        const fetchStatistics = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await axios.get(
                    `individual-statistics?collection_id=${collectionID}&annotation_type=${selectedCollection.annotation_type_name}`
                );

                setStatistics(response.data?.data || []);
            } catch (err) {
                setError(`Failed to fetch statistics: ${err.response?.data?.message || err.message}`);
            } finally {
                setLoading(false);
            }
        };

        fetchStatistics();
    }, [collectionID, selectedCollection]);

    const handleNavigate = async (docId, topicId) => {
        try {
            await axios.post('jump-to-document', {
                document: docId,
                topic: topicId,
                collection: collectionID
            });

            SetDocumentID(docId);
            navigate(`/index`);
        } catch (err) {
            console.error('Navigation failed:', err);
        }
    };

    return (
        <section className="main__content my-stats">
            <h3 className="page-title">My Statistics</h3>

            <div className="statistics-container">
                <h4 className="section-title">Individual Topic Statistics</h4>
                
                {loading ? (
                    <div className="loading-container">
                        <div className="loading-spinner" />
                    </div>
                ) : error ? (
                    <div className="error-message">
                        <AlertCircle className="error-icon" size={20} />
                        <p>{error}</p>
                    </div>
                ) : statistics ? (
                    <StatisticsTable data={statistics} onNavigate={handleNavigate} />
                ) : (
                    <p className="no-data-message">No statistics available.</p>
                )}
            </div>
        </section>
    );
};

export default MyStatisticsPage;
