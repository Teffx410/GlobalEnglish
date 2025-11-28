// src/components/AdminTomaAsistencia.js
import React, { useEffect, useState } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function fechasClaseDelHorario(horario, fechaInicio, fechaFin = new Date()) {
  const diasSemana = {
    Lunes: 1,
    Martes: 2,
    "Miércoles": 3,
    Jueves: 4,
    Viernes: 5,
    "Sábado": 6,
    Domingo: 0,
  };
  if (!horario?.dia_semana || !diasSemana.hasOwnProperty(horario.dia_semana)) {
    return [];
  }

  let result = [];
  let actual = new Date(fechaInicio);
  let fin = typeof fechaFin === "string" ? new Date(fechaFin) : fechaFin;
  actual.setHours(0, 0, 0, 0);
  fin.setHours(0, 0, 0, 0);

  while (actual.getDay() !== diasSemana[horario.dia_semana]) {
    actual.setDate(actual.getDate() + 1);
  }
  while (actual <= fin) {
    result.push(new Date(actual));
    actual.setDate(actual.getDate() + 7);
  }
  return result;
}

function normalizaHora(h) {
  if (!h) return "";
  const partes = String(h).split(":");
  if (partes.length >= 2) {
    return `${partes[0].padStart(2, "0")}:${partes[1].padStart(2, "0")}`;
  }
  return h;
}

function AdminTomaAsistencia() {
  const [tutores, setTutores] = useState([]);
  const [selectedTutor, setSelectedTutor] = useState("");
  const [aulas, setAulas] = useState([]);
  const [selectedAula, setSelectedAula] = useState("");
  const [horarios, setHorarios] = useState([]); // SOLO activos
  const [id_tutor_aula, setIdTutorAula] = useState(null);
  const [motivos, setMotivos] = useState([]);
  const [msg, setMsg] = useState("");
  const [historialAsistencias, setHistorialAsistencias] = useState([]);
  const [modal, setModal] = useState({
    open: false,
    fecha: "",
    hora: "",
    fin: "",
    dia: "",
    horario: null,
    asistenciaExistente: null,
  });
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    dictada: "S",
    horas_dictadas: 2,
    motivo: "",
    reposicion: "N",
    fecha_reposicion: "",
  });

  useEffect(() => {
    axios
      .get(`${BASE}/admin/listar-tutores`)
      .then(r => setTutores(r.data || []))
      .catch(() => setMsg("Error al cargar tutores."));

    axios
      .get(`${BASE}/admin/listar-motivos-inasistencia`)
      .then(r => setMotivos(r.data || []))
      .catch(() => setMsg("Error al cargar motivos."));
  }, []);

  const handleTutorChange = async e => {
    const id = e.target.value;
    setSelectedTutor(id);
    setAulas([]);
    setSelectedAula("");
    setHorarios([]);
    setHistorialAsistencias([]);
    setIdTutorAula(null);
    setMsg("");

    if (!id) return;

    try {
      const r = await axios.get(`${BASE}/admin/listar-aulas-tutor`, {
        params: { id_persona: id },
      });
      setAulas(r.data || []);
    } catch {
      setMsg("Error al cargar aulas del tutor.");
    }
  };

  const handleAulaChange = async e => {
    const id = e.target.value;
    setSelectedAula(id);
    setMsg("");
    setHorarios([]);
    setHistorialAsistencias([]);
    setIdTutorAula(null);

    if (!id || !selectedTutor) return;

    try {
      const rs = await axios.get(`${BASE}/horarios-aula-activos/${id}`);
      setHorarios(rs.data || []);

      const ra = await axios.get(
        `${BASE}/id-tutor-aula/${selectedTutor}/${id}`
      );
      setIdTutorAula(ra.data?.id_tutor_aula || null);

      const ha = await axios.get(
        `${BASE}/reportes/aula/${id}/asistencia`
      );
      setHistorialAsistencias(ha.data || []);
    } catch {
      setMsg("Error al cargar datos del aula (horarios/asistencia).");
    }
  };

  // construir fechas posibles a partir de horarios activos
  let fechasPosibles = [];
  const hoy = new Date();
  horarios.forEach(hor => {
    if (!hor.fechainicio) return;
    const fechasDeEsteHorario = fechasClaseDelHorario(
      hor,
      hor.fechainicio,
      hoy
    ).map(d => ({
      fecha: d.toISOString().slice(0, 10),
      dia: hor.dia_semana,
      hora: normalizaHora(hor.h_inicio),
      fin: normalizaHora(hor.h_final),
      horario: hor,
    }));
    fechasPosibles = fechasPosibles.concat(fechasDeEsteHorario);
  });
  fechasPosibles.sort(
    (a, b) =>
      a.fecha.localeCompare(b.fecha) || a.hora.localeCompare(b.hora)
  );

  const asistenciaPorDiaHora = {};
  historialAsistencias.forEach(a => {
    const fechaOk = a.fecha_clase ? String(a.fecha_clase).split("T")[0] : "";
    const key = fechaOk + "_" + normalizaHora(a.hora_inicio);
    asistenciaPorDiaHora[key] = a;
  });

  const abrirModalAsistencia = (row, asistencia) => {
    if (asistencia) {
      setForm({
        dictada: asistencia.dictada || "S",
        horas_dictadas: asistencia.horas_dictadas || 2,
        motivo: asistencia.id_motivo || "",
        reposicion: asistencia.reposicion || "N",
        fecha_reposicion: asistencia.fecha_reposicion || "",
      });
      setModal({
        open: true,
        ...row,
        asistenciaExistente: asistencia,
      });
    } else {
      setForm({
        dictada: "S",
        horas_dictadas: 2,
        motivo: "",
        reposicion: "N",
        fecha_reposicion: "",
      });
      setModal({
        open: true,
        ...row,
        asistenciaExistente: null,
      });
    }
    setMsg("");
  };

  const handleFormChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === "checkbox" ? (checked ? "S" : "N") : value,
    }));
    setMsg("");
  };

  const buscarHorarioSemana = async (fecha, hora) => {
    const resp = await axios.get(
      `${BASE}/asistencia/encontrar-horario-semana`,
      {
        params: {
          id_aula: selectedAula,
          fecha_clase: fecha,
          hora_inicio: hora,
        },
      }
    );
    return {
      id_horario: resp.data.id_horario,
      id_semana: resp.data.id_semana,
      corresponde_horario: resp.data.corresponde_horario,
      es_festivo: resp.data.es_festivo,
    };
  };

  const tomarAsistencia = async e => {
    e.preventDefault();
    if (!selectedAula || !id_tutor_aula) {
      setMsg("Debe seleccionar tutor y aula.");
      return;
    }
    setLoading(true);
    try {
      const aux = await buscarHorarioSemana(modal.fecha, modal.hora);
      if (!aux.id_horario || !aux.id_semana) {
        setMsg("No se encontró horario/semana para esa fecha y hora.");
        setLoading(false);
        return;
      }

      const payload = {
        id_aula: parseInt(selectedAula),
        id_tutor_aula: parseInt(id_tutor_aula),
        id_horario: parseInt(aux.id_horario),
        id_semana: parseInt(aux.id_semana),
        fecha_clase: modal.fecha,
        hora_inicio: modal.hora,
        hora_fin: modal.fin || undefined,
        dictada: form.dictada,
        horas_dictadas: form.horas_dictadas
          ? parseInt(form.horas_dictadas)
          : 0,
        reposicion: form.reposicion,
        fecha_reposicion: form.fecha_reposicion || undefined,
        id_motivo: form.motivo ? parseInt(form.motivo) : undefined,
        corresponde_horario:
          aux.corresponde_horario !== undefined
            ? parseInt(aux.corresponde_horario)
            : 1,
        es_festivo:
          aux.es_festivo !== undefined ? parseInt(aux.es_festivo) : 0,
      };

      Object.keys(payload).forEach(k => {
        if (
          payload[k] === undefined ||
          payload[k] === null ||
          payload[k] === ""
        ) {
          delete payload[k];
        }
      });

      if (modal.asistenciaExistente && modal.asistenciaExistente.id_asist) {
        await axios.put(
          `${BASE}/asistir-aula/${modal.asistenciaExistente.id_asist}`,
          payload
        );
        setMsg("Asistencia modificada correctamente.");
      } else {
        await axios.post(`${BASE}/asistir-aula`, payload);
        setMsg("Asistencia registrada correctamente.");
      }
      setModal({ open: false });
      const ha = await axios.get(
        `${BASE}/reportes/aula/${selectedAula}/asistencia`
      );
      setHistorialAsistencias(ha.data || []);
    } catch (err) {
      let detalle = "Error al registrar asistencia.";
      if (err.response && err.response.data) {
        if (Array.isArray(err.response.data.detail)) {
          detalle = err.response.data.detail
            .map(el =>
              typeof el === "string" ? el : el.msg || JSON.stringify(el)
            )
            .join(", ");
        } else if (typeof err.response.data.detail === "object") {
          detalle = JSON.stringify(err.response.data.detail);
        } else {
          detalle = err.response.data.detail;
        }
      }
      setMsg("Error: " + detalle);
    }
    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: "100%",
        margin: "24px 20px",
        background: "#fafbfe",
        borderRadius: 15,
        boxShadow: "0 2px 10px #e1e5f3",
        padding: "30px 40px",
      }}
    >
      <h2
        style={{
          fontWeight: "bold",
          fontSize: "2.3em",
          letterSpacing: ".01em",
        }}
      >
        Toma de asistencia
      </h2>

      <div
        style={{
          display: "flex",
          gap: 18,
          flexWrap: "wrap",
          alignItems: "center",
          marginBottom: 18,
        }}
      >
        <label>
          <b>Tutor:</b>
          <select
            className="aulas-form-input"
            value={selectedTutor}
            onChange={handleTutorChange}
            style={{ marginLeft: 8, minWidth: 160 }}
          >
            <option value="">Seleccione tutor</option>
            {tutores.map(t => (
              <option value={t.id_persona} key={t.id_persona}>
                {t.nombre}
              </option>
            ))}
          </select>
        </label>

        {aulas.length > 0 && (
          <label>
            <b>Aula:</b>
            <select
              className="aulas-form-input"
              value={selectedAula}
              onChange={handleAulaChange}
              style={{ marginLeft: 8, minWidth: 160 }}
            >
              <option value="">Seleccione aula</option>
              {aulas.map(a => (
                <option key={a.id_aula} value={a.id_aula}>
                  #{a.id_aula} - Grado {a.grado}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div
        style={{
          marginTop: 24,
          background: "#fff",
          borderRadius: 10,
          padding: "18px 25px",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "1.02em",
          }}
        >
          <thead>
            <tr style={{ background: "#eaf3ff" }}>
              <th style={{ borderRadius: "8px 0 0 0" }}>Fecha</th>
              <th>Día</th>
              <th>Hora inicio</th>
              <th>Hora fin</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            {fechasPosibles.map(row => {
              const key = row.fecha + "_" + normalizaHora(row.hora);
              const asistencia = asistenciaPorDiaHora[key];
              const fechaActual = new Date();
              const esFuturo = new Date(row.fecha) > fechaActual;
              return (
                <tr
                  key={key}
                  style={{ background: asistencia ? "#e7fbe5" : "inherit" }}
                >
                  <td>{row.fecha}</td>
                  <td>{row.dia}</td>
                  <td>{row.hora}</td>
                  <td>{row.fin}</td>
                  <td>
                    {asistencia ? (
                      <button
                        className="aulas-btn"
                        style={{ background: "#FF9534" }}
                        onClick={() => abrirModalAsistencia(row, asistencia)}
                        disabled={loading}
                      >
                        Modificar
                      </button>
                    ) : esFuturo ? (
                      <span style={{ color: "#9aa", fontWeight: 500 }}>
                        Futuro
                      </span>
                    ) : (
                      <button
                        className="aulas-btn"
                        onClick={() => abrirModalAsistencia(row, null)}
                        disabled={loading}
                      >
                        Registrar
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {fechasPosibles.length === 0 && (
          <div
            style={{
              padding: 15,
              color: "#a13",
              fontWeight: "bold",
            }}
          >
            No hay horarios asignados o no hay fechas posibles.
          </div>
        )}
      </div>

      {modal.open && (
        <div
          style={{
            position: "fixed",
            left: 0,
            top: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,.13)",
            zIndex: 999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: "26px 36px",
              borderRadius: 15,
              minWidth: 320,
              minHeight: 180,
              boxShadow: "0 6px 28px #aaa",
            }}
          >
            <h3
              style={{
                marginTop: 2,
                marginBottom: 15,
                fontWeight: 700,
              }}
            >
              {modal.asistenciaExistente
                ? "Modificar asistencia"
                : "Registrar asistencia"}
              <br />
              <span
                style={{
                  fontWeight: 400,
                  fontSize: ".67em",
                }}
              >
                {modal.fecha} {modal.dia} {modal.hora}-{modal.fin}
              </span>
            </h3>

            <form
              onSubmit={tomarAsistencia}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 13,
              }}
            >
              <label>
                <b>¿La clase se dictó?</b>
                <input
                  type="radio"
                  name="dictada"
                  value="S"
                  checked={form.dictada === "S"}
                  onChange={handleFormChange}
                  style={{ marginLeft: 8, marginRight: 3 }}
                />
                Sí
                <input
                  type="radio"
                  name="dictada"
                  value="N"
                  checked={form.dictada === "N"}
                  onChange={handleFormChange}
                  style={{ marginLeft: 18, marginRight: 3 }}
                />
                No
              </label>

              <label>
                Horas dictadas:
                <input
                  type="number"
                  name="horas_dictadas"
                  value={form.horas_dictadas}
                  min="0"
                  max="12"
                  onChange={handleFormChange}
                  style={{ marginLeft: 8, width: 55 }}
                />
              </label>

              {form.dictada === "N" && (
                <>
                  <label>
                    Motivo inasistencia:
                    <select
                      name="motivo"
                      value={form.motivo}
                      onChange={handleFormChange}
                      style={{ marginLeft: 8 }}
                    >
                      <option value="">Seleccione motivo</option>
                      {motivos.map(m => (
                        <option key={m.id_motivo} value={m.id_motivo}>
                          {m.descripcion}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    ¿Hubo reposición?
                    <input
                      type="checkbox"
                      name="reposicion"
                      checked={form.reposicion === "S"}
                      onChange={handleFormChange}
                      style={{ marginLeft: 6 }}
                    />
                  </label>

                  {form.reposicion === "S" && (
                    <label>
                      Fecha reposición:
                      <input
                        type="date"
                        name="fecha_reposicion"
                        value={form.fecha_reposicion}
                        onChange={handleFormChange}
                        style={{ marginLeft: 7, minWidth: 94 }}
                      />
                    </label>
                  )}
                </>
              )}

              <div style={{ marginTop: 12 }}>
                <button
                  className="aulas-btn"
                  type="submit"
                  style={{ marginRight: 13 }}
                  disabled={loading}
                >
                  {modal.asistenciaExistente
                    ? "Guardar cambios"
                    : "Registrar"}
                </button>
                <button
                  onClick={() => setModal({ open: false })}
                  type="button"
                  style={{
                    background: "#eee",
                    borderRadius: 6,
                    border: "none",
                    padding: "7px 21px",
                  }}
                  disabled={loading}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {msg && (
        <div
          style={{
            color: msg.startsWith("Error") ? "#b21" : "#197d2c",
            background: msg.startsWith("Error") ? "#fbe5e9" : "#e7fbe5",
            fontWeight: 500,
            marginTop: 18,
            padding: "10px 15px",
            borderRadius: 6,
            border: msg.startsWith("Error")
              ? "1.3px solid #d88490"
              : "1.3px solid #81cc99",
          }}
        >
          {msg}
        </div>
      )}
    </div>
  );
}

export default AdminTomaAsistencia;
