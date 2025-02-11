import React from "react";
import {Users, X} from "lucide-react";
import "./styles.css";
import { IconFile } from "@tabler/icons-react";

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

const DocumentList = ({ documents, onNavigate }) => (
    <div className="document-list">
        {documents?.map((doc) => (
            <div key={doc.id} className="document-item" onClick={() => onNavigate(doc.id)}>
                <div className="document-info">
                    <p className="document-title"><IconFile/>{doc.title}</p>
                    {doc.language && <p className="document-meta">Language: {doc.language}</p>}
                    {doc.grade !== undefined && <p className="document-meta">Grade: {doc.grade}</p>}
                    {doc.comment && <p className="document-meta">Comment: {doc.comment}</p>}
                    {doc?.annotators && (
                        <div className="document-users">
                            <Users className="w-4 h-4 mr-1.5" />
                            <span className="truncate">
                                {doc.annotators.join(", ")}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        ))}
        {documents?.length === 0 && (
            <p className="no-documents">No documents available</p>
        )}
    </div>
);

export { Modal, DocumentList };
