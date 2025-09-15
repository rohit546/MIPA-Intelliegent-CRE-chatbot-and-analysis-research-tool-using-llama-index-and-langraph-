export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';

export const CHATBOT_MODES = {
    QUERY: 'query',
    ADDRESS_DETAILS: 'address_details',
};

export const API_ENDPOINTS = {
    FETCH_PROPERTIES: '/properties',
    FETCH_ADDRESS_DETAILS: '/chat',
};

export const DEFAULT_PROPERTY_IMAGE = 'https://via.placeholder.com/150';

export const GALLERY_ITEMS_PER_PAGE = 10;

export const ERROR_MESSAGES = {
    FETCH_PROPERTIES: 'Error fetching properties. Please try again later.',
    FETCH_ADDRESS_DETAILS: 'Error fetching address details. Please try again later.',
};