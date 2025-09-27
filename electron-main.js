import { app, BrowserWindow, ipcMain, dialog } from 'electron'; //app controls cycle of electron to know when electron ready, quits app etc
import path from 'path'; //node built in path system to build path for differen os
import { fileURLToPath } from 'url';// allows __filename and __dirname to be used

const __filename = fileURLToPath(import.meta.url); //this becomes a string with full absolute path to THIS FILE (electron-main.js)
const __dirname = path.dirname(__filename); //__dirname is the folder path (which is Munch_ai_app)

ipcMain.handle('dialog:openFiles', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
        properties: ['openFile', 'multiSelections']
    });
    console.log(filePaths)
    return canceled ? null : filePaths; //
});


ipcMain.handle('dialog:openDirectory', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
        properties: ['openDirectory'] // only folders
    });
    return canceled ? null : filePaths[0];
});


function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'), //preload is in the root aswell
        },
    });

    win.loadURL('http://localhost:5173'); //Only use now because not in production, so quicker and allows update, no internet required
    //win.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
