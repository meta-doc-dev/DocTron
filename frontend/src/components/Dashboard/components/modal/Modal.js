import React, { useMemo } from "react";
import { AgGridReact } from 'ag-grid-react';
import {X} from "lucide-react";
import "./styles.css";
import { IconUsers } from "@tabler/icons-react";
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { FileText } from 'lucide-react';
import './styles.css';

const Modal = ({ title, isOpen, onClose, children }) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h3>{title}</h3>
                    <button className="modal-close" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="modal-content">{children}</div>
            </div>
        </div>
    );
};

const DocumentList = ({ documents, onNavigate }) => {
    const hasData = (key) => documents.some(doc => doc[key] !== undefined && doc[key] !== null && doc[key] !== "");

    const columnDefs = useMemo(() => {
        const columns = [
            hasData("title") && {
                field: "title",
                headerName: "Title",
                cellRenderer: (params) => (
                    <span className="clickable-cell cell-title" onClick={() => onNavigate(params.data.id)}>
                        <FileText className="table-icon" /> {params.value}
                    </span>
                ),
                flex: 2,
                minWidth: 200
            },
            hasData("language") && {
                field: "language",
                headerName: "Language",
                flex: 1,
                minWidth: 100
            },
            hasData("grade") && {
                field: "grade",
                headerName: "Grade",
                flex: 0,
                width: 80,
                minWidth: 60,
                cellStyle: { textAlign: "center" }
            },
            hasData("comment") && {
                field: "comment",
                headerName: "Comment",
                flex: 2,
                minWidth: 200
            },
            hasData("annotators") && {
                field: "annotators",
                headerName: "Annotators",
                cellRenderer: (params) => (
                    <span>
                        <IconUsers className="table-icon" /> {params.value?.length ? params.value.join(", ") : "N/A"}
                    </span>
                ),
                flex: 2,
                minWidth: 180
            }
        ].filter(Boolean); // Remove `false` values (columns with no data)

        return columns;
    }, [documents]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true,
        flex: 1,
        minWidth: 100
    }), []);

    return (
        <div className="sortable-table-container ag-theme-alpine">
            <AgGridReact
                rowData={documents}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                domLayout="autoHeight"
                suppressCellFocus={true}
                animateRows={true}
            />
        </div>
    );
};

export { Modal, DocumentList };
