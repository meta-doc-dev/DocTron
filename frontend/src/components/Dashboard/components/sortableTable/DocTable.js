import React, {useCallback, useContext, useMemo} from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ClientSideRowModelModule, themeQuartz } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import axios from "axios";
import {AppContext} from "../../../../App";
import {useNavigate} from "react-router-dom";
import "./styles.css"

const GradeValueRenderer = (props) => {
    if (!props.value || props.value === 'NaN') {
        return <span className="text-gray-400 italic">0</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
      {props.value}
    </span>
    );
};

const AnnotationTableGrid = ({ data, selectedTopicId }) => {
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

    const { columnDefs, rowData } = useMemo(() => {
        // Get unique users and labels
        const users = new Set();
        const allLabels = new Set();
        const allGradeRanges = new Map();

        data.results.forEach(doc => {
            doc.data.forEach(annotation => {
                users.add(annotation.username);
                if (annotation.labels) {
                    Object.entries(annotation.labels).forEach(([labelName, labelData]) => {
                        allLabels.add(labelName);
                        const grades = Object.keys(labelData.grades);
                        const existingGrades = allGradeRanges.get(labelName) || new Set();
                        grades.forEach(grade => existingGrades.add(grade));
                        allGradeRanges.set(labelName, existingGrades);
                    });
                }
            });
        });

        // Create column definitions
        const columnDefs = [
            {
                field: 'doc_id',
                headerName: 'Document ID',
                pinned: 'left',
                sortable: true,
                filter: true,
                width: 200,
                cellClass: 'font-mono'
            }
        ];

        // Add columns for each user
        Array.from(users).forEach(user => {
            const userColumns = {
                headerName: user,
                children: [
                    {
                        headerName: '# Annotations',
                        field: `${user}_total`,
                        width: 150,
                        sortable: true,
                        cellRenderer: GradeValueRenderer,
                    }
                ]
            };

            // Add columns for each label
            Array.from(allLabels).forEach(label => {
                const gradeRange = Array.from(allGradeRanges.get(label) || []).sort((a, b) => Number(a) - Number(b));
                userColumns.children.push({
                    headerName: label,
                    children: gradeRange.map(grade => ({
                        headerName: `${grade}`,
                        field: `${user}_${label}_${grade}`,
                        width: 120,
                        sortable: true,
                        cellRenderer: GradeValueRenderer
                    }))
                });
            });

            columnDefs.push(userColumns);
        });

        // Process data for rows
        const rowData = data.results.map(doc => {
            const row = {
                document_id: doc.document_id,
                doc_id: doc.doc_id
            };

            // Initialize all user fields with NaN
            users.forEach(user => {
                row[`${user}_total`] = 'NaN';
                allLabels.forEach(label => {
                    const gradeRange = Array.from(allGradeRanges.get(label) || []);
                    gradeRange.forEach(grade => {
                        row[`${user}_${label}_${grade}`] = 'NaN';
                    });
                });
            });

            // Fill in actual values
            doc.data.forEach(annotation => {
                const user = annotation.username;
                row[`${user}_total`] = annotation.total_num_annotation;

                if (annotation.labels) {
                    Object.entries(annotation.labels).forEach(([label, labelData]) => {
                        Object.entries(labelData.grades).forEach(([grade, count]) => {
                            row[`${user}_${label}_${grade}`] = count;
                        });
                    });
                }
            });

            return row;
        });

        return { columnDefs, rowData };
    }, [data]);

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
                theme={themeQuartz}
                columnDefs={columnDefs}
                onRowClicked={(params) => {
                    if (params.data?.document_id) {
                        handleNavigate(params.data.document_id);
                    }
                }}
                defaultColDef={defaultColDef}
                suppressHorizontalScroll={true}
                enableCellTextSelection={true}
                pagination={false}
                animateRows={true}
                modules={[ClientSideRowModelModule]}
            />
        </div>
    );
};

export default AnnotationTableGrid;


