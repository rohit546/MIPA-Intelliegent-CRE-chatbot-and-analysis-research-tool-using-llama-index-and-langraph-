import React, { useState } from 'react';
import './Chatbot-new.css';
import QueryMode from './QueryMode';
import AddressDetailsMode from './AddressDetailsMode';

const Chatbot = ({ onPropertiesFound }) => {
    const [mode, setMode] = useState('query'); // 'query' or 'address'

    const toggleMode = () => {
        setMode((prevMode) => (prevMode === 'query' ? 'address' : 'query'));
    };

    return (
        <div className="chatbot">
            <div className="chatbot-header">
                <h2>AI Property Assistant</h2>
                <button onClick={toggleMode}>
                    Switch to {mode === 'query' ? 'Address Details' : 'Query'} Mode
                </button>
            </div>
            <div className="chatbot-body">
                {mode === 'query' ? (
                    <QueryMode onPropertiesFound={onPropertiesFound} />
                ) : (
                    <AddressDetailsMode />
                )}
            </div>
        </div>
    );
};

export default Chatbot;