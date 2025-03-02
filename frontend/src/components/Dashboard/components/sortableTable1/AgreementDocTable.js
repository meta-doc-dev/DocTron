import React, {useCallback, useContext, useMemo, useState} from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ClientSideRowModelModule, themeQuartz } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import axios from "axios";
import {AppContext} from "../../../../App";
import {useNavigate} from "react-router-dom";
import "./styles.css"
import {Col, Row} from "react-bootstrap";
import "./agreement.css"

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

const AgreementDocTable = ({ data, selectedTopicId }) => {
    const {
        // topic: [selectedTopicId],
        //document_id: [documentID, setDocumentID],
        collection: [collectionID]
    } = useContext(AppContext)
    const [documentID, setDocumentID] = useState(null)
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

      /*  data.results.forEach(doc => {
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
        });*/

        const customStyles = `
            .custom-header {
                font-size: 18px !important;
            }
        `;
        // Create column definitions
        const columnDefs = [
            {
                field: 'doc_id',
                headerName: 'Document ID',
                pinned: 'left',

                sortable: true,
                filter: true,
                width: 150,
                cellClass: 'font-mono'
            },
            {
                headerName: 'IAA metrics',
                children: [
                    {
                        headerName: 'Fleiss kappa',
                        field: `fleiss`,
                        width: 120,
                        headerClass: "custom-header",
                        sortable: true,
                        cellRenderer: GradeValueRenderer,
                    },
                    {
                        headerName: 'Krippendorff’s alpha',
                        field: `krippendorff`,
                        width: 120,
                        headerClass: "custom-header",
                        sortable: true,
                        cellRenderer: GradeValueRenderer,
                    },
                ]
            },
        ];

        // Add columns for each user
      /*  Array.from(users).forEach(user => {
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
            };*/

            // Add columns for each label
      /*      Array.from(allLabels).forEach(label => {
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
            });*/

            //columnDefs.push(userColumns);
        //});

        // Process data for rows
        const rowData = data.results.map(doc => {
            const row = {
                document_id: doc.document_id,
                doc_id: doc.doc_id,
                fleiss: doc.fleiss,
                krippendorff: doc.krippendorff
            };

            // Initialize all user fields with NaN
          /*  users.forEach(user => {
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
            });*/

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

    const usernames = ["Demo","Alice", "Bob", "Charlie"];

    const columnDefsCoehns = [
        {
            field: "username",
            headerName: "User",
            pinned: "left",
            width: 120,
            headerClass: "custom-header", // Applica stile personalizzato
            cellClass: "custom-username-cell" // Applica stile alla prima colonna
        },
        ...usernames.map((user) => ({
            field: user,
            headerName: user,
            width: 120,
            editable: true,
            cellStyle: (params) => {
                if (params.value === '-'){
                    return { backgroundColor: 'white', color: 'black' }; // Rosso per valori bassi
                }else{
                    const value = parseFloat(params.value); // Convertiamo il valore in numero
                    if (value < 0) {
                        return { backgroundColor: 'rgba(255, 255, 255, 0.2)' }; // Bianco trasparente
                    } else if (value <= 0.2) {
                        return { backgroundColor: 'rgba(224, 247, 250, 0.5)' }; // Blu molto chiaro con trasparenza
                    } else if (value <= 0.4) {
                        return { backgroundColor: 'rgba(128, 222, 234, 0.5)' }; // Blu chiaro con trasparenza
                    } else if (value <= 0.6) {
                        return { backgroundColor: 'rgba(38, 198, 218, 0.5)' }; // Blu medio con trasparenza
                    } else if (value <= 0.8) {
                        return { backgroundColor: 'rgba(0, 151, 167, 0.5)' }; // Blu scuro con trasparenza
                    } else if (value <= 1) {
                        return { backgroundColor: 'rgba(0, 96, 100, 0.5)' }; // Blu molto scuro con trasparenza
                    }
                }

            },
            headerClass: "custom-header" // Applica lo stesso stile agli altri header
        })),
    ];

    const valuesMap = {}; // Per memorizzare i valori e garantire la simmetria

    const rowDataCoehns = usernames.map((userRow) => {
        let row = { username: userRow };
        usernames.forEach((userCol) => {
            if (userRow === userCol) {
                row[userCol] = "—"; // Diagonale
            } else if (valuesMap[userCol] && valuesMap[userCol][userRow] !== undefined) {
                row[userCol] = valuesMap[userCol][userRow]; // Usa il valore già generato
            } else {
                const value = Math.random().toFixed(2).toString(); // Numero tra 0 e 1 con 2 decimali
                row[userCol] = value;

                if (!valuesMap[userRow]) valuesMap[userRow] = {};
                valuesMap[userRow][userCol] = value; // Salva il valore per la simmetria
            }
        });
        return row;
    });


    return (
        <div style={{display:'inline-flex', height: '100%'}}>
            <div style={{width: '400px'}}>
                <div className="ag-theme-alpine sortable-table-container">
                    <AgGridReact
                        rowData={rowData}
                        theme={themeQuartz}
                        columnDefs={columnDefs}
                        onRowClicked={(params) => {
                            setDocumentID(params.data.doc_id);
                        }}
                        defaultColDef={defaultColDef}
                        suppressHorizontalScroll={true}
                        enableCellTextSelection={true}
                        pagination={false}
                        animateRows={true}
                        modules={[ClientSideRowModelModule]}
                    />
                </div>

            </div>

            <div style={{flex:1, margin: '20px'}}>
                Coehn's Kappa for the document: {documentID ? documentID : ''}

                <div className="ag-theme-quartz" id="tableAg" style={{height: 400, width: "100%"}}>
                    <AgGridReact
                        rowData={rowDataCoehns}
                        columnDefs={columnDefsCoehns}
                        defaultColDef={{resizable: true}}
                        domLayout="autoHeight"
                    />
                </div>
            </div>
        </div>


    );
};

export default AgreementDocTable;


