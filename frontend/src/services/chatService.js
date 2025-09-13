import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

export const sendMessage = async (message) => {
    try {
        const response = await axios.post(`${API_URL}/api/chat/send`, { message });
        return response.data;
    } catch (error) {
        console.error("Error sending message:", error);
        throw error;
    }
};

export const fetchAddressDetails = async (address) => {
    try {
        const response = await axios.get(`${API_URL}/api/chat/address`, { params: { address } });
        return response.data;
    } catch (error) {
        console.error("Error fetching address details:", error);
        throw error;
    }
};