const fileInput = document.getElementById("file-input");
const fileCountText = document.getElementById("file-count");
const qualitySlider = document.getElementById("quality-range");
const qualityValue = document.getElementById("quality-value");
const resizeSlider = document.getElementById("resize-range");
const resizeValue = document.getElementById("resize-value");

fileInput.addEventListener("change", () => {
    const count = fileInput.files.length;
    fileCountText.textContent = count === 0
        ? "Nenhuma imagem selecionada"
        : `${count} imagem${count > 1 ? "s" : ""} selecionada${count > 1 ? "s" : ""}`;
});

qualitySlider.addEventListener("input", () => {
    qualityValue.textContent = qualitySlider.value;
});

resizeSlider.addEventListener("input", () => {
    resizeValue.textContent = resizeSlider.value;
});

document.getElementById("upload-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const statusDiv = document.getElementById("status");
    statusDiv.innerHTML = "⏳ Compactando...";

    const formData = new FormData();
    const files = fileInput.files;

    for (let file of files) {
        formData.append("files", file);
    }

    formData.append("quality", qualitySlider.value);
    formData.append("resize", resizeSlider.value);

    const response = await fetch("/upload/", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        statusDiv.innerHTML = "❌ Erro ao compactar as imagens.";
        return;
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get("content-disposition");
    const filename = contentDisposition
        ? contentDisposition.split("filename=")[1].replace(/["']/g, "")
        : "imagens_compactadas.zip";

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    statusDiv.innerHTML = `✅ Download iniciado: ${filename}`;
});
