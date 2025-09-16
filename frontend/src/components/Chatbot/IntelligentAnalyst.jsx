import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, TrendingUp, MapPin, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import './IntelligentAnalyst.css';

const IntelligentAnalyst = ({ propertyAddress, smartyData, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [analysisStage, setAnalysisStage] = useState('initial');
  const [confidenceLevel, setConfidenceLevel] = useState(0);
  const [nextSteps, setNextSteps] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Start the analysis when component mounts
    startAnalysis();
  }, []);

  const startAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8003/start-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: propertyAddress,
          smarty_data: smartyData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const result = await response.json();
      
      setSessionId(result.session_id);
      setAnalysisStage(result.analysis_stage);
      setConfidenceLevel(result.confidence_level);
      setNextSteps(result.next_steps);
      
      // Add initial analyst message
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: result.analyst_message,
        timestamp: new Date().toLocaleTimeString(),
        metadata: {
          stage: result.analysis_stage,
          confidence: result.confidence_level,
          followUpQuestions: result.follow_up_questions
        }
      }]);

    } catch (error) {
      console.error('Error starting analysis:', error);
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: "I'm sorry, I'm having trouble starting the analysis. Please try again.",
        timestamp: new Date().toLocaleTimeString(),
        metadata: { error: true }
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8003/continue-analysis/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to continue analysis');
      }

      const result = await response.json();
      
      setAnalysisStage(result.analysis_stage);
      setConfidenceLevel(result.confidence_level);
      setNextSteps(result.next_steps);

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: result.analyst_message,
        timestamp: new Date().toLocaleTimeString(),
        metadata: {
          stage: result.analysis_stage,
          confidence: result.confidence_level,
          dataCollected: result.data_collected,
          followUpQuestions: result.follow_up_questions
        }
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I apologize, I didn't catch that. Could you repeat your response?",
        timestamp: new Date().toLocaleTimeString(),
        metadata: { error: true }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStageIcon = (stage) => {
    switch (stage) {
      case 'initial': return <Clock className="stage-icon" size={16} />;
      case 'gathering': return <TrendingUp className="stage-icon" size={16} />;
      case 'analyzing': return <Bot className="stage-icon" size={16} />;
      case 'complete': return <CheckCircle className="stage-icon" size={16} />;
      default: return <AlertCircle className="stage-icon" size={16} />;
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="intelligent-analyst">
      <div className="analyst-header">
        <div className="header-info">
          <div className="property-info">
            <MapPin size={20} />
            <div>
              <h3>Property Analysis Session</h3>
              <p>{propertyAddress}</p>
            </div>
          </div>
          <button onClick={onClose} className="close-button">×</button>
        </div>
        
        <div className="analysis-status">
          <div className="status-item">
            {getStageIcon(analysisStage)}
            <span>Stage: {analysisStage}</span>
          </div>
          <div className="status-item">
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ 
                  width: `${confidenceLevel * 100}%`,
                  backgroundColor: getConfidenceColor(confidenceLevel)
                }}
              />
            </div>
            <span>Confidence: {Math.round(confidenceLevel * 100)}%</span>
          </div>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'bot' ? (
                  <Bot size={20} />
                ) : (
                  <User size={20} />
                )}
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="sender-name">
                    {message.type === 'bot' ? 'Marcus Rodriguez (Senior Analyst)' : 'You'}
                  </span>
                  <span className="message-time">{message.timestamp}</span>
                </div>
                <div className="message-text">
                  {message.content}
                </div>
                {message.metadata?.followUpQuestions && message.metadata.followUpQuestions.length > 0 && (
                  <div className="follow-up-questions">
                    <p><strong>Key questions to consider:</strong></p>
                    <ul>
                      {message.metadata.followUpQuestions.map((q, index) => (
                        <li key={index}>{q}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {message.metadata?.stage === 'complete' && (
                  <div className="analysis-complete">
                    <CheckCircle size={16} />
                    <span>Analysis Complete</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="sender-name">Marcus Rodriguez (Senior Analyst)</span>
                </div>
                <div className="typing-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span>Analyzing...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="next-steps">
            {nextSteps.length > 0 && (
              <div className="steps-display">
                <span>Next: {nextSteps[0]}</span>
              </div>
            )}
          </div>
          
          <div className="input-area">
            <input
              type="text"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder="Share your insights about this property..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
              className="message-input"
            />
            <button 
              onClick={sendMessage}
              disabled={!currentMessage.trim() || isLoading}
              className="send-button"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligentAnalyst;
