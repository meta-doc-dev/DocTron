import React from "react";
import "./style.css";

const StatCard = ({ title, value, children }) => {
    return (
        <div className={`stat__card ${children ? "has-children" : ""}`}>
            <h3 className="card__title">{title}</h3>
            <div className="card__value">{value}{children}</div>
        </div>
    );
};

export default StatCard;