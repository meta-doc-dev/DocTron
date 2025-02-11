import React, { useState, useRef, useEffect } from 'react';
import "./styles.css";

const Tooltip = ({ text, children, position = "top" }) => {
    const [visible, setVisible] = useState(false);
    const [tooltipPosition, setTooltipPosition] = useState(position);
    const tooltipRef = useRef(null);

    useEffect(() => {
        if (!visible || !tooltipRef.current) return;

        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        let newPosition = position;

        if (tooltipRect.top < 0) {
            newPosition = "bottom";
        } else if (tooltipRect.bottom > windowHeight) {
            newPosition = "top";
        } else if (tooltipRect.left < 0) {
            newPosition = "right";
        } else if (tooltipRect.right > windowWidth) {
            newPosition = "left";
        }

        setTooltipPosition(newPosition);
    }, [visible, position]);

    return (
        <div 
            className="tooltip-container"
            onMouseEnter={() => setVisible(true)}
            onMouseLeave={() => setVisible(false)}
        >
            {children}
            {visible && (
                <div ref={tooltipRef} className={`tooltip tooltip-${tooltipPosition}`}>
                    {text}
                </div>
            )}
        </div>
    );
};

export default Tooltip;