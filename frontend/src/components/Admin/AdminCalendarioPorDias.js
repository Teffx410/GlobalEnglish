// src/components/AdminCalendarioPorDias.js
import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function getMonthName(month) {
  return [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
  ][month - 1];
}

function getNumberOfDays(month, year) {
  return new Date(year, month, 0).getDate();
}

function AdminCalendarioPorDias() {
  const hoy = new Date();
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [festivos, setFestivos] = useState([]);
  const [semanas, setSemanas] = useState([]);
  const [msg, setMsg] = useState("");
  const [generando, setGenerando] = useState(false);

  // form festivos
  const [festivoForm, setFestivoForm] = useState({
    fecha: "",
    descripcion: "",
  });
  const [msgFestivo, setMsgFestivo] = useState("");

  useEffect(() => { cargarFestivos(); }, [anio]);
  useEffect(() => { cargarSemanas(); }, [anio]);

  const cargarFestivos = async () => {
    const resp = await axios.get(`${BASE}/admin/listar-festivos?anio=${anio}`);
    setFestivos(resp.data || []);
  };

  const cargarSemanas = async () => {
    const res = await axios.get(`${BASE}/admin/listar-semanas`);
    setSemanas(res.data || []);
  };

  const generarSemanas = async () => {
    setGenerando(true);
    setMsg("");
    try {
      const res = await axios.post(
        `${BASE}/admin/generar-calendario-semanas?anio=${anio}`
      );
      setMsg(res.data.msg || "Semanas generadas exitosamente.");
      setTimeout(cargarSemanas, 800);
    } catch (err) {
      setMsg(err.response?.data?.detail || "Error al generar semanas.");
    } finally {
      setTimeout(() => setGenerando(false), 700);
    }
  };

  const handleFestivoChange = e => {
    const { name, value } = e.target;
    setFestivoForm(f => ({ ...f, [name]: value }));
    setMsgFestivo("");
  };

  const registrarFestivo = async e => {
    e.preventDefault();
    if (!festivoForm.fecha || !festivoForm.descripcion.trim()) {
      setMsgFestivo("Debes ingresar fecha y descripción.");
      return;
    }
    try {
      const res = await axios.post(`${BASE}/admin/crear-festivo`, festivoForm);
      setMsgFestivo(res.data.msg || "Festivo registrado.");
      setFestivoForm({ fecha: "", descripcion: "" });
      cargarFestivos();
    } catch (err) {
      setMsgFestivo(
        err.response?.data?.detail || "Error al registrar festivo."
      );
    }
  };

  const diasEnMes = getNumberOfDays(mes, anio);
  const primerDia = new Date(anio, mes - 1, 1).getDay();
  const celdasInicio = primerDia === 0 ? 6 : primerDia - 1;

  function semanasEnMes() {
    return (semanas || [])
      .filter(
        s =>
          (parseInt(s.fecha_inicio.slice(5, 7)) === mes ||
            parseInt(s.fecha_fin.slice(5, 7)) === mes) &&
          parseInt(s.fecha_inicio.slice(0, 4)) === anio
      )
      .sort((a, b) => a.numero_semana - b.numero_semana);
  }

  const semanasMes = semanasEnMes();

  const esHoy = d =>
    hoy.getDate() === d &&
    hoy.getMonth() + 1 === mes &&
    hoy.getFullYear() === anio;

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 8,
        }}
      >
        <div>
          <h2 style={{ marginBottom: 4 }}>Calendario mensual</h2>
          <span style={{ fontSize: "0.95em", color: "#6b7280" }}>
            Semanas y festivos académicos del año seleccionado.
          </span>
        </div>
        <button
          className="aulas-btn"
          style={{ minWidth: 180 }}
          disabled={generando}
          onClick={generando ? undefined : generarSemanas}
        >
          {generando ? "Generando..." : "Generar semanas"}
        </button>
      </div>

      {/* Controles año / mes */}
      <div
        className="aulas-form"
        style={{
          marginTop: 10,
          marginBottom: 12,
          background: "#f4f7fe",
          borderRadius: 14,
          padding: "10px 14px",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <button
            type="button"
            className="btn-editar"
            style={{ padding: "6px 10px" }}
            disabled={generando}
            onClick={() => setAnio(y => Math.max(2010, parseInt(y) - 1))}
          >
            ⏪
          </button>
          <input
            type="number"
            min={2010}
            max={2100}
            value={anio}
            onChange={e => {
              const v = parseInt(e.target.value || hoy.getFullYear());
              setAnio(v);
            }}
            className="aulas-form-input"
            style={{ width: 90, textAlign: "center" }}
          />
          <button
            type="button"
            className="btn-editar"
            style={{ padding: "6px 10px" }}
            disabled={generando}
            onClick={() => setAnio(y => Math.min(2100, parseInt(y) + 1))}
          >
            ⏩
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            type="button"
            className="btn-editar"
            style={{ padding: "6px 10px" }}
            disabled={generando}
            onClick={() => setMes(m => (m > 1 ? m - 1 : 12))}
          >
            ◀
          </button>
          <span
            style={{
              fontWeight: "bold",
              fontSize: "1.15em",
              color: "#2563eb",
              minWidth: 130,
              textAlign: "center",
            }}
          >
            {getMonthName(mes)} {anio}
          </span>
          <button
            type="button"
            className="btn-editar"
            style={{ padding: "6px 10px" }}
            disabled={generando}
            onClick={() => setMes(m => (m < 12 ? m + 1 : 1))}
          >
            ▶
          </button>
        </div>
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

      {/* Panel festivos: solo formulario, sin listado de texto */}
      <div
        style={{
          background: "#f9fbff",
          borderRadius: 14,
          border: "1px solid #e5e7eb",
          padding: "10px 14px",
          marginBottom: 14,
        }}
      >
        <h3 style={{ marginBottom: 10, fontSize: "1.02em" }}>
          Festivos del {anio}
        </h3>
        <form
          onSubmit={registrarFestivo}
          className="aulas-form"
          style={{ marginBottom: 0 }}
        >
          <input
            type="date"
            name="fecha"
            value={festivoForm.fecha}
            onChange={handleFestivoChange}
            className="aulas-form-input"
          />
          <input
            type="text"
            name="descripcion"
            value={festivoForm.descripcion}
            onChange={handleFestivoChange}
            placeholder="Descripción"
            className="aulas-form-input"
          />
          <button type="submit" className="aulas-btn">
            Registrar festivo
          </button>
        </form>
        {msgFestivo && (
          <div
            style={{
              marginTop: 6,
              fontSize: "0.9em",
              color: msgFestivo.toLowerCase().includes("error")
                ? "#b91c1c"
                : "#166534",
            }}
          >
            {msgFestivo}
          </div>
        )}
      </div>

      {/* Calendario con columna de semanas delgada y festivos sin cambiar tamaño */}
      <div
        style={{
          marginTop: 6,
          borderRadius: 16,
          border: "1px solid #e5e7eb",
          background: "#f9fbff",
          padding: 12,
        }}
      >
        <table
          style={{
            borderCollapse: "separate",
            borderSpacing: 6,
            width: "100%",
            fontSize: "0.96em",
          }}
        >
          <thead>
            <tr>
              <th
                style={{
                  width: 70, // columna semana más delgada
                  padding: "6px 4px",
                  textAlign: "left",
                  color: "#6b7280",
                  fontWeight: 600,
                  background: "#eef3ff",
                  borderRadius: 10,
                }}
              >
                Semana
              </th>
              {["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"].map(d => (
                <th
                  key={d}
                  style={{
                    padding: "6px 4px",
                    textAlign: "center",
                    color: "#2563eb",
                    fontWeight: 700,
                    background: "#eef3ff",
                    borderRadius: 10,
                  }}
                >
                  {d}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(() => {
              const filas = [];
              let dia = 1;
              let indiceSemanaMes = 0;

              while (dia <= diasEnMes) {
                const celdas = [];
                const semanaInfo =
                  indiceSemanaMes < semanasMes.length
                    ? semanasMes[indiceSemanaMes]
                    : null;
                const etiquetaSemana = semanaInfo
                  ? `Semana ${semanaInfo.numero_semana}`
                  : "";

                // Columna de semana
                celdas.push(
                  <td
                    key={`sem-${indiceSemanaMes}`}
                    style={{
                      width: 70,
                      padding: "0 4px",
                      fontSize: "0.85em",
                      color: "#6b7280",
                      verticalAlign: "top",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {etiquetaSemana}
                  </td>
                );

                for (let c = 0; c < 7; c++) {
                  if (filas.length === 0 && c < celdasInicio) {
                    celdas.push(<td key={`vacio-0-${c}`} />);
                  } else if (dia > diasEnMes) {
                    celdas.push(<td key={`vacio-${filas.length}-${c}`} />);
                  } else {
                    const festivoObj = festivos.find(
                      f =>
                        parseInt(f.fecha.slice(0, 4)) === anio &&
                        parseInt(f.fecha.slice(5, 7)) === mes &&
                        parseInt(f.fecha.slice(8, 10)) === dia
                    );
                    const esFestivo = !!festivoObj;
                    const esDiaHoy = esHoy(dia);
                    const fondoBase = esFestivo
                      ? "#fff5f5"
                      : esDiaHoy
                      ? "#e0f2fe"
                      : "#ffffff";

                    celdas.push(
                      <td
                        key={`d-${dia}-${c}`}
                        style={{
                          padding: 0,
                          width: "13%",
                        }}
                      >
                        <div
                          style={{
                            background: fondoBase,
                            borderRadius: 12,
                            border: esFestivo
                              ? "1.5px solid #f97373"
                              : esDiaHoy
                              ? "1.5px solid #2563eb"
                              : "1px solid #e5e7eb",
                            width: "100%",
                            maxWidth: 140,
                            height: 72,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "flex-start",
                            padding: "4px 6px",
                            boxSizing: "border-box",
                            margin: "0 auto",
                          }}
                        >
                          <span
                            style={{
                              fontWeight: 600,
                              color: esFestivo ? "#b91c1c" : "#111827",
                            }}
                          >
                            {dia}
                          </span>

                          {esDiaHoy && (
                            <span
                              style={{
                                fontSize: "0.72em",
                                color: "#2563eb",
                                marginTop: 2,
                              }}
                            >
                              Hoy
                            </span>
                          )}

                          {esFestivo && (
                            <span
                              title={festivoObj.descripcion}
                              style={{
                                marginTop: "auto",
                                fontSize: "0.7em",
                                color: "#b91c1c",
                                textAlign: "center",
                                maxWidth: "100%",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                              }}
                            >
                              ★ {festivoObj.descripcion}
                            </span>
                          )}
                        </div>
                      </td>
                    );
                    dia++;
                  }
                }

                filas.push(<tr key={`fila-${filas.length}`}>{celdas}</tr>);
                indiceSemanaMes++;
              }
              return filas;
            })()}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminCalendarioPorDias;
