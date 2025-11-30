// src/components/Admin/AdminFestivos.js
import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

const MESES = [
  "Enero","Febrero","Marzo","Abril","Mayo","Junio",
  "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
];

function diasEnMes(mes, anio) {
  return new Date(anio, mes, 0).getDate();
}

function AdminFestivos({ anio: anioProp, onFestivosChange }) {
  const rol = localStorage.getItem("rol") || "SIN_ROL";
  const esAdministrativo = rol === "ADMINISTRATIVO";

  const hoy = new Date();
  const [anio, setAnio] = useState(anioProp || hoy.getFullYear());
  const [mes, setMes] = useState(hoy.getMonth() + 1);

  const [dia, setDia] = useState("");
  const [desc, setDesc] = useState("");
  const [festivos, setFestivos] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const cargarFestivos = async year => {
    setMsg("");
    try {
      const resp = await axios.get(`${BASE}/admin/listar-festivos`, {
        params: { anio: year },
      });
      setFestivos(resp.data || []);
      if (onFestivosChange) onFestivosChange(resp.data || []);
    } catch {
      setMsg("Error al cargar festivos.");
    }
  };

  useEffect(() => {
    if (esAdministrativo) {
      cargarFestivos(anio);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anio, esAdministrativo]);

  const handleAdd = async e => {
    e.preventDefault();
    setMsg("");
    if (!dia || !desc) {
      setMsg("Completa todos los campos.");
      return;
    }
    setLoading(true);
    try {
      const resp = await axios.post(`${BASE}/admin/agregar-festivo`, {
        fecha: dia,
        descripcion: desc,
      });
      setMsg(resp.data.msg || "Festivo registrado.");
      setDia("");
      setDesc("");
      cargarFestivos(anio);
    } catch {
      setMsg("Error en registro.");
    }
    setLoading(false);
  };

  if (!esAdministrativo) {
    return (
      <div className="aulas-panel" style={{ margin: "24px 20px" }}>
        <h2>Gestión de festivos</h2>
        <p>Esta opción está disponible únicamente para el rol ADMINISTRATIVO.</p>
      </div>
    );
  }

  const totalDias = diasEnMes(mes, anio);
  const primerDiaSemana = new Date(anio, mes - 1, 1).getDay();
  const offset = primerDiaSemana === 0 ? 6 : primerDiaSemana - 1;

  const festivoDeDia = d =>
    festivos.find(
      f =>
        parseInt(f.fecha.slice(0, 4)) === anio &&
        parseInt(f.fecha.slice(5, 7)) === mes &&
        parseInt(f.fecha.slice(8, 10)) === d
    );

  const esHoy = d =>
    hoy.getFullYear() === anio &&
    hoy.getMonth() + 1 === mes &&
    hoy.getDate() === d;

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      {/* Header */}
      <div style={{ marginBottom: 12 }}>
        <h2 className="festivos-title">Festivos del programa</h2>
        <span className="festivos-subtitle">
          Gestiona los festivos académicos y visualízalos en calendario.
        </span>
      </div>

      {/* Controles año / mes + formulario */}
      <div className="festivos-toolbar">
        {/* Año */}
        <div className="festivos-year">
          <button
            type="button"
            className="btn-editar"
            onClick={() => setAnio(a => Math.max(2010, a - 1))}
          >
            ⏪
          </button>
          <input
            type="number"
            value={anio}
            min={2010}
            max={2100}
            onChange={e =>
              setAnio(Number(e.target.value) || new Date().getFullYear())
            }
            className="aulas-form-input festivos-year-input"
          />
          <button
            type="button"
            className="btn-editar"
            onClick={() => setAnio(a => Math.min(2100, a + 1))}
          >
            ⏩
          </button>
        </div>

        {/* Mes */}
        <div className="festivos-month">
          <button
            type="button"
            className="btn-editar"
            onClick={() => setMes(m => (m > 1 ? m - 1 : 12))}
          >
            ◀
          </button>
          <span className="festivos-month-label">
            {MESES[mes - 1]} {anio}
          </span>
          <button
            type="button"
            className="btn-editar"
            onClick={() => setMes(m => (m < 12 ? m + 1 : 1))}
          >
            ▶
          </button>
        </div>

        {/* Formulario de nuevo festivo */}
        <form className="festivos-form" onSubmit={handleAdd}>
          <input
            type="date"
            value={dia}
            onChange={e => setDia(e.target.value)}
            className="aulas-form-input"
          />
          <input
            type="text"
            placeholder="Descripción"
            value={desc}
            onChange={e => setDesc(e.target.value)}
            className="aulas-form-input festivos-desc-input"
          />
          <button type="submit" className="aulas-btn" disabled={loading}>
            {loading ? "Guardando..." : "Registrar festivo"}
          </button>
        </form>
      </div>

      {msg && (
        <div
          style={{
            marginBottom: 12,
            padding: "8px 10px",
            borderRadius: 8,
            background: msg.toLowerCase().includes("error")
              ? "#ffe2e2"
              : "#e0f7ea",
            color: msg.toLowerCase().includes("error") ? "#b91c1c" : "#166534",
            fontSize: "0.95em",
          }}
        >
          {msg}
        </div>
      )}

      {/* Calendario mensual de festivos */}
      <div className="festivos-calendar">
        <table className="festivos-table">
          <thead>
            <tr>
              {["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"].map(d => (
                <th key={d} className="festivos-day-header">
                  {d}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(() => {
              const filas = [];
              let diaNum = 1;
              while (diaNum <= totalDias) {
                const celdas = [];
                for (let c = 0; c < 7; c++) {
                  if (filas.length === 0 && c < offset) {
                    celdas.push(<td key={`v-0-${c}`} />);
                  } else if (diaNum > totalDias) {
                    celdas.push(<td key={`v-${filas.length}-${c}`} />);
                  } else {
                    const fest = festivoDeDia(diaNum);
                    const f = !!fest;
                    const h = esHoy(diaNum);

                    celdas.push(
                      <td key={`d-${diaNum}-${c}`} style={{ padding: 0, width: "14%" }}>
                        <div
                          className={`festivos-day-box ${
                            f ? "festivo" : h ? "hoy" : "normal"
                          }`}
                        >
                          <span
                            className={`festivos-day-number ${f ? "festivo" : ""}`}
                          >
                            {diaNum}
                          </span>
                          {h && (
                            <span className="festivos-today-label">Hoy</span>
                          )}
                          {f && (
                            <span
                              title={fest.descripcion}
                              className="festivos-day-desc"
                            >
                              ★ {fest.descripcion}
                            </span>
                          )}
                        </div>
                      </td>
                    );
                    diaNum++;
                  }
                }
                filas.push(<tr key={`fila-${filas.length}`}>{celdas}</tr>);
              }
              return filas;
            })()}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminFestivos;
