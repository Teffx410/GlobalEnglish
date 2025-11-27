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

<<<<<<< HEAD

const locales = { es: esES };


=======
const locales = { es: esES };

>>>>>>> main
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

<<<<<<< HEAD

=======
>>>>>>> main
function diaSemanaToNumber(dia) {
  const days = { "Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 0 };
  return days[dia] ?? 1;
}

<<<<<<< HEAD

=======
>>>>>>> main
// Paleta pastel
const aulaColors = [
  "#A3CEF1", "#CDF2CA", "#FFE5B4", "#FFD6E0", "#FDE7C8",
  "#E9DEF7", "#D2F6F7", "#FFDEB4", "#D6E4FF"
];

<<<<<<< HEAD

function convertirHorarioAEventos(horarios, fechaBase) {
  if (!horarios || horarios.length === 0) return [];
  
  const baseWeek = startOfWeek(fechaBase, { weekStartsOn: 1 });

  return horarios
    .filter(h => {
      // Si no tiene fecha de inicio, lo muestra siempre
      if (!h.fecha_inicio) return true;
      // Convertir a Date si viene como string
      const fechaInicio = new Date(h.fecha_inicio);
      // La semana actual solo muestra eventos si ya empezó el horario vigente
      return baseWeek >= startOfWeek(fechaInicio, { weekStartsOn: 1 });
    })
    .map((h, idx) => {
      // ... lo demás igual
      let dayNum = diaSemanaToNumber(h.dia_semana);
      let baseDate = new Date(baseWeek);
      baseDate.setDate(baseWeek.getDate() + (dayNum === 0 ? 6 : dayNum - 1));
      const [hInit, mInit] = h.h_inicio.split(":").map(Number);
      const [hFin, mFin] = h.h_final.split(":").map(Number);
      let start = new Date(baseDate);
      start.setHours(hInit, mInit, 0, 0);
      let end = new Date(baseDate);
      end.setHours(hFin, mFin, 0, 0);

      return {
        title: `Aula ${h.id_aula} · Grado ${h.grado}`,
        start,
        end,
        allDay: false,
        tooltip: `Día: ${h.dia_semana}, ${h.h_inicio}-${h.h_final}\nCont: ${h.es_continuo === "S" ? "Sí" : "No"}\nMinutos: ${h.minutos_equiv}`,
        bgcolor: aulaColors[h.id_aula % aulaColors.length]
      };
    });
}


function HorarioTutorCalendar() {
  const [tutores, setTutores] = useState([]);
  const [selectedTutor, setSelectedTutor] = useState("");
  const [horarios, setHorarios] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [fechaView, setFechaView] = useState(new Date());
  const [error, setError] = useState("");


  useEffect(() => {
    axios.get("http://localhost:8000/personas")
      .then(r => {
        const tutoresFiltered = r.data.filter(p => p.rol === "TUTOR");
        setTutores(tutoresFiltered);
      })
      .catch(err => {
        console.error("Error al cargar tutores:", err);
        setError("Error al cargar tutores");
      });
  }, []);


  function handleTutorChange(e) {
  const id = e.target.value;
  setSelectedTutor(id);
  setError("");
  
  if (id) {
    axios.get(`http://localhost:8000/horarios-tutor/${id}`)
      .then(r => {
        console.log("✓ Respuesta exitosa:", r.data);
        setHorarios(r.data);
        setEventos(convertirHorarioAEventos(r.data, new Date()));
        setFechaView(new Date());
      })
      .catch(err => {
        console.error("✗ ERROR en la solicitud:", err.response?.status, err.response?.data);
        console.error("URL intentada:", `http://localhost:8000/horarios-tutor/${id}`);
        console.error("Mensaje completo:", err.message);
        setError(`Error: ${err.response?.data?.detail || err.message}`);
        setHorarios([]);
        setEventos([]);
      });
  } else {
    setHorarios([]);
    setEventos([]);
  }
}




  function handleNavigate(nuevaFecha) {
    setFechaView(nuevaFecha);
    if (horarios && horarios.length > 0) {
      setEventos(convertirHorarioAEventos(horarios, nuevaFecha));
    }
  }

=======
function convertirHorarioAEventos(horarios) {
  const hoy = new Date();
  const baseWeek = startOfWeek(hoy, { weekStartsOn: 1 });
  return horarios.map((h, idx) => {
    let dayNum = diaSemanaToNumber(h.dia_semana);
    let baseDate = new Date(baseWeek);
    baseDate.setDate(baseWeek.getDate() + (dayNum === 0 ? 6 : dayNum - 1));
    const [hInit, mInit] = h.h_inicio.split(":").map(Number);
    const [hFin, mFin] = h.h_final.split(":").map(Number);
    let start = new Date(baseDate); start.setHours(hInit, mInit, 0, 0);
    let end = new Date(baseDate); end.setHours(hFin, mFin, 0, 0);
    return {
      title: `Aula ${h.id_aula} · Grado ${h.grado}`,
      start,
      end,
      allDay: false,
      tooltip: `Día: ${h.dia_semana}, ${h.h_inicio}-${h.h_final}\nCont: ${h.es_continuo === "S" ? "Sí" : "No"}\nMinutos: ${h.minutos_equiv}`,
      bgcolor: aulaColors[h.id_aula % aulaColors.length]
    };
  });
}

function HorarioTutorCalendar() {
  const [tutores, setTutores] = useState([]);
  const [selectedTutor, setSelectedTutor] = useState("");
  const [eventos, setEventos] = useState([]);
  const [fechaView, setFechaView] = useState(new Date()); // <-- fecha mostrada en el calendario

  useEffect(() => {
    axios.get("http://localhost:8000/personas")
      .then(r => setTutores(r.data.filter(p => p.rol === "TUTOR")));
  }, []);

  function handleTutorChange(e) {
    const id = e.target.value;
    setSelectedTutor(id);
    if (id) {
      axios.get(`http://localhost:8000/horarios-tutor/${id}`).then(r => {
        setEventos(convertirHorarioAEventos(r.data));
      });
    } else {
      setEventos([]);
    }
  }

  function handleNavigate(nuevaFecha) {
    setFechaView(nuevaFecha); // <-- Navegación
  }
>>>>>>> main

  return (
    <div className="instituciones-panel">
      <h2 style={{ marginBottom: "24px", color: "#3269fb", fontWeight: "bold" }}>Horario Semanal Visual del Tutor</h2>
<<<<<<< HEAD
      
      <select 
        className="aulas-form-input" 
        style={{ maxWidth: 400, fontWeight: 'bold', color: '#26436c' }} 
        value={selectedTutor} 
        onChange={handleTutorChange}
      >
        <option value="">Seleccione Tutor</option>
        {tutores.map(t =>
          <option key={t.id_persona} value={t.id_persona}>
            {t.nombre} ({t.correo})
          </option>
        )}
      </select>
      
      {error && (
        <div style={{ 
          color: "#a11", 
          padding: "10px", 
          background: "#ffefef", 
          borderRadius: "4px", 
          marginBottom: "10px",
          marginTop: "10px"
        }}>
          ❌ {error}
        </div>
      )}
      
=======
      <select className="aulas-form-input" style={{ maxWidth: 400, fontWeight: 'bold', color: '#26436c' }} value={selectedTutor} onChange={handleTutorChange}>
        <option value="">Seleccione Tutor</option>
        {tutores.map(t =>
          <option key={t.id_persona} value={t.id_persona}>{t.nombre} ({t.correo})</option>
        )}
      </select>
>>>>>>> main
      <div style={{
        height: "600px",
        marginTop: "36px",
        borderRadius: "17px",
        overflow: "hidden",
        background: "#f8fafe",
        boxShadow: "0 3px 16px #36576018"
      }}>
        <Calendar
          localizer={localizer}
          events={eventos}
          startAccessor="start"
          endAccessor="end"
          defaultDate={fechaView}
<<<<<<< HEAD
          date={fechaView}
          onNavigate={handleNavigate}
=======
          date={fechaView}                  // <-- Este prop sincroniza la fecha mostrada
          onNavigate={handleNavigate}       // <-- Ahora los botones funcionan!
>>>>>>> main
          defaultView="week"
          views={["week"]}
          culture="es"
          toolbar
<<<<<<< HEAD
          messages={{ 
            week: "Semana", 
            day: "Día", 
            today: "Hoy", 
            previous: "Atrás", 
            next: "Siguiente" 
          }}
=======
          messages={{ week: "Semana", day: "Día", today: "Hoy", previous: "Atrás", next: "Siguiente" }}
>>>>>>> main
          eventPropGetter={event => ({
            style: {
              backgroundColor: event.bgcolor,
              color: "#243347",
              borderRadius: "12px",
              border: "none",
              fontWeight: 400,
              fontSize: "0.55em",
              padding: "1px 4px",
              boxShadow: "0 2px 10px #3269fb18",
              lineHeight: 1.07,
              whiteSpace: "pre-line"
            }
          })}
          tooltipAccessor={event => event.tooltip}
        />
      </div>
    </div>
  );
}

<<<<<<< HEAD

=======
>>>>>>> main
export default HorarioTutorCalendar;
