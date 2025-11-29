// src/components/Admin/AdminScoreEstudiante.js
import React, { useEffect, useState } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminScoreEstudiante() {
  const [filas, setFilas] = useState([]);      // [{id_estudiante,nombres,apellidos,score_entrada,score_salida}]
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // Cargar todos los estudiantes con sus scores
  useEffect(() => {
    const cargar = async () => {
      try {
        const r = await axios.get(`${BASE}/admin/estudiantes`);
        const ests = r.data || [];
        // Si tu endpoint de estudiantes ya trae score_entrada/score_salida, los usas tal cual.
        // Si no, inicialízalos en null.
        const conScores = ests.map(e => ({
          id_estudiante: e.id_estudiante,
          nombres: e.nombres,
          apellidos: e.apellidos,
          score_entrada: e.score_entrada ?? "",
          score_salida: e.score_salida ?? "",
        }));
        setFilas(conScores);
        setMsg("");
      } catch (e) {
        console.error(e);
        setMsg("Error al cargar estudiantes.");
      }
    };
    cargar();
  }, []);

  const handleChange = (id_est, campo, valor) => {
    setFilas(prev =>
      prev.map(f =>
        f.id_estudiante === id_est ? { ...f, [campo]: valor } : f
      )
    );
    setMsg("");
  };

  const guardarTodos = async () => {
    setLoading(true);
    setMsg("");
    try {
      const peticiones = filas.map(f =>
        axios.post(`${BASE}/admin/score-estudiante`, {
          id_estudiante: f.id_estudiante,
          score_entrada:
            f.score_entrada !== "" && f.score_entrada !== null
              ? Number(f.score_entrada)
              : null,
          score_salida:
            f.score_salida !== "" && f.score_salida !== null
              ? Number(f.score_salida)
              : null,
        })
      );
      await Promise.all(peticiones);
      setMsg("Scores guardados correctamente.");
    } catch (e) {
      console.error(e);
      setMsg("Error al guardar scores de estudiantes.");
    }
    setLoading(false);
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 18 }}>
        <h2>Score de entrada y salida</h2>
        <button
          className="aulas-btn"
          type="button"
          onClick={guardarTodos}
          disabled={loading || filas.length === 0}
          style={{ minWidth: 170 }}
        >
          {loading ? "Guardando..." : "Guardar cambios"}
        </button>
      </div>

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>Estudiante</th>
              <th style={{ textAlign: "center" }}>Score entrada</th>
              <th style={{ textAlign: "center" }}>Score salida</th>
            </tr>
          </thead>
          <tbody>
            {filas.map(f => (
              <tr key={f.id_estudiante}>
                <td>
                  {f.nombres} {f.apellidos}
                </td>
                <td style={{ textAlign: "center" }}>
                  <input
                    type="number"
                    step="0.1"
                    className="aulas-form-input"
                    style={{ width: 90 }}
                    value={f.score_entrada}
                    onChange={e =>
                      handleChange(f.id_estudiante, "score_entrada", e.target.value)
                    }
                    disabled={loading}
                  />
                </td>
                <td style={{ textAlign: "center" }}>
                  <input
                    type="number"
                    step="0.1"
                    className="aulas-form-input"
                    style={{ width: 90 }}
                    value={f.score_salida}
                    onChange={e =>
                      handleChange(f.id_estudiante, "score_salida", e.target.value)
                    }
                    disabled={loading}
                  />
                </td>
              </tr>
            ))}
            {filas.length === 0 && (
              <tr>
                <td colSpan={3} style={{ textAlign: "center", padding: 12 }}>
                  No hay estudiantes para mostrar.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {msg && (
        <div
          style={{
            marginTop: 16,
            padding: "10px 14px",
            borderRadius: 6,
            border: msg.startsWith("Error")
              ? "1px solid #fecaca"
              : "1px solid #bbf7d0",
            background: msg.startsWith("Error") ? "#fef2f2" : "#ecfdf3",
            color: msg.startsWith("Error") ? "#b91c1c" : "#166534",
            fontWeight: 500,
          }}
        >
          {msg}
        </div>
      )}
    </div>
  );
}

export default AdminScoreEstudiante;
