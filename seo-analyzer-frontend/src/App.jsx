import React, { useState } from 'react';
import './App.css';
import ServicesModule from './components/services/ServicesModule';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';

function App() {
  const [currentModule, setCurrentModule] = useState('services');

  // Function to render the appropriate module based on the current selection
  const renderModule = () => {
    switch (currentModule) {
      case 'services':
        return <ServicesModule />;
      case 'dashboard':
        return <div className="p-4">Dashboard Module (Not Implemented)</div>;
      case 'audit':
        return <div className="p-4">Audit Module (Not Implemented)</div>;
      case 'keywords':
        return <div className="p-4">Keywords Module (Not Implemented)</div>;
      case 'monitoring':
        return <div className="p-4">Monitoring Module (Not Implemented)</div>;
      default:
        return <ServicesModule />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar currentModule={currentModule} setCurrentModule={setCurrentModule} />
      
      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-4">
          {renderModule()}
        </main>
      </div>
    </div>
  );
}

export default App;