import React from 'react';

// DEV-COMMENT: This component is responsible for listing recent chats and projects.
// For now, it's a static placeholder. In a real application, this would be populated
// with data, likely from a local database or the backend.

const ProjectSidebar = () => {
  return (
    <div className="sidebar">
      <h2>Projects</h2>
      <div className="pane-content">
        <ul>
          <li>Project Alpha</li>
          <li>Project Beta</li>
          <li>General Conversation</li>
        </ul>
      </div>
    </div>
  );
};

export default ProjectSidebar;
