import React from 'react';

function Navigation({ activePage, onNavigate }) {
  const pages = [
    { key: 'evaluate', label: 'Evaluate Candidate', icon: '' },
    { key: 'dashboard', label: 'Recruiter Dashboard', icon: '' },
  ];

  return (
    <nav className="nav-bar">
      <div className="nav-links">
        {pages.map((page) => (
          <button
            key={page.key}
            className={`nav-link ${activePage === page.key ? 'active' : ''}`}
            onClick={() => onNavigate(page.key)}
            id={`nav-${page.key}`}
          >
            <span className="nav-link-icon">{page.icon}</span>
            <span className="nav-link-label">{page.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}

export default Navigation;
