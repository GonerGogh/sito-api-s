  const form = document.getElementById("loginForm");
        const msg = document.getElementById("msg");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            try {
                const res = await axios.post("http://localhost:5002/login", {
                    username, password
                });

                const data = res.data;
                msg.innerHTML = `<div class="alert success">Bienvenido ${data.role}!</div>`;

                localStorage.setItem("token", data.token);
                localStorage.setItem("role", data.role);
                localStorage.setItem("matricula", username);

                // Redirigir según rol
                if (data.role === "alumno") {
                    window.location.href = "alumnos.html";
                } else if (data.role === "profesor") {
                    window.location.href = "profesor.html";
                } else if (data.role === "rh") {
                    window.location.href = "rh.html";
                } else if (data.role === "servicios") {
                    window.location.href = "servicios.html";
                }

            } catch (err) {
                let errorMessage = "Usuario o contraseña incorrectos";
                if (err.response && err.response.data && err.response.data.error) {
                    errorMessage = err.response.data.error;
                }
                msg.innerHTML = `<div class="alert danger">${errorMessage}</div>`;
            }
        });