import React, { useState, useEffect } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  Filter, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  PlayCircle, 
  MoreHorizontal,
  FileText,
  User,
  Calendar,
  Tag
} from 'lucide-react';

const ServiceRequestsAdmin = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRequest, setExpandedRequest] = useState(null);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionData, setActionData] = useState({
    status: '',
    adminNotes: ''
  });

  // Cargar solicitudes al iniciar
  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      // Construir URL con filtros
      let url = '/api/v1/services/requests';
      if (filter !== 'all') {
        url += `?status=${filter}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Error fetching service requests');
      }
      
      const data = await response.json();
      
      // Ordenar por fecha
      let sortedData = [...data];
      if (sortBy === 'newest') {
        sortedData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } else if (sortBy === 'oldest') {
        sortedData.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      }
      
      setRequests(sortedData);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleStatusChange = async (requestId, newStatus) => {
    try {
      const response = await fetch(`/api/v1/services/requests/${requestId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          admin_notes: actionData.adminNotes
        }),
      });
      
      if (!response.ok) {
        throw new Error('Error updating service request status');
      }
      
      // Actualizar estado local
      setRequests(requests.map(req => 
        req.id === requestId 
          ? {...req, status: newStatus, admin_notes: actionData.adminNotes} 
          : req
      ));
      
      setShowActionModal(false);
      setSelectedRequest(null);
      
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleExpandToggle = (requestId) => {
    if (expandedRequest === requestId) {
      setExpandedRequest(null);
    } else {
      setExpandedRequest(requestId);
    }
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
  };

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    
    let sortedData = [...requests];
    if (newSort === 'newest') {
      sortedData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (newSort === 'oldest') {
      sortedData.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    }
    
    setRequests(sortedData);
  };

  const openActionModal = (request, initialStatus) => {
    setSelectedRequest(request);
    setActionData({
      status: initialStatus,
      adminNotes: request.admin_notes || ''
    });
    setShowActionModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setActionData({
      ...actionData,
      [name]: value
    });
  };

  // Obtener icono según el estado
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      case 'in_progress':
        return <PlayCircle className="w-5 h-5 text-purple-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  // Obtener clase de color según el estado
  const getStatusClass = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-purple-100 text-purple-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Formatear fecha ISO a formato legible
  const formatDate = (isoDate) => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Modal para acciones
  const ActionModal = () => {
    if (!showActionModal || !selectedRequest) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
          <div className="border-b px-6 py-4">
            <h3 className="text-xl font-bold text-gray-900">Update Request Status</h3>
            <p className="text-gray-600">{selectedRequest.service.name}</p>
          </div>
          
          <div className="p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Status
              </label>
              <select
                name="status"
                value={actionData.status}
                onChange={handleInputChange}
                className="w-full border rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Admin Notes
              </label>
              <textarea
                name="adminNotes"
                value={actionData.adminNotes}
                onChange={handleInputChange}
                rows="4"
                className="w-full border rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add notes about this request..."
              ></textarea>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={() => setShowActionModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleStatusChange(selectedRequest.id, actionData.status)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Update Status
              </button>
            </div>
          </div>
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
          <h1 className="text-3xl font-bold text-white">Service Requests Management</h1>
          <p className="text-blue-100 mt-2">Manage and process client service requests</p>
        </div>
      </div>
      
      {/* Contenido Principal */}
      <div className="container mx-auto px-4 py-8">
        {/* Filtros y Ordenación */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap items-center mb-4 md:mb-0">
            <div className="flex items-center mr-6 mb-2 md:mb-0">
              <Filter className="w-5 h-5 text-gray-500 mr-2" />
              <span className="text-sm font-medium text-gray-700 mr-2">Status:</span>
              <div className="relative">
                <select
                  value={filter}
                  onChange={(e) => handleFilterChange(e.target.value)}
                  className="border-gray-300 rounded-md text-sm py-1 pl-3 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="flex items-center">
            <span className="text-sm font-medium text-gray-700 mr-2">Sort by:</span>
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => handleSortChange(e.target.value)}
                className="border-gray-300 rounded-md text-sm py-1 pl-3 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Lista de Solicitudes */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
          </div>
        ) : requests.length > 0 ? (
          <div className="space-y-4">
            {requests.map(request => (
              <div key={request.id} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Encabezado de la solicitud */}
                <div 
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                  onClick={() => handleExpandToggle(request.id)}
                >
                  <div className="flex items-center">
                    {getStatusIcon(request.status)}
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-gray-900">{request.service.name}</h3>
                      <div className="flex items-center mt-1">
                        <User className="w-4 h-4 text-gray-500 mr-1" />
                        <span className="text-sm text-gray-600 mr-4">{request.user_email}</span>
                        <Calendar className="w-4 h-4 text-gray-500 mr-1" />
                        <span className="text-sm text-gray-500">{formatDate(request.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(request.status)}`}>
                      {request.status}
                    </span>
                    {expandedRequest === request.id ? (
                      <ChevronUp className="w-5 h-5 text-gray-500 ml-4" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500 ml-4" />
                    )}
                  </div>
                </div>
                
                {/* Contenido expandido */}
                {expandedRequest === request.id && (
                  <div className="px-4 pb-4 border-t border-gray-100 pt-3">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center">
                          <FileText className="w-4 h-4 mr-1" /> Client Message
                        </h4>
                        <div className="bg-gray-50 p-3 rounded border text-sm text-gray-800">
                          {request.message || "No message provided"}
                        </div>
                      </div>
                      
                      {request.project_name && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1 flex items-center">
                            <Tag className="w-4 h-4 mr-1" /> Project
                          </h4>
                          <div className="bg-gray-50 p-3 rounded border text-sm text-gray-800">
                            {request.project_name}
                          </div>
                        </div>
                      )}
                      
                      {request.custom_fields && Object.keys(request.custom_fields).length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Custom Fields</h4>
                          <div className="bg-gray-50 p-3 rounded border">
                            <dl className="text-sm divide-y divide-gray-200">
                              {Object.entries(request.custom_fields).map(([key, value]) => (
                                <div key={key} className="py-1 first:pt-0 last:pb-0">
                                  <dt className="font-medium text-gray-700">{key}</dt>
                                  <dd className="text-gray-600 mt-1">
                                    {typeof value === 'string' ? value : JSON.stringify(value)}
                                  </dd>
                                </div>
                              ))}
                            </dl>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {request.admin_notes && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-1">Admin Notes</h4>
                        <div className="bg-blue-50 p-3 rounded border border-blue-100 text-sm text-gray-800">
                          {request.admin_notes}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex justify-end space-x-2 mt-4">
                      {request.status === 'pending' && (
                        <>
                          <button
                            onClick={() => openActionModal(request, 'approved')}
                            className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => openActionModal(request, 'cancelled')}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
                          >
                            Cancel
                          </button>
                        </>
                      )}
                      
                      {request.status === 'approved' && (
                        <button
                          onClick={() => openActionModal(request, 'in_progress')}
                          className="px-3 py-1 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700"
                        >
                          Start Work
                        </button>
                      )}
                      
                      {request.status === 'in_progress' && (
                        <button
                          onClick={() => openActionModal(request, 'completed')}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                        >
                          Mark as Completed
                        </button>
                      )}
                      
                      <button
                        onClick={() => openActionModal(request, request.status)}
                        className="px-3 py-1 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50 flex items-center"
                      >
                        <MoreHorizontal className="w-4 h-4 mr-1" /> Other Action
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No service requests found</h3>
            <p className="text-gray-600">There are no service requests matching your filters.</p>
          </div>
        )}
      </div>
      
      {/* Modal de acción */}
      <ActionModal />
    </div>
  );
};

export default ServiceRequestsAdmin;