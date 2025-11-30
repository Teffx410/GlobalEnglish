// src/components/Auth/Login.js
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../../styles/Login.css";

function Login({ setToken }) {
  const [form, setForm] = useState({ correo: "", contrasena: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = e =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError("");
    try {
      const resp = await axios.post(
        "http://localhost:8000/login",
        {
          correo: form.correo,
          contrasena: form.contrasena,
        },
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      console.log("RESPUESTA DEL BACKEND:", resp.data);

      if (resp.data.ftoken && resp.data.rol && resp.data.nombre_user) {
        setToken(resp.data.ftoken);
        localStorage.setItem("token", resp.data.ftoken);
        localStorage.setItem("rol", resp.data.rol);
        localStorage.setItem("nombre_user", resp.data.nombre_user);

        // guardar id_persona correctamente
        if (
          resp.data.id_persona !== undefined &&
          resp.data.id_persona !== null
        ) {
          localStorage.setItem("id_persona", String(resp.data.id_persona));
        } else {
          localStorage.removeItem("id_persona");
        }

        // Redirección según rol
        switch (resp.data.rol) {
          case "TUTOR":
            navigate("/tutor/dashboard");
            break;
          case "ADMINISTRADOR":
          case "ADMINISTRATIVO":
            navigate("/admin/dashboard");
            break;
          default:
            navigate("/login");
        }
      } else {
        setError("Credenciales incorrectas.");
      }
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError("Credenciales incorrectas.");
      } else if (
        err.code === "ERR_NETWORK" ||
        (err.message &&
          (err.message.includes("Network Error") ||
            err.message.includes("ECONNREFUSED")))
      ) {
        setError("No se pudo conectar con el servidor. Verifica el backend.");
      } else {
        setError("Error al iniciar sesión.");
      }
    }
  };

  return (
    <div className="login-bg">
      <div className="login-card">
        <div className="login-header">
          <img src="/logo.png" alt="GlobalEnglish" className="login-logo" />
        </div>
        <form onSubmit={handleSubmit}>
          <label htmlFor="correo">Email</label>
          <div className="login-input-group">
            <span className="login-icon">
              <i className="bi bi-envelope"></i>
            </span>
            <input
              type="email"
              name="correo"
              id="correo"
              placeholder="tu@email.com"
              value={form.correo}
              onChange={handleChange}
              required
            />
          </div>
          <label htmlFor="contrasena">Contraseña</label>
          <div className="login-input-group">
            <span className="login-icon">
              <i className="bi bi-lock"></i>
            </span>
            <input
              type="password"
              name="contrasena"
              id="contrasena"
              placeholder="******"
              value={form.contrasena}
              onChange={handleChange}
              required
            />
          </div>
          <button className="login-btn" type="submit">
            Iniciar Sesión
          </button>
          {error && <div className="login-error">{error}</div>}
        </form>
      </div>
    </div>
  );
}

export default Login;
