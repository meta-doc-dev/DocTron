import React from 'react';
import { COLUMN_TYPES } from './types';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';

const SortableTableHeader = ({ columns, sortConfig, onSort, labelStructure }) => {
    const getSortIcon = (key) => {
        if (sortConfig.key !== key) return null;
        return sortConfig.direction === 'asc' ? <IconChevronUp /> : sortConfig.direction === 'desc' ? <IconChevronDown /> : <></>;
    };

    return (
        <thead>
            <tr>
                {columns.map((column, index) => {
                    if (column.type === COLUMN_TYPES.LABEL) {
                        return (
                            <th key={column.key} colSpan={Object.keys(labelStructure[column.key] || {}).length}>
                                {column.label}
                            </th>
                        );
                    }
                    return (
                        <th key={column.key} onClick={() => onSort(column.key)}
                            className={
                                index === 0 ? "col-topic-id"
                                    : index === 1 ? "col-topic-title"
                                        : index === 2 ? "col-annotated"
                                            : index === 3 ? "col-missing"
                                                : "col-label"
                            }>
                            <div>{column.label} {getSortIcon(column.key)}</div>
                        </th>
                    );
                })}
            </tr>
            {Object.keys(labelStructure).length > 0 && (
                <tr>
                    <th colSpan={columns.filter(col => col.type !== COLUMN_TYPES.LABEL).length}></th>
                    {Object.entries(labelStructure).map(([label, grades]) =>
                        Object.keys(grades).map(grade => (
                            <th key={`${label}-${grade}`} onClick={() => onSort(`${label}-${grade}`)}
                                className="col-label"
                            >
                                <div>
                                    {grade} {getSortIcon(`${label}-${grade}`)}
                                </div>
                            </th>
                        ))
                    )}
                </tr>
            )}
        </thead>
    );
};

export default SortableTableHeader;
