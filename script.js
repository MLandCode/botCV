document.getElementById("cv-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const cvFile = document.getElementById("cv-upload").files[0];
    const jobDescription = document.getElementById("job-description").value;

    if (!cvFile || !jobDescription) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    // Leer el archivo PDF como texto
    const reader = new FileReader();
    reader.onload = async () => {
        const cvText = reader.result;

        // Enviar datos al backend para análisis básico
        const response = await fetch("/analyze-basic", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cv: cvText, job_description: jobDescription }),
        });

        const data = await response.json();
        document.getElementById("basic-analysis").innerHTML = `<strong>Análisis básico:</strong> ${data.analysis}`;
        document.getElementById("pay-button").classList.remove("hidden");
    };

    reader.readAsText(cvFile);
});

document.getElementById("pay-button").addEventListener("click", async () => {
    // Redirigir al usuario al enlace de pago de PayPal
    const response = await fetch("/create-payment", { method: "POST" });
    const data = await response.json();
    window.location.href = data.approval_url;
});