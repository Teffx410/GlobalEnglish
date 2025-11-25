import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function AsignarTutorAula() {
  const [aulas, setAulas] = useState([]);
  const [personas, setPersonas] = useState([]); // Solo mostrar tutores
  const [form, setForm] = useState({
    id_aula: "",
    id_persona: "",
    fecha_inicio: "",
    motivo_cambio: "",
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/aulas").then(r => setAulas(r.data));
    axios.get("http://localhost:8000/personas").then(r => {
      // Filtra solo tutores
      setPersonas(r.data.filter(p => p.rol === "TUTOR"));
    });
  }, []);

  function finalizarAsignacion(idTutorAula) {
  if (!window.confirm("¿Finalizar esta asignación de tutor?")) return;
  axios
    .put(`http://localhost:8000/asignacion-tutor/${idTutorAula}/fin`)
    .then(() => {
      setMsg("Asignación de tutor finalizada");
      if (form.id_aula) {
        axios
          .get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
          .then((r) => setHistorial(r.data));
      }
    })
    .catch((err) => {
      setMsg(err.response?.data?.detail || "Error al finalizar asignación");
    });
}

function eliminarAsignacion(idTutorAula) {
  if (!window.confirm("¿Eliminar esta asignación del histórico?")) return;
  axios
    .delete(`http://localhost:8000/asignacion-tutor/${idTutorAula}`)
    .then(() => {
      setMsg("Asignación eliminada del histórico");
      if (form.id_aula) {
        axios
          .get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
          .then((r) => setHistorial(r.data));
      }
    })
    .catch((err) => {
      setMsg(err.response?.data?.detail || "Error al eliminar asignación");
    });
}

function prepararMovimiento(h) {
  // Prepara el formulario de arriba para mover este tutor a otra aula
  setForm((f) => ({
    ...f,
    id_persona: h.id_persona,
    motivo_cambio: f.motivo_cambio || `Movimiento desde aula ${h.id_aula}`,
    // opcional: limpiar aula para que el usuario elija la nueva
    id_aula: ""
  }));
  setMsg("Selecciona el aula de destino arriba y pulsa 'Asignar Tutor' para moverlo.");
}

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_aula" && value) {
      axios.get(`http://localhost:8000/historial-tutores-aula/${value}`)
        .then(r => setHistorial(r.data));
    }
  }

  function asignarTutor(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/asignar-tutor-aula", form)
      .then(r => {
        setMsg(r.data.msg);
        if (form.id_aula) {
          axios.get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      })
      .catch(() => setMsg("Error al asignar tutor"));
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Tutor a Aula</h2>
      <form className="instituciones-form" onSubmit={asignarTutor}>
        <select className="aulas-form-input" name="id_aula" value={form.id_aula} onChange={handleFormChange} required>
          <option value="">Aula</option>
          {aulas.map(a =>
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - Grado {a.grado} - Inst {a.id_institucion} Sede {a.id_sede}
            </option>
          )}
        </select>
        <select className="aulas-form-input" name="id_persona" value={form.id_persona} onChange={handleFormChange} required>
          <option value="">Tutor</option>
          {personas.map(p =>
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo})
            </option>
          )}
        </select>
        <input className="aulas-form-input" type="date" name="fecha_inicio" value={form.fecha_inicio} onChange={handleFormChange}/>
        <input className="aulas-form-input" type="text" name="motivo_cambio" value={form.motivo_cambio} onChange={handleFormChange} placeholder="Motivo (opcional)" />
        <button type="submit" className="aulas-btn">Asignar Tutor</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
      <h3>Historial tutores aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID hist</th>
              <th>Aula</th>
              <th>Tutor</th>
              <th>Correo</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Motivo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {historial.map((h) => (
              <tr key={h.id_tutor_aula}>
                <td>{h.id_tutor_aula}</td>
                <td>
                  {`Aula #${h.id_aula} - Grado ${h.grado} - Inst ${h.id_institucion} Sede ${h.id_sede}`}
                </td>
                <td>{h.nombre_tutor}</td>
                <td>{h.correo_tutor}</td>
                <td>{h.fecha_inicio}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.motivo_cambio || "-"}</td>
                <td>
                  {/* Finalizar solo si está activo */}
                  {!h.fecha_fin && (
                    <button
                      className="btn-editar"
                      type="button"
                      onClick={() => finalizarAsignacion(h.id_tutor_aula)}
                    >
                      Finalizar
                    </button>
                  )}
                  {/* Mover siempre disponible */}
                  <button
                    className="btn-editar"
                    type="button"
                    onClick={() => prepararMovimiento(h)}
                    style={{ marginLeft: "4px" }}
                  >
                    Mover
                  </button>
                  {/* Eliminar registro del histórico */}
                  <button
                    className="btn-eliminar"
                    type="button"
                    onClick={() => eliminarAsignacion(h.id_tutor_aula)}
                    style={{ marginLeft: "4px" }}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {historial.length === 0 && (
              <tr>
                <td colSpan={8}>No hay historial</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default AsignarTutorAula;
