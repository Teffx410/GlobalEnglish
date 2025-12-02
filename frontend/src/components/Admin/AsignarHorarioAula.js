// src/components/AsignarHorarioAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function AsignarHorarioAula() {
  const [aulas, setAulas] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [form, setForm] = useState({
    id_aula: "",
    id_horario: "",
    fecha_inicio: "",
    fecha_fin: ""
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(false);

  // estado para el modal de finalización
  const [showModal, setShowModal] = useState(false);
  const [finFecha, setFinFecha] = useState("");
  const [finIdHist, setFinIdHist] = useState(null);

  useEffect(() => {
    axios
      .get(`${BASE}/aulas`)
      .then((r) => setAulas(r.data || []))
      .catch((err) => {
        console.error("Error cargando aulas:", err);
        setMsg("Error al cargar aulas");
      });

    axios
      .get(`${BASE}/horarios`)
      .then((r) => setHorarios(r.data || []))
      .catch((err) => {
        console.error("Error cargando horarios:", err);
        setMsg("Error al cargar horarios");
      });
  }, []);

  function cargarHistorial(idAula) {
    if (!idAula) {
      setHistorial([]);
      return;
    }
    axios
      .get(`${BASE}/historial-horarios-aula/${idAula}`)
      .then((r) => setHistorial(r.data || []))
      .catch((err) => {
        console.error("Error cargando historial:", err);
        setHistorial([]);
      });
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
    if (name === "id_aula") {
      cargarHistorial(value);
    }
  }

  function asignarHorario(e) {
    e.preventDefault();
    setMsg("");
    setLoading(true);

    axios
      .post(`${BASE}/asignar-horario-aula`, form)
      .then((r) => {
        if (r.data?.error) {
          console.warn("Validación horario:", r.data.error);
          setMsg(r.data.error);
        } else {
          setMsg(r.data.msg || "Horario asignado correctamente.");
          cargarHistorial(form.id_aula);
        }
      })
      .catch((err) => {
        console.error("Error asignar horario:", err);
        setMsg(
          err.response?.data?.detail ||
            err.response?.data?.error ||
            "Error al asignar horario."
        );
      })
      .finally(() => setLoading(false));
  }

  // abrir modal
  function abrirModalFin(idHist) {
    setFinIdHist(idHist);
    setFinFecha("");
    setShowModal(true);
  }

  // confirmar desde el modal
  async function confirmarFin() {
    if (!finIdHist) return;
    setMsg("");
    try {
      // fecha_fin se envía como query param, NO en el body
      const params = {};
      if (finFecha) {
        params.fecha_fin = finFecha; // YYYY-MM-DD
      }

      const r = await axios.put(
        `${BASE}/historial-horarios-aula/${finIdHist}/fin`,
        null,
        { params }
      );

      setMsg(r.data.msg || "Horario marcado como finalizado.");
      setShowModal(false);
      setFinIdHist(null);
      cargarHistorial(form.id_aula);
    } catch (err) {
      console.error("Error finalizar horario:", err);
      setMsg(err.response?.data?.detail || "Error al finalizar horario.");
    }
  }

  function cerrarModal() {
    setShowModal(false);
    setFinIdHist(null);
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Horario a Aula</h2>

      <form className="instituciones-form" onSubmit={asignarHorario}>
        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Aula</option>
          {aulas.map((a) => (
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - Grado {a.grado} - Inst {a.id_institucion} Sede{" "}
              {a.id_sede}
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_horario"
          value={form.id_horario}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Horario</option>
          {horarios.map((h) => (
            <option key={h.id_horario} value={h.id_horario}>
              {h.dia_semana} {h.h_inicio}-{h.h_final} ({h.minutos_equiv} min{" "}
              {h.es_continuo === "S" ? "Cont." : "No"})
            </option>
          ))}
        </select>

        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
          required
          disabled={loading}
        />

        <input
          className="aulas-form-input"
          type="date"
          name="fecha_fin"
          value={form.fecha_fin}
          onChange={handleFormChange}
          disabled={loading}
          placeholder="Fecha fin (opcional)"
        />

        <button
          type="submit"
          className="aulas-btn"
          disabled={loading || !form.id_aula || !form.id_horario}
        >
          {loading ? "Asignando..." : "Asignar Horario"}
        </button>
      </form>

      {msg && <div style={{ marginBottom: "10px" }}>{msg}</div>}

      <h3>Historial horarios aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID hist</th>
              <th>ID Horario</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Día</th>
              <th>Horario</th>
              <th>Min.</th>
              <th>Cont.</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {historial.map((h) => (
              <tr key={h.id_hist_horario}>
                <td>{h.id_hist_horario}</td>
                <td>{h.id_horario}</td>
                <td>{h.fecha_inicio}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.dia_semana}</td>
                <td>
                  {h.h_inicio} - {h.h_final}
                </td>
                <td>{h.minutos_equiv}</td>
                <td>{h.es_continuo === "S" ? "Sí" : "No"}</td>
                <td>
                  {!h.fecha_fin && (
                    <button
                      type="button"
                      className="btn-editar"
                      onClick={() => abrirModalFin(h.id_hist_horario)}
                    >
                      Finalizar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {historial.length === 0 && (
              <tr>
                <td colSpan={9}>No hay historial</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal para fecha de finalización */}
      {showModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 999
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: "20px 24px",
              borderRadius: 8,
              minWidth: 320,
              boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: 12 }}>
              Finalizar horario
            </h3>
            <p style={{ marginBottom: 8 }}>
              Seleccione la fecha de finalización (deje vacío para usar la fecha
              de hoy).
            </p>
            <input
              type="date"
              className="aulas-form-input"
              value={finFecha}
              onChange={(e) => setFinFecha(e.target.value)}
              style={{ marginBottom: 12 }}
            />
            <div
              style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}
            >
              <button
                type="button"
                className="aulas-btn aulas-btn-secundario"
                onClick={cerrarModal}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="aulas-btn"
                onClick={confirmarFin}
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AsignarHorarioAula;
