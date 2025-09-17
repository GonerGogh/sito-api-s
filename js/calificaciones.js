// 🔹 Backend URLs
const PROFESORES_URL = 'http://localhost:5005';
const SERVICIOS_URL = 'http://localhost:5003';

// Tomar datos del profesor desde localStorage
const profesor = {
    matricula: localStorage.getItem('matricula'),
    role: localStorage.getItem('role'),
    token: localStorage.getItem('token')
};

if (!profesor.matricula || profesor.role !== 'profesor') {
    alert("No hay sesión de profesor válida. Redirigiendo al login...");
    window.location.href = 'login.html';
}

// Botones de navegación
const btnCalificacionesNav = document.getElementById('btnCalificaciones');
const btnContrasenaNav = document.getElementById('btnCambiarContrasena');

const seccionCalificaciones = document.getElementById('seccionCalificaciones');
const seccionContrasena = document.getElementById('seccionContrasena');

btnCalificacionesNav.addEventListener('click', () => {
    seccionCalificaciones.style.display = 'block';
    seccionContrasena.style.display = 'none';
});

btnContrasenaNav.addEventListener('click', () => {
    seccionCalificaciones.style.display = 'none';
    seccionContrasena.style.display = 'block';
});

// ------------------- Calificaciones -------------------
const grupoSelect = document.getElementById('grupoSelect');
const alumnoSelect = document.getElementById('alumnoSelect');
const calificacionInput = document.getElementById('calificacionInput');
const btnEnviar = document.getElementById('btnEnviar');
const mensajeDiv = document.getElementById('mensaje');

async function cargarGrupos() {
    try {
        const res = await fetch(`${PROFESORES_URL}/profesoresL`);
        const profesores = await res.json();
        const profData = profesores.find(p => p.matriculaP === profesor.matricula);

        if (!profData) return alert("Profesor no encontrado");

        const gruposAsignados = profData.grupos || [];
        if (gruposAsignados.length === 0) return alert("No tiene grupos asignados");

        grupoSelect.innerHTML = gruposAsignados.map(g => `<option value="${g}">${g}</option>`).join('');
        cargarAlumnos(gruposAsignados[0]);
    } catch (err) {
        console.error(err);
        alert("Error cargando grupos del profesor");
    }
}

grupoSelect.addEventListener('change', () => {
    const grupo = grupoSelect.value;
    cargarAlumnos(grupo);
});

async function cargarAlumnos(grupo) {
    try {
        const res = await fetch(`${SERVICIOS_URL}/gruposL`);
        const grupos = await res.json();
        const grupoFiltrado = grupos.find(g => g.nombre_grupo === grupo && g.profesor_responsable === profesor.matricula);

        if (!grupoFiltrado || !grupoFiltrado.alumnos.length) {
            alumnoSelect.innerHTML = '<option value="">No hay alumnos asignados</option>';
            return;
        }

        alumnoSelect.innerHTML = grupoFiltrado.alumnos.map(m => `<option value="${m}">${m}</option>`).join('');
    } catch (err) {
        console.error(err);
        alumnoSelect.innerHTML = '<option value="">Error cargando alumnos</option>';
    }
}

btnEnviar.addEventListener('click', async () => {
    const grupo = grupoSelect.value;
    const alumno = alumnoSelect.value;
    const calificacion = calificacionInput.value;
    if (!alumno || !calificacion) return alert("Seleccione alumno y calificación");

    try {
        const res = await fetch(`${PROFESORES_URL}/profesores/${profesor.matricula}/calificaciones`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${profesor.token}`
            },
            body: JSON.stringify({ matricula: alumno, grupo, calificacion })
        });

        const data = await res.json();
        if (res.status === 200 || res.status === 201) {
            mensajeDiv.textContent = data.msg;
            mensajeDiv.style.color = 'green';
            calificacionInput.value = '';
        } else {
            mensajeDiv.textContent = data.error || 'Error';
            mensajeDiv.style.color = 'red';
        }
    } catch (err) {
        console.error(err);
        mensajeDiv.textContent = 'Error enviando calificación';
        mensajeDiv.style.color = 'red';
    }
});

cargarGrupos();

// ------------------- Cambio de contraseña -------------------
const nuevaContrasenaInput = document.getElementById('nuevaContrasena');
const btnCambiar = document.getElementById('btnCambiar');
const mensajeContrasenaDiv = document.getElementById('mensajeContrasena');

btnCambiar.addEventListener('click', async () => {
    const nueva = nuevaContrasenaInput.value;
    if (!nueva) return alert("Ingrese una nueva contraseña");

    try {
        const res = await fetch(`${PROFESORES_URL}/profesores/${profesor.matricula}/cambiar_contrasena`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nueva_contrasena: nueva })
        });

        const data = await res.json();
        if (res.status === 200) {
            mensajeContrasenaDiv.textContent = data.msg;
            mensajeContrasenaDiv.style.color = 'green';
            nuevaContrasenaInput.value = '';
        } else {
            mensajeContrasenaDiv.textContent = data.error || 'Error';
            mensajeContrasenaDiv.style.color = 'red';
        }
    } catch (err) {
        console.error(err);
        mensajeContrasenaDiv.textContent = 'Error cambiando contraseña';
        mensajeContrasenaDiv.style.color = 'red';
    }
});

const btnCerrarSesion = document.getElementById('btnCerrarSesion');

btnCerrarSesion.addEventListener('click', () => {
    // Limpiar localStorage
    localStorage.clear();
    // Redirigir a login
    window.location.href = 'login.html';
});
