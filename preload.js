/**
 * NBACore Desktop — Preload Script
 * 安全地暴露 API 给渲染进程
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('nbaAPI', {
  getApiUrl: () => ipcRenderer.invoke('get-api-url'),
  getServerStatus: () => ipcRenderer.invoke('get-server-status'),
  restartServer: () => ipcRenderer.invoke('restart-server'),
  onServerRestarted: (callback) => {
    ipcRenderer.on('server-restarted', (event, data) => callback(data));
  },
});
