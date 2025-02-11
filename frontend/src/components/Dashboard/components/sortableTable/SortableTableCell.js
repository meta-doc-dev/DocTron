import React from 'react';
import { COLUMN_TYPES } from './types';

const SortableTableCell = ({ column, topic, onClick }) => {
    const getCellClassName = (hasData) => {
        return `table-cell ${hasData ? 'has-data clickable-cell' : ''}`;
    };

    if (column.type === COLUMN_TYPES.LABEL) {        
        const [labelName, grade] = column.label.split('-');
        const count = topic.labels?.[labelName]?.[grade] || 0;
        return (
            <td
                className={getCellClassName(count > 0)}
                onClick={() => count > 0 && onClick(topic, 'label', labelName, grade)}
            >
                {count}
            </td>
        );
    }

    return (
        <td className={getCellClassName(topic[column.key])} onClick={() => onClick(topic, column.type)}>
            {topic[column.key]}
        </td>
    );
};

export default SortableTableCell;
