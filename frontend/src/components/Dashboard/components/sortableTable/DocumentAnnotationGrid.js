import React, { useCallback, useContext, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AppContext } from '../../../../App';
import { useNavigate } from 'react-router-dom';
import {
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    ModuleRegistry,
    ValidationModule,
    NumberFilterModule,
    TextFilterModule,
    ColumnAutoSizeModule,
    PaginationModule
} from "ag-grid-community";
import "./styles.css";
import axios from 'axios';

ModuleRegistry.registerModules([
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    ClientSideRowModelModule,
    ValidationModule,
    NumberFilterModule,
    TextFilterModule,
    ColumnAutoSizeModule,
    PaginationModule
]);

const DocumentContentRenderer = (props) => {
    const content = props.value;
    if (!content) return null;

    return (
        <>
            <div className="text-sm">{content.pubmed_id}</div>
        </>
    )
    // NOT REMOVE
    // return (
    //     <div className="p-2">
    //         <div className="font-semibold mb-1">{content.title}</div>
    //         <div className="text-sm text-gray-600 mb-1">PubMed: {content.pubmed_id}</div>
    //         <div className="text-xs text-gray-500 line-clamp-2">{content.text}</div>
    //     </div>
    // );
};

const PassageRenderer = (props) => {
    if (!props.value) return <span className="text-gray-400 italic">No passage</span>;
    return (
        <div className="p-2">
            <div className="text-sm">{props.value}</div>
        </div>
    );
};


const LabelRenderer = (props) => {
    if (!props.value && props.value !== 0) {
        return <span className="text-gray-400 italic">-</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
            {props.value}
        </span>
    );
};
const DocumentAnnotationGrid = ({ data, selectedTopicId, labelRanges = [0, 1, 2] }) => {
    const {
        // topic: [selectedTopicId],
        document_id: [documentID, setDocumentID],
        collection: [collectionID]
    } = useContext(AppContext)

    const navigate = useNavigate();

    const handleNavigate = useCallback(async (docId) => {  
        console.log(data, collectionID);
        
        try {
            await axios.post("/jump-to-document", {
                document: docId,
                topic: selectedTopicId,
                collection: collectionID
            });
            setDocumentID(docId);
            window.location.assign("/index");
        } catch (error) {
            console.error("Navigation failed:", error);
        }
    }, [collectionID, selectedTopicId, navigate, setDocumentID]);

    // Process data and determine if we have passages
    const { rowData, hasPassages, labelTypes } = useMemo(() => {
        const labelSet = new Set();
        let hasPassages = false;

        // First pass: collect all labels and check for passages
        data.results.forEach(doc => {
            doc.data.forEach(annotation => {
                if (annotation.actual_passage_text) {
                    hasPassages = true;
                }
                if (annotation.labels) {
                    Object.keys(annotation.labels).forEach(label => labelSet.add(label));
                }
            });
        });

        // Process row data
        const rows = [];
        data.results.forEach(doc => {
            if (doc.data.length === 0) {
                let empty_row = {
                    document_id: doc.document_id,
                    doc_id: doc.document_content.doc_id,
                    document_content: doc.document_content,
                    labels: {}
                }
                if (hasPassages) {
                    empty_row.passage_text = null;
                }
                rows.push(empty_row);
            } else if (!hasPassages) {
                // Document-level row
                doc.data.forEach((docData, index) => {
                    rows.push({
                        document_id: doc.document_id,
                        doc_id: doc.document_content.doc_id,
                        document_content: doc.document_content,
                        labels: docData.labels || {},
                    });
                });
            } else {
                doc.data.forEach((passage, index) => {
                    rows.push({
                        document_id: doc.document_id,
                        doc_id: doc.document_content.doc_id,
                        document_content: doc.document_content,
                        passage_text: passage.actual_passage_text,
                        labels: passage.labels || {},
                        passage_id: passage.passage_id
                    });
                });
            }
        });

        return {
            rowData: rows,
            labelTypes: Array.from(labelSet),
            hasPassages
        };
    }, [data]);

    const columnDefs = useMemo(() => {
        const cols = [
            {
                field: 'doc_id',
                headerName: 'Document ID',
                pinned: 'left',
                width: 200,
                flex: 1,
            },
            // {
            //     field: 'document_content',
            //     headerName: 'Document Content',
            //     width: 400,
            //     cellRenderer: DocumentContentRenderer,
            //     flex: 1,
            //     valueGetter: (params) => console.log(params)
                
            // },
            {
                field: 'document_content.title',
                headerName: 'Title',
                width: 400,
                flex: 1,
            },
            {
                field: 'document_content.text',
                headerName: 'Content',
                width: 400,
                flex: 1,
            },
        ];

        if (hasPassages) {
            cols.push({
                field: 'passage_text',
                headerName: 'Passage',
                width: 300,
                cellRenderer: PassageRenderer
            });
        }

        // Add label columns with range sub-columns
        labelTypes.forEach(label => {
            const labelColumn = {
                headerName: label,
                children: labelRanges.map(range => ({
                    headerName: `${range}`,
                    valueGetter: params => {
                        if (!params.data?.labels || !params.data.labels[label]) return null;
                        return params.data.labels[label] === range.toString() ? 'x' : null;
                    },
                    width: 100,
                    cellRenderer: LabelRenderer
                }))
            };
            cols.push(labelColumn);
        });

        return cols;
    }, [rowData, labelTypes, labelRanges]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true,
        suppressMovable: true
    }), []);

    return (
        <div className="ag-theme-alpine sortable-table-container">
            <AgGridReact
                rowData={rowData}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                onRowClicked={(params) => {
                    if (params.data?.document_id) {
                        handleNavigate(params.data.document_id);
                    }
                }}
                rowClass="clickable-cell"
                suppressHorizontalScroll={false}
                enableCellTextSelection={true}
                enableCellSpan={true}
                pagination={true}
                paginationPageSize={10}
                paginationPageSizeSelector={false}
                onGridReady={(params) => {
                    params.api.sizeColumnsToFit();
                }}
            />
        </div>
    );
};

export default DocumentAnnotationGrid;