const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    selectFilePath: () => ipcRenderer.invoke('dialog:openFiles'), //To access file path
    selectDirectoryPath: () => ipcRenderer.invoke('dialog:openDirectory'), //To access folder paths
});
