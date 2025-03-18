// API module for services functionality
// src/api/services.js

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Get all service categories
export const getServiceCategories = async () => {
  try {
    const response = await fetch(`${API_URL}/services/categories`);
    if (!response.ok) throw new Error('Failed to fetch service categories');
    return await response.json();
  } catch (error) {
    console.error('Error fetching service categories:', error);
    throw error;
  }
};

// Get services by category ID
export const getServicesByCategory = async (categoryId) => {
  try {
    const response = await fetch(`${API_URL}/services/categories/${categoryId}`);
    if (!response.ok) throw new Error('Failed to fetch services for category');
    return await response.json();
  } catch (error) {
    console.error(`Error fetching services for category ${categoryId}:`, error);
    throw error;
  }
};

// Get services by category slug
export const getServicesByCategorySlug = async (slug) => {
  try {
    const response = await fetch(`${API_URL}/services/categories/slug/${slug}`);
    if (!response.ok) throw new Error('Failed to fetch services for category');
    return await response.json();
  } catch (error) {
    console.error(`Error fetching services for category ${slug}:`, error);
    throw error;
  }
};

// Get service details by ID
export const getServiceById = async (serviceId) => {
  try {
    const response = await fetch(`${API_URL}/services/${serviceId}`);
    if (!response.ok) throw new Error('Failed to fetch service details');
    return await response.json();
  } catch (error) {
    console.error(`Error fetching service details for ID ${serviceId}:`, error);
    throw error;
  }
};

// Submit a service request
export const submitServiceRequest = async (requestData) => {
  try {
    const response = await fetch(`${API_URL}/services/requests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) throw new Error('Failed to submit service request');
    return await response.json();
  } catch (error) {
    console.error('Error submitting service request:', error);
    throw error;
  }
};

// Get user's service requests
export const getUserServiceRequests = async () => {
  try {
    const response = await fetch(`${API_URL}/services/requests`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (!response.ok) throw new Error('Failed to fetch service requests');
    return await response.json();
  } catch (error) {
    console.error('Error fetching user service requests:', error);
    throw error;
  }
};

// Get featured services
export const getFeaturedServices = async () => {
  try {
    const response = await fetch(`${API_URL}/services/featured`);
    if (!response.ok) throw new Error('Failed to fetch featured services');
    return await response.json();
  } catch (error) {
    console.error('Error fetching featured services:', error);
    throw error;
  }
};