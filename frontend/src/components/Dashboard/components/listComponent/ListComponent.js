import React, { useMemo } from "react";
import "./style.css";
import { IconWriting } from "@tabler/icons-react";

const ListComponent = ({ title, items, selectedItem, onClick, renderItem, itemKey = "id", className }) => {
  const isGrouped = !Array.isArray(items);

  return (
    <div className={`list__container ${className}`}>
      {title && <div className="list__heading">{title}</div>}

      {isGrouped
        ?
        Object.entries(items).map(([annotationType, collections]) => (
          <div key={annotationType} className="list__group">
            <h3 className="list__group-header"><IconWriting /> {annotationType}</h3>
            <ul className="container__list">
              {collections.map((item) => (
                renderItem ? renderItem(item) :
                  <ListItem
                    key={item[itemKey]}
                    item={item}
                    onClick={onClick}
                    selectedItem={selectedItem}
                    itemKey={itemKey}
                  />
              ))}
            </ul>
          </div>
        ))
        :
        <ul className="container__list">
          {items.map((item) => (
            renderItem ? renderItem(item) :
              <ListItem
                key={item[itemKey]}
                item={item}
                onClick={onClick}
                selectedItem={selectedItem}
                itemKey={itemKey}
              />
          ))}
        </ul>
      }
    </div>
  );
};

const ListItem = ({ item, onClick, selectedItem, itemKey }) => {
  return (
    <li className={`list__item ${selectedItem === item[itemKey] ? "list__item--selected" : ""}`}>
      <div className="list__item-content" onClick={() => onClick(item[itemKey])}>
        <span>{item.name}</span>
      </div>
    </li>
  );
};

export default ListComponent;
