import React from 'react';

const Navbar = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="flex items-center justify-between px-6 py-3">
        <h1 className="text-xl font-semibold text-gray-800">SEO Analyzer</h1>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="bg-gray-100 rounded-md py-2 px-4 w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center">
            <img
              src="/api/placeholder/32/32"
              alt="User Avatar"
              className="w-8 h-8 rounded-full"
            />
            <span className="ml-2 text-gray-700">John Doe</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;