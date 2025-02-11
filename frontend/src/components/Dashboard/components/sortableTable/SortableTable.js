import React, {useMemo, useState} from "react";
import {DocumentList, Modal} from "../modal/Modal";
import SortableTableHeader from "./SortableTableHeader";
import SortableTableCell from "./SortableTableCell";
import {COLUMN_TYPES} from "./types";
import "../tabs/styles.css";
import "./styles.css";

const getDefaultColumns = () => [
    {key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID},
    {key: "topic_title", label: "Topic Name", type: COLUMN_TYPES.TOPIC_TITLE},
    {key: "number_of_annotated_documents", label: "Annotated Documents", type: COLUMN_TYPES.ANNOTATED},
    {key: "number_of_missing_documents", label: "Missing Documents", type: COLUMN_TYPES.MISSING}
];

const SortableTable = (
    {
        data,
        onNavigate,
        columns = getDefaultColumns(),
        labelRange = {},
        annotationType = "",
        withModals = false
    }
) => {
    const [sortConfig, setSortConfig] = useState({key: null, direction: null});
    const [modalContent, setModalContent] = useState(null);

    const {labelStructure, generatedColumns, extendedColumns} = useMemo(() => {
        const customColumns = [];
        if (annotationType === "Passages annotation") {
            customColumns.push({
                key: 'number_of_passages',
                label: 'Total Number of Passages',
                type: COLUMN_TYPES.CUSTOM,
                render: (topic) => topic.number_of_passages || 0
            });
        }

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

        const baseColumns = [...columns, ...customColumns];

        return {
            labelStructure: labelRange,
            generatedColumns: [...baseColumns, ...labelColumns],
            extendedColumns: [...baseColumns, ...labelColumnsWithRanges]
        };
    }, [data, annotationType]);

    const handleSort = (key) => {
        setSortConfig((prev) => ({
            key,
            direction: prev.key === key ? prev.direction === "asc" ? "desc" : prev.direction === "desc" ? null : "asc" : "asc",
        }));
    };

    const sortedData = useMemo(() => {
        if (!sortConfig.key || !sortConfig.direction) return data;
        return [...data].sort((a, b) => {
            let aValue = a[sortConfig.key];
            let bValue = b[sortConfig.key];

            if (sortConfig.key.includes("-")) {
                const [label, grade] = sortConfig.key.split("-");
                aValue = a.labels?.[label]?.[grade] || 0;
                bValue = b.labels?.[label]?.[grade] || 0;
            }

            if (!isNaN(aValue) && !isNaN(bValue)) {
                return sortConfig.direction === "asc" ? aValue - bValue : bValue - aValue;
            }

            return sortConfig.direction === "asc"
                ? String(aValue).localeCompare(String(bValue))
                : String(bValue).localeCompare(String(aValue));
        });
    }, [data, sortConfig]);

    const handleCellClick = (rowData, columnType, labelName, grade) => {
        if (!withModals) return;

        console.log("handleCellClick Called:", { rowData, columnType, labelName, grade });

        const getModalContent = () => {
            switch (columnType) {
                case "annotated":
                    return rowData.annotated_documents?.length
                        ? {
                            topic: rowData.id,
                            title: `Annotated Documents - ${rowData.topic_title}`,
                            data: rowData.annotated_documents
                        }
                        : null;
                case "missing":
                    return rowData.missing_documents?.length
                        ? {
                            topic: rowData.id,
                            title: `Missing Documents - ${rowData.topic_title}`,
                            data: rowData.missing_documents
                        }
                        : null;
                case "label":
                    return rowData.label_documents?.[labelName]?.[grade]?.length
                        ? {
                            topic: rowData.id,
                            title: `${labelName} - Grade ${grade} - ${rowData.topic_title}`,
                            data: rowData.label_documents[labelName][grade]
                        }
                        : null;
                default:
                    return null;
            }
        };

        const content = getModalContent();
        if (content) setModalContent(content);
    };

    return (
        <div className="sortable-table-container">
            <table className="sortable-table">
                <SortableTableHeader
                    columns={generatedColumns}
                    sortConfig={sortConfig}
                    onSort={handleSort}
                    labelStructure={labelStructure}
                />
                <tbody>
                {sortedData.map((topic) => (
                    <tr key={topic.topic_id}>
                        {extendedColumns.map((column, i) => (
                            <SortableTableCell
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

            {withModals && (
                <Modal
                    isOpen={!!modalContent}
                    onClose={() => setModalContent(null)}
                    title={modalContent?.title || ""}
                >
                    <DocumentList
                        documents={modalContent?.data || []}
                        onNavigate={(docId) => {
                            onNavigate(docId, modalContent.topic);
                            setModalContent(modalContent?.data);
                        }}
                    />
                </Modal>
            )}
        </div>
    );
};

export default SortableTable;
