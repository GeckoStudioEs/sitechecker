import React, { useState, useEffect } from 'react';

const ServiceRequestForm = ({ serviceId = 5, onSubmit = () => {}, onCancel = () => {} }) => {
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    message: '',
    projectId: '',
    customFields: {}
  });
  const [projects, setProjects] = useState([]);
  
  // Fetch service details and user projects
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // This would be a real API call in production
        // Simulate service data
        const serviceData = {
          id: serviceId,
          name: 'Keyword Research',
          description: 'Complete keyword research for your website',
          price: 149,
          price_type: 'fixed',
          category: {
            id: 2,
            name: 'Keyword Research'
          }
        };
        
        // Simulate projects data
        const projectsData = [
          { id: 1, name: 'My Blog' },
          { id: 2, name: 'E-commerce Store' },
          { id: 3, name: 'Corporate Website' }
        ];
        
        setService(serviceData);
        setProjects(projectsData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };
    
    fetchData();
  }, [serviceId]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // In a real app, this would make an API call
    const requestData = {
      service_id: serviceId,
      project_id: formData.projectId ? parseInt(formData.projectId) : null,
      message: formData.message,
      custom_fields: formData.customFields
    };
    
    onSubmit(requestData);
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Request Service: {service?.name}</h2>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Service Information</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-700 mb-2">{service?.description}</p>
          <p className="font-medium">
            Category: <span className="text-gray-700">{service?.category?.name}</span>
          </p>
          <p className="font-medium">
            Price: <span className="text-gray-700">
              {service?.price_type === 'fixed' ? `$${service?.price}` : 
               service?.price_type === 'hourly' ? `$${service?.price}/hour` :
               service?.price_type === 'monthly' ? `$${service?.price}/month` :
               `$${service?.price}`}
            </span>
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="projectId" className="block text-sm font-medium mb-1">
            Select Project (optional)
          </label>
          <select 
            id="projectId"
            name="projectId"
            value={formData.projectId}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a project --</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label htmlFor="message" className="block text-sm font-medium mb-1">
            Message (details, requirements, questions)
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            rows={5}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Please describe your needs and requirements in detail..."
          />
        </div>
        
        <div className="flex justify-end space-x-4 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Submit Request
          </button>
        </div>
      </form>
    </div>
  );
};

export default ServiceRequestForm;