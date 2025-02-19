import React, { useMemo } from 'react';
import {ArrowBack} from "@mui/icons-material";

const LabelsDisplay = ({ labels }) => {
    if (!labels) {
        return <span className="text-sm text-gray-400 italic">No labels</span>;
    }

    return (
        <div className="flex flex-wrap gap-2">
            {Object.entries(labels).map(([key, value]) => (
                <span
                    key={key}
                    className={`px-2 py-1 text-sm rounded-full font-medium ${
                        value === "1"
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                    }`}
                >
          {key}: {value}
        </span>
            ))}
        </div>
    );
};

export const IndividualDocumentTable = ({ data, type = "Graded labeling"}) => {
    const processedData = useMemo(() => {
        return data.results.map(doc => ({
            documentId: doc.document_id,
            title: doc.document_content.title,
            text: doc.document_content.text,
            // Handle both document-level and passage-level data structures
            content: type === "Graded labeling"
                ? [{ labels: doc.data?.[0]?.labels }]
                : (doc.data?.length > 0
                        ? doc.data.map(passage => ({
                            passageId: passage.passage_id,
                            passageText: passage.actual_passage_text,
                            labels: passage.labels
                        }))
                        : [{ passageId: null, passageText: null, labels: null }]
                )
        }));
    }, [data, type]);

    return (
        <div className="w-full overflow-x-auto rounded-lg shadow">
            <table className="w-full border-collapse bg-white">
                <thead className="bg-gray-50">
                <tr>
                    <th className="p-4 text-left font-medium text-gray-600 border-b w-1/5">Document ID</th>
                    <th className="p-4 text-left font-medium text-gray-600 border-b w-1/5">Document Title</th>
                    {type === "passage" && (
                        <th className="p-4 text-left font-medium text-gray-600 border-b w-2/5">Passage</th>
                    )}
                    <th className="p-4 text-left font-medium text-gray-600 border-b w-1/5">Labels</th>
                </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                {processedData.map((doc) => (
                    doc.content.map((item, index) => (
                        <tr
                            key={`${doc.documentId}-${item.passageId || index}`}
                            className="hover:bg-gray-50 transition-colors"
                        >
                            {index === 0 && (
                                <>
                                    <td
                                        className="p-4 text-sm text-gray-900 font-mono border-r border-gray-100"
                                        rowSpan={doc.content.length}
                                    >
                                        {doc.documentId}
                                    </td>
                                    <td
                                        className="p-4 text-sm text-gray-900 border-r border-gray-100"
                                        rowSpan={doc.content.length}
                                    >
                                        {doc.title}
                                    </td>
                                </>
                            )}
                            {type === "passage" && (
                                <td className="p-4 text-sm text-gray-700">
                                    {item.passageText || (
                                        <span className="text-gray-400 italic">No passage available</span>
                                    )}
                                </td>
                            )}
                            <td className="p-4">
                                <LabelsDisplay labels={item.labels} />
                            </td>
                        </tr>
                    ))
                ))}
                </tbody>
            </table>
        </div>
    );
};

const GradeDistribution = ({ grades }) => {
    if (!grades) return <span className="text-gray-400 italic">No grades</span>;

    return (
        <div className="flex flex-wrap gap-1">
            {Object.entries(grades).map(([grade, count]) => (
                <span key={grade} className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
          {grade}: {count}
        </span>
            ))}
        </div>
    );
};

const LabelGrades = ({ labels }) => {
    if (!labels) return <span className="text-gray-400 italic">No labels</span>;

    return (
        <div className="space-y-2">
            {Object.entries(labels).map(([labelName, data]) => (
                <div key={labelName} className="border-b border-gray-100 pb-2 last:border-0">
                    <div className="text-sm font-medium text-gray-700 mb-1">{labelName}</div>
                    <div className="text-xs text-gray-600">Total: {data.total}</div>
                    <GradeDistribution grades={data.grades} />
                </div>
            ))}
        </div>
    );
};

export const GlobalDocumentTable = ({ data }) => {
    const { processedData, users, uniqueLabels } = useMemo(() => {
        const users = new Set();
        const labels = new Set();

        // First pass to collect all users and labels
        data.results.forEach(doc => {
            doc.data.forEach(annotation => {
                users.add(annotation.username);
                if (annotation.labels) {
                    Object.keys(annotation.labels).forEach(label => labels.add(label));
                }
            });
        });

        // Process data for each document
        const processedData = data.results.map(doc => {
            const rowData = {
                document_id: doc.document_id,
                annotations: {}
            };

            // Initialize annotations for each user
            Array.from(users).forEach(user => {
                rowData.annotations[user] = {
                    total: 0,
                    labels: null
                };
            });

            // Fill in actual annotations
            doc.data.forEach(annotation => {
                rowData.annotations[annotation.username] = {
                    total: annotation.total_num_annotation,
                    labels: annotation.labels
                };
            });

            return rowData;
        });

        return {
            processedData,
            users: Array.from(users),
            uniqueLabels: Array.from(labels)
        };
    }, [data]);

    return (
        <div className="w-full overflow-x-auto rounded-lg shadow">
            <table className="w-full border-collapse bg-white">
                <thead className="bg-gray-50">
                <tr>
                    <th className="p-4 text-left font-medium text-gray-600 border-b">Document ID</th>
                    {users.map(user => (
                        <th key={user} className="p-4 text-left font-medium text-gray-600 border-b">
                            {user}
                        </th>
                    ))}
                </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                {processedData.map((row) => (
                    <tr key={row.document_id} className="hover:bg-gray-50 transition-colors">
                        <td className="p-4 text-sm text-gray-900 font-mono">
                            {row.document_id}
                        </td>
                        {users.map(user => (
                            <td key={`${row.document_id}-${user}`} className="p-4">
                                <div className="min-w-[200px]">
                                    <div className="text-sm text-gray-600 mb-2">
                                        Total Annotations: {row.annotations[user].total}
                                    </div>
                                    <LabelGrades labels={row.annotations[user].labels} />
                                </div>
                            </td>
                        ))}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

