// src/components/Dashboard/TutorLayout.js
import React from "react";
import { Outlet } from "react-router-dom";
import AdminSidebar from "./AdminSidebar";
import "../../styles/AdminDashboard.css";
import "../../styles/AdminLayout.css";

function TutorLayout() {
  // Forzamos la clase de layout para tutor
  const layoutClass = "layout-tutor";

  return (
    <div className={`admin-dashboard-container ${layoutClass}`}>
      <AdminSidebar />
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  );
}

export default TutorLayout;
