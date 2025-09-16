import React, { useState } from 'react';
import { AlertCircle, CheckCircle, Clock, MessageCircle, TrendingUp, MapPin, DollarSign, Users } from 'lucide-react';
import './PropertyScoring.css';

const PropertyScoring = ({ onScore, loading = false }) => {
  const [address, setAddress] = useState('');
  const [scoringResult, setScoringResult] = useState(null);
  const [currentQuestions, setCurrentQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [showQuestions, setShowQuestions] = useState(false);

  const handleAnalyze = async () => {
    if (!address.trim()) {
      alert('Please enter an address');
      return;
    }

    try {
      const response = await fetch('http://localhost:8003/score-address', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setScoringResult(result);
      
      if (result.scoring_analysis.user_questions && result.scoring_analysis.user_questions.length > 0) {
        setCurrentQuestions(result.scoring_analysis.user_questions);
        setShowQuestions(true);
      }

      if (onScore) {
        onScore(result);
      }
    } catch (error) {
      console.error('Error analyzing property:', error);
      alert('Failed to analyze property. Please try again.');
    }
  };

  const handleAnswerQuestion = (question, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [question]: answer
    }));
  };

  const submitAnswers = async () => {
    // This would send answers back to refine the scoring
    console.log('User answers:', userAnswers);
    setShowQuestions(false);
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'Poor';
  };

  const renderCriteriaScore = (name, score, description) => (
    <div key={name} className="criteria-item">
      <div className="criteria-header">
        <span className="criteria-name">{name}</span>
        <span className={`criteria-score ${getScoreColor(score)}`}>
          {score.toFixed(1)}/10
        </span>
      </div>
      <div className="score-bar">
        <div 
          className="score-fill" 
          style={{ width: `${score * 10}%`, backgroundColor: score >= 6 ? '#10b981' : score >= 4 ? '#f59e0b' : '#ef4444' }}
        />
      </div>
      {description && <p className="criteria-description">{description}</p>}
    </div>
  );

  return (
    <div className="property-scoring">
      <div className="scoring-header">
        <h2>🎯 IMST Property Scoring System</h2>
        <p>AI-powered analysis using the Independent Multi-Site Testing methodology</p>
      </div>

      <div className="address-input-section">
        <div className="input-group">
          <MapPin className="input-icon" size={20} />
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Enter property address (e.g., 123 Main St, Atlanta, GA)"
            className="address-input"
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
          />
          <button 
            onClick={handleAnalyze}
            disabled={loading || !address.trim()}
            className="analyze-button"
          >
            {loading ? (
              <>
                <Clock className="animate-spin" size={16} />
                Analyzing...
              </>
            ) : (
              <>
                <TrendingUp size={16} />
                Analyze Property
              </>
            )}
          </button>
        </div>
      </div>

      {scoringResult && (
        <div className="scoring-results">
          {/* Overall Score */}
          <div className="overall-score-card">
            <div className="score-main">
              <div className="score-circle">
                <span className={`score-number ${getScoreColor(scoringResult.scoring_analysis.overall_score)}`}>
                  {scoringResult.scoring_analysis.overall_score.toFixed(1)}
                </span>
                <span className="score-max">/10</span>
              </div>
              <div className="score-info">
                <h3>Overall IMST Score</h3>
                <p className={`score-label ${getScoreColor(scoringResult.scoring_analysis.overall_score)}`}>
                  {getScoreLabel(scoringResult.scoring_analysis.overall_score)}
                </p>
                <p className="confidence">
                  Confidence: {scoringResult.scoring_analysis.confidence_level}
                </p>
              </div>
            </div>
          </div>

          {/* Property Summary */}
          <div className="property-summary">
            <h3>📍 Property Overview</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <MapPin size={16} />
                <span>{scoringResult.combined_insights.property_summary.address.fullAddress}</span>
              </div>
              <div className="summary-item">
                <Users size={16} />
                <span>Type: {scoringResult.combined_insights.property_summary.property_type || 'Unknown'}</span>
              </div>
              <div className="summary-item">
                <DollarSign size={16} />
                <span>Zoning: {scoringResult.combined_insights.property_summary.zoning || 'Unknown'}</span>
              </div>
            </div>
          </div>

          {/* Detailed Criteria Scores */}
          <div className="criteria-scores">
            <h3>📊 Detailed Analysis</h3>
            <div className="criteria-grid">
              {renderCriteriaScore('Location', scoringResult.scoring_analysis.criteria_scores.location, 'Highway access, visibility, traffic patterns')}
              {renderCriteriaScore('Market', scoringResult.scoring_analysis.criteria_scores.market, 'Demographics, income levels, population density')}
              {renderCriteriaScore('Brand', scoringResult.scoring_analysis.criteria_scores.brand, 'Brand compatibility and competitive positioning')}
              {renderCriteriaScore('Facility', scoringResult.scoring_analysis.criteria_scores.facility, 'Site size, layout potential, infrastructure')}
              {renderCriteriaScore('Merchandising', scoringResult.scoring_analysis.criteria_scores.merchandising, 'Local preferences and product mix')}
              {renderCriteriaScore('Access & Visibility', scoringResult.scoring_analysis.criteria_scores.access_visibility, 'Ingress/egress and highway visibility')}
            </div>
          </div>

          {/* Red Flags */}
          {scoringResult.scoring_analysis.red_flags && scoringResult.scoring_analysis.red_flags.length > 0 && (
            <div className="red-flags">
              <h3>⚠️ Red Flags</h3>
              <div className="flags-list">
                {scoringResult.scoring_analysis.red_flags.map((flag, index) => (
                  <div key={index} className="flag-item">
                    <AlertCircle className="flag-icon" size={16} />
                    <span>{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {scoringResult.scoring_analysis.recommendations && scoringResult.scoring_analysis.recommendations.length > 0 && (
            <div className="recommendations">
              <h3>💡 Recommendations</h3>
              <div className="recommendations-list">
                {scoringResult.scoring_analysis.recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <CheckCircle className="rec-icon" size={16} />
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Reasoning */}
          {scoringResult.scoring_analysis.reasoning && (
            <div className="ai-reasoning">
              <h3>🤖 AI Analysis</h3>
              <p>{scoringResult.scoring_analysis.reasoning}</p>
            </div>
          )}

          {/* Data Gaps */}
          {scoringResult.scoring_analysis.data_gaps && scoringResult.scoring_analysis.data_gaps.length > 0 && (
            <div className="data-gaps">
              <h3>📋 Data Gaps Identified</h3>
              <div className="gaps-list">
                {scoringResult.scoring_analysis.data_gaps.map((gap, index) => (
                  <div key={index} className="gap-item">
                    <div className="gap-header">
                      <span className="gap-field">{gap.field}</span>
                      <span className={`gap-confidence confidence-${gap.confidence}`}>
                        {gap.confidence} confidence
                      </span>
                    </div>
                    <p className="gap-description">{gap.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* User Questions Modal */}
      {showQuestions && currentQuestions.length > 0 && (
        <div className="questions-modal">
          <div className="modal-content">
            <div className="modal-header">
              <MessageCircle size={24} />
              <h3>Help us improve the analysis</h3>
              <p>Please answer these questions to get a more accurate score:</p>
            </div>
            
            <div className="questions-list">
              {currentQuestions.map((question, index) => (
                <div key={index} className="question-item">
                  <label className="question-label">{question}</label>
                  <textarea
                    placeholder="Your answer..."
                    value={userAnswers[question] || ''}
                    onChange={(e) => handleAnswerQuestion(question, e.target.value)}
                    className="question-input"
                    rows={3}
                  />
                </div>
              ))}
            </div>

            <div className="modal-actions">
              <button 
                onClick={() => setShowQuestions(false)}
                className="btn-secondary"
              >
                Skip Questions
              </button>
              <button 
                onClick={submitAnswers}
                className="btn-primary"
                disabled={Object.keys(userAnswers).length === 0}
              >
                Submit Answers
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyScoring;
