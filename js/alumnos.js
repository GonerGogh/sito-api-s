async function initDashboard() {
  const token = localStorage.getItem("token");
  const matricula = localStorage.getItem("matricula");

  if (!token || !matricula) {
    window.location.href = "login.html";
    return;
  }

  document.getElementById("userName").innerText = matricula;
  const cont = document.getElementById("calificaciones");
  cont.innerHTML = "Cargando...";

  try {
    // Petición 1: Obtener la lista de grupos
    const resGrupos = await fetch(`http://localhost:5004/alumnos/${matricula}/grupo`);
    const gruposAlumno = await resGrupos.json();

    // Petición 2: Obtener calificaciones
    const resCalificaciones = await fetch(`http://localhost:5004/alumnos/${matricula}/calificaciones`, {
      headers: { "Authorization": token }
    });
    const dataCalificaciones = await resCalificaciones.json();
    const calificacionesAlumno = dataCalificaciones.calificaciones || {};

    if (resGrupos.status === 404) {
      cont.innerHTML = "<p>No estás inscrito en ningún grupo.</p>";
      return;
    }
let html = `
  <div class="table-container">
    <div class="table-header">Calificaciones</div>
    <div class="table-subheader">
      <span><b>Matrícula:</b> ${matricula}</span>
      <span><b>Alumno:</b> ${document.getElementById("userName").innerText}</span>
    </div>
    <table class="table-custom">
      <thead>
        <tr>
          <th>No.</th>
          <th>Grupo</th>
          <th>Profesor</th>
          <th>Calificación</th>
        </tr>
      </thead>
      <tbody>
`;

gruposAlumno.forEach((grupo, index) => {
  const calificacionObj = calificacionesAlumno[grupo.nombre_grupo];
  const calificacion = calificacionObj ? calificacionObj.calificacion : "N/A";
  const profesorNombre = grupo.profesor_responsable?.nombre || "Sin asignar";
  const profesorMatricula = grupo.profesor_responsable?.matricula ? ` (${grupo.profesor_responsable.matricula})` : "";

  html += `
    <tr>
      <td>${index + 1}</td>
      <td>${grupo.nombre_grupo}</td>
      <td>${profesorNombre}${profesorMatricula}</td>
      <td>${calificacion}</td>
    </tr>
  `;
});

html += `
      </tbody>
    </table>
  </div>
`;

cont.innerHTML = html;


  } catch(err) {
    document.getElementById("calificaciones").innerHTML = `<p>Error al obtener los datos. (${err.message})</p>`;
  }

  // Eventos de navegación
  document.getElementById("linkGrupos").addEventListener("click", () => {
    document.getElementById("seccionGrupos").style.display = "block";
    document.getElementById("seccionPassword").style.display = "none";
  });

  document.getElementById("linkPassword").addEventListener("click", () => {
    document.getElementById("seccionGrupos").style.display = "none";
    document.getElementById("seccionPassword").style.display = "block";
  });

  // Cambiar contraseña
  const passwordForm = document.getElementById("passwordForm");
  passwordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nueva = document.getElementById("newPassword").value;
    try {
      const res = await fetch(`http://localhost:5004/alumnos/${matricula}/cambiar_contrasena`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nueva_contrasena: nueva })
      });
      const data = await res.json();
      if (res.ok) {
        document.getElementById("msg").innerText = data.msg;
        document.getElementById("errMsg").innerText = "";
      } else {
        document.getElementById("errMsg").innerText = data.error || "Error desconocido";
        document.getElementById("msg").innerText = "";
      }
    } catch(err) {
      document.getElementById("errMsg").innerText = `Error: ${err.message}`;
    }
  });

  // Cerrar sesión
  document.getElementById("logout").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "login.html";
  });
}

// Ejecutar al cargar
initDashboard();