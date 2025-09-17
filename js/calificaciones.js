const grupoSelect = document.getElementById('grupoSelect');
const alumnoSelect = document.getElementById('alumnoSelect');
const calificacionInput = document.getElementById('calificacionInput');
const btnEnviar = document.getElementById('btnEnviar');
const mensajeDiv = document.getElementById('mensaje');

// 🔹 Backend URLs
const PROFESORES_URL = 'http://localhost:5005';
const ALUMNADO_URL = 'http://localhost:5004';
const SERVICIOS_URL = 'http://localhost:5003';

// Tomar datos del profesor desde localStorage
const profesor = {
    matricula: localStorage.getItem('matricula'),
    role: localStorage.getItem('role'),
    token: localStorage.getItem('token')
};

if (!profesor.matricula || profesor.role !== 'profesor') {
    alert("No hay sesión de profesor válida. Redirigiendo al login...");
    window.location.href = 'login.html'; // tu página de login
}

// Cargar grupos del profesor al iniciar (supongamos que hay un endpoint que devuelve sus grupos)
async function cargarGrupos() {
    try {
        const res = await fetch(`${PROFESORES_URL}/profesoresL`);
        const profesores = await res.json();
        const profData = profesores.find(p => p.matriculaP === profesor.matricula);

        if (!profData) {
            alert("Profesor no encontrado");
            return;
        }

        const gruposAsignados = profData.grupos || [];
        if (gruposAsignados.length === 0) {
            alert("No tiene grupos asignados");
            return;
        }

        // Poblar select de grupos
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

        // Filtrar el grupo seleccionado y donde el profesor sea responsable
        const grupoFiltrado = grupos.find(g => 
            g.nombre_grupo === grupo && 
            g.profesor_responsable === profesor.matricula
        );

        // Si no hay grupo válido
        if (!grupoFiltrado || !grupoFiltrado.alumnos.length) {
            alumnoSelect.innerHTML = '<option value="">No hay alumnos asignados</option>';
            return;
        }

        // Llenar el select con las matrículas de los alumnos
        alumnoSelect.innerHTML = grupoFiltrado.alumnos
            .map(matricula => `<option value="${matricula}">${matricula}</option>`)
            .join('');

    } catch (err) {
        console.error(err);
        alumnoSelect.innerHTML = '<option value="">Error cargando alumnos</option>';
    }
}


// Enviar calificación
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
        if (res.status === 201) {
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

// Inicializar
cargarGrupos();
