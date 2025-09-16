import React, { useState } from 'react';
import './Chatbot-new.css';
import QueryMode from './QueryMode';
import AddressDetailsMode from './AddressDetailsMode';
import SmartAnalyst from './SmartAnalyst';

const Chatbot = ({ onPropertiesFound }) => {
    const [mode, setMode] = useState('query'); // 'query' or 'address'
    const [showAnalyst, setShowAnalyst] = useState(false);
    const [analysisData, setAnalysisData] = useState(null);

    const toggleMode = () => {
        setMode((prevMode) => (prevMode === 'query' ? 'address' : 'query'));
    };

    const handleStartAnalysis = (address, smartyData) => {
        setAnalysisData({ address, smartyData });
        setShowAnalyst(true);
    };

    const handleCloseAnalyst = () => {
        setShowAnalyst(false);
        setAnalysisData(null);
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
                    <AddressDetailsMode onStartAnalysis={handleStartAnalysis} />
                )}
            </div>
            
            {/* Smart Analyst Modal */}
            {showAnalyst && analysisData && (
                <SmartAnalyst
                    propertyAddress={analysisData.address}
                    smartyData={analysisData.smartyData}
                    onClose={handleCloseAnalyst}
                />
            )}
        </div>
    );
};

export default Chatbot;