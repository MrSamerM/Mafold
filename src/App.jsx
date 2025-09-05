import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ViewFolders from './pages/ViewFolders';
import AddFolders from './pages/AddFolders';
import Munch from './pages/Munch';
import './styles/App.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('view-folders');

  const renderContent = () => {
    switch (activeTab) {
      case 'view-folders':
        return <ViewFolders />;
      case 'add-folders':
        return <AddFolders />;
      case 'munch':
        return <Munch />;
      default:
        return <ViewFolders />;
    }
  };

  return (
    <div className="app">
      <Sidebar className="sidebar" activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="main-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default App;
