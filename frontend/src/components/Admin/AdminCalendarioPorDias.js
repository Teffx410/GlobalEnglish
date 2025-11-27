import React, { useState, useEffect } from "react";
import axios from "axios";
import AdminFestivos from "./AdminFestivos"; // Tu componente para agregar festivos

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
  const [mes, setMes] = useState(hoy.getMonth() + 1); // 1-12
  const [festivos, setFestivos] = useState([]);
  const [semanas, setSemanas] = useState([]);
  const [msg, setMsg] = useState("");
  const [generando, setGenerando] = useState(false);

  useEffect(() => { cargarFestivos(); }, [anio, mes]);
  useEffect(() => { cargarSemanas(); }, [anio]);

  const cargarFestivos = async () => {
    let resp = await axios.get(`${BASE}/admin/listar-festivos?anio=${anio}`);
    setFestivos(resp.data);
  };
  const cargarSemanas = async () => {
    let res = await axios.get(`${BASE}/admin/listar-semanas`);
    setSemanas(res.data || []);
  };
  // Genera semanas para el año seleccionado
  const generarSemanas = async () => {
    setGenerando(true);
    setMsg("");
    try {
      const res = await axios.post(`${BASE}/admin/generar-calendario-semanas?anio=${anio}`);
      setMsg(res.data.msg || "Semanas generadas.");
      setTimeout(cargarSemanas, 800);
    } catch (err) {
      setMsg(
        err.response && err.response.data && err.response.data.detail
          ? err.response.data.detail
          : "Error al generar semanas."
      );
    }
    setTimeout(() => setGenerando(false), 1000);
  };

  const diasEnMes = getNumberOfDays(mes, anio);
  const diasFestivos = festivos
    .filter(f => parseInt(f.fecha.slice(5, 7)) === mes)
    .map(f => ({ dia: parseInt(f.fecha.slice(8, 10)), desc: f.descripcion }));
  const primerDia = new Date(anio, mes - 1, 1).getDay();
  const celdasInicio = primerDia === 0 ? 6 : primerDia - 1;

  function semanaDeDia(d) {
    // yyyy-mm-dd
    const fechaStr = `${anio}-${mes.toString().padStart(2, "0")}-${d.toString().padStart(2, "0")}`;
    for (let s of semanas) {
      if (s.fecha_inicio <= fechaStr && s.fecha_fin >= fechaStr) {
        return s.numero_semana;
      }
    }
    return "";
  }

  function semanasEnMes() {
    return semanas
      .filter(
        s =>
          (parseInt(s.fecha_inicio.slice(5, 7)) === mes || parseInt(s.fecha_fin.slice(5, 7)) === mes) &&
          parseInt(s.fecha_inicio.slice(0, 4)) === anio
      )
      .sort((a, b) => a.numero_semana - b.numero_semana);
  }

  const esHoy = d =>
    hoy.getDate() === d &&
    hoy.getMonth() + 1 === mes &&
    hoy.getFullYear() === anio;

  return (
    <div style={{ maxWidth: 760, margin: "auto", background: "#fafdff", borderRadius: 12, padding: "28px 32px" }}>
      <h2>Calendario mensual</h2>
      <div style={{ display: "flex", alignItems: "center", gap: 15, marginBottom: 18 }}>
        <button disabled={generando} onClick={() => setAnio(y => Math.max(2010, parseInt(y) - 1))}>⏪ Año</button>
        <input type="number" min={2010} max={2100} value={anio} onChange={e => { setAnio(parseInt(e.target.value)); setMes(1); }} style={{ width: 70, textAlign: "center" }} />
        <button disabled={generando} onClick={() => setAnio(y => Math.min(2100, parseInt(y) + 1))}>Año ⏩</button>
        <button disabled={generando} onClick={() => setMes(m => m > 1 ? m - 1 : 12)}>&lt; Mes</button>
        <span style={{ fontWeight: "bold", fontSize: "1.15em" }}>{getMonthName(mes)}</span>
        <button disabled={generando} onClick={() => setMes(m => m < 12 ? m + 1 : 1)}>Mes &gt;</button>
        <button className="aulas-btn" style={{ minWidth: 140 }} disabled={generando} onClick={generarSemanas}>
          {generando ? "Generando..." : "Generar semanas"}
        </button>
      </div>
      {msg && <div style={{ marginBottom: 11, color: msg.toLowerCase().includes("error") ? "#a21" : "#197d2c" }}>{msg}</div>}

      {/* Panel de festivos */}
      <AdminFestivos anio={anio} />

      <div style={{ margin: "20px 0 0 0" }}>
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr style={{ background: "#eee" }}>
              <th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th><th>Dom</th>
            </tr>
          </thead>
          <tbody>
            {(() => {
              const filas = [];
              let dia = 1;
              let semanaActualFila = "";
              for (let f = 0; dia <= diasEnMes; f++) {
                const celdas = [];
                let nroSemanaFila = "";
                for (let c = 0; c < 7; c++) {
                  if ((f === 0 && c < celdasInicio) || dia > diasEnMes) {
                    celdas.push(<td key={`${f}-${c}`} style={{ background: "#fff" }}></td>);
                  } else {
                    const festivo = diasFestivos.find(df => df.dia === dia);
                    const nroSem = semanaDeDia(dia);
                    if (!nroSemanaFila && nroSem) nroSemanaFila = nroSem;
                    celdas.push(
                      <td key={`${f}-${c}`} style={{
                        background: festivo ? "#ffefef" : esHoy(dia) ? "#e0fafd" : "#f8fafd",
                        border: festivo ? "2px solid #e66" : esHoy(dia) ? "2px solid #19b" : "1px solid #dde",
                        color: festivo ? "#c11" : "#222",
                        fontWeight: festivo || nroSem ? "bold" : "normal",
                        textAlign: "center",
                        borderRadius: 8,
                        fontSize: nroSem && semanaActualFila !== nroSem ? "1.13em" : "1em"
                      }}>
                        {dia}
                        {festivo && <div style={{ fontSize: "0.83em" }}>★ {festivo.desc}</div>}
                        {esHoy(dia) && <div style={{ fontSize: "0.78em", color: "#19b" }}>Hoy</div>}
                        {nroSem && semanaActualFila !== nroSem && (
                          <div style={{
                            fontSize: "0.81em", color: "#703eb1", marginTop: 2, fontWeight: 600
                          }}>Semana {nroSem}</div>
                        )}
                      </td>
                    );
                    semanaActualFila = nroSem || semanaActualFila;
                    dia++;
                  }
                }
                filas.push(<tr key={`fila${f}`}>{celdas}</tr>);
              }
              return filas;
            })()}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 20 }}>
        <b>Semanas del mes:</b>
        <ul>
          {semanasEnMes().length === 0 && <li style={{ color: "#b51" }}>No hay semanas generadas para este año.</li>}
          {semanasEnMes().map(s =>
            <li key={s.id_semana}>
              <b>Semana {s.numero_semana}:</b> {s.fecha_inicio} → {s.fecha_fin}
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}

export default AdminCalendarioPorDias;
