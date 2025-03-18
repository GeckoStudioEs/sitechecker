import React from 'react';
import ServiceRequestForm from './ServiceRequestForm';

const ServiceRequestModal = ({ isOpen, serviceId, onClose, onSubmit }) => {
  if (!isOpen) return null;
  
  const handleSubmit = (data) => {
    onSubmit(data);
    // Close the modal after submission
    onClose();
  };
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="relative bg-white rounded-lg shadow-lg max-w-2xl w-full mx-auto">
        <div className="absolute right-0 top-0 pr-4 pt-4">
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <span className="text-2xl">&times;</span>
          </button>
        </div>
        
        <div className="p-6">
          <ServiceRequestForm 
            serviceId={serviceId} 
            onSubmit={handleSubmit} 
            onCancel={onClose} 
          />
        </div>
      </div>
    </div>
  );
};

export default ServiceRequestModal;