import '../styles/ViewFolders.css';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function ViewFolders() {

    const [folders, setFolders] = useState([])

    useEffect(() => {

        const getFolders = async () => {
            const res = await axios.get('http://localhost:8000/get-folders')
            if (res.data) {
                setFolders(res.data)
            }

        };

        getFolders()
    }, [])

    return (
        <div className="view-folders-page">
            <div className="page-header">
                <h1 className="page-title">View Folders</h1>
            </div>

            <div className="content-wrapper">
                <div className="content-area-box">
                    <div className='view-folder-content'>
                        <h1 className='view-folder-headers'>All Directories</h1>
                        <div className='view-all-folders'>
                            {folders.map((folder) => (
                                <div key={folder.id} className='folder-details'>

                                    {/* <!-- Folder icon from Tabler Icons - https://tabler.io/icons/icon/folder --> */}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="yellow" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-folder">
                                        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                        <path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2" />
                                    </svg>
                                    <label>{folder.folder_name}</label>
                                    <button>Update Folder</button>
                                    <button>Delete Folder</button>

                                </div>
                            ))}

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}


