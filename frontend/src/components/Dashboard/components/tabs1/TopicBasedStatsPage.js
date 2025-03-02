import React, { useState } from "react";
import SortableTable from "../sortableTable/SortableTable";
import "../../style.css"
import "./styles.css"

const TopicBasedStatsPage = () => {
  const [selectedTopic, setSelectedTopic] = useState(null);

  const mockTopicStats = [
    { topic: "Topic A", annotated_docs: 10, unannotated_docs: 5, total_annotations: 50 },
    { topic: "Topic B", annotated_docs: 8, unannotated_docs: 3, total_annotations: 30 },
  ];

  return (
    <section className="main__content topic-stats">
      <h3>Topic-Based Statistics</h3>

      <div className="select-container">
        <label>Select Topic:</label>
        <select onChange={(e) => setSelectedTopic(e.target.value)}>
          <option value="">All</option>
          {mockTopicStats.map((t, index) => (
            <option key={index} value={t.topic}>{t.topic}</option>
          ))}
        </select>
      </div>

      <SortableTable
        data={mockTopicStats.filter(t => !selectedTopic || t.topic === selectedTopic)}
        columns={["topic", "annotated_docs", "unannotated_docs", "total_annotations"]}
      />
    </section>
  );
};

export default TopicBasedStatsPage;
