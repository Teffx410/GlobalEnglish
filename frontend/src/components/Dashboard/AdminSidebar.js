import React from "react";
import { Link } from "react-router-dom";
import { FaUserCircle } from "react-icons/fa";
import { BsHouse, BsClipboardData, BsPeople, BsCalendar, BsBarChart } from "react-icons/bs";
import { MdApartment, MdLocationCity } from "react-icons/md";
import { AiOutlineTeam } from "react-icons/ai";
import "../../styles/AdminDashboard.css";

function AdminSidebar() {
  const nombre = localStorage.getItem("nombre_user") || "Sin nombre";
  const rol = localStorage.getItem("rol") || "Sin rol";

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("rol");
    localStorage.removeItem("nombre_user");
    window.location.href = "/login";
  }

  return (
    <aside className="admin-sidebar">
      <div className="sidebar-header">
        <img src="/logo192.png" alt="GlobalEnglish" className="sidebar-logo" />
        <span className="sidebar-title">GlobalEnglish</span>
      </div>
      <div className="sidebar-user-row">
        <FaUserCircle size={38} className="sidebar-user-icon" />
        <div>
          <div className="sidebar-user-name">{nombre}</div>
          <div className="sidebar-rol">{rol}</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <Link className="sidebar-link" to="/admin/dashboard">
              <BsClipboardData size={22} /> Dashboard
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/administracion">
              <MdApartment size={22} /> Administración
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/usuarios">
              <AiOutlineTeam size={22} /> Usuarios
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/instituciones">
              <BsHouse size={22} /> Instituciones
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/sedes">
              <MdLocationCity size={22} /> Sedes
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/calendario">
              <BsCalendar size={22} /> Calendario
            </Link>
          </li>
          <li>
            <Link className="sidebar-link" to="/admin/reportes">
              <BsBarChart size={22} /> Reportes
            </Link>
          </li>
        </ul>
      </nav>
      <button className="sidebar-logout" onClick={handleLogout}>Cerrar Sesión</button>
    </aside>
  );
}

export default AdminSidebar;
