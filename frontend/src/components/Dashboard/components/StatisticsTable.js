import React, { useState, useMemo } from 'react';
import { Modal, DocumentList } from './modal/Modal';
import { StatisticsTableHeader } from './sortableTable/StatisticsTableHeader';
import { StatisticsTableCell } from './sortableTable/StatisticsTableCell';
import { COLUMN_TYPES } from './sortableTable/types';
import '../style.css';
import './sortableTable.css';

const getDefaultColumns = () => [
    { key: 'topic_id', label: 'Topic ID', type: COLUMN_TYPES.TOPIC_ID },
    { key: 'topic_title', label: 'Topic Name', type: COLUMN_TYPES.TOPIC_TITLE },
    { key: 'number_of_annotated_documents', label: 'Annotated Documents', type: COLUMN_TYPES.ANNOTATED },
    { key: 'number_of_missing_documents', label: 'Missing Documents', type: COLUMN_TYPES.MISSING }
];

const StatisticsTable = ({ data, labelRange, onNavigate, annotationType }) => {
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [modalContent, setModalContent] = useState(null);

    const { labelStructure, columns, extendedColumns } = useMemo(() => {
        const customColumns = [];
        if (annotationType === 'Passages annotation') {
            customColumns.push({
                key: 'number_of_passages',
                label: 'Total Number of Passages',
                type: COLUMN_TYPES.CUSTOM,
                render: (topic) => topic.number_of_passages || 0
            });
        }

        // Generate label columns dynamically based on label ranges
        const labelColumns = Object.keys(labelRange).map(key => ({
            key,
            label: key,
            type: COLUMN_TYPES.LABEL
        }));

        const labelColumnsWithRanges = Object.entries(labelRange).flatMap(([key, values]) =>
            values.map(value => ({
                key: `${key}-${value}`,
                label: `${key}-${value}`,
                type: COLUMN_TYPES.LABEL
            }))
        );

        const baseColumns = [...getDefaultColumns(), ...customColumns];
        return {
            labelStructure: labelRange,
            columns: [...baseColumns, ...labelColumns],
            extendedColumns: [...baseColumns, ...labelColumnsWithRanges]
        };
    }, [data, annotationType]);

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    const sortedData = useMemo(() => {
        if (!sortConfig.key) return data;
        return [...data].sort((a, b) => {
            let aValue = a[sortConfig.key];
            let bValue = b[sortConfig.key];

            if (sortConfig.key.includes('-')) {
                const [label, grade] = sortConfig.key.split('-');
                aValue = a.labels?.[label]?.[grade] || 0;
                bValue = b.labels?.[label]?.[grade] || 0;
            }

            return sortConfig.direction === 'asc'
                ? aValue > bValue ? 1 : -1
                : aValue < bValue ? 1 : -1;
        });
    }, [data, sortConfig]);

    const handleCellClick = (topicData, columnType, labelName, grade) => {
        const getModalContent = () => {
            switch (columnType) {
                case 'annotated':
                    return topicData.annotated_documents?.length > 0 ? {
                        topic: topicData.id,
                        title: `Annotated Documents - ${topicData.topic_title}`,
                        data: topicData.annotated_documents
                    } : null;
                case 'missing':
                    return topicData.missing_documents?.length > 0 ? {
                        topic: topicData.id,
                        title: `Missing Documents - ${topicData.topic_title}`,
                        data: topicData.missing_documents
                    } : null;
                case 'label':
                    return topicData.label_documents?.[labelName]?.[grade]?.length > 0 ? {
                        topic: topicData.id,
                        title: `${labelName} - Grade ${grade} - ${topicData.topic_title}`,
                        data: topicData.label_documents[labelName][grade]
                    } : null;
                default:
                    return null;
            }
        };

        const content = getModalContent();
        if (content) {
            setModalContent(content);
        }
    };

    return (
        <div className="dashboard global-stats">
            <div className="sortable-table-container">
                <table className="sortable-table">
                    <StatisticsTableHeader
                        columns={columns}
                        sortConfig={sortConfig}
                        onSort={handleSort}
                        labelStructure={labelStructure}
                    />
                    <tbody>
                        {sortedData.map((topic) => (
                            <tr key={topic.topic_id}>
                                {extendedColumns.map((column, i) => (
                                    <StatisticsTableCell
                                        key={`${i}_${column.key}`}
                                        column={column}
                                        topic={topic}
                                        onClick={handleCellClick}
                                    />
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={!!modalContent}
                onClose={() => setModalContent(null)}
                title={modalContent?.title || ''}
            >
                <DocumentList
                    documents={modalContent?.data || []}
                    onNavigate={(docId) => {
                        onNavigate(docId, modalContent.topic);
                        setModalContent(null);
                    }}
                />
            </Modal>
        </div>
    );
};

export default StatisticsTable;
