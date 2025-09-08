// import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ViewFolders from './pages/ViewFolders';
import EditFolders from './pages/EditFolders';
import AddFolders from './pages/AddFolders';
import Munch from './pages/Munch';
import './styles/App.css';
import { Routes, Route } from 'react-router-dom';

const App = () => {

  return (
    <div className="app">
      <Sidebar className="sidebar" />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<ViewFolders />} />
          <Route path="/add-folder" element={<AddFolders />} />
          <Route path="/munch" element={<Munch />} />
          <Route path="/edit/:id" element={<EditFolders />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
