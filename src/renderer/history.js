export function mostrarHistorialFosiles() {
    const historial = JSON.parse(localStorage.getItem('historial_fosiles')) || [];
    const container = document.getElementById('historialContainer');

    if (!container) return;

    if (historial.length === 0) {
        container.innerHTML = "<p class='text-gray-400'>No hay clasificaciones guardadas aún.</p>";
    } else {
        historial.forEach(item => {
            const entry = document.createElement('div');
            entry.className = "p-4 bg-gray-800 rounded shadow";

            // Obtener las 4 probabilidades más altas
            let topProbHTML = '';
            if (item.all_probabilities) {
                const top4 = Object.entries(item.all_probabilities)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4);

                topProbHTML = `
                    <div class="mt-2">
                        <p class="font-semibold">Top 4 Predicciones:</p>
                        <ul class="list-disc list-inside text-sm text-gray-300">
                            ${top4.map(([label, prob]) => 
                                `<li>${label}: ${(prob).toFixed(2)}%</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            entry.innerHTML = `
                <p><strong>Fecha:</strong> ${item.timestamp}</p>
                <p><strong>Predicción Principal:</strong> ${item.prediction}</p>
                <p><strong>Confianza:</strong> ${item.confidence}%</p>
                <p><strong>Imagen:</strong></p>
                <img src="${item.image}" alt="Imagen del fósil" class="w-32 h-auto mt-2 rounded border border-gray-600" />
                ${topProbHTML}
            `;
            container.appendChild(entry);
        });
    }
}
