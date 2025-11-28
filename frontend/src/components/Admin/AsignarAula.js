import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function AsignarAula() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [instituciones, setInstituciones] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [form, setForm] = useState({
    id_estudiante: "",
    id_institucion: "",
    id_sede: "",
    id_aula: ""
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/estudiantes").then(r => setEstudiantes(r.data));
    axios.get("http://localhost:8000/instituciones").then(r => setInstituciones(r.data));
    axios.get("http://localhost:8000/aulas").then(r => setAulas(r.data));
  }, []);

  function cargarSedes(id_institucion) {
    if (!id_institucion) {
      setSedes([]);
      return;
    }
    axios.get("http://localhost:8000/sedes")
      .then(r => {
        setSedes(r.data.filter(s => s.id_institucion === Number(id_institucion)));
      });
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_institucion") {
      setForm(f => ({ ...f, id_sede: "", id_aula: "" }));
      cargarSedes(value);
    }
    if (name === "id_sede") {
      setForm(f => ({ ...f, id_aula: "" }));
    }
    setMsg("");
  }

  function aulasFiltradas() {
    if (!form.id_institucion || !form.id_sede) return [];
    return aulas.filter(
      a =>
        a.id_institucion === Number(form.id_institucion) &&
        a.id_sede === Number(form.id_sede)
    );
  }

  async function asignar(e) {
    e.preventDefault();
    setMsg("");
    if (!form.id_estudiante || !form.id_aula) {
      setMsg("Selecciona un estudiante y un aula");
      return;
    }
    try {
      await axios.post("http://localhost:8000/asignar-estudiante-aula", {
        id_estudiante: form.id_estudiante,
        id_aula: form.id_aula
      });
      setMsg("Estudiante asignado correctamente");
      setForm({
        id_estudiante: "",
        id_institucion: "",
        id_sede: "",
        id_aula: ""
      });
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setMsg("Error: " + err.response.data.detail);
      } else {
        setMsg("Error al asignar estudiante");
      }
    }
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Estudiante a Aula</h2>
      <form className="instituciones-form" onSubmit={asignar}>
        <select
          className="aulas-form-input"
          name="id_estudiante"
          value={form.id_estudiante}
          onChange={handleFormChange}
          required
        >
          <option value="">Estudiante</option>
          {estudiantes.map(est => (
            <option key={est.id_estudiante} value={est.id_estudiante}>
              {est.nombres} {est.apellidos} (ID: {est.id_estudiante})
            </option>
          ))}
        </select>
        <select
          className="aulas-form-input"
          name="id_institucion"
          value={form.id_institucion}
          onChange={handleFormChange}
          required
        >
          <option value="">Institución</option>
          {instituciones.map(i => (
            <option key={i.id_institucion} value={i.id_institucion}>
              {i.nombre_inst}
            </option>
          ))}
        </select>
        <select
          className="aulas-form-input"
          name="id_sede"
          value={form.id_sede}
          onChange={handleFormChange}
          required
          disabled={!form.id_institucion}
        >
          <option value="">Sede</option>
          {sedes.map(s => (
            <option key={s.id_sede} value={s.id_sede}>
              {s.direccion} ({s.id_sede})
            </option>
          ))}
        </select>
        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
          disabled={!form.id_sede}
        >
          <option value="">Aula</option>
          {aulasFiltradas().map(a => (
            <option key={a.id_aula} value={a.id_aula}>
              Grado {a.grado} ({a.id_aula})
            </option>
          ))}
        </select>
        <button type="submit" className="aulas-btn">Asignar</button>
      </form>
      {msg && (
        <div style={{
          color: msg.toLowerCase().includes("error") ? "red" : "green",
          marginBottom: "10px"
        }}>{msg}</div>
      )}
    </div>
  );
}

export default AsignarAula;
