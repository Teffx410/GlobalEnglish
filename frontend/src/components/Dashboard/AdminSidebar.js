import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaUserCircle } from "react-icons/fa";
import { BsHouse, BsClipboardData, BsPeople, BsCalendar, BsBarChart } from "react-icons/bs";
import { MdApartment, MdLocationCity, MdSchool, MdWatchLater } from "react-icons/md";
import { AiOutlineTeam } from "react-icons/ai";
import "../../styles/AdminDashboard.css";

function AdminSidebar() {
  const nombre = localStorage.getItem("nombre_user") || "Sin nombre";
  const rol = localStorage.getItem("rol") || "Sin rol";
  const location = useLocation();

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("rol");
    localStorage.removeItem("nombre_user");
    window.location.href = "/login";
  }

  function isActive(path) {
    return location.pathname === path;
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
            <Link className={`sidebar-link${isActive("/admin/dashboard") ? " active" : ""}`} to="/admin/dashboard">
              <BsClipboardData size={22} /> Dashboard
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/administracion") ? " active" : ""}`} to="/admin/administracion">
              <MdApartment size={22} /> Administración
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/personas") ? " active" : ""}`} to="/admin/personas">
              <AiOutlineTeam size={22} /> Personas
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/usuarios") ? " active" : ""}`} to="/admin/usuarios">
              <AiOutlineTeam size={22} /> Usuarios
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/instituciones") ? " active" : ""}`} to="/admin/instituciones">
              <BsHouse size={22} /> Instituciones
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/sedes") ? " active" : ""}`} to="/admin/sedes">
              <MdLocationCity size={22} /> Sedes
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/aulas") ? " active" : ""}`} to="/admin/aulas">
              <MdSchool size={22} /> Aulas
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/horarios") ? " active" : ""}`} to="/admin/horarios">
              <MdWatchLater size={22} /> Horarios
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/asignar-horario") ? " active" : ""}`} to="/admin/asignar-horario">
              <MdWatchLater size={22} /> Asignar Horario
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/asignar-tutor") ? " active" : ""}`} to="/admin/asignar-tutor">
              <MdSchool size={22} /> Asignar Tutor
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/periodos") ? " active" : ""}`} to="/admin/periodos">
              <MdSchool size={22} /> Periodos
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/componentes") ? " active" : ""}`} to="/admin/componentes">
              <MdSchool size={22} /> Componentes
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/estudiantes") ? " active" : ""}`} to="/admin/estudiantes">
              <BsPeople size={22} /> Estudiantes
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/asignar-aula") ? " active" : ""}`} to="/admin/asignar-aula">
              <MdSchool size={22} /> Asignar Aula
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/mover-estudiante") ? " active" : ""}`} to="/admin/mover-estudiante">
              <MdSchool size={22} /> Mover Estudiante
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/calendario") ? " active" : ""}`} to="/admin/calendario">
              <BsCalendar size={22} /> Calendario
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/reportes") ? " active" : ""}`} to="/admin/reportes">
              <BsBarChart size={22} /> Reportes
            </Link>
          </li>
          <li>
            <Link className={`sidebar-link${isActive("/admin/horario-tutor-visual") ? " active" : ""}`} to="/admin/horario-tutor-visual">
              <MdSchool size={22} /> Horario Visual Tutor
            </Link>
          </li>
        </ul>
      </nav>
      <button className="sidebar-logout" onClick={handleLogout}>Cerrar Sesión</button>
    </aside>
  );
}

export default AdminSidebar;
