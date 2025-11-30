// src/components/Dashboard/AdminSidebar.js
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaUserCircle, FaChalkboardTeacher, FaClipboardCheck } from "react-icons/fa";
import { BsHouse, BsClipboardData, BsPeople, BsCalendar, BsBarChart } from "react-icons/bs";
import { MdApartment, MdLocationCity, MdSchool, MdWatchLater } from "react-icons/md";
import { AiOutlineTeam } from "react-icons/ai";
import "../../styles/AdminDashboard.css";

function AdminSidebar() {
  const nombre = localStorage.getItem("nombre_user") || "Sin nombre";
  const rol = localStorage.getItem("rol") || "SIN_ROL";
  const location = useLocation();

  const esAdmin = rol === "ADMINISTRADOR";
  const esAdministrativo = rol === "ADMINISTRATIVO";
  const esTutor = rol === "TUTOR";

  // Prefijo base según rol: admin o tutor
  const basePath = esTutor ? "/tutor" : "/admin";

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("rol");
    localStorage.removeItem("nombre_user");
    localStorage.removeItem("id_persona");
    window.location.href = "/login";
  }

  function isActive(path) {
    return location.pathname === path;
  }

  return (
    <aside className="admin-sidebar">
      <div className="sidebar-header">
        <img src="/logo-icon.png" alt="GlobalEnglish" className="sidebar-logo" />
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
          {/* Dashboard visible para todos */}
          <li>
            <Link
              className={`sidebar-link${isActive(`${basePath}/dashboard`) ? " active" : ""}`}
              to={`${basePath}/dashboard`}
            >
              <BsClipboardData size={22} /> Dashboard
            </Link>
          </li>

          {/* Gestión operativa: solo ADMINISTRATIVO y ADMINISTRADOR */}
          {(esAdministrativo || esAdmin) && (
            <>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/instituciones`) ? " active" : ""}`}
                  to={`${basePath}/instituciones`}
                >
                  <BsHouse size={22} /> Instituciones
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/sedes`) ? " active" : ""}`}
                  to={`${basePath}/sedes`}
                >
                  <MdLocationCity size={22} /> Sedes
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/aulas`) ? " active" : ""}`}
                  to={`${basePath}/aulas`}
                >
                  <MdSchool size={22} /> Aulas
                </Link>
              </li>
              
              
              
              
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/horarios`) ? " active" : ""}`}
                  to={`${basePath}/horarios`}
                >
                  <MdWatchLater size={22} /> Horarios
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/asignar-horario`) ? " active" : ""}`}
                  to={`${basePath}/asignar-horario`}
                >
                  <MdWatchLater size={22} /> Asignar Horario
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/asignar-tutor`) ? " active" : ""}`}
                  to={`${basePath}/asignar-tutor`}
                >
                  <MdSchool size={22} /> Asignar Tutor
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/periodos`) ? " active" : ""}`}
                  to={`${basePath}/periodos`}
                >
                  <MdSchool size={22} /> Periodos
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/componentes`) ? " active" : ""}`}
                  to={`${basePath}/componentes`}
                >
                  <MdSchool size={22} /> Componentes
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/estudiantes`) ? " active" : ""}`}
                  to={`${basePath}/estudiantes`}
                >
                  <BsPeople size={22} /> Estudiantes
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/asignar-aula`) ? " active" : ""}`}
                  to={`${basePath}/asignar-aula`}
                >
                  <MdSchool size={22} /> Asignar Aula
                </Link>
              </li>

              {/* Festivos solo para ADMINISTRATIVO */}
              {esAdministrativo && (
                <li>
                  <Link
                    className={`sidebar-link${isActive(`${basePath}/festivos`) ? " active" : ""}`}
                    to={`${basePath}/festivos`}
                  >
                    <BsCalendar size={22} /> Festivos
                  </Link>
                </li>
              )}

              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/motivos-inasistencia`) ? " active" : ""}`}
                  to={`${basePath}/motivos-inasistencia`}
                >
                  <FaClipboardCheck size={22} /> Motivos Inasistencia
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/score-estudiante`) ? " active" : ""}`}
                  to={`${basePath}/score-estudiante`}
                >
                  <MdSchool size={22} /> Score Entrada/Salida
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/verificar-asistencia-tutor`) ? " active" : ""}`}
                  to={`${basePath}/verificar-asistencia-tutor`}
                >
                  <FaClipboardCheck size={22} /> Verificar Asistencia Tutor
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/personas`) ? " active" : ""}`}
                  to={`${basePath}/personas`}
                >
                  <AiOutlineTeam size={22} /> Personas
                </Link>
              </li>
            </>
          )}

          {/* Solo ADMINISTRADOR especial */}
          {esAdmin && (
            <>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/usuarios`) ? " active" : ""}`}
                  to={`${basePath}/usuarios`}
                >
                  <AiOutlineTeam size={22} /> Usuarios
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/calendario`) ? " active" : ""}`}
                  to={`${basePath}/calendario`}
                >
                  <BsCalendar size={22} /> Calendario Semanas
                </Link>
              </li>
            </>
          )}

          {/* Funciones de tutor: visibles para TUTOR, ADMINISTRATIVO y ADMINISTRADOR */}
          {(esTutor || esAdministrativo || esAdmin) && (
            <>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/ingreso-notas`) ? " active" : ""}`}
                  to={`${basePath}/ingreso-notas`}
                >
                  <MdSchool size={22} /> Ingreso de Notas
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/toma-asistencia-estudiante`) ? " active" : ""}`}
                  to={`${basePath}/toma-asistencia-estudiante`}
                >
                  <FaChalkboardTeacher size={22} /> Toma Asistencia Estudiante
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/asistencia-aula`) ? " active" : ""}`}
                  to={`${basePath}/asistencia-aula`}
                >
                  <FaClipboardCheck size={22} /> Toma de Asistencia Aula
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/horario-tutor-visual`) ? " active" : ""}`}
                  to={`${basePath}/horario-tutor-visual`}
                >
                  <MdSchool size={22} /> Horario Tutor
                </Link>
              </li>
              <li>
                <Link
                  className={`sidebar-link${isActive(`${basePath}/reporte-autogestion-tutor`) ? " active" : ""}`}
                  to={`${basePath}/reporte-autogestion-tutor`}
                >
                  <FaClipboardCheck size={22} /> Rep. Autogestión
                </Link>
              </li>
            </>
          )}

          {/* Reportes generales */}
          {(esAdministrativo || esAdmin) && (
            <li>
              <Link
                className={`sidebar-link${isActive(`${basePath}/reportes`) ? " active" : ""}`}
                to={`${basePath}/reportes`}
              >
                <BsBarChart size={22} /> Reportes
              </Link>
            </li>
          )}
        </ul>
      </nav>

      <button className="sidebar-logout" onClick={handleLogout}>
        Cerrar Sesión
      </button>
    </aside>
  );
}

export default AdminSidebar;
