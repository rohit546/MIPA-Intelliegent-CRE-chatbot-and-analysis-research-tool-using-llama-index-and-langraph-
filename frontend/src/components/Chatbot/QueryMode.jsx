import React, { useState, useEffect } from 'react';
import { sendMessage } from '../../services/chatService';

const QueryMode = ({ onPropertiesFound }) => {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Add welcome message on component mount
    useEffect(() => {
        const welcomeMessage = {
            type: 'bot',
            content: '🏢 Welcome to Mighty Investment Property Analyzer! I can help you analyze Georgia commercial properties using natural language. Try asking:\n\n• "Show me gas stations under $500k"\n• "Find retail properties in Atlanta"\n• "Properties between 2-5 acres in Walton County"\n• "Count all properties by county"\n\nI use advanced AI to understand your queries and will show matching properties below!'
        };
        setMessages([welcomeMessage]);
    }, []);

    const handleSendQuery = async () => {
        if (!query.trim()) return;

        const userMessage = { type: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Send query to LlamaIndex backend
            const response = await sendMessage(query);
            
            const botMessage = { 
                type: 'bot', 
                content: response.response,
                metadata: {
                    sql_query: response.sql_query,
                    validation_status: response.validation_status,
                    was_corrected: response.was_corrected,
                    correction_explanation: response.correction_explanation
                }
            };
            
            setMessages(prev => [...prev, botMessage]);
            
            // If properties were found, notify parent component to display them
            if (response.properties && response.properties.length > 0 && onPropertiesFound) {
                onPropertiesFound(response.properties, query);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = { 
                type: 'bot', 
                content: `❌ Sorry, I encountered an error processing your request. Please make sure the backend server is running and try again.\n\nError: ${error.message}` 
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }

        setQuery('');
    };

    return (
        <div className="query-mode">
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.type}`}>
                        <div className="message-content">
                            {msg.content}
                            {/* Show technical details for bot messages if available */}
                            {msg.type === 'bot' && msg.metadata && (
                                <div className="technical-details" style={{ marginTop: '10px', padding: '8px', background: 'rgba(0,0,0,0.1)', borderRadius: '4px', fontSize: '0.8em' }}>
                                    {msg.metadata.sql_query && (
                                        <div><strong>SQL:</strong> <code>{msg.metadata.sql_query}</code></div>
                                    )}
                                    {msg.metadata.validation_status && (
                                        <div><strong>Status:</strong> {msg.metadata.validation_status}</div>
                                    )}
                                    {msg.metadata.was_corrected && msg.metadata.correction_explanation && (
                                        <div><strong>Auto-corrected:</strong> {msg.metadata.correction_explanation}</div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message bot">
                        <div className="message-content">
                            <div className="loading-dots">🤔 Processing your query with AI...</div>
                        </div>
                    </div>
                )}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about Georgia properties... (e.g., 'Show me gas stations under $500k')"
                    onKeyPress={(e) => e.key === 'Enter' && handleSendQuery()}
                />
                <button onClick={handleSendQuery} disabled={!query.trim() || isLoading}>
                    {isLoading ? 'Processing...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default QueryMode;