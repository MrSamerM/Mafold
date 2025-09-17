import '../styles/Munch.css';
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid'
import axios from 'axios';

export default function Munch() {

    const [files, setFiles] = useState([])



    const onDrop = useCallback(acceptedFiles => {

        const withIds = acceptedFiles.map(f => ({ id: uuidv4(), file: f }))
        setFiles(prev => [...prev, ...withIds])
        console.log(acceptedFiles)

    }, [])

    const removeFile = (id) => {
        setFiles(prev => prev.filter(f => f.id !== id))
    }

    const handleFile = async () => {
        for (const [index, f] of files.entries()) {
            const formData = new FormData();           // new FormData for each file
            formData.append('file', f.file);           // append the actual file
            formData.append('uuid', f.id);             // append the UUID

            try {
                await axios.post('http://localhost:8000/manage-file/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                console.log(`Uploaded file ${f.file.name} with UUID ${f.id} successfully`);
                setFiles(prev => prev.filter(file => file.id !== f.id));

            } catch (e) {
                console.error('Error uploading file', f.file.name, e);
            }
        }
    };


    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })


    return (
        <div className="munch-page">
            <div className="page-header">
                <h1 className="page-title">Manage Files</h1>
            </div>

            <div className="content-wrapper">
                <div className="content-area-box" {...getRootProps()}>
                    <h1 className='select-files-header'>Select Files</h1>
                    <input {...getInputProps()} />
                    {
                        isDragActive ?
                            <p>Drop the files here ...</p> :
                            files.length == 0 ? <p>Drag 'n' drop some files here, or click to select files</p> :
                                files.map(({ id, file }) => (
                                    <div key={id} className='file-details'>

                                        {/* <!-- Folder icon from Tabler Icons - https://tabler.io/icons/icon/folder --> */}
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="yellow" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-folder">
                                            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                            <path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2" />
                                        </svg>
                                        <label>{file.name}</label>
                                        <button onClick={(e) => {
                                            e.stopPropagation();
                                            removeFile(id);
                                        }}>
                                            Delete Folder
                                        </button>
                                    </div>
                                ))
                    }
                    <button onClick={(e) => {
                        e.stopPropagation();
                        handleFile();
                    }}>
                        Save information
                    </button>
                </div>
            </div>
        </div>
    );
};
