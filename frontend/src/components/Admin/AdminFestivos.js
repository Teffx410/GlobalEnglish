import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminFestivos({anio, onFestivosChange}) {
  const [dia, setDia] = useState("");
  const [desc, setDesc] = useState("");
  const [festivos, setFestivos] = useState([]);
  const [msg, setMsg] = useState("");

  const cargarFestivos = async () => {
    let resp = await axios.get(`${BASE}/admin/listar-festivos?anio=${anio}`);
    setFestivos(resp.data);
    if (onFestivosChange) onFestivosChange(resp.data);
  };

  useEffect(() => {
    cargarFestivos();
    // eslint-disable-next-line
  }, [anio]);

  const handleAdd = async (e) => {
    e.preventDefault();
    setMsg("");
    if (!dia || !desc) { setMsg("Completa todos los campos!"); return; }
    try {
      let resp = await axios.post(`${BASE}/admin/agregar-festivo`, { fecha: dia, descripcion: desc });
      setMsg(resp.data.msg);
      setDia(""); setDesc("");
      cargarFestivos();
    } catch {
      setMsg("Error en registro.");
    }
  };

  return (
    <div style={{marginTop:24}}>
      <h4>Festivos del {anio}</h4>
      <form onSubmit={handleAdd} style={{display:"flex",gap:10,alignItems:"center",marginBottom:8}}>
        <input type="date" value={dia} onChange={e=>setDia(e.target.value)} />
        <input type="text" placeholder="Descripción" value={desc} onChange={e=>setDesc(e.target.value)} />
        <button type="submit">Registrar festivo</button>
      </form>
      {msg && <div style={{marginBottom:8,color:msg.includes("ya existe")?"orange":"green"}}>{msg}</div>}
      <ul>
        {festivos.map(f=>(
          <li key={f.id_festivo}><b>{f.fecha}</b>: {f.descripcion}</li>
        ))}
      </ul>
    </div>
  );
}

export default AdminFestivos;
