import React, { useMemo, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { Modal, DocumentList as ModalContent } from "../modal/Modal";
import {COLUMN_TYPES} from "./types";
import {
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    ModuleRegistry, TooltipModule,
} from "ag-grid-community";
import "./styles.css";

ModuleRegistry.registerModules([
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    TooltipModule,
]);

const CustomTooltip = ({ value, type }) => {
    return (
        <div className="custom-tooltip" style={{ backgroundColor: '#999' }}>
            <div>
                <b>Custom Tooltip</b>
            </div>
            <div>{value}</div>
        </div>
    )
}

const SortableTable = ({
    data,
    onNavigate,
    setSelectedTopic,
    setActualSelectedTopic,
    columns = [
        { key: "topic_id", label: "Topic ID", type: COLUMN_TYPES.TOPIC_ID },
        { key: "topic_title", label: "Topic", type: COLUMN_TYPES.TOPIC_TITLE },
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

    // Note: set 0 for data showing modal, 1 for document table modal
    const [modalType, setModalType] = useState(0);
    
    const handleCellClick = (params, columnType) => {
        if (!withModals) return;

        const rowData = params.data;

        if (columnType === COLUMN_TYPES.TOPIC_TITLE) {
            setModalType(0); // useless
            setModalContent({ title: 'Topic Info', data: rowData.topic_info });
            return;
        }

        setModalType(1);

        if (columnType === COLUMN_TYPES.TOPIC_ID) {
            setSelectedTopic(rowData.topic_id);
            setActualSelectedTopic(rowData.id);
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


    const getHeaderTooltipText = (label) => {
        switch (label) {
            case COLUMN_TYPES.AVG_ANNOTATORS:
                return `Average number of annotators per document (Total annotations / Number of unique documents)`;
            case "Missing Documents":
                return "Documents that are missing";
            case "Avg":
                return "Topic title";
            default:
                return "";
        }
    }

    const columnDefs = useMemo(() => {
        const baseColumns = columns.map(col => ({
            field: col.key,
            headerName: col.label,
            sortable: true,
            filter: true,
            // tooltipComponentParams: { type: col.type },
            headerTooltip: getHeaderTooltipText(col.type),
            onCellClicked: (params) => handleCellClick(params, col.type),
            cellClass: (params) => {
                const clickableCases = {
                    [COLUMN_TYPES.ANNOTATED]: params.data.annotated_documents?.length > 0,
                    [COLUMN_TYPES.MISSING]: params.data.missing_documents?.length > 0,
                    [COLUMN_TYPES.TOPIC_ID]: true,
                    [COLUMN_TYPES.TOPIC_TITLE]: true
                };
                return clickableCases[col.type] ? 'clickable-cell' : '';
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
        // tooltipComponent: CustomTooltip,
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
                tooltipShowDelay={500}
            />
            {withModals && modalContent && (
                <Modal
                    isOpen={!!modalContent}
                    onClose={() => setModalContent(null)}
                    title={modalContent?.title || ""}
                >
                    {modalType ? (
                        <ModalContent
                        documents={modalContent?.data || []}
                        onNavigate={(docId) => {
                            onNavigate(docId, modalContent.topic);
                            setModalContent(null);
                        }}
                    />) : (
                        <div>
                            {Object.entries(modalContent?.data).map(([key, value]) => (
                                <div key={key}>
                                    <strong>{key}</strong>: {value}
                                </div>
                            ))}
                        </div>
                    )}
                </Modal>
            )}
        </div>
    );
};

export default SortableTable;
