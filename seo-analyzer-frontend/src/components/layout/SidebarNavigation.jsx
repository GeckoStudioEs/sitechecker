import React, { useState } from 'react';
import { 
  Home, 
  BarChart2, 
  Search, 
  Tag, 
  Activity, 
  LineChart, 
  Lightbulb, 
  Briefcase, 
  Wrench, 
  Settings,
  ChevronDown,
  ChevronRight,
  HelpCircle,
  Info
} from 'lucide-react';

const SidebarNavigation = ({ activeSection = 'dashboard' }) => {
  const [expandedSections, setExpandedSections] = useState({
    keywordResearch: true,
    siteAudit: false
  });

  const toggleSection = (section) => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section]
    });
  };

  return (
    <div className="h-screen bg-white border-r border-gray-200 w-64 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center">
          <BarChart2 className="h-6 w-6 text-blue-500" />
          <span className="ml-2 font-semibold text-gray-800">SEO Analyzer</span>
        </div>
      </div>

      {/* Navegación */}
      <div className="flex-1 overflow-y-auto py-2">
        <ul className="space-y-1">
          {/* Proyectos */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'projects' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Home className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Projects</span>
            </a>
          </li>

          {/* Dashboard */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'dashboard' 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <BarChart2 className={`mr-3 flex-shrink-0 h-5 w-5 ${
                activeSection === 'dashboard' ? 'text-blue-500' : 'text-gray-500'
              }`} />
              <span>Dashboard</span>
            </a>
          </li>

          {/* Keyword Research */}
          <li className="px-2">
            <button 
              className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
              onClick={() => toggleSection('keywordResearch')}
            >
              <div className="flex items-center">
                <Tag className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
                <span>Keyword Research</span>
              </div>
              {expandedSections.keywordResearch ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
            
            {expandedSections.keywordResearch && (
              <ul className="mt-1 space-y-1 pl-10">
                <li>
                  <a 
                    href="#" 
                    className={`flex items-center px-3 py-1.5 text-sm font-medium rounded-md ${
                      activeSection === 'keywordResearch.general' 
                        ? 'text-blue-700' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>Keyword Research</span>
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className={`flex items-center px-3 py-1.5 text-sm font-medium rounded-md ${
                      activeSection === 'keywordResearch.rankTracker' 
                        ? 'text-blue-700' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <span>Rank Tracker</span>
                  </a>
                </li>
              </ul>
            )}
          </li>
          
          {/* Site Audit */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'siteAudit' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Search className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Site Audit</span>
            </a>
          </li>
          
          {/* Site Monitoring */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'siteMonitoring' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Activity className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Site Monitoring</span>
            </a>
          </li>
          
          {/* Rank Tracker */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'rankTracker' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <LineChart className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Rank Tracker</span>
            </a>
          </li>
          
          {/* Insights */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'insights' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Lightbulb className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Insights</span>
              <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">3</span>
            </a>
          </li>
          
          {/* Separador para los módulos adicionales */}
          <li className="mt-6 px-6">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
              More Features
            </div>
          </li>
          
          {/* Agency Solutions */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'agencySolutions' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Briefcase className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Agency Solutions</span>
              <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">new</span>
            </a>
          </li>
          
          {/* Extra Tools */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'extraTools' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Wrench className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Extra Tools</span>
            </a>
          </li>
          
          {/* Services */}
          <li className="px-2">
            <a 
              href="#" 
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                activeSection === 'services' 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Settings className="mr-3 flex-shrink-0 h-5 w-5 text-gray-500" />
              <span>Services</span>
              <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">new</span>
            </a>
          </li>
        </ul>
      </div>

      {/* Sección inferior */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center py-2">
          <div className="flex-shrink-0">
            <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">U</span>
            </div>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-700">Usuario Demo</p>
            <p className="text-xs text-gray-500">3 projects</p>
          </div>
        </div>
        
        <div className="mt-3 flex space-x-4 text-xs">
          <button className="text-gray-500 hover:text-gray-700">
            <HelpCircle className="h-4 w-4" />
          </button>
          <button className="text-gray-500 hover:text-gray-700">
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default SidebarNavigation;