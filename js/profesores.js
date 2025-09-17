// ===============================
// Función para mostrar la sección del tab seleccionado
// ===============================
function showSection(sectionId) {
  // Ocultar todas las secciones
  const sections = document.querySelectorAll('.tab-content');
  sections.forEach(section => section.classList.add('d-none'));

  // Quitar la clase 'active' de todos los tabs
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => tab.classList.remove('active'));

  // Mostrar la sección seleccionada
  const selectedSection = document.getElementById(`section-${sectionId}`);
  if (selectedSection) {
    selectedSection.classList.remove('d-none');
  }

  // Marcar el tab seleccionado como 'active'
  const selectedTab = document.getElementById(`tab-${sectionId}`);
  if (selectedTab) {
    selectedTab.classList.add('active');
  }
}

// ===============================
// Registrar profesor
// ===============================
async function registrarProfesor(event) {
  event.preventDefault();

  const nombreP = document.getElementById("nombre").value.trim();
  const matriculaP = document.getElementById("matricula").value.trim();

  try {
    const response = await fetch("http://localhost:5004/profesoresR", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombreP, matriculaP }),
    });

    if (response.ok) {
      alert("Profesor registrado exitosamente ✅");
      document.getElementById("registerForm").reset();
      loadProfesores(); // refrescar tabla
    } else {
      const error = await response.json();
      alert(`Error al registrar profesor: ${error.msg}`);
    }
  } catch (err) {
    console.error("Error al conectar con la API:", err);
    alert("No se pudo conectar con el servidor.");
  }
}

// ===============================
// Eliminar profesor
// ===============================
async function eliminarProfesor(event) {
  event.preventDefault();

  const matricula = document.getElementById("matriculaDel").value.trim();

  try {
    const response = await fetch(`http://localhost:5004/profesores?matricula=${matricula}`, {
      method: "DELETE",
    });

    if (response.ok) {
      alert("Profesor eliminado exitosamente 🗑️");
      document.getElementById("deleteForm").reset();
      loadProfesores(); // refrescar tabla
    } else {
      const error = await response.json();
      alert(`Error al eliminar profesor: ${error.msg}`);
    }
  } catch (err) {
    console.error("Error al conectar con la API:", err);
    alert("No se pudo conectar con el servidor.");
  }
}

// ===============================
// Listar profesores
// ===============================
async function loadProfesores() {
  console.log("Cargando profesores...");
  const profesoresTable = document.getElementById("profesoresTable");
  const profesoresCount = document.getElementById("profesoresCount");

  // Mensaje de carga
  profesoresTable.innerHTML = `
    <tr>
      <td colspan="2" class="text-center text-muted" style="padding: 3rem;">
        <div>
          <span style="font-size: 2rem; opacity: 0.5;">📋</span>
          <p class="mt-2">Cargando profesores...</p>
        </div>
      </td>
    </tr>
  `;

  try {
    const response = await fetch("http://localhost:5004/profesoresGet");
    console.log("Respuesta de la API: ", response);

    if (response.ok) {
      const profesores = await response.json();
      console.log("Datos recibidos de la API: ", profesores);

      if (Array.isArray(profesores) && profesores.length > 0) {
        // Renderizar filas de la tabla
        const rows = profesores.map(p => `
          <tr>
            <td>${p.nombreP}</td>
            <td>${p.matriculaP}</td>
          </tr>
        `).join("");

        profesoresTable.innerHTML = rows;
        profesoresCount.textContent = `Total de profesores registrados: ${profesores.length}`;
      } else {
        profesoresTable.innerHTML = `
          <tr>
            <td colspan="2" class="text-center text-muted">No hay profesores registrados</td>
          </tr>
        `;
        profesoresCount.textContent = "No hay registros en la base de datos.";
      }
    } else {
      profesoresTable.innerHTML = `
        <tr>
          <td colspan="2" class="text-center text-danger">Error al cargar la lista de profesores</td>
        </tr>
      `;
    }
  } catch (err) {
    console.error("Error al conectar con la API:", err);
    profesoresTable.innerHTML = `
      <tr>
        <td colspan="2" class="text-center text-danger">No se pudo conectar con el servidor</td>
      </tr>
    `;
  }
}

// ===============================
// Inicialización
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  loadProfesores();
});
