import React, { useMemo, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { Modal, DocumentList as ModalContent } from "../modal/Modal";
import {
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    ModuleRegistry,
} from "ag-grid-community";
import "./styles.css";

ModuleRegistry.registerModules([
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
]);

const COLUMN_TYPES = {
    TOPIC_ID: 'topic_id',
    TOPIC_TITLE: 'topic_title',
    ANNOTATORS: 'annotators',
    ANNOTATED: 'annotated',
    MISSING: 'missing',
    LABEL: 'label',
    CUSTOM: 'custom'
};

const DocumentList = ({ documents, onNavigate }) => {
    if (!documents?.length) return null;

    return (
        <div className="document-list-container">
            {documents.map((doc) => (
                <div
                    key={doc.id}
                    className="document-item"
                    onClick={() => onNavigate(doc.id)}
                >
                    <p className="document-title">{doc.title}</p>
                    <p className="document-meta">{doc.language}</p>
                </div>
            ))}
        </div>
    );
};

const SortableTable = ({
    data,
    onNavigate,
    setSelectedTopic,
    columns = [
        { key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID },
        { key: "topic_title", label: "Topic Name", type: COLUMN_TYPES.TOPIC_TITLE },
        {
            key: "number_of_annotated_documents",
            label: "Annotated Documents",
            type: COLUMN_TYPES.ANNOTATED
        },
        {
            key: "number_of_missing_documents",
            label: "Missing Documents",
            type: COLUMN_TYPES.MISSING
        }
    ],
    labelRange = {
        "relevancy": [0, 1, 2],
        "clarity": [0, 1, 2]
    },
    annotationType = "",
    withModals = false
}) => {
    const [modalContent, setModalContent] = useState(null);
    
    const handleCellClick = (params, columnType) => {
        if (!withModals) return;

        const rowData = params.data;
        console.log(rowData);
        

        if (columnType === COLUMN_TYPES.TOPIC_ID) {
            setSelectedTopic(rowData.topic_id);
            return;
        }

        const getModalContent = () => {
            switch (columnType) {
                case "annotated":
                    return rowData.annotated_documents?.length
                        ? { topic: rowData.id, title: `Annotated Documents - ${rowData.topic_title}`, data: rowData.annotated_documents }
                        : null;
                case "missing":
                    return rowData.missing_documents?.length
                        ? { topic: rowData.id, title: `Missing Documents - ${rowData.topic_title}`, data: rowData.missing_documents }
                        : null;
                case "label":
                    const [labelName, grade] = params.colDef.field.split('-');
                    return rowData.label_documents?.[labelName]?.[grade]?.length
                        ? { topic: rowData.id, title: `${labelName} - Grade ${grade} - ${rowData.topic_title}`, data: rowData.label_documents[labelName][grade] }
                        : null;
                default:
                    return null;
            }
        };

        const content = getModalContent();
        if (content) setModalContent(content);
    };

    const columnDefs = useMemo(() => {
        const baseColumns = columns.map(col => ({
            field: col.key,
            headerName: col.label,
            sortable: true,
            filter: true,
            onCellClicked: (params) => handleCellClick(params, col.type),
            cellClass: (params) => {
                if (col.type === COLUMN_TYPES.ANNOTATED && params.data.annotated_documents?.length) {
                    return 'clickable-cell';
                }
                if (col.type === COLUMN_TYPES.MISSING && params.data.missing_documents?.length) {
                    return 'clickable-cell';
                }
                if (col.type === COLUMN_TYPES.TOPIC_ID) {
                    return 'clickable-cell';
                }
                return '';
            },
            width: col.type === COLUMN_TYPES.LABEL || col.type === COLUMN_TYPES.CUSTOM ? 80 : 200,
            minWidth: col.type === COLUMN_TYPES.LABEL || col.type === COLUMN_TYPES.CUSTOM ? 60 : 150,
            flex: col.type === COLUMN_TYPES.LABEL || col.type === COLUMN_TYPES.CUSTOM ? 0 : 1,
        }));

        if (annotationType === "Passages annotation") {
            baseColumns.push({
                field: 'number_of_passages',
                headerName: 'Total Number of Passages',
                sortable: true,
                filter: true,
                valueGetter: (params) => params.data.number_of_passages || 0,
                width: 100, // Adjusted width for small numeric values
            });
        }

        const labelColumns = Object.entries(labelRange).map(([label, grades]) => ({
            headerName: label.charAt(0).toUpperCase() + label.slice(1),
            children: grades.map(grade => ({
                field: `${label}-${grade}`,
                headerName: grade.toString(),
                sortable: true,
                filter: true,
                valueGetter: (params) => params.data.labels?.[label]?.[grade] || 0,
                onCellClicked: (params) => handleCellClick(params, 'label'),
                cellClass: (params) => params.data?.labels?.[label]?.[grade] > 0 ? "clickable-cell" : "",
                width: 80,
                minWidth: 60,
                flex: 0,
            }))
        }));

        return [...baseColumns, ...labelColumns];
    }, [columns, labelRange, annotationType]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true,
        suppressMovable: true,
        flex: 1,
        // minWidth: 100
    }), []);

    const gridOptions = {
        suppressCellFocus: true,
        animateRows: true,
    };

    return (
        <div className='sortable-table-container'>
            <AgGridReact
                rowData={data}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                gridOptions={gridOptions}
                enableCellTextSelection={true}
                suppressContextMenu={true}
            />
            {withModals && (
                <Modal
                    isOpen={!!modalContent}
                    onClose={() => setModalContent(null)}
                    title={modalContent?.title || ""}
                >
                    <ModalContent
                        documents={modalContent?.data || []}
                        onNavigate={(docId) => {
                            onNavigate(docId, modalContent.topic);
                            setModalContent(null);
                        }}
                    />
                </Modal>
            )}
        </div>
    );
};

export default SortableTable;
