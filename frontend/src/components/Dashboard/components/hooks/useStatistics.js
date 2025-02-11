import { useState, useEffect } from 'react';
import axios from 'axios';

export const useStatistics = (collectionID, annotationType) => {
    const [indStatistics, setIndStatistics] = useState(null);
    const [globalStatistics, setGlobalStatistics] = useState(null);
    const [labelRange, setLabelRange] = useState({});
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!collectionID || !annotationType) return;
        
        const fetchStatistics = async () => {
            try {
                setError(null);
                setLoading(true);
                const response = await axios(
                    `individual-statistics?collection_id=${collectionID}&annotation_type=${annotationType}`
                );
                setIndStatistics(response.data.data);
                setLabelRange(response.data.label_range);
            } catch (err) {
                setError(`Failed to fetch statistics`);
            } finally {
                setLoading(false);
            }
        };

        if (collectionID && annotationType) {
            fetchStatistics().then(r => r);
        }
    }, [collectionID, annotationType]);

    useEffect(() => {
        if (!collectionID || !annotationType) return;

        const fetchGlobalStatistics = async () => {
            try {
                setError(null);
                setLoading(true);
                const response = await axios(
                    `global-statistics?collection_id=${collectionID}&annotation_type=${annotationType}`
                );
                setGlobalStatistics(response.data.data);
                setLabelRange(response.data.label_range);
            } catch (err) {
                setError(`Failed to fetch statistics`);
            } finally {
                setLoading(false);
            }
        };

        if (collectionID && annotationType) {
            fetchGlobalStatistics().then(r => r);
        }
    }, [collectionID, annotationType]);

    return { indStatistics, globalStatistics, labelRange, error, loading };
};