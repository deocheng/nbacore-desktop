/**
 * NBACore Desktop — Electron Main Process
 * ========================================
 * 启动时自动拉起 Python 后端 API 服务器，
 * 然后创建窗口加载前端页面。
 */
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn, exec } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

// ── Prevent crashes on some Windows environments ──
app.disableHardwareAcceleration();
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-gpu-sandbox');
app.commandLine.appendSwitch('disable-software-rasterizer');
app.commandLine.appendSwitch('disable-features', 'HardwareMediaKeyHandling,MediaSessionService');

// ── Configuration ──
const API_PORT = 5577;
const API_HOST = '127.0.0.1';
const PYTHON_EXE = process.env.NBA_PYTHON || 'python';
const SERVER_SCRIPT = path.join(__dirname, 'server', 'api_server.py');

let mainWindow = null;
let serverProcess = null;
let serverReady = false;

// ── Start Python API Server ──
function startApiServer() {
  console.log('[Main] Starting API server...');
  console.log('[Main] Python:', PYTHON_EXE);
  console.log('[Main] Script:', SERVER_SCRIPT);

  // Clean proxy env
  const env = { ...process.env };
  delete env.HTTP_PROXY;
  delete env.HTTPS_PROXY;
  delete env.http_proxy;
  delete env.https_proxy;

  serverProcess = spawn(PYTHON_EXE, [SERVER_SCRIPT, '--port', String(API_PORT)], {
    cwd: __dirname,
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  serverProcess.stdout.on('data', (data) => {
    const text = data.toString().trim();
    if (text) console.log('[API]', text);
  });

  serverProcess.stderr.on('data', (data) => {
    const text = data.toString().trim();
    if (text) console.error('[API:ERR]', text);
  });

  serverProcess.on('exit', (code) => {
    console.log(`[Main] API server exited with code ${code}`);
    serverProcess = null;
  });

  serverProcess.on('error', (err) => {
    console.error('[Main] Failed to start API server:', err.message);
  });
}

// ── Wait for API server to be ready ──
function waitForServer(maxRetries = 30) {
  return new Promise((resolve, reject) => {
    let retries = 0;

    const check = () => {
      const req = http.get(
        { hostname: API_HOST, port: API_PORT, path: '/api/health', timeout: 2000 },
        (res) => {
          let data = '';
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => {
            if (res.statusCode === 200) {
              console.log('[Main] API server is ready!');
              serverReady = true;
              resolve();
            } else {
              retry();
            }
          });
        }
      );

      req.on('error', () => retry());
      req.on('timeout', () => {
        req.destroy();
        retry();
      });
    };

    const retry = () => {
      retries++;
      if (retries >= maxRetries) {
        reject(new Error(`API server not ready after ${maxRetries} retries`));
        return;
      }
      setTimeout(check, 1000);
    };

    check();
  });
}

// ── Create main window ──
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'NBACore Desktop',
    backgroundColor: '#0a0e17',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Load the renderer
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // Open DevTools in dev mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ── App lifecycle ──
app.whenReady().then(async () => {
  console.log('[Main] Electron is ready, starting API server...');
  // Start API server first
  startApiServer();

  try {
    // Wait for server to be ready
    await waitForServer();
    console.log('[Main] Server ready, creating window...');
  } catch (err) {
    console.error('[Main]', err.message);
    console.error('[Main] Starting window anyway — API may not be available');
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Kill API server
  if (serverProcess) {
    console.log('[Main] Killing API server...');
    try {
      // On Windows, use taskkill to kill the process tree
      spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
    } catch (e) {
      serverProcess.kill();
    }
    serverProcess = null;
  }

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// ── IPC handlers ──
ipcMain.handle('get-api-url', () => {
  return `http://${API_HOST}:${API_PORT}`;
});

ipcMain.handle('get-server-status', () => {
  return { ready: serverReady, port: API_PORT };
});

ipcMain.handle('restart-server', () => {
  if (serverProcess) {
    try {
      spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
    } catch (e) {
      serverProcess.kill();
    }
    serverProcess = null;
  }
  setTimeout(() => {
    startApiServer();
    waitForServer(15).then(() => {
      serverReady = true;
      if (mainWindow) {
        mainWindow.webContents.send('server-restarted', { ready: true });
      }
    }).catch(() => {
      if (mainWindow) {
        mainWindow.webContents.send('server-restarted', { ready: false });
      }
    });
  }, 2000);
  return { status: 'restarting' };
});

// ── Global error handlers ──
process.on('uncaughtException', (err) => {
  console.error('[Main] Uncaught Exception:', err.message);
  console.error(err.stack);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[Main] Unhandled Rejection:', reason);
});

app.on('gpu-process-crashed', (event) => {
  console.warn('[Main] GPU process crashed');
});

app.on('renderer-process-crashed', (event, webContents) => {
  console.warn('[Main] Renderer process crashed');
});

app.on('child-process-gone', (event, details) => {
  console.warn('[Main] Child process gone:', details.type, details.reason);
});
