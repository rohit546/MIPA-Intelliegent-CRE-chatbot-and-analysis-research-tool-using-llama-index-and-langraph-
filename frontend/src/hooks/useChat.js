import { useState } from 'react';
import { fetchChatResponse } from '../services/chatService';

const useChat = () => {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const sendMessage = async (userMessage) => {
        setLoading(true);
        setError(null);
        
        // Add user message to chat
        setMessages((prevMessages) => [
            ...prevMessages,
            { text: userMessage, sender: 'user' },
        ]);

        try {
            const response = await fetchChatResponse(userMessage);
            setMessages((prevMessages) => [
                ...prevMessages,
                { text: response.data, sender: 'bot' },
            ]);
        } catch (err) {
            setError('Failed to fetch response from the chatbot.');
        } finally {
            setLoading(false);
        }
    };

    return {
        messages,
        loading,
        error,
        sendMessage,
    };
};

export default useChat;