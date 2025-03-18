import React from 'react';

const Sidebar = ({ currentModule, setCurrentModule }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'audit', label: 'Site Audit', icon: '🔍' },
    { id: 'keywords', label: 'Keywords', icon: '🔤' },
    { id: 'monitoring', label: 'Monitoring', icon: '📈' },
    { id: 'services', label: 'Services', icon: '🛠️' },
  ];

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center">
          <span className="text-2xl mr-2">🚀</span>
          <h1 className="text-xl font-bold">SEO Analyzer</h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`flex items-center w-full px-3 py-2 rounded-md text-sm ${
              currentModule === item.id
                ? 'bg-gray-900 text-white'
                : 'text-gray-300 hover:bg-gray-700'
            }`}
            onClick={() => setCurrentModule(item.id)}
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* User Menu */}
      <div className="p-4 border-t border-gray-700">
        <button className="flex items-center w-full px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded-md">
          <span className="mr-3 text-lg">⚙️</span>
          Settings
        </button>
        <button className="flex items-center w-full px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded-md">
          <span className="mr-3 text-lg">🚪</span>
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;