import React, { useState } from 'react';
import { AlertCircle, Loader2, CheckCircle } from 'lucide-react';

const ProjectCreationForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    protocol: 'https',
    tags: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      // Preparar los datos del proyecto
      const projectData = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag !== '')
      };

      // Llamada a la API de tu backend
      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}` // Asumiendo que guardas el token en localStorage
        },
        body: JSON.stringify(projectData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear el proyecto');
      }

      const result = await response.json();
      setSuccess(true);
      // Reiniciar el formulario después de éxito
      setFormData({
        name: '',
        domain: '',
        protocol: 'https',
        tags: ''
      });
      
      // Puedes redirigir al usuario a la página del proyecto o mostrar un mensaje de éxito
      console.log('Proyecto creado:', result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateDomain = (domain) => {
    const pattern = /^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
    return pattern.test(domain);
  };

  const isFormValid = formData.name && formData.domain && validateDomain(formData.domain);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Crear Nuevo Proyecto SEO</h2>
      
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md flex items-center text-green-700">
          <CheckCircle className="h-5 w-5 mr-2" />
          <span>¡Proyecto creado con éxito!</span>
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Proyecto
          </label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Mi Proyecto SEO"
          />
          <p className="mt-1 text-sm text-gray-500">Un nombre descriptivo para identificar tu proyecto</p>
        </div>
        
        <div className="mb-4">
          <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-1">
            Dominio
          </label>
          <div className="flex">
            <select
              name="protocol"
              value={formData.protocol}
              onChange={handleChange}
              className="px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="https">https://</option>
              <option value="http">http://</option>
            </select>
            <input
              id="domain"
              name="domain"
              type="text"
              value={formData.domain}
              onChange={handleChange}
              required
              className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="ejemplo.com"
            />
          </div>
          {formData.domain && !validateDomain(formData.domain) && (
            <p className="mt-1 text-sm text-red-600">Formato de dominio inválido</p>
          )}
          <p className="mt-1 text-sm text-gray-500">Introduce el dominio sin 'www' ni rutas adicionales</p>
        </div>
        
        <div className="mb-6">
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
            Etiquetas (opcional)
          </label>
          <input
            id="tags"
            name="tags"
            type="text"
            value={formData.tags}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="ecommerce, blog, marketing"
          />
          <p className="mt-1 text-sm text-gray-500">Separa las etiquetas con comas</p>
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!isFormValid || loading}
            className={`flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isFormValid && !loading ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-400 cursor-not-allowed'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin mr-2 h-4 w-4" />
                Creando...
              </>
            ) : 'Crear Proyecto'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProjectCreationForm;