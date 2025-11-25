// src/components/Dashboard/AdminLayout.js
import React from "react";
import { Outlet } from "react-router-dom";
import AdminSidebar from "./AdminSidebar";
import "../../styles/AdminDashboard.css";

function AdminLayout() {
  return (
    <div className="admin-dashboard-container">
      <AdminSidebar />
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  );
}
export default AdminLayout;
