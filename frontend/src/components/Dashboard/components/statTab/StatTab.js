// StatsTabs.jsx
import React from 'react';
import "./style.css";
import { IconChartLine, IconSquareCheck, IconUsers } from '@tabler/icons-react';
import Tooltip from '../tooltip/Tooltip';

const STATS_TABS = [
    {
        id: 'individual',
        label: 'Individual Stats',
        icon: IconChartLine,
        description: 'View your personal annotation statistics'
    },
    {
        id: 'global',
        label: 'Global Stats',
        icon: IconUsers,
        description: 'Compare statistics across all annotators'
    },
    {
        id: 'inter-agreement',
        label: 'Inter-Agreement',
        icon: IconSquareCheck,
        description: 'Check annotation agreement between users'
    }
];

const StatsTabs = ({ activeTab, onTabChange }) => {
    return (
        <div className="stats-container">
            <nav className="stats-tabs" role="tablist">
                {STATS_TABS.map(({ id, label, icon: Icon, description }) => (
                    <Tooltip key={id} text={description} position="left">
                        <button
                            className={`stats-tab ${activeTab === id ? 'active' : ''}`}
                            onClick={() => onTabChange(id)}
                            role="tab"
                            aria-selected={activeTab === id}
                        >
                            <Icon className="stats-tab-icon" />
                            <span>{label}</span>
                        </button>
                    </Tooltip>
                ))}
            </nav>
        </div>
    );
};

export default StatsTabs;
