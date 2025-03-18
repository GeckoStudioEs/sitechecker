import React, { useState, useEffect } from 'react';
import { ArrowRight, Check, Award, Tag } from 'lucide-react';

const ServiceCatalog = () => {
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [services, setServices] = useState([]);
  const [featuredServices, setFeaturedServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [requestData, setRequestData] = useState({
    message: '',
    projectId: '',
    customFields: {}
  });
  const [projects, setProjects] = useState([]);

  // Cargar categorías al iniciar
  useEffect(() => {
    fetchCategories();
    fetchFeaturedServices();
    fetchUserProjects();
  }, []);

  // Cargar servicios cuando cambia la categoría activa
  useEffect(() => {
    if (activeCategory) {
      fetchServicesByCategory(activeCategory.slug);
    }
  }, [activeCategory]);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/services/categories');
      if (!response.ok) {
        throw new Error('Error fetching categories');
      }
      const data = await response.json();
      setCategories(data);
      
      // Establecer la primera categoría como activa si no hay ninguna
      if (data.length > 0 && !activeCategory) {
        setActiveCategory(data[0]);
      }
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchFeaturedServices = async () => {
    try {
      const response = await fetch('/api/v1/services/featured');
      if (!response.ok) {
        throw new Error('Error fetching featured services');
      }
      const data = await response.json();
      setFeaturedServices(data);
    } catch (err) {
      console.error('Error loading featured services:', err);
    }
  };

  const fetchServicesByCategory = async (categorySlug) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/services/categories/${categorySlug}/services`);
      if (!response.ok) {
        throw new Error(`Error fetching services for category: ${categorySlug}`);
      }
      const data = await response.json();
      setServices(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchUserProjects = async () => {
    try {
      const response = await fetch('/api/v1/projects');
      if (response.ok) {
        const data = await response.json();
        setProjects(data.items || []);
      }
    } catch (err) {
      console.error('Error loading user projects:', err);
    }
  };

  const handleCategoryClick = (category) => {
    setActiveCategory(category);
  };

  const handleRequestService = (service) => {
    setSelectedService(service);
    setShowRequestForm(true);
    // Reiniciar el formulario
    setRequestData({
      message: '',
      projectId: '',
      customFields: {}
    });
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/v1/services/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_id: selectedService.id,
          project_id: requestData.projectId || null,
          message: requestData.message,
          custom_fields: requestData.customFields
        }),
      });
      
      if (!response.ok) {
        throw new Error('Error submitting service request');
      }
      
      // Éxito
      alert('Your service request has been submitted successfully!');
      setShowRequestForm(false);
      setSelectedService(null);
      
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRequestData({
      ...requestData,
      [name]: value
    });
  };

  const handleCustomFieldChange = (e) => {
    const { name, value } = e.target;
    setRequestData({
      ...requestData,
      customFields: {
        ...requestData.customFields,
        [name]: value
      }
    });
  };

  // Componente para mostrar una tarjeta de servicio
  const ServiceCard = ({ service, featured = false }) => (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden border ${featured ? 'border-yellow-400' : 'border-gray-200'}`}>
      {featured && (
        <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 flex items-center justify-center">
          <Award className="w-4 h-4 mr-1" />
          FEATURED
        </div>
      )}
      <div className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{service.name}</h3>
        <p className="text-gray-600 mb-4">{service.description}</p>
        
        {service.benefits && service.benefits.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Benefits:</h4>
            <ul className="space-y-1">
              {service.benefits.map((benefit, index) => (
                <li key={index} className="flex items-start">
                  <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-600 text-sm">{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="flex justify-between items-center mt-6">
          <div>
            <span className="text-sm text-gray-500">Price</span>
            <p className="text-2xl font-bold text-gray-900">
              ${service.price?.toFixed(2) || "Contact us"}
              {service.price_type !== 'fixed' && service.price && (
                <span className="text-sm font-normal text-gray-500 ml-1">
                  /{service.price_type === 'hourly' ? 'hour' : service.price_type === 'per_word' ? 'word' : 'month'}
                </span>
              )}
            </p>
          </div>
          <button
            onClick={() => handleRequestService(service)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2 flex items-center transition-colors"
          >
            Request <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );

  // Modal para solicitar servicio
  const RequestServiceModal = () => {
    if (!showRequestForm || !selectedService) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
          <div className="border-b px-6 py-4">
            <h3 className="text-xl font-bold text-gray-900">Request Service</h3>
            <p className="text-gray-600">{selectedService.name}</p>
          </div>
          
          <form onSubmit={handleRequestSubmit} className="p-6">
            {/* Selector de proyecto */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project (optional)
              </label>
              <select
                name="projectId"
                value={requestData.projectId}
                onChange={handleInputChange}
                className="w-full border rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a project</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
            </div>
            
            {/* Mensaje */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              <textarea
                name="message"
                value={requestData.message}
                onChange={handleInputChange}
                rows="4"
                className="w-full border rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe your requirements..."
                required
              ></textarea>
            </div>
            
            {/* Campos personalizados según el tipo de servicio */}
            {selectedService.category_id === 1 && ( // Link Building
              <div className="mb-4 p-3 border rounded-md bg-gray-50">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Link Building Information</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Target Website
                    </label>
                    <input
                      type="text"
                      name="targetWebsite"
                      value={requestData.customFields.targetWebsite || ''}
                      onChange={handleCustomFieldChange}
                      className="w-full border rounded-md py-2 px-3 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Anchor Text
                    </label>
                    <input
                      type="text"
                      name="anchorText"
                      value={requestData.customFields.anchorText || ''}
                      onChange={handleCustomFieldChange}
                      className="w-full border rounded-md py-2 px-3 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Desired anchor text"
                    />
                  </div>
                </div>
              </div>
            )}
            
            {selectedService.category_id === 2 && ( // Keyword Research
              <div className="mb-4 p-3 border rounded-md bg-gray-50">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Keyword Research Information</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Industry/Niche
                    </label>
                    <input
                      type="text"
                      name="industry"
                      value={requestData.customFields.industry || ''}
                      onChange={handleCustomFieldChange}
                      className="w-full border rounded-md py-2 px-3 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Health, Finance, Technology"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Main Competitors
                    </label>
                    <input
                      type="text"
                      name="competitors"
                      value={requestData.customFields.competitors || ''}
                      onChange={handleCustomFieldChange}
                      className="w-full border rounded-md py-2 px-3 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="List of main competitors, separated by commas"
                    />
                  </div>
                </div>
              </div>
            )}
            
            {/* Otros campos personalizados para otros tipos de servicios */}
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={() => setShowRequestForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Submit Request
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  if (error) {
    return <div className="text-red-600 p-4">Error: {error}</div>;
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Encabezado */}
      <div className="bg-blue-700 py-8 px-4">
        <div className="container mx-auto">
          <h1 className="text-3xl font-bold text-white">SEO Services</h1>
          <p className="text-blue-100 mt-2">Boost your online presence with our professional SEO services</p>
        </div>
      </div>
      
      {/* Contenido Principal */}
      <div className="container mx-auto px-4 py-8">
        {/* Servicios Destacados */}
        {featuredServices.length > 0 && (
          <div className="mb-12">
            <div className="flex items-center mb-6">
              <Award className="w-6 h-6 text-yellow-500 mr-2" />
              <h2 className="text-2xl font-bold text-gray-900">Featured Services</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredServices.map(service => (
                <ServiceCard key={service.id} service={service} featured={true} />
              ))}
            </div>
          </div>
        )}
        
        {/* Navegación por Categorías y Servicios */}
        <div className="flex flex-col md:flex-row">
          {/* Panel de categorías */}
          <div className="w-full md:w-1/4 mb-6 md:mb-0 md:mr-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Categories</h2>
            <div className="bg-white rounded-lg shadow">
              <ul className="divide-y divide-gray-200">
                {categories.map(category => (
                  <li key={category.id}>
                    <button
                      onClick={() => handleCategoryClick(category)}
                      className={`w-full text-left px-4 py-3 flex items-center hover:bg-gray-50 transition-colors ${
                        activeCategory && activeCategory.id === category.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                    >
                      <span className="text-gray-900 font-medium">{category.name}</span>
                      {category.services_count > 0 && (
                        <span className="ml-auto bg-gray-100 text-gray-700 text-xs rounded-full px-2 py-1">
                          {category.services_count}
                        </span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          {/* Listado de servicios */}
          <div className="w-full md:w-3/4">
            {activeCategory && (
              <>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{activeCategory.name}</h2>
                    {activeCategory.description && (
                      <p className="text-gray-600 mt-1">{activeCategory.description}</p>
                    )}
                  </div>
                  <Tag className="w-6 h-6 text-blue-600" />
                </div>
                
                {loading ? (
                  <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
                  </div>
                ) : services.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {services.map(service => (
                      <ServiceCard key={service.id} service={service} />
                    ))}
                  </div>
                ) : (
                  <div className="bg-white rounded-lg shadow p-6 text-center">
                    <p className="text-gray-600">No services available in this category.</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Modal de solicitud de servicio */}
      <RequestServiceModal />
    </div>
  );
};

export default ServiceCatalog;