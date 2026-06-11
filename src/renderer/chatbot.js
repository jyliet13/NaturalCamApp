const chatWindow = document.getElementById('chatWindow');
const buttons = document.querySelectorAll('.question-btn');

// Crear audio solo si el navegador lo soporta
let audio = null;
try {
  audio = new Audio('Sound/chatpop.mp3'); // Ajusta la ruta a donde lo pongas
} catch (e) {
  console.warn("No se pudo inicializar el audio:", e);
}

const respuestas = {
  "¿Qué es un fósil?": "Un fósil es el resto o impresión conservada de un organismo que vivió en el pasado.",
  "¿Cómo se forman los fósiles?": "Los fósiles se forman cuando restos de organismos quedan enterrados y se preservan con el tiempo.",
  "¿Qué tipos de fósiles existen?": "Existen fósiles de cuerpo, fósiles de huellas, moldes, impresiones y más.",
  "¿Dónde se encuentran los fósiles?": "Se encuentran en rocas sedimentarias, a menudo en zonas que fueron antiguos lagos, mares o ríos.",
  "¿cómo subo una imagen?": "Haz clic en 'SELECCIONAR IMAGEN' y elige una desde tu dispositivo.",
  "¿cómo clasifico un fósil?": "Después de subir la imagen, haz clic en 'CLASIFICAR FÓSIL' y verás el resultado.",
  "¿puedo ver clasificaciones anteriores?": "Sí, en el menú lateral, haz clic en 'HISTORIAL DE CLASIFICACIONES'.",
  "¿qué es esta app?": "Es una herramienta para identificar fósiles mediante inteligencia artificial.",
  "¿qué es un fósil?": "Un fósil es el resto o impresión de un organismo preservado en roca.",
  "¿cómo se forma un fósil?": "Se forma cuando un organismo queda enterrado y sus restos se conservan con el tiempo.",
  "¿cuál es el fósil más antiguo?": "Algunos fósiles de microorganismos tienen más de 3.500 millones de años.",
  "¿qué fósil te gusta más?": "Me encantan los ammonites, ¡tienen forma de espiral y son muy antiguos!",
  "¿sabes de dinosaurios?": "¡Claro! Aunque esta app se enfoca más en fósiles marinos.",
  "¿eres un robot real?": "Soy Dennis, tu guía virtual. ¡Pero tengo mucha información útil!"
};

function reproducirSonido() {
  try {
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(e => console.warn("No se pudo reproducir el sonido:", e));
    }
  } catch (e) {
    console.warn("Error al reproducir sonido:", e);
  }
}

function agregarMensaje(remitente, mensaje) {
  if (!chatWindow) return; // Verificar que chatWindow exista
  const mensajeElemento = document.createElement('div');
  mensajeElemento.classList.add('chat-message', remitente === 'Tú' ? 'user' : 'bot');
  mensajeElemento.textContent = mensaje;

  chatWindow.appendChild(mensajeElemento);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  reproducirSonido();
}

function mostrarRespuestaConTyping(pregunta) {
  if (!chatWindow) return; // Verificar que chatWindow exista
  agregarMensaje("Tú", pregunta);

  const typing = document.createElement('div');
  typing.className = 'chat-message bot';
  typing.textContent = "Escribiendo...";
  chatWindow.appendChild(typing);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  setTimeout(() => {
    typing.remove();
    const respuesta = respuestas[pregunta] || "No tengo una respuesta para eso aún.";
    agregarMensaje("Bot", respuesta);
  }, 900);
}

// Solo agregar event listeners si los botones existen
if (buttons && buttons.length > 0) {
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const pregunta = button.dataset.question;
      mostrarRespuestaConTyping(pregunta);
    });
  });
}