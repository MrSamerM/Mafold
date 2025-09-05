import '../styles/AddFolders.css';
import { useState } from 'react';
import axios from 'axios';


export default function AddFolders() {

    const [folderName, setFolderName] = useState("Must add a folder");
    const [folderPath, setFolderPath] = useState("");
    const [requirements, setRequirements] = useState(["", "", "", "", "", ""]);

    const handleSelection = async () => {

        const res = await axios.get('http://localhost:8000/pick-folder')
        if (res.data.folderName) {
            setFolderName(res.data.folderName)
            setFolderPath(res.data.folderPath)
        }
    };

    const handleRequirementChange = (index, value) => {
        const newRequirements = [...requirements];
        newRequirements[index] = value;
        setRequirements(newRequirements);
    };

    const handleSave = async () => {
        if (!folderPath) return alert("Please select a folder first!");

        const cleanRequirements = requirements.filter(r => r.trim() !== "").map(r => ({ description: r }));

        const data = {
            folder_name: folderName,
            folder_path: folderPath,
            requirements: cleanRequirements
        }

        try {
            await axios.post('http://localhost:8000/save-folder', data)
            alert("Folder saved to database!");
            setFolderName("Must add a folder");
            setFolderPath("");
            setRequirements(["", "", "", "", "", ""]);

        } catch (e) {
            console.log("Error when saving", e)
            alert("Internal Error!");
        }

    };

    return (
        <div className="add-folders-page">
            <div className="page-header">
                <h1 className="page-title">Add Folders</h1>
            </div>

            <div className="content-wrapper">
                <div className="content-area-box">
                    <div className='add-folder-content'>
                        <h1 className='add-folder-headers'>Select a Folder</h1>
                        <div className='select-folder-content'>
                            {/* <!-- Folder icon from Tabler Icons - https://tabler.io/icons/icon/folder --> */}
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="yellow" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-folder">
                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                <path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2" />
                            </svg>
                            <label>{folderName}</label>
                            <button onClick={handleSelection}>Add Folder</button>
                        </div>
                    </div>

                    <div className='add-folder-content'>
                        <h1 className='add-folder-headers'>Add Requirements</h1>

                        <div className='requirement-input-group'>
                            <label htmlFor='first-requirement'>First Requirement <span className='red-star'>*</span></label>
                            <input id="first-requirement" type='text' placeholder='requirement one' value={requirements[0]} onChange={(evt) => handleRequirementChange(0, evt.target.value)} />
                        </div>
                        <div className='requirement-input-group'>
                            <label htmlFor='second-requirement'>Second Requirement</label>
                            <input id="second-requirement" type='text' placeholder='requirement two' value={requirements[1]} onChange={(evt) => handleRequirementChange(1, evt.target.value)} />
                        </div>
                        <div className='requirement-input-group'>
                            <label htmlFor='third-requirement'>Third Requirement</label>
                            <input id="third-requirement" type='text' placeholder='requirement three' value={requirements[2]} onChange={(evt) => handleRequirementChange(2, evt.target.value)} />
                        </div>
                        <div className='requirement-input-group'>
                            <label htmlFor='fourth-requirement'>Fourth Requirement</label>
                            <input id="fourth-requirement" type='text' placeholder='requirement four' value={requirements[3]} onChange={(evt) => handleRequirementChange(3, evt.target.value)} />
                        </div>
                        <div className='requirement-input-group'>
                            <label htmlFor='fifth-requirement'>Fifth Requirement</label>
                            <input id="fifth-requirement" type='text' placeholder='requirement five' value={requirements[4]} onChange={(evt) => handleRequirementChange(4, evt.target.value)} />
                        </div>
                    </div>
                    <button onClick={handleSave}>Save information</button>
                </div>
            </div>
        </div>
    );
};
