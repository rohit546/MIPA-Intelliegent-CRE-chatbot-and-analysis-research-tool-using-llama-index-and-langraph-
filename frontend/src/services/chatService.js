import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';

export const sendMessage = async (message) => {
    try {
        const response = await axios.post(`${API_URL}/chat`, { message });
        return response.data;
    } catch (error) {
        console.error("Error sending message:", error);
        throw error;
    }
};

export const fetchAddressDetails = async (address) => {
    try {
        // This endpoint doesn't exist in the backend, using chat instead
        const response = await axios.post(`${API_URL}/chat`, { message: `Tell me about this address: ${address}` });
        return response.data;
    } catch (error) {
        console.error("Error fetching address details:", error);
        throw error;
    }
};