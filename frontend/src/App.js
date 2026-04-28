import React, { useState } from "react";
import "./App.css";
import Navigation from "./components/Navigation";
import CandidateUpload from "./components/CandidateUpload";
import RecruiterDashboard from "./components/RecruiterDashboard";
import CandidateDetail from "./components/CandidateDetail";

function App() {
  const [activePage, setActivePage] = useState("evaluate");
  const [detailCandidateId, setDetailCandidateId] = useState(null);

  const handleNavigate = (page) => {
    setActivePage(page);
    setDetailCandidateId(null);
  };

  const handleViewCandidate = (id) => {
    setDetailCandidateId(id);
    setActivePage("detail");
  };

  return (
    <div className="app-root">
      <Navigation activePage={activePage} onNavigate={handleNavigate} />

      <main className="main-content">
        {/* Unified Candidate Evaluation Page */}
        {activePage === "evaluate" && (
          <CandidateUpload onViewCandidate={handleViewCandidate} />
        )}

        {/* Recruiter Dashboard Page */}
        {activePage === "dashboard" && (
          <RecruiterDashboard onViewCandidate={handleViewCandidate} />
        )}

        {/* Candidate Detail Page */}
        {activePage === "detail" && detailCandidateId && (
          <CandidateDetail
            candidateId={detailCandidateId}
            onBack={() => setActivePage("dashboard")}
          />
        )}
      </main>
    </div>
  );
}

export default App;
