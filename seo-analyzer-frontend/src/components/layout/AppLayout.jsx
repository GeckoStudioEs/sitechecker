import React, { useState } from 'react';
import { 
  BarChart3, Search, Gauge, KeyRound, Bell, Settings, 
  Menu, X, LogOut, User, Home, PieChart, Tags, FileText, Briefcase 
} from 'lucide-react';

const AppLayout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Barra superior */}
      <header className="bg-white shadow-sm z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <button
                type="button"
                className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 md:hidden"
                onClick={toggleSidebar}
              >
                <span className="sr-only">Abrir menú lateral</span>
                <Menu className="h-6 w-6" />
              </button>
              <div className="flex-shrink-0 flex items-center">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">SEO Analyzer</span>
              </div>
            </div>
            <div className="flex items-center">
              <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500">
                <span className="sr-only">Ver notificaciones</span>
                <Bell className="h-6 w-6" />
              </button>
              <div className="ml-3 relative">
                <div>
                  <button className="max-w-xs bg-gray-800 rounded-full flex items-center text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                    <span className="sr-only">Abrir menú de usuario</span>
                    <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white">
                      <User className="h-5 w-5" />
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="md:flex">
        {/* Menú lateral para móviles */}
        <div className={`fixed inset-0 flex z-40 md:hidden ${isSidebarOpen ? '' : 'hidden'}`}>
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={toggleSidebar}></div>
          <div className="relative flex-1 flex flex-col max-w-xs w-full pt-5 pb-4 bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={toggleSidebar}
              >
                <span className="sr-only">Cerrar menú lateral</span>
                <X className="h-6 w-6 text-white" />
              </button>
            </div>
            <div className="flex-shrink-0 flex items-center px-4">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">SEO Analyzer</span>
            </div>
            <div className="mt-5 flex-1 h-0 overflow-y-auto">
              <nav className="px-2 space-y-1">
                <NavItem href="/dashboard" icon={<Home />} text="Dashboard" active={true} />
                <NavItem href="/projects" icon={<PieChart />} text="Proyectos" />
                <NavItem href="/audit" icon={<Search />} text="Auditoría" />
                <NavItem href="/keywords" icon={<Tags />} text="Keywords" />
                <NavItem href="/monitor" icon={<Gauge />} text="Monitoreo" />
                <NavItem href="/services" icon={<Briefcase />} text="Servicios" />
                <NavItem href="/reports" icon={<FileText />} text="Informes" />
                <NavItem href="/settings" icon={<Settings />} text="Configuración" />
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
              <button className="flex-shrink-0 group block">
                <div className="flex items-center">
                  <div className="ml-3">
                    <p className="text-base font-medium text-gray-700 group-hover:text-gray-900">Usuario Demo</p>
                    <p className="text-sm font-medium text-gray-500 group-hover:text-gray-700">Cerrar sesión</p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Menú lateral para escritorio */}
        <div className="hidden md:flex md:flex-shrink-0">
          <div className="flex flex-col w-64">
            <div className="flex flex-col h-0 flex-1">
              <div className="flex items-center h-16 flex-shrink-0 px-4 bg-white border-r border-gray-200">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">SEO Analyzer</span>
              </div>
              <div className="flex-1 flex flex-col overflow-y-auto border-r border-gray-200 bg-white">
                <nav className="flex-1 px-2 py-4 bg-white space-y-1">
                  <NavItem href="/dashboard" icon={<Home />} text="Dashboard" />
                  <NavItem href="/projects" icon={<PieChart />} text="Proyectos" active={true} />
                  <NavItem href="/audit" icon={<Search />} text="Auditoría" />
                  <NavItem href="/keywords" icon={<Tags />} text="Keywords" />
                  <NavItem href="/monitor" icon={<Gauge />} text="Monitoreo" />
                  <NavItem href="/services" icon={<Briefcase />} text="Servicios" />
                  <NavItem href="/reports" icon={<FileText />} text="Informes" />
                  <NavItem href="/settings" icon={<Settings />} text="Configuración" />
                </nav>
              </div>
            </div>
          </div>
        </div>
        
        {/* Contenido principal */}
        <div className="flex flex-col w-0 flex-1 overflow-hidden">
          <main className="flex-1 relative overflow-y-auto focus:outline-none">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};

// Componente para ítems de navegación
const NavItem = ({ href, icon, text, active = false }) => {
  return (
    <a
      href={href}
      className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
        active
          ? 'bg-blue-100 text-blue-900'
          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
      }`}
    >
      <div className={`mr-3 h-6 w-6 ${active ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'}`}>
        {icon}
      </div>
      {text}
    </a>
  );
};

export default AppLayout;