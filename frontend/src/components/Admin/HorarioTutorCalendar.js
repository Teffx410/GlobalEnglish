// src/components/Admin/HorarioTutorCalendar.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Calendar, dateFnsLocalizer } from "react-big-calendar";
import format from "date-fns/format";
import parse from "date-fns/parse";
import startOfWeek from "date-fns/startOfWeek";
import getDay from "date-fns/getDay";
import esES from "date-fns/locale/es";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

const locales = { es: esES };

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

function diaSemanaToNumber(dia) {
  const days = {
    Lunes: 1,
    Martes: 2,
    Miércoles: 3,
    Jueves: 4,
    Viernes: 5,
    Sábado: 6,
    Domingo: 0,
  };
  return days[dia] ?? 1;
}

// Paleta pastel
const aulaColors = [
  "#A3CEF1",
  "#CDF2CA",
  "#FFE5B4",
  "#FFD6E0",
  "#FDE7C8",
  "#E9DEF7",
  "#D2F6F7",
  "#FFDEB4",
  "#D6E4FF",
];

function convertirHorarioAEventos(horarios, fechaBase) {
  if (!horarios || horarios.length === 0) return [];

  const baseWeek = startOfWeek(fechaBase, { weekStartsOn: 1 });

  return horarios
    .filter(h => {
      if (!h.fecha_inicio) return true;
      const fechaInicio = new Date(h.fecha_inicio);
      return baseWeek >= startOfWeek(fechaInicio, { weekStartsOn: 1 });
    })
    .map(h => {
      const dayNum = diaSemanaToNumber(h.dia_semana);
      const baseDate = new Date(baseWeek);
      baseDate.setDate(baseWeek.getDate() + (dayNum === 0 ? 6 : dayNum - 1));
      const [hInit, mInit] = h.h_inicio.split(":").map(Number);
      const [hFin, mFin] = h.h_final.split(":").map(Number);
      const start = new Date(baseDate);
      start.setHours(hInit, mInit, 0, 0);
      const end = new Date(baseDate);
      end.setHours(hFin, mFin, 0, 0);

      return {
        title: `Aula ${h.id_aula} · Grado ${h.grado}`,
        start,
        end,
        allDay: false,
        tooltip: `Día: ${h.dia_semana}, ${h.h_inicio}-${h.h_final}\nCont: ${
          h.es_continuo === "S" ? "Sí" : "No"
        }\nMinutos: ${h.minutos_equiv}`,
        bgcolor: aulaColors[h.id_aula % aulaColors.length],
      };
    });
}

function HorarioTutorCalendar() {
  const rol = localStorage.getItem("rol");
  const esSoloTutor = rol === "TUTOR";
  const idPersonaSesion = localStorage.getItem("id_persona") || "";

  const [tutores, setTutores] = useState([]);
  const [selectedTutor, setSelectedTutor] = useState(
    esSoloTutor ? idPersonaSesion : ""
  );
  const [horarios, setHorarios] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [fechaView, setFechaView] = useState(new Date());
  const [error, setError] = useState("");

  // cargar tutores solo si no es tutor
  useEffect(() => {
    if (!esSoloTutor) {
      axios
        .get(`${BASE}/personas`)
        .then(r => {
          const tutoresFiltered = (r.data || []).filter(p => p.rol === "TUTOR");
          setTutores(tutoresFiltered);
        })
        .catch(err => {
          console.error("Error al cargar tutores:", err);
          setError("Error al cargar tutores");
        });
    }
  }, [esSoloTutor]);

  // si es tutor, cargar su horario directamente
  useEffect(() => {
    if (!esSoloTutor) return;
    if (!idPersonaSesion) return;
    cargarHorarioTutor(idPersonaSesion);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [esSoloTutor, idPersonaSesion]);

  const cargarHorarioTutor = id => {
    setSelectedTutor(id);
    setError("");
    if (id) {
      axios
        .get(`${BASE}/horarios-tutor/${id}`)
        .then(r => {
          setHorarios(r.data || []);
          setEventos(convertirHorarioAEventos(r.data || [], new Date()));
          setFechaView(new Date());
        })
        .catch(err => {
          console.error(
            "✗ ERROR en la solicitud:",
            err.response?.status,
            err.response?.data
          );
          setError(`Error: ${err.response?.data?.detail || err.message}`);
          setHorarios([]);
          setEventos([]);
        });
    } else {
      setHorarios([]);
      setEventos([]);
    }
  };

  function handleTutorChange(e) {
    const id = e.target.value;
    cargarHorarioTutor(id);
  }

  function handleNavigate(nuevaFecha) {
    setFechaView(nuevaFecha);
    if (horarios && horarios.length > 0) {
      setEventos(convertirHorarioAEventos(horarios, nuevaFecha));
    }
  }

  return (
    <div className="instituciones-panel">
      <h2 className="asistencia-title">
        Horario semanal visual del tutor
      </h2>

      {/* Selector solo visible para admin/administrativo */}
      {!esSoloTutor && (
        <select
          className="aulas-form-input"
          style={{ maxWidth: 400 }}
          value={selectedTutor}
          onChange={handleTutorChange}
        >
          <option value="">Seleccione Tutor</option>
          {tutores.map(t => (
            <option key={t.id_persona} value={t.id_persona}>
              {t.nombre} ({t.correo})
            </option>
          ))}
        </select>
      )}

      {error && (
        <div
          style={{
            color: "#a11",
            padding: "10px",
            background: "#ffefef",
            borderRadius: "4px",
            marginBottom: "10px",
            marginTop: "10px",
          }}
        >
          ❌ {error}
        </div>
      )}

      <div className="tutor-calendar-wrapper">
        <Calendar
          localizer={localizer}
          events={eventos}
          startAccessor="start"
          endAccessor="end"
          defaultDate={fechaView}
          date={fechaView}
          onNavigate={handleNavigate}
          defaultView="week"
          views={["week"]}
          culture="es"
          toolbar
          messages={{
            week: "Semana",
            day: "Día",
            today: "Hoy",
            previous: "Atrás",
            next: "Siguiente",
          }}
          eventPropGetter={event => ({
            style: {
              backgroundColor: event.bgcolor,
              color: "#243347",
              borderRadius: "12px",
              border: "none",
              fontWeight: 400,
              fontSize: "0.75em",
              padding: "4px 6px",
              boxShadow: "0 2px 10px #3269fb18",
              whiteSpace: "pre-line",
            },
          })}
          tooltipAccessor={event => event.tooltip}
        />
      </div>
    </div>
  );
}

export default HorarioTutorCalendar;
