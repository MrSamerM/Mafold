import '../styles/Sidebar.css'
import { NavLink } from 'react-router-dom';
import MaFolder from '../assets/MaFolder2.png'

export default function Sidebar() {
    return (
        <div className="sidebar">
            <div className="logo-section">
                <div className="logo">
                    <img src={MaFolder} />
                </div>
                <div className="app-name">MaFolder</div>
            </div>

            {/* Navigation */}
            <div className="nav-section">
                <div className="nav-title">Organization</div>

                <NavLink to="/" end className={({ isActive }) => `nav-button ${isActive ? "active" : ""}`}>
                    <div className="nav-icon">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M10 4H4c-1.11 0-2 .89-2 2v6c0 1.11.89 2 2 2h6c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm10 0h-6c-1.11 0-2 .89-2 2v6c0 1.11.89 2 2 2h6c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zM10 14H4c-1.11 0-2 .89-2 2v6c0 1.11.89 2 2 2h6c1.11 0 2-.89 2-2v-6c0-1.11-.89-2-2-2zm10 0h-6c-1.11 0-2 .89-2 2v6c0 1.11.89 2 2 2h6c1.11 0 2-.89 2-2v-6c0-1.11-.89-2-2-2z" />
                        </svg>
                    </div>
                    <div>
                        <div>View Folders</div>
                        <div className="nav-description">Browse your organized folders</div>
                    </div>
                </NavLink>

                <NavLink to="/add-folder" className={({ isActive }) => `nav-button ${isActive ? "active" : ""}`}>
                    <div className="nav-icon">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                        </svg>
                    </div>
                    <div>
                        <div>Add Folders</div>
                        <div className="nav-description">Set requirements</div>
                    </div>
                </NavLink>

                <NavLink to="/munch" className={({ isActive }) => `nav-button ${isActive ? "active" : ""}`}>
                    <div className="nav-icon">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div>
                        <div>Manage</div>
                        <div className="nav-description">Sort Files</div>
                    </div>
                </NavLink>
            </div>
        </div>
    );
}
