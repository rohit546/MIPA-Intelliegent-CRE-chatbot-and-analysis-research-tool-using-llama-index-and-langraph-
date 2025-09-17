import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, CheckCircle, Clock, Eye, Brain, Database, X, TrendingUp } from 'lucide-react';

const SmartAnalyst = ({ propertyAddress, smartyData, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [dataChecklist, setDataChecklist] = useState({});
  const [currentTask, setCurrentTask] = useState('');
  const [progress, setProgress] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeAnalysis();
  }, []);

  const initializeAnalysis = async () => {
    console.log('Smarty Data received:', smartyData); // Debug log
    
    // Show what data we have from Smarty
    const smartyDataPoints = extractSmartyDataPoints(smartyData);
    console.log('Extracted data points:', smartyDataPoints); // Debug log
    setDataChecklist(smartyDataPoints);
    
    // Calculate initial progress
    const completed = Object.values(smartyDataPoints).filter(v => v && v !== 'Missing').length;
    const total = Object.keys(smartyDataPoints).length;
    const progressPercent = total > 0 ? (completed / total) * 100 : 0;
    console.log(`Progress: ${completed}/${total} = ${progressPercent}%`); // Debug log
    setProgress(progressPercent);

    // Show complete property context from Smarty
    const propertyInfo = smartyData?.property_info || {};
    const financialInfo = smartyData?.financial_info || {};
    const locationInfo = smartyData?.location_info || {};
    
    const contextMessage = `🏢 COMPLETE PROPERTY ANALYSIS

📍 PROPERTY DETAILS:
• Address: ${propertyAddress}
• Type: ${propertyInfo.property_type || 'Unknown'}
• Zoning: ${propertyInfo.zoning || 'Unknown'}
• Year Built: ${propertyInfo.year_built || 'Unknown'}
• Building: ${propertyInfo.building_sqft || 'Unknown'} sq ft
• Lot: ${propertyInfo.lot_sqft ? parseInt(propertyInfo.lot_sqft).toLocaleString() : 'Unknown'} sq ft (${propertyInfo.acres || 'Unknown'} acres)

💰 FINANCIAL DATA:
• Market Value: ${financialInfo.market_value || 'Unknown'}
• Last Sale: ${financialInfo.deed_sale_price || 'Unknown'} (${financialInfo.deed_sale_date || 'Unknown'})
• Annual Taxes: ${financialInfo.tax_billed_amount || 'Unknown'}
• Owner: ${propertyInfo.owner_name || 'Unknown'}

🗺️ LOCATION:
• County: ${locationInfo.county || 'Unknown'}
• Metro: ${locationInfo.cbsa_name || 'Unknown'}

⚠️ MISSING CRITICAL DATA FOR IMST:
• Traffic Count (vehicles/day)
• Nearby Competition 
• Demographics & Income
• Highway Visibility
• Access Quality

🎯 Ready to start IMST analysis with Marcus...`;

    setMessages([{
      id: Date.now(),
      type: 'system',
      content: contextMessage,
      timestamp: new Date().toLocaleTimeString()
    }]);

    // Start AI analysis
    setCurrentTask('🤖 Starting AI analysis...');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8003/start-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address: propertyAddress,
          smarty_data: smartyData
        }),
      });

      if (!response.ok) throw new Error('Failed to start analysis');

      const result = await response.json();
      setSessionId(result.session_id);
      setCurrentTask('✅ Analysis started');

      // Add initial message
      addMessage('bot', result.analyst_message);

    } catch (error) {
      console.error('Error:', error);
      addMessage('bot', "I'm having technical issues. Let me try a simpler approach. What's the daily traffic count on this road?");
    } finally {
      setIsLoading(false);
    }
  };

  const extractSmartyDataPoints = (data) => {
    console.log('Raw smarty data in extract:', data); // Debug log
    
    // Extract from the complete Smarty response structure
    const propertyInfo = data?.property_info || {};
    const financialInfo = data?.financial_info || {};
    const locationInfo = data?.location_info || {};
    
    // IMST Required Data Points with actual Smarty data
    const imstData = {
      '📍 Property Type': propertyInfo.property_type || 'Missing',
      '📏 Building Area': propertyInfo.building_sqft ? `${propertyInfo.building_sqft} sq ft` : 'Missing',
      '📐 Lot Size': propertyInfo.lot_sqft ? `${parseInt(propertyInfo.lot_sqft).toLocaleString()} sq ft` : 'Missing',
      '🏞️ Acres': propertyInfo.acres ? `${propertyInfo.acres} acres` : 'Missing',
      '🏛️ Zoning': propertyInfo.zoning || 'Missing',
      '📅 Year Built': propertyInfo.year_built || 'Missing',
      '💰 Market Value': financialInfo.market_value ? `$${parseInt(financialInfo.market_value.replace(/[$,]/g, '')).toLocaleString()}` : 'Missing',
      '🏦 Last Sale': financialInfo.deed_sale_price ? `$${parseInt(financialInfo.deed_sale_price.replace(/[$,]/g, '')).toLocaleString()}` : 'Missing',
      '🗺️ County': locationInfo.county || 'Missing',
      '🏙️ Metro Area': locationInfo.cbsa_name ? 'Atlanta Metro' : 'Missing',
      '👤 Owner': propertyInfo.owner_name || 'Missing',
      '🏢 Owner Type': propertyInfo.ownership_type || 'Missing',
      // Critical missing data for IMST
      '🚗 Traffic Count': 'Missing', // Critical for gas stations
      '🏪 Competition': 'Missing',   // Critical for analysis
      '👥 Demographics': 'Missing',  // Critical for market analysis
      '👁️ Visibility': 'Missing',    // Critical for gas stations
      '🛣️ Highway Access': 'Missing', // Critical for gas stations
      '⛽ Fuel Delivery': 'Missing'   // Critical for gas stations
    };
    
    console.log('Extracted IMST data:', imstData); // Debug log
    return imstData;
  };

  const addMessage = (type, content) => {
    const newMessage = {
      id: Date.now(),
      type,
      content,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId) return;

    addMessage('user', currentMessage);
    setCurrentMessage('');
    setIsLoading(true);
    setCurrentTask('🧠 AI analyzing your input...');

    try {
      const response = await fetch(`http://localhost:8003/continue-analysis/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentMessage }),
      });

      if (!response.ok) throw new Error('Failed to continue analysis');

      const result = await response.json();
      setCurrentTask('✅ Analysis updated');
      
      // Update progress based on data collected
      updateProgress(result.data_collected);
      
      addMessage('bot', result.analyst_message);

    } catch (error) {
      console.error('Error:', error);
      addMessage('bot', "Could you clarify that? I need specific details.");
    } finally {
      setIsLoading(false);
      setCurrentTask('');
    }
  };

  const updateProgress = (dataCollected) => {
    const updatedChecklist = { ...dataChecklist };
    
    // Update checklist based on collected data
    Object.keys(dataCollected || {}).forEach(key => {
      if (key.includes('traffic')) updatedChecklist['🚗 Traffic Count'] = '✅ User Provided';
      if (key.includes('competition')) updatedChecklist['🏪 Competition'] = '✅ User Provided';
      if (key.includes('demographic')) updatedChecklist['👥 Demographics'] = '✅ User Provided';
      if (key.includes('visibility')) updatedChecklist['👁️ Visibility'] = '✅ User Provided';
      if (key.includes('access')) updatedChecklist['🛣️ Highway Access'] = '✅ User Provided';
      if (key.includes('fuel')) updatedChecklist['⛽ Fuel Delivery'] = '✅ User Provided';
    });
    
    setDataChecklist(updatedChecklist);
    
    // Update progress
    const completed = Object.values(updatedChecklist).filter(v => v && v !== 'Missing').length;
    const total = Object.keys(updatedChecklist).length;
    setProgress(total > 0 ? (completed / total) * 100 : 0);
  };

  const activateResearchMode = async () => {
    if (!sessionId) return;
    
    setCurrentTask('🔍 AI researching missing data...');
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8003/research-property/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) throw new Error('Research failed');

      const result = await response.json();
      
      // Update progress with researched data
      updateProgress(result.research_results);
      
      // Add research results message
      addMessage('system', `🔍 ADVANCED RESEARCH COMPLETE

📊 RESEARCHED DATA:
${Object.entries(result.research_results).map(([key, value]) => `• ${key}: ${value}`).join('\n')}

🎯 Confidence increased to ${Math.round(result.confidence_level * 100)}%
Ready for final analysis!`);

      setCurrentTask('✅ Research complete!');

    } catch (error) {
      console.error('Research error:', error);
      addMessage('system', '⚠️ Research mode temporarily unavailable. Please provide data manually.');
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="fixed inset-0 bg-white z-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Rohit</h3>
            <p className="text-sm text-gray-600">Senior Property Analyst • IMST Specialist</p>
            <p className="text-xs text-gray-500">{propertyAddress}</p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Data & Progress */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 p-6 overflow-y-auto">
          {/* Progress Section */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-900">Analysis Progress</h4>
              <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div 
                className="bg-gradient-to-r from-gray-700 to-gray-900 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            
            {currentTask && (
              <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-lg p-3 mb-4 shadow-sm">
                <Brain className="w-4 h-4 text-gray-700 animate-pulse" />
                <span className="text-sm text-gray-700">{currentTask}</span>
              </div>
            )}
          </div>

          {/* IMST Data Checklist */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4" />
              <span>IMST Data Points</span>
            </h4>
            
            <div className="space-y-3">
              {Object.entries(dataChecklist).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between py-2 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    {value && value !== 'Missing' ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <Clock className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${value && value !== 'Missing' ? 'text-green-700' : 'text-red-600'}`}>
                      {key}
                    </span>
                  </div>
                  {value && value !== 'Missing' && !value.includes('✅') && (
                    <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                      {value}
                    </span>
                  )}
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div className="flex justify-between text-sm">
                <span className="text-green-700 font-medium">
                  Available: {Object.values(dataChecklist).filter(v => v && v !== 'Missing').length}
                </span>
                <span className="text-red-600 font-medium">
                  Missing: {Object.values(dataChecklist).filter(v => !v || v === 'Missing').length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Chat */}
        <div className="flex-1 flex flex-col bg-white">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 w-full">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start space-x-3 max-w-full w-full ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'bot' ? 'bg-gray-900' :
                    message.type === 'system' ? 'bg-gray-600' : 'bg-gray-700'
                  }`}>
                    {message.type === 'bot' ? <Bot className="w-4 h-4 text-white" /> : 
                     message.type === 'system' ? <Database className="w-4 h-4 text-white" /> : 
                     <User className="w-4 h-4 text-white" />}
                  </div>
                  
                  <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-xs font-medium text-gray-600">
                        {message.type === 'bot' ? 'Rohit' : 
                         message.type === 'system' ? 'Property Data' : 'You'}
                      </span>
                      <span className="text-xs text-gray-500">{message.timestamp}</span>
                    </div>
                    
                    <div className={`rounded-lg px-4 py-3 w-full border ${
                      message.type === 'bot' ? 'bg-gray-100 text-gray-900 border-gray-200' :
                      message.type === 'system' ? 'bg-gray-50 text-gray-800 border-gray-300' :
                      'bg-gray-900 text-white border-gray-700'
                    }`}>
                      {message.type === 'system' ? (
                        <pre className="whitespace-pre-wrap text-sm font-mono">
                          {message.content}
                        </pre>
                      ) : (
                        <pre className="text-sm leading-relaxed whitespace-pre-wrap font-mono overflow-x-auto">{message.content}</pre>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3 max-w-2xl">
                  <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex flex-col items-start">
                    <span className="text-xs font-medium text-gray-600 mb-1">Rohit</span>
                    <div className="bg-gray-100 border border-gray-200 rounded-lg px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-700 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-700 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-700 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-700">Analyzing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-6 bg-gray-50">
            {/* Research Mode Button */}
            {sessionId && Object.values(dataChecklist).filter(v => !v || v === 'Missing').length > 3 && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 mb-3">🔍 Want me to research missing data automatically?</p>
                <button 
                  onClick={activateResearchMode}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                  disabled={isLoading}
                >
                  🤖 Activate Advanced Research Mode
                </button>
              </div>
            )}
            
            <div className="flex items-center space-x-4">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Answer Rohit's question..."
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                disabled={isLoading}
                className="flex-1 bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              />
              <button 
                onClick={sendMessage} 
                disabled={!currentMessage.trim() || isLoading}
                className="bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg p-3 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer - AI Status */}
      <div className="bg-gray-100 border-t border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Brain className="w-4 h-4 text-gray-700" />
            <span className="text-xs text-gray-600">GPT-4 Turbo</span>
          </div>
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4 text-gray-700" />
            <span className="text-xs text-gray-600">Smarty API + User Input</span>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          IMST Analysis • Real Estate Intelligence
        </div>
      </div>
    </div>
  );
};

export default SmartAnalyst;
