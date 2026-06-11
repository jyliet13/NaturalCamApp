// Importa los módulos necesarios de Electron
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const appRoot = path.join(__dirname, '..');
let pythonProcess = null;

// Función para crear la ventana principal de la aplicación
const createWindow = () => {
  // Crea una nueva ventana de navegador con dimensiones y configuraciones específicas
  const mainWindow = new BrowserWindow({
    width: 1440, // Ancho de la ventana
    height: 900, // Alto de la ventana
    resizable: true, // Evita que el usuario pueda cambiar el tamaño de la ventana (Nota: tu comentario dice 'true' pero el valor original es 'false')

    webPreferences: {
      nodeIntegration: true, // Habilita la integración de Node.js en la ventana web (permite usar require en index.html)
      contextIsolation: false, // Deshabilita el aislamiento de contexto (para simplificar el acceso a Node.js desde el renderer)
    },

    icon: path.join(appRoot, 'pages', 'assets', 'ICon.ico'),
    // Configuración para una ventana sin marco (útil para diseños personalizados de barra de título)
    // frame: false, // Descomenta si quieres crear tu propia barra de título en HTML/CSS
  });

  // Carga el archivo HTML de la interfaz de usuario de la aplicación
  // Asegúrate de que 'index.html' está en la misma carpeta que 'main.js'
  mainWindow.loadFile(path.join(appRoot, 'public', 'index.html'));

  // Asegúrate de que el proceso de Python se termine cuando la ventana se cierre
  mainWindow.on('closed', () => {
    if (pythonProcess) {
      console.log('Terminando proceso de Python...');
      try {
        if (process.platform === 'win32' && pythonProcess.pid) {
          // En Windows, usa taskkill para terminar forzosamente sin prompts
          require('child_process').exec(`taskkill /PID ${pythonProcess.pid} /F /T`, (err) => {
            if (err) console.log('Error terminando proceso:', err);
          });
        } else {
          pythonProcess.kill('SIGTERM');
        }
      } catch (err) {
        console.error('Error al terminar proceso Python:', err);
      }
      pythonProcess = null; // Limpia la referencia
    }
  });

  // *******************************************************************
  // *** CRÍTICO PARA LA DEPURACIÓN: DESCOMENTA LA SIGUIENTE LÍNEA ***
  // *** Asegúrate de que no haya un '//' delante de ella.         ***
  // *******************************************************************
   mainWindow.webContents.openDevTools(); // ¡Esta línea debe estar activa para que aparezcan las DevTools!
};

// Función para iniciar el servidor de la API de Python
const startPythonAPI = () => {
  // La ruta a tu script de Python. Asumimos que 'Api.py' está en la misma carpeta que 'main.js'.
  const pythonScriptPath = path.join(__dirname, 'backend', 'Api.py');
  let pythonExecutable = 'python';
  if (process.platform === 'win32') {
    const venvPythonPath = path.join(appRoot, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPythonPath)) {
      pythonExecutable = venvPythonPath;
    }
  }

  console.log(`Intentando iniciar la API de Python: ${pythonExecutable} ${pythonScriptPath}`);

  // Inicia el proceso de Python. El 'cwd' (current working directory)
  // asegura que Python se ejecute desde la carpeta de tu aplicación.
  const spawnOptions = {
    cwd: path.join(__dirname, 'backend'),
    stdio: 'pipe', // Captura stdout/stderr pero no muestra ventana
    detached: false,
  };

  // En Windows, usa creationflags para evitar mostrar ventana de consola
  if (process.platform === 'win32') {
    spawnOptions.windowsHide = true;
  }

  pythonProcess = spawn(pythonExecutable, [pythonScriptPath], spawnOptions);

  // Escucha la salida estándar del proceso de Python (útil para logs)
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data.toString()}`);
  });

  // Escucha los errores del proceso de Python (crucial para depuración)
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data.toString()}`);
  });

  // Maneja el evento de cierre del proceso de Python
  pythonProcess.on('close', (code) => {
    console.log(`Proceso de Python cerrado con código: ${code}`);
    pythonProcess = null; // Limpia la referencia cuando el proceso termina
  });

  // Maneja cualquier error que ocurra al intentar iniciar el proceso
  pythonProcess.on('error', (err) => {
    console.error('Error al iniciar el proceso de Python:', err);
    // Puedes mostrar un mensaje al usuario aquí si el error es crítico
  });
};

// Este método será llamado cuando Electron haya terminado de inicializarse
// y esté listo para crear ventanas de navegador.
// Algunas APIs solo pueden ser usadas después de que este evento ocurra.
app.whenReady().then(() => {
  startPythonAPI(); // Inicia la API de Python primero
  createWindow(); // Luego crea la ventana principal

  // Asegura que una ventana se abra si la aplicación se activa sin ventanas abiertas (solo macOS)
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});


// Cierra la aplicación cuando todas las ventanas están cerradas, excepto en macOS.
// En macOS, es común que las aplicaciones y su barra de menú permanezcan activas
// hasta que el usuario cierra explícitamente con Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // Si el proceso de Python aún está activo, termínalo antes de salir.
    if (pythonProcess) {
      console.log('Terminando proceso de Python antes de salir de la aplicación...');
      try {
        if (process.platform === 'win32' && pythonProcess.pid) {
          // En Windows, usa taskkill para terminar forzosamente sin prompts
          require('child_process').execSync(`taskkill /PID ${pythonProcess.pid} /F /T`, { stdio: 'ignore' });
        } else {
          pythonProcess.kill('SIGTERM');
        }
      } catch (err) {
        console.log('Error al terminar proceso Python:', err.message);
      }
      pythonProcess = null;
    }
    app.quit(); // Cierra la aplicación si no estamos en macOS
  }
});
