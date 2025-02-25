import React, { useCallback, useContext, useMemo, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import {
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    ModuleRegistry,
    NumberFilterModule,
    TextFilterModule,
    ColumnAutoSizeModule,
    PaginationModule,
    ClientSideRowModelApiModule
} from "ag-grid-community";
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AppContext } from '../../../../App';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import "./styles.css";
import {ReactLassoSelect} from "react-lasso-select";

ModuleRegistry.registerModules([
    CellSpanModule,
    ClientSideRowModelModule,
    RowAutoHeightModule,
    ColumnApiModule,
    CellStyleModule,
    RowStyleModule,
    NumberFilterModule,
    TextFilterModule,
    ColumnAutoSizeModule,
    PaginationModule,
    ClientSideRowModelApiModule
]);

// Renderer for displaying passage text
const PassageRenderer = (props) => {
    if (!props.value) {
        return <span className="text-gray-400 italic">No passage</span>;
    }
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

const EntityCountRenderer = (props) => {
    if (!props.value || props.value === 0) {
        return <span className="text-gray-400 italic">None</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
            {props.value} {props.value === 1 ? 'entity' : 'entities'}
        </span>
    );
};

const ConceptCountRenderer = (props) => {
    if (!props.value || props.value === 0) {
        return <span className="text-gray-400 italic">None</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
            {props.value} {props.value === 1 ? 'concept' : 'concepts'}
        </span>
    );
};

// New renderer for facts count
const FactCountRenderer = (props) => {
    if (!props.value || props.value === 0) {
        return <span className="text-gray-400 italic">None</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-amber-100 text-amber-800">
            {props.value} {props.value === 1 ? 'fact' : 'facts'}
        </span>
    );
};

// New renderer for relationships count
const RelationshipCountRenderer = (props) => {
    if (!props.value || props.value === 0) {
        return <span className="text-gray-400 italic">None</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-indigo-100 text-indigo-800">
            {props.value} {props.value === 1 ? 'relationship' : 'relationships'}
        </span>
    );
};

// New renderer for objects count
const ObjectCountRenderer = (props) => {
    if (!props.value || props.value === 0) {
        return <span className="text-gray-400 italic">None</span>;
    }
    return (
        <span className="px-2 py-1 text-xs rounded-full bg-pink-100 text-pink-800">
            {props.value} {props.value === 1 ? 'object' : 'objects'}
        </span>
    );
};

// Existing full width cell renderers (kept as is)
const EntityTaggingFullWidthCellRenderer = (props) => {
    const {data} = props;

    if (!data.entity_tags || Object.keys(data.entity_tags).length === 0) {
        return (
            <div className="full-width-cell">
                <div className="no-data">No entity tags found for this document</div>
            </div>
        );
    }

    // Convert entity tags to a flat array for the table
    const tableRows = [];
    Object.entries(data.entity_tags).forEach(([tagName, entities]) => {
        if (Array.isArray(entities)) {
            entities.forEach(entity => {
                tableRows.push({
                    tagType: tagName,
                    entityText: entity.mention_text || '-',
                    position: entity.start && entity.stop ? `${entity.start}-${entity.stop}` : '-',
                    comment: entity.comment || "-"
                });
            });
        }
    });

    return (
        <div className="full-width-cell">
            <div className="full-width-title">Entity Tagging Details ({tableRows.length} entities)</div>
            <div className="full-width-content">
                <table className="entity-table">
                    <thead>
                    <tr>
                        <th>Tag Type</th>
                        <th>Entity Text</th>
                        <th>Position</th>
                        <th>Comment</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableRows.length > 0 ? (
                        tableRows.map((row, index) => (
                            <tr key={index} className="entity-row">
                                <td className="tag-type-cell">{row.tagType}</td>
                                <td className="entity-text-cell">"{row.entityText}"</td>
                                <td className="entity-position-cell">{row.position}</td>
                                <td className="entity-comment-cell">{row.comment}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4" className="no-data">No entity data found</td>
                        </tr>
                    )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const EntityLinkingFullWidthCellRenderer = (props) => {
    const {data} = props;

    if (!data.concept_types || Object.keys(data.concept_types).length === 0) {
        return (
            <div className="full-width-cell">
                <div className="no-data">No concepts found for this document</div>
            </div>
        );
    }

    // Convert concept data to a flat array for the table
    const tableRows = [];
    Object.entries(data.concept_types).forEach(([typeName, concepts]) => {
        if (Array.isArray(concepts)) {
            concepts.forEach((concept) => {
                if (concept.entities && Array.isArray(concept.entities)) {
                    concept.entities.forEach((entity) => {
                        tableRows.push({
                            type: typeName,
                            conceptName: concept.concept_name || '-',
                            conceptId: concept.concept_url || '-',
                            entityText: entity.mention_text || '-',
                            position: entity.start && entity.stop ? `${entity.start}-${entity.stop}` : '-'
                        });
                    });
                }
            });
        }
    });

    return (
        <div className="full-width-cell">
            <div className="full-width-title">Entity Linking Details ({tableRows.length} linked entities)</div>
            <div className="full-width-content">
                <table className="concept-table">
                    <thead>
                    <tr>
                        <th>Type</th>
                        <th>Concept Name</th>
                        <th>Concept ID</th>
                        <th>Entity Text</th>
                        <th>Position</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableRows.length > 0 ? (
                        tableRows.map((row, index) => (
                            <tr key={index} className="concept-row">
                                <td className="type-cell">{row.type}</td>
                                <td className="concept-name-cell">{row.conceptName}</td>
                                <td className="concept-id-cell">{row.conceptId}</td>
                                <td className="entity-text-cell">"{row.entityText}"</td>
                                <td className="entity-position-cell">{row.position}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5" className="no-data">No entity linking data found</td>
                        </tr>
                    )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const FactsFullWidthCellRenderer = (props) => {
    const {data} = props;

    if (!data.facts || data.facts.length === 0) {
        return (
            <div className="full-width-cell">
                <div className="no-data">No facts found for this document</div>
            </div>
        );
    }

    return (
        <div className="full-width-cell">
            <div className="full-width-title">Facts Details ({data.facts.length} facts)</div>
            <div className="full-width-content">
                <table className="facts-table">
                    <thead>
                    <tr>
                        <th>Subject</th>
                        <th>Subject Type</th>
                        <th>Predicate</th>
                        <th>Predicate Type</th>
                        <th>Object</th>
                        <th>Object Type</th>
                        <th>Comment</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.facts.map((fact, index) => (
                        <tr key={index} className="fact-row">
                            <td className="fact-cell">{fact.subject.concept_url}</td>
                            <td className="fact-type-cell">{fact.subject.name}</td>
                            <td className="fact-cell">{fact.predicate.concept_url}</td>
                            <td className="fact-type-cell">{fact.predicate.name}</td>
                            <td className="fact-cell">{fact.object.concept_url}</td>
                            <td className="fact-type-cell">{fact.object.name}</td>
                            <td className="fact-comment-cell">{fact.comment || "-"}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

// New Full Width Cell Renderer for Relationships Annotation
const RelationshipsFullWidthCellRenderer = (props) => {
    const {data} = props;

    if (!data.relationships || data.relationships.length === 0) {
        return (
            <div className="full-width-cell">
                <div className="no-data">No relationships found for this document</div>
            </div>
        );
    }

    console.log(data.relationships)

    return (
        <div className="full-width-cell">
            <div className="full-width-title">Relationships Details ({data.relationships.length} relationships)</div>
            <div className="full-width-content">
                <table className="relationships-table">
                    <thead>
                    <tr>
                        <th>Subject Text</th>
                        <th>Subject Position</th>
                        <th>Predicate Text</th>
                        <th>Predicate Position</th>
                        <th>Object Text</th>
                        <th>Object Position</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.relationships.map((rel, index) => (
                        <tr key={index} className="relationship-row">
                            <td className="rel-text-cell">"{rel.subject.text || '-'}"</td>
                            <td className="rel-position-cell">
                                {rel.subject.start && rel.subject.stop ?
                                    `${rel.subject.start}-${rel.subject.stop}` : '-'}
                            </td>
                            <td className="rel-text-cell">"{rel.predicate.text || '-'}"</td>
                            <td className="rel-position-cell">
                                {rel.predicate.start && rel.predicate.stop ?
                                    `${rel.predicate.start}-${rel.predicate.stop}` : '-'}
                            </td>
                            <td className="rel-text-cell">"{rel.object.text || '-'}"</td>
                            <td className="rel-position-cell">
                                {rel.object.start && rel.object.stop ?
                                    `${rel.object.start}-${rel.object.stop}` : '-'}
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

// New Full Width Cell Renderer for Object Detection
const ObjectsFullWidthCellRenderer = (props) => {
    const {data} = props;
    const imgSrc = data.doc_image
    console.log(imgSrc, data)
    const hasImage = !!imgSrc;

    if (!data.objects || data.objects.length === 0) {
        return (
            <div className="full-width-cell">
                <div className="no-data">No detected objects found for this document</div>
            </div>
        );
    }

    return (
        <div className="full-width-cell">
            <div className="full-width-title">Detected Objects Details ({data.objects.length} objects)</div>
            <div className="full-width-content">
                <table className="objects-table">
                    <thead>
                    <tr>
                        <th>Object ID</th>
                        <th>Coordinates</th>
                        <th>Labels</th>
                        <th>Comment</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.objects.map((obj, index) => (
                        <tr key={index} className="object-row">
                            <td className="object-id-cell">{index + 1}</td>
                            <td className="object-coords-cell">
                                {hasImage ? <ReactLassoSelect
                                    value={obj.points.split(" ").map((c) => c.split(",").map(Number)).map(([x, y]) => ({ x, y }))}
                                    src={`data:image/png;base64,${imgSrc}`}
                                    imageStyle={{ width: `${200}px` }}
                                /> : '-'}
                            </td>
                            <td className="object-labels-cell">
                                {obj.labels && obj.labels.length > 0 ?
                                    obj.labels.map(label =>
                                        <span key={label.label} className="object-label-pill">
                                            {label.label}: {label.grade}
                                        </span>
                                    ) : '-'}
                            </td>
                            <td className="object-comment-cell">{obj.comment || "-"}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const DocumentAnnotationGrid = ({ data, selectedTopicId, labelRanges = [0, 1, 2] }) => {
    const {
        document_id: [documentID, setDocumentID],
        collection: [collectionID]
    } = useContext(AppContext);

    const navigate = useNavigate();

    const handleNavigate = useCallback(async (docId) => {
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


    // Process data and determine annotation type
    const { rowData, annotationType, labelTypes, entityTypes, conceptTypes, hasFullWidthRows } = useMemo(() => {
        // Detect annotation type by examining data structure
        let detectedType = "unknown";
        const labelSet = new Set();
        const entityTypeSet = new Set();
        const conceptTypeSet = new Set();

        if (data.results && data.results.length > 0) {
            const firstDoc = data.results[0];

            if (firstDoc.data && firstDoc.data.length > 0) {
                // Check if it's a fact annotation
                if (firstDoc.data.some(item => item.facts)) {
                    detectedType = "Facts annotation";
                }
                // Check if it's a relationship annotation
                else if (firstDoc.data.some(item => item.relationships)) {
                    detectedType = "Relationships annotation";
                }
                // Check if it's an object detection
                else if (firstDoc.data.some(item => item.objects)) {
                    detectedType = "Object detection";
                }
                // Check if it has entity tagging (tag_name and entities)
                else if (firstDoc.data.some(item => item.tag_name && item.entities)) {
                    detectedType = "Entity tagging";
                }
                // Check if it has entity linking (type_name and concepts)
                else if (firstDoc.data.some(item => item.type_name && item.concepts)) {
                    detectedType = "Entity linking";
                }
                // Check if it has passage annotations
                else if (firstDoc.data.some(item => item.actual_passage_text)) {
                    detectedType = "Passages annotation";
                }
                // Check if it has Graded labeling labels
                else if (firstDoc.data.some(item => item.labels)) {
                    detectedType = "Graded labeling";
                }
            }
        }

        // Collect all label types for Graded labeling annotations
        if (detectedType === "Graded labeling" || detectedType === "Passages annotation") {
            data.results.forEach(doc => {
                doc.data.forEach(annotation => {
                    if (annotation.labels) {
                        Object.keys(annotation.labels).forEach(label => labelSet.add(label));
                    }
                });
            });
        }

        // Process row data based on annotation type
        const rows = [];

        data.results.forEach(doc => {
            const docId = doc.document_id;
            let totalEntityCount = 0;
            // Base document information
            const baseDocInfo = {
                document_id: docId,
                doc_id: doc.document_content?.document_id || doc.doc_id,
                title: doc.document_content?.title || doc.doc_id,
                text: doc.document_content?.text?.substring(0, 150) + "..." || "No text available",
                pubmed_id: doc.document_content?.pubmed_id || "",
            };

            // Handle empty documents
            if (!doc.data || doc.data.length === 0) {
                rows.push({
                    ...baseDocInfo,
                    entityCount: 0,
                    conceptCount: 0,
                    factCount: 0,
                    relationshipCount: 0,
                    objectCount: 0,
                });
                return;
            }

            switch (detectedType) {
                case "Graded labeling":
                    // Document-level Graded labeling labels
                    doc.data.forEach((docData) => {
                        rows.push({
                            ...baseDocInfo,
                            labels: docData.labels || {},
                        });
                    });
                    break;

                case "Passages annotation":
                    // Passage-level annotations
                    doc.data.forEach((passage) => {
                        rows.push({
                            ...baseDocInfo,
                            passage_text: passage.actual_passage_text,
                            labels: passage.labels || {},
                            passage_id: passage.passage_id
                        });
                    });
                    break;

                case "Entity tagging":
                    // Create a single row for each document with entity tagging data
                    const entityMap = {};

                    doc.data.forEach(tag => {
                        if (tag.tag_name) {
                            entityMap[tag.tag_name] = tag.entities || [];
                            totalEntityCount += (tag.entities || []).length;
                        }
                    });

                    rows.push({
                        ...baseDocInfo,
                        entity_tags: entityMap,
                        entityCount: totalEntityCount,
                    });

                    rows.push({
                        ...baseDocInfo,
                        entity_tags: entityMap,
                        entityCount: totalEntityCount,
                        fullWidth: true,
                        expanded: false
                    });
                    break;

                case "Entity linking":
                    // Create a single row for each document with concept linking data
                    const conceptMap = {};
                    let totalConceptCount = 0;

                    doc.data.forEach(type => {
                        if (type.type_name) {
                            conceptMap[type.type_name] = type.concepts || [];
                            totalConceptCount += (type.concepts || []).length;

                            (type.concepts || []).forEach(concept => {
                                totalEntityCount += (concept.entities || []).length;
                            });
                        }
                    });

                    rows.push({
                        ...baseDocInfo,
                        concept_types: conceptMap,
                        conceptCount: totalConceptCount,
                        entityCount: totalEntityCount,
                    });

                    rows.push({
                        ...baseDocInfo,
                        concept_types: conceptMap,
                        conceptCount: totalConceptCount,
                        entityCount: totalEntityCount,
                        fullWidth: true,
                        expanded: false
                    });
                    break;

                case "Facts annotation":
                    // Process fact annotations
                    let totalFactCount = 0;
                    const facts = [];

                    doc.data.forEach(dataItem => {
                        if (dataItem.facts) {
                            facts.push(...dataItem.facts);
                            totalFactCount += dataItem.facts.length;
                        }
                    });

                    rows.push({
                        ...baseDocInfo,
                        facts: facts,
                        factCount: totalFactCount,
                    });

                    // Add full width row
                    if (totalFactCount > 0) {
                        rows.push({
                            ...baseDocInfo,
                            facts: facts,
                            factCount: totalFactCount,
                            fullWidth: true,
                            expanded: false
                        });
                    }
                    break;

                case "Relationships annotation":
                    // Process relationship annotations
                    let totalRelationshipCount = 0;
                    const relationships = [];

                    doc.data.forEach(dataItem => {
                        if (dataItem.relationships) {
                            relationships.push(...dataItem.relationships);
                            totalRelationshipCount += dataItem.relationships.length;
                        }
                    });

                    rows.push({
                        ...baseDocInfo,
                        relationships: relationships,
                        relationshipCount: totalRelationshipCount,
                    });

                    // Add full width row
                    if (totalRelationshipCount > 0) {
                        rows.push({
                            ...baseDocInfo,
                            relationships: relationships,
                            relationshipCount: totalRelationshipCount,
                            fullWidth: true,
                            expanded: false
                        });
                    }
                    break;

                case "Object detection":
                    // Process object detection annotations
                    let totalObjectCount = 0;
                    const objects = [];

                    doc.data.forEach(dataItem => {
                        if (dataItem.objects) {
                            objects.push(...dataItem.objects);
                            totalObjectCount += dataItem.objects.length;
                        }
                    });

                    rows.push({
                        ...baseDocInfo,
                        objects: objects,
                        objectCount: totalObjectCount,
                    });

                    // Add full width row
                    if (totalObjectCount > 0) {
                        rows.push({
                            ...baseDocInfo,
                            doc_image: doc.document_content?.doc_image || null,
                            objects: objects,
                            objectCount: totalObjectCount,
                            fullWidth: true,
                            expanded: false
                        });
                    }
                    break;

                default:
                    // Unknown format, just add basic document info
                    rows.push(baseDocInfo);
            }
        });

        return {
            rowData: rows,
            annotationType: detectedType,
            labelTypes: Array.from(labelSet),
            entityTypes: Array.from(entityTypeSet),
            conceptTypes: Array.from(conceptTypeSet),
            hasFullWidthRows: detectedType === "Entity tagging" || detectedType === "Entity linking" ||
                detectedType === "Facts annotation" || detectedType === "Relationships annotation" ||
                detectedType === "Object detection"
        };
    }, [data]);


    const fullWidthCellRenderer = useCallback((props) => {
        switch (annotationType) {
            case "Entity tagging":
                return <EntityTaggingFullWidthCellRenderer {...props} />;
            case "Entity linking":
                return <EntityLinkingFullWidthCellRenderer {...props} />;
            case "Facts annotation":
                return <FactsFullWidthCellRenderer {...props} />;
            case "Relationships annotation":
                return <RelationshipsFullWidthCellRenderer {...props} />;
            case "Object detection":
                return <ObjectsFullWidthCellRenderer {...props} />;
            default:
                return null;
        }
    }, [annotationType]);

    // Set row height for full width rows
    const getRowHeight = useCallback((params) => {
        if (params.data && params.data.fullWidth) {
            // Adjust height based on count of items
            if (params.data.entityCount) {
                return Math.max(160, params.data?.entityCount * 40 + 100);
            } else if (params.data.factCount) {
                return Math.max(160, params.data?.factCount * 40 + 100);
            } else if (params.data.relationshipCount) {
                return Math.max(160, params.data?.relationshipCount * 40 + 100);
            } else if (params.data.objectCount) {
                return Math.max(160, params.data?.objectCount * 150 + 100);
            }
            return 300; // Default height
        }
        return undefined; // Use default height for normal rows
    }, [annotationType]);

    const isFullWidthRow = useCallback(({rowNode}) => {
        return rowNode.data.fullWidth;
    }, []);

    const columnDefs = useMemo(() => {
        // Base columns for all annotation types
        const cols = [
            {
                field: 'doc_id',
                headerName: 'Document ID',
                pinned: 'left',
                width: 150,
                flex: 1,
            },
            {
                field: 'title',
                headerName: 'Title',
                width: 300,
                flex: 2,
            },
            {
                field: 'pubmed_id',
                headerName: 'PubMed ID',
                width: 120,
                flex: 1,
            }
        ];

        // Add annotation-specific columns
        switch (annotationType) {
            case "Passages annotation":
                // Add passage column for passage annotations
                cols.push({
                    field: 'passage_text',
                    headerName: 'Passage',
                    width: 300,
                    flex: 2,
                    cellRenderer: PassageRenderer
                });

                // Add label columns with grade ranges
                labelTypes.forEach(label => {
                    const labelColumn = {
                        headerName: label,
                        children: labelRanges.map(range => ({
                            headerName: `${range}`,
                            valueGetter: params => {
                                if (!params.data?.labels || !params.data.labels[label]) return null;
                                return params.data.labels[label] === range.toString() ? '✓' : null;
                            },
                            width: 80,
                            cellRenderer: LabelRenderer
                        }))
                    };
                    cols.push(labelColumn);
                });
                break;

            case "Graded labeling":
                // Add label columns with grade ranges for document-level annotations
                labelTypes.forEach(label => {
                    const labelColumn = {
                        headerName: label,
                        children: labelRanges.map(range => ({
                            headerName: `${range}`,
                            valueGetter: params => {
                                if (!params.data?.labels || params.data.labels[label] === undefined) {
                                    return null;
                                }
                                // Convert both to strings for comparison
                                return params.data.labels[label].toString() === range.toString() ? '✓' : null;
                            },
                            width: 80,
                            cellRenderer: LabelRenderer
                        }))
                    };
                    cols.push(labelColumn);
                });
                break;

            case "Entity tagging":
                // Add column for total entity count
                cols.push({
                    field: 'entityCount',
                    headerName: 'Entities',
                    width: 120,
                    cellRenderer: EntityCountRenderer
                });
                break;

            case "Entity linking":
                // Add column for total concept and entity counts
                cols.push({
                    field: 'conceptCount',
                    headerName: 'Concepts',
                    width: 120,
                    cellRenderer: ConceptCountRenderer
                });

                cols.push({
                    field: 'entityCount',
                    headerName: 'Entities',
                    width: 120,
                    cellRenderer: EntityCountRenderer
                });
                break;

            case "Facts annotation":
                // Add column for total facts count
                cols.push({
                    field: 'factCount',
                    headerName: 'Facts',
                    width: 120,
                    cellRenderer: FactCountRenderer
                });
                break;

            case "Relationships annotation":
                // Add column for total relationships count
                cols.push({
                    field: 'relationshipCount',
                    headerName: 'Relationships',
                    width: 150,
                    cellRenderer: RelationshipCountRenderer
                });
                break;

            case "Object detection":
                // Add column for total objects count
                cols.push({
                    field: 'objectCount',
                    headerName: 'Objects',
                    width: 120,
                    cellRenderer: ObjectCountRenderer
                });
                break;
        }

        return cols;
    }, [annotationType, labelTypes, labelRanges]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        // filter: true,
        suppressMovable: true
    }), []);

    return (
        <div className="ag-theme-alpine sortable-table-container">
            <style>{`
                .full-width-cell {
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    overflow-x: auto;
                }
                
                .full-width-title {
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 15px;
                    color: #333;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 8px;
                }
                
                .full-width-content {
                    display: flex;
                    flex-direction: column;
                }
                
                /* Table styles for all annotation types */
                .entity-table, .concept-table, .facts-table, .relationships-table, .objects-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }
                
                .entity-table th, .concept-table th, .facts-table th, .relationships-table th, .objects-table th {
                    background-color: #e0f2f1;
                    color: #00796b;
                    text-align: left;
                    padding: 10px;
                    font-weight: 600;
                    border-bottom: 2px solid #b2dfdb;
                }
                
                .entity-table td, .concept-table td, .facts-table td, .relationships-table td, .objects-table td {
                    padding: 8px 10px;
                    border-bottom: 1px solid #e0e0e0;
                }
                
                .entity-row:hover, .concept-row:hover, .fact-row:hover, .relationship-row:hover, .object-row:hover {
                    background-color: #f5f5f5;
                }
                
                /* Entity Tagging styles */
                .tag-type-cell, .type-cell {
                    font-weight: 600;
                    color: #00796b;
                    background-color: #e8f5e9;
                }
                
                .entity-text-cell {
                    font-weight: 500;
                }
                
                .entity-position-cell, .concept-id-cell {
                    font-family: monospace;
                    color: #555;
                }
                
                .entity-comment-cell {
                    color: #757575;
                    font-style: italic;
                }
                
                .concept-name-cell {
                    font-weight: 500;
                    color: #673ab7;
                }
                
                /* Fact Annotation styles */
                .fact-cell {
                    font-weight: 500;
                }
                
                .fact-type-cell {
                    color: #ff6f00;
                    background-color: #fff8e1;
                    font-weight: 600;
                }
                
                .fact-comment-cell {
                    color: #757575;
                    font-style: italic;
                }
                
                /* Relationship Annotation styles */
                .rel-text-cell {
                    font-weight: 500;
                }
                
                .rel-position-cell {
                    font-family: monospace;
                    color: #555;
                }
                
                /* Object Detection styles */
                .object-id-cell {
                    font-weight: 600;
                }
                
                .object-coords-cell {
                    font-family: monospace;
                    color: #555;
                }
                
                .object-labels-cell {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 5px;
                }
                
                .object-label-pill {
                    background-color: #e1bee7;
                    color: #6a1b9a;
                    padding: 2px 6px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                }
                
                .object-comment-cell {
                    color: #757575;
                    font-style: italic;
                }
                
                /* Object Detection Image Layout */
                .object-detection-layout {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                
                @media (min-width: 1024px) {
                    .object-detection-layout {
                        flex-direction: row;
                    }
                    
                    .object-image-container {
                        flex: 1;
                    }
                    
                    .objects-table-container {
                        flex: 1;
                    }
                }
                
                .object-image-container {
                    position: relative;
                    min-height: 300px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    overflow: hidden;
                }
                
                .image-with-overlays {
                    position: relative;
                    width: 100%;
                    height: 100%;
                }
                
                .object-image {
                    display: block;
                    width: 100%;
                    height: auto;
                    max-height: 500px;
                    object-fit: contain;
                }
                
                .object-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                }
                
                .object-polygon {
                    cursor: pointer;
                    pointer-events: all;
                    transition: all 0.2s ease;
                }
                
                .object-polygon:hover {
                    fill-opacity: 0.5;
                    stroke-width: 3;
                }
                
                .object-polygon.selected {
                    fill-opacity: 0.5;
                    stroke-width: 3;
                }
                
                .no-image-placeholder {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 300px;
                    background-color: #f0f0f0;
                    color: #777;
                    font-style: italic;
                }
                
                .selected-row {
                    background-color: #e8f5e9;
                    font-weight: 500;
                }
                
                .expansion-btn {
                    background-color: #e57373;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 8px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                    font-weight: 500;
                    font-size: 13px;
                }
                
                .expansion-btn:hover {
                    background-color: #c62828;
                }
                
                .expansion-btn.expanded {
                    background-color: #00796b;
                }
                
                .expansion-btn.expanded:hover {
                    background-color: #005a4f;
                }
                
                .no-data {
                    color: #999;
                    font-style: italic;
                    padding: 10px;
                    text-align: center;
                }
            `}</style>
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
                paginationPageSizeSelector={[5, 10, 20, 50]}
                isFullWidthRow={isFullWidthRow}
                fullWidthCellRenderer={fullWidthCellRenderer}
                getRowHeight={getRowHeight}
                onGridReady={(params) => {
                    params.api.sizeColumnsToFit();
                    // If we have full width rows, redraw the grid to ensure proper row heights
                    if (hasFullWidthRows) {
                        setTimeout(() => params.api.resetRowHeights(), 0);
                    }
                }}
            />
        </div>
    );
};

export default DocumentAnnotationGrid;