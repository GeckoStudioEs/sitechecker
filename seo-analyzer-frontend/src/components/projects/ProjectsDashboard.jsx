import React, { useState, useEffect } from 'react';
import { Search, Globe, Calendar, Tag, ChevronRight, AlertCircle, PlusCircle } from 'lucide-react';
import ProjectCreationForm from './ProjectCreationForm'; // Importamos el componente anterior

const ProjectsDashboard = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    // Función para cargar los proyectos
    const fetchProjects = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/v1/projects', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Error al cargar los proyectos');
        }
        
        const data = await response.json();
        setProjects(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProjects();
  }, []);
  
  // Para esta demo, usaremos datos de ejemplo si no tenemos proyectos
  useEffect(() => {
    if (!loading && projects.length === 0 && !error) {
      // Datos de ejemplo para la demostración
      setProjects([
        {
          id: 1,
          name: 'Mi Tienda Online',
          domain: 'mitienda.com',
          protocol: 'https',
          created_at: '2023-09-15T14:30:00Z',
          tags: ['ecommerce', 'retail'],
          site_score: 78
        },
        {
          id: 2,
          name: 'Blog Corporativo',
          domain: 'empresa.com/blog',
          protocol: 'https',
          created_at: '2023-08-22T10:15:00Z',
          tags: ['blog', 'contenido'],
          site_score: 65
        },
        {
          id: 3,
          name: 'Sitio Inmobiliario',
          domain: 'inmuebles.es',
          protocol: 'https',
          created_at: '2023-10-05T09:45:00Z',
          tags: ['inmobiliaria', 'servicios'],
          site_score: 82
        }
      ]);
    }
  }, [loading, projects, error]);

  // Filtrar proyectos basados en el término de búsqueda
  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (project.tags && project.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  // Formatear fecha
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-ES', options);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Mis Proyectos SEO</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <PlusCircle className="h-5 w-5 mr-2" />
          {showCreateForm ? 'Ocultar Formulario' : 'Nuevo Proyecto'}
        </button>
      </div>
      
      {showCreateForm && (
        <div className="mb-8">
          <ProjectCreationForm />
        </div>
      )}
      
      <div className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="Buscar proyectos por nombre, dominio o etiquetas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-800 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando proyectos...</p>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          {filteredProjects.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-gray-500">No se encontraron proyectos. Crea tu primer proyecto para comenzar.</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredProjects.map(project => (
                <li key={project.id} className="hover:bg-gray-50">
                  <a href={`/projects/${project.id}`} className="block">
                    <div className="px-6 py-4 flex items-center">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-lg font-medium text-gray-900 truncate">{project.name}</h3>
                          {project.site_score !== undefined && (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              project.site_score >= 80 ? 'bg-green-100 text-green-800' :
                              project.site_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              Score: {project.site_score}
                            </span>
                          )}
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <Globe className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                          <span>{project.protocol}://{project.domain}</span>
                        </div>
                        <div className="mt-2 flex items-center">
                          <div className="flex items-center text-sm text-gray-500">
                            <Calendar className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            <span>Creado el {formatDate(project.created_at)}</span>
                          </div>
                          
                          {project.tags && project.tags.length > 0 && (
                            <div className="ml-6 flex items-center text-sm text-gray-500">
                              <Tag className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                              <div className="flex flex-wrap gap-1">
                                {project.tags.map(tag => (
                                  <span key={tag} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      <div>
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      </div>
                    </div>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectsDashboard;