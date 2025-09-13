import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const propertyService = {
    fetchProperties: async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/properties`);
            return response.data;
        } catch (error) {
            console.error("Error fetching properties:", error);
            throw error;
        }
    },

    fetchPropertyById: async (id) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/properties/${id}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching property with ID ${id}:`, error);
            throw error;
        }
    }
};

export default propertyService;