
// Carga de iconos después de que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    const ammonitesIcon = document.getElementById('ammonites_icon');
    
    // Crear y pre-cargar los iconos para los botones
    const folderIcon = new Image(); 
    folderIcon.src = 'assets/folder_icon.png';
    folderIcon.alt = 'Folder Icon';
    folderIcon.className = 'inline-block mr-3';
    // Se inserta después de que el elemento exista en el DOM
    document.getElementById('imageUploadLabel').prepend(folderIcon);

    const magnifyingGlassIcon = new Image(); 
    magnifyingGlassIcon.src = 'assets/magnifying_glass_icon.png';
    magnifyingGlassIcon.alt = 'Magnifying Glass Icon';
    magnifyingGlassIcon.className = 'inline-block mr-3';
    // Se inserta después de que el elemento exista en el DOM
    document.getElementById('predictButton').prepend(magnifyingGlassIcon);
    
    const resetIcon = new Image();
    resetIcon.src = 'assets/reset_icon.png'; // Asegúrate de tener este archivo en assets/
    resetIcon.alt = 'Reset Icon';
    resetIcon.className = 'inline-block mr-3 w-8 h-8 image-rendering: pixelated;';
    // Se inserta después de que el elemento exista en el DOM
    document.getElementById('newClassificationButton').prepend(resetIcon);


    // Función para mostrar un icono una vez cargado
    const showIcon = (iconElement) => {
        iconElement.classList.remove('hidden');
    };

    // Asignar listeners para cargar y mostrar los iconos
    ammonitesIcon.onload = () => showIcon(ammonitesIcon);
    folderIcon.onload = () => showIcon(folderIcon);
    magnifyingGlassIcon.onload = () => showIcon(magnifyingGlassIcon);
    resetIcon.onload = () => showIcon(resetIcon);

    // Forzar la carga si ya están completos (ej. por caché)
    if (ammonitesIcon.complete) showIcon(ammonitesIcon);
    if (folderIcon.complete) showIcon(folderIcon);
    if (magnifyingGlassIcon.complete) showIcon(magnifyingGlassIcon);
    if (resetIcon.complete) showIcon(resetIcon);
});

// Obtener referencias a los elementos del DOM principales
const dynamicContentArea = document.getElementById('dynamicContentArea');
const errorMessage = document.getElementById('errorMessage');
const mainAppTitle = document.getElementById('mainAppTitle'); // El título principal

// Referencias a los botones del menú lateral
const menuButtonClassify = document.getElementById('menuButton-classify');
const menuButtonHistory = document.getElementById('menuButton-history');
const menuButtonExplore = document.getElementById('menuButton-explore');
const menuButtonAbout = document.getElementById('menuButton-about');

// Almacenamiento del historial (en memoria por simplicidad)
const classificationHistory = [];

// --- Funciones para gestionar el contenido dinámico ---

// Función para resetear el estado de la aplicación de clasificación
// Esta función se llama para limpiar los campos y botones relacionados con la clasificación
const resetClassificationState = () => {
    // Solo resetea los elementos si están presentes en el DOM actual
    const imageUpload = document.getElementById('imageUpload');
    const previewImage = document.getElementById('previewImage');
    const predictButton = document.getElementById('predictButton');
    const resultsDiv = document.getElementById('results');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const placeholderText = document.getElementById('placeholder-text');
    const newClassificationButton = document.getElementById('newClassificationButton');

    if (imageUpload) imageUpload.value = '';
    if (previewImage) {
        previewImage.src = '';
        previewImage.classList.add('hidden');
    }
    if (placeholderText) placeholderText.classList.remove('hidden');
    if (predictButton) {
        predictButton.classList.add('hidden');
        predictButton.disabled = true;
    }
    if (resultsDiv) resultsDiv.classList.add('hidden');
    if (loadingSpinner) loadingSpinner.style.display = 'none';
    if (errorMessage) errorMessage.classList.add('hidden');
    if (newClassificationButton) newClassificationButton.classList.add('hidden');

    selectedFile = null; // Reinicia el archivo seleccionado global
};

// Función para actualizar la visualización del historial
const updateHistoryDisplay = () => {
    const historyUl = document.getElementById('historyUl');
    if (!historyUl) return; // Asegurarse de que el elemento exista

    historyUl.innerHTML = ''; // Limpiar la lista actual
    if (classificationHistory.length === 0) {
        historyUl.innerHTML = '<li class="text-gray-400">Aún no hay clasificaciones en el historial de esta sesión.</li>';
        return;
    }

    classificationHistory.forEach((item) => {
        const li = document.createElement('li');
        li.className = 'border-b border-gray-700 py-2 text-sm md:text-base';
        // Usamos una estructura más robusta para el historial para evitar inyecciones si los datos contuvieran HTML
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'text-white block mb-1';
        timestampSpan.textContent = `**${item.timestamp}**`; // Se usará para mostrar el timestamp

        const predictionSpan = document.createElement('span');
        predictionSpan.className = 'text-lg text-fuchsia-300';
        predictionSpan.textContent = `${item.prediction.toUpperCase()}`;

        const confidenceSpan = document.createElement('span');
        confidenceSpan.className = 'text-emerald-300 ml-2';
        confidenceSpan.textContent = `(${item.confidence.toFixed(2)}%)`;

        li.appendChild(timestampSpan);
        li.appendChild(predictionSpan);
        li.appendChild(confidenceSpan);
        
        historyUl.prepend(li); // Añadir los más recientes al principio
    });
};

// Función para cargar y mostrar una sección específica
const loadAndShowSection = async (sectionFileName, menuButtonElement) => {
    errorMessage.classList.add('hidden'); // Ocultar errores al cambiar de sección
    // loadingSpinner.style.display = 'none'; // Ocultar spinner si estaba activo
    // No ocultar el spinner aquí porque podría ser necesario en la nueva sección

    // Quitar el estilo 'active' de todos los botones del menú
    document.querySelectorAll('.sidebar-item').forEach(btn => btn.classList.remove('active'));
    // Activar el botón de menú correspondiente
    menuButtonElement.classList.add('active');

    try {
        // Cargar el contenido HTML de la sección
        const response = await fetch(`${sectionFileName}`);
        if (!response.ok) {
            throw new Error(`No se pudo cargar la sección ${sectionFileName}: ${response.statusText}`);
        }
        const htmlContent = await response.text();
        dynamicContentArea.innerHTML = htmlContent;

        // Después de cargar el contenido, necesitamos re-enlazar los eventos si es la sección de clasificación
        if (sectionFileName === 'classification_section.html') {
            // Re-obtener referencias a los elementos del DOM que se acaban de cargar
            const imageUpload = document.getElementById('imageUpload');
            const previewImage = document.getElementById('previewImage');
            const predictButton = document.getElementById('predictButton');
            const resultsDiv = document.getElementById('results');
            const predictedClassSpan = document.getElementById('predictedClass');
            const confidenceSpan = document.getElementById('confidence');
            const allProbabilitiesDiv = document.getElementById('allProbabilities');
            const placeholderText = document.getElementById('placeholder-text');
            const newClassificationButton = document.getElementById('newClassificationButton');
            const loadingSpinner = document.getElementById('loadingSpinner'); // Obtener referencia al spinner de la sección

            // Re-adjuntar listeners de eventos
            if (imageUpload) imageUpload.addEventListener('change', handleImageUploadChange);
            if (predictButton) predictButton.addEventListener('click', handlePredictClick);
            if (newClassificationButton) newClassificationButton.addEventListener('click', resetClassificationState);

            // Re-inicializar el estado de la sección de clasificación
            resetClassificationState();
            // Asegurarse de que los iconos de los botones se re-muestren
            // Estos ya se precargan en el DOMContentLoaded principal, pero si se recarga la sección, se deben volver a adjuntar.
            // La forma más robusta es que los iconos estén en el HTML de la sección si son exclusivos de ella,
            // o que la lógica de inserción de iconos se ejecute cada vez que se carga la sección.
            // Para simplificar, asumimos que los iconos ya están en el HTML de la sección o se insertan.
            
            // Volver a insertar los iconos en los botones (si no están ya en el HTML de la sección)
            const folderIcon = document.querySelector('#imageUploadLabel img');
            const magnifyingGlassIcon = document.querySelector('#predictButton img');
            const resetIcon = document.querySelector('#newClassificationButton img');

            if (folderIcon && !document.querySelector('#imageUploadLabel .inline-block.mr-3')) {
                document.getElementById('imageUploadLabel').prepend(folderIcon);
                folderIcon.classList.remove('hidden');
            }
            if (magnifyingGlassIcon && !document.querySelector('#predictButton .inline-block.mr-3')) {
                document.getElementById('predictButton').prepend(magnifyingGlassIcon);
                magnifyingGlassIcon.classList.remove('hidden');
            }
            if (resetIcon && !document.querySelector('#newClassificationButton .inline-block.mr-3')) {
                document.getElementById('newClassificationButton').prepend(resetIcon);
                resetIcon.classList.remove('hidden');
            }

        } else if (sectionFileName === 'history.html') {
            updateHistoryDisplay(); // Actualizar el historial si es la sección de historial
        }

        // Mostrar u ocultar el título principal de la app según la sección
        if (sectionFileName === 'classification_section.html') {
            mainAppTitle.classList.remove('hidden');
        } else {
            mainAppTitle.classList.add('hidden'); // El título de la sección se mostrará dentro de su propio HTML
        }

    } catch (error) {
        console.error("Error al cargar la sección:", error);
        errorMessage.textContent = `ERROR: No se pudo cargar la sección "${sectionFileName}". ${error.message}`;
        errorMessage.classList.remove('hidden');
    }
};


// --- Lógica de la Sección de Clasificación (manejadores de eventos) ---
let selectedFile = null;
const API_URL = 'http://127.0.0.1:5000/predict';

function handleImageUploadChange(event) {
    const imageUpload = document.getElementById('imageUpload');
    const previewImage = document.getElementById('previewImage');
    const predictButton = document.getElementById('predictButton');
    const resultsDiv = document.getElementById('results');
    const placeholderText = document.getElementById('placeholder-text');
    const newClassificationButton = document.getElementById('newClassificationButton');

    selectedFile = event.target.files[0];
    if (selectedFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (previewImage) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
            }
            if (placeholderText) placeholderText.classList.add('hidden');
            if (predictButton) {
                predictButton.classList.remove('hidden');
                predictButton.disabled = false;
            }
            if (resultsDiv) resultsDiv.classList.add('hidden');
            if (errorMessage) errorMessage.classList.add('hidden');
            if (newClassificationButton) newClassificationButton.classList.add('hidden');
        };
        reader.readAsDataURL(selectedFile);
    } else {
        resetClassificationState();
    }
}

async function handlePredictClick() {
    const predictButton = document.getElementById('predictButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsDiv = document.getElementById('results');
    const predictedClassSpan = document.getElementById('predictedClass');
    const confidenceSpan = document.getElementById('confidence');
    const allProbabilitiesDiv = document.getElementById('allProbabilities');
    const newClassificationButton = document.getElementById('newClassificationButton');

    if (!selectedFile) {
        errorMessage.textContent = "¡ERROR! Por favor, selecciona una imagen primero.";
        errorMessage.classList.remove('hidden');
        return;
    }

    if (loadingSpinner) loadingSpinner.style.display = 'block';
    if (predictButton) predictButton.disabled = true;
    if (newClassificationButton) newClassificationButton.disabled = true;
    if (resultsDiv) resultsDiv.classList.add('hidden');
    if (errorMessage) errorMessage.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorDetails = "Error desconocido.";
            try {
                const errorJson = await response.json();
                if (errorJson.error) {
                    errorDetails = errorJson.error;
                }
            } catch (parseError) {
                errorDetails = await response.text();
            }
            throw new Error(`Error en la API (${response.status}): ${errorDetails}`);
        }

        const data = await response.json();
        
        if (predictedClassSpan) predictedClassSpan.innerHTML = `CLASE PREDICHA: <span style="color:#F4D03F;">${data.predicted_class.toUpperCase()}</span>`;
        if (confidenceSpan) confidenceSpan.innerHTML = `CONFIANZA: <span style="color:#B4F8C8;">${data.confidence.toFixed(2)}%</span>`;

        if (allProbabilitiesDiv) {
            allProbabilitiesDiv.innerHTML = `<h3 class="probabilities-title">═ PROBABILIDADES ═</h3>`;
            const ul = document.createElement('ul');
            ul.classList.add('list-none', 'p-0', 'm-0');
            
            if (data.all_predictions) {
                // Ordenar las probabilidades de mayor a menor
                const sortedProbabilities = Object.entries(data.all_predictions).sort(([,probA], [,probB]) => probB - probA);

                for (const [className, prob] of sortedProbabilities) {
                    const li = document.createElement('li');
                    li.classList.add('probability-item');
                    li.innerHTML = `<span>${className.toUpperCase()}: ${prob.toFixed(2)}%</span>
                                    <div class="probability-bar-container">
                                        <div class="probability-bar" style="width: ${prob}%;"></div>
                                    </div>`;
                    ul.appendChild(li);
                }
            }
            allProbabilitiesDiv.appendChild(ul);
        }

        if (resultsDiv) resultsDiv.classList.remove('hidden');
        if (newClassificationButton) newClassificationButton.classList.remove('hidden');
        
        // Guardar la clasificación en el historial
        const now = new Date();
        const timestamp = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
        classificationHistory.push({
            timestamp: timestamp,
            prediction: data.predicted_class, // Asegúrate de usar 'predicted_class' del backend
            confidence: data.confidence * 100 // Multiplicar por 100 para porcentaje
        });

    } catch (error) {
        console.error('Error al clasificar la imagen:', error);
        if (errorMessage) {
            errorMessage.innerHTML = `<span>!</span> ERROR: ${error.message}. Asegúrate de que el servidor de la API esté corriendo.`;
            errorMessage.classList.remove('hidden');
        }
    } finally {
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        if (predictButton) predictButton.disabled = false;
        if (newClassificationButton) newClassificationButton.disabled = false;
    }
}

// --- Event Listeners para los botones del menú lateral ---
menuButtonClassify.addEventListener('click', () => loadAndShowSection('classification_section.html', menuButtonClassify));
menuButtonHistory.addEventListener('click', () => loadAndShowSection('history.html', menuButtonHistory));
menuButtonExplore.addEventListener('click', () => loadAndShowSection('explore.html', menuButtonExplore));
menuButtonAbout.addEventListener('click', () => loadAndShowSection('about.html', menuButtonAbout));


// --- Carga inicial de la sección de clasificación ---
document.addEventListener('DOMContentLoaded', () => {
    loadAndShowSection('classification_section.html', menuButtonClassify); // Carga la sección de clasificación al inicio
});
