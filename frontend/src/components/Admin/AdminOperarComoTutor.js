import React, { useState, useEffect } from "react";
import axios from "axios";
const BASE = "http://localhost:8000";

function AdminOperarComoTutor() {
  const [tutores, setTutores] = useState([]);
  const [clases, setClases] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);
  const [tutorSel, setTutorSel] = useState("");
  const [claseSel, setClaseSel] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    axios.get(`${BASE}/admin/listar-tutores`).then(res => setTutores(res.data));
  }, []);

  const cargarClases = async id_persona => {
    setClases([]);
    setClaseSel("");
    setEstudiantes([]);
    if (!id_persona) return;
    let r = await axios.get(`${BASE}/admin/listar-clases-tutor?id_persona=${id_persona}`);
    setClases(r.data);
  };

  const cargarEstudiantes = async (id_asist) => {
    let resp = await axios.get(`${BASE}/admin/listar-asistencia-estudiantes?id_asist=${id_asist}`);
    setEstudiantes(resp.data);
  };

  const marcarAsistencia = async (est, asistio) => {
    setMsg("");
    await axios.post(`${BASE}/admin/registrar-asistencia-estudiante`, {
      id_asist: claseSel,
      id_estudiante: est.id_estudiante,
      asistio,
      observacion: ""
    });
    cargarEstudiantes(claseSel);
    setMsg("Guardado");
  };

  return (
    <div style={{maxWidth:900,margin:"auto",padding:20,background:"#fafdff",borderRadius:8}}>
      <h2>Asistencia por tutor</h2>
      <div style={{marginBottom:14}}>
        <label>Tutor:&nbsp;</label>
        <select value={tutorSel} onChange={e => {setTutorSel(e.target.value); cargarClases(e.target.value);}}>
          <option value="">Seleccione tutor</option>
          {tutores.map(t => (
            <option value={t.id_persona} key={t.id_persona}>{t.nombre}</option>
          ))}
        </select>
      </div>
      {clases.length > 0 &&
        <div style={{marginBottom:14}}>
          <label>Clase (fecha):&nbsp;</label>
          <select value={claseSel} onChange={e => {setClaseSel(e.target.value); cargarEstudiantes(e.target.value);}}>
            <option value="">Seleccione clase</option>
            {clases.map(c => (
              <option value={c.id_asist} key={c.id_asist}>
                {c.fecha_clase} (Aula {c.id_aula})
              </option>
            ))}
          </select>
        </div>
      }
      {estudiantes.length > 0 &&
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>¿Presente?</th>
              <th>Observación</th>
            </tr>
          </thead>
          <tbody>
            {estudiantes.map(e => (
              <tr key={e.id_estudiante}>
                <td>{e.nombres} {e.apellidos}</td>
                <td>
                  <button style={{ background: e.asistio === 'S' ? '#afffa4' : "#f5f5f5", marginRight:8 }}
                    onClick={() => marcarAsistencia(e, e.asistio === 'S' ? 'N' : 'S')}
                  >
                    {e.asistio === 'S' ? "✔" : "✗"}
                  </button>
                </td>
                <td>{e.observacion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      }
      {msg && <div>{msg}</div>}
      {claseSel && estudiantes.length === 0 && <div style={{marginTop:12,color:"#999"}}>No hay estudiantes registrados para la clase.</div>}
    </div>
  );
}

export default AdminOperarComoTutor;
