import '../styles/Sidebar.css'
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
    return (
        <div className="sidebar">
            {/* Logo + Branding */}
            <div className="logo-section">
                <div className="logo">
                    <svg viewBox="0 0 100 100" fill="white">
                        <path d="M15 85 C15 85, 15 60, 15 50 C15 30, 25 20, 35 20 C35 20, 35 50, 35 70 L35 85 Z" />
                        <path d="M40 85 C40 85, 40 45, 40 35 C40 15, 50 5, 60 5 C60 5, 60 35, 60 55 L60 85 Z" />
                        <path d="M65 85 C65 85, 65 60, 65 50 C65 30, 75 20, 85 20 C85 20, 85 50, 85 70 L85 85 Z" />
                        <path d="M25 20 C20 15, 30 10, 35 15 C40 10, 50 15, 45 20" />
                        <path d="M50 5 C45 0, 55 -5, 60 0 C65 -5, 75 0, 70 5" />
                        <path d="M75 20 C70 15, 80 10, 85 15 C90 10, 100 15, 95 20" />
                    </svg>
                </div>
                <div className="app-name">Munch AI</div>
                <div className="app-subtitle">Smart File Organization</div>
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
                        <div className="nav-description">Set requirements & criteria</div>
                    </div>
                </NavLink>

                <NavLink to="/munch" className={({ isActive }) => `nav-button ${isActive ? "active" : ""}`}>
                    <div className="nav-icon">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div>
                        <div>Munch</div>
                        <div className="nav-description">AI analyzes & sorts files</div>
                    </div>
                </NavLink>
            </div>
        </div>
    );
}
