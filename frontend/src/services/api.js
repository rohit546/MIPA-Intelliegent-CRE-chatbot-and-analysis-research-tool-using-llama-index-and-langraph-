import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchProperties = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // Add pagination
    params.append('page', filters.page || 1);
    params.append('limit', filters.limit || 20);
    
    // Add filters
    if (filters.property_type) {
      params.append('property_type', filters.property_type);
    }
    if (filters.min_price) {
      params.append('min_price', filters.min_price);
    }
    if (filters.max_price) {
      params.append('max_price', filters.max_price);
    }
    
    const response = await api.get(`/api/properties?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
};

export const fetchPropertyDetails = async (propertyId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/properties/${propertyId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching property details:', error);
        throw error;
    }
};

export const submitQuery = async (query) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, { message: query });
        return response.data;
    } catch (error) {
        console.error('Error submitting query:', error);
        throw error;
    }
};

export const fetchAddressDetails = async (address) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat/address`, { address });
        return response.data;
    } catch (error) {
        console.error('Error fetching address details:', error);
        throw error;
    }
};