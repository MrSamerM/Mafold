import '../styles/Munch.css';
import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

export default function Munch() {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        console.log(files)
    }, [files])

    const removeFile = (id) => {
        setFiles(prev => prev.filter(f => f.id !== id));
    };

    // Handle sending files to backend
    const handleFile = async () => {
        for (const f of files) {
            const data = {
                uuid: f.id,
                name: f.file.name,
                path: f.fullPath
            };

            try {
                await axios.post('http://localhost:8000/manage-file/', data);
                console.log(`Sent metadata for ${f.file.name} with UUID ${f.id}`);
                setFiles(prev => prev.filter(file => file.id !== f.id));
            } catch (e) {
                console.error('Error sending metadata for', f.file.name, e);
            }
        }
    };

    const handleSelectFiles = async () => {
        if (!window.electron?.selectFilePath) return;

        const paths = await window.electron.selectFilePath(); // array of selected file paths
        if (!paths || paths.length === 0) return;

        const fileObjects = paths.map(p => ({
            id: uuidv4(),
            file: { name: p.split(/[\\/]/).pop() }, // get filename
            fullPath: p.replace(/\\/g, '/')
        }));

        setFiles(prev => [...prev, ...fileObjects]); // append all selected files
    };

    const handleAreaClick = async (e) => {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            return;
        }
        await handleSelectFiles();
    };

    return (
        <div className="munch-page">
            <div className="page-header">
                <h1 className="page-title">Manage Files</h1>
            </div>

            <div className="content-wrapper">
                <div className="content-area-box" onClick={handleAreaClick}>
                    <h1 className='select-files-header'>Select Files</h1>
                    {files.length === 0 ?
                        <p>Click white box to select files</p>
                        :
                        files.map(({ id, file }) => (
                            <div key={id} className='file-details'>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="yellow" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="icon icon-tabler icon-tabler-folder">
                                    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                    <path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2" />
                                </svg>
                                <label>{file.name}</label>
                                <button onClick={(e) => { e.stopPropagation(); removeFile(id); }}>
                                    Delete
                                </button>
                            </div>
                        ))}

                    <button onClick={(e) => { e.stopPropagation(); handleFile(); }}>
                        Manage
                    </button>
                </div>
            </div>
        </div>
    );
};
