# Real Estate Data Pipeline & Analysis System
## Comprehensive Market Intelligence Platform

---

## 🎯 **Project Vision**
Transform MIPA into a sophisticated real estate analysis platform that provides:
- **Competitive Analysis** - Track competitor properties, sales, and market positioning
- **Risk Assessment** - Crime rates, environmental risks, market volatility
- **Foot Traffic Analysis** - Consumer behavior and location attractiveness
- **Market Intelligence** - Pricing trends, demand patterns, investment opportunities
- **Predictive Analytics** - Future market predictions and ROI forecasting

---

## 📊 **Data Sources & Integration Strategy**

### 1. **Core Real Estate Data**
```python
# Primary Data Sources
REAL_ESTATE_SOURCES = {
    "property_listings": {
        "crexi": "Commercial real estate listings",
        "loopnet": "Commercial properties",
        "realtor": "Residential + commercial",
        "zillow": "Property values and trends",
        "apartments": "Multi-family properties"
    },
    "transaction_data": {
        "coStar": "Commercial sales data",
        "real_capital_analytics": "Investment transactions",
        "public_records": "Deed transfers, sales prices"
    },
    "market_data": {
        "cbre": "Market reports and trends",
        "jll": "Commercial market intelligence",
        "colliers": "Global market insights"
    }
}
```

### 2. **Competitive Intelligence Sources**
```python
COMPETITIVE_SOURCES = {
    "direct_competitors": {
        "properties": "Track competitor property portfolios",
        "pricing": "Monitor asking prices and sales",
        "occupancy": "Track vacancy rates and tenant mix",
        "marketing": "Analyze listing strategies and positioning"
    },
    "market_players": {
        "investors": "Track major property investors",
        "developers": "Monitor new development projects",
        "brokers": "Analyze brokerage activity and deals"
    }
}
```

### 3. **Risk & Safety Data**
```python
RISK_SOURCES = {
    "crime_data": {
        "fbi_ucr": "Uniform Crime Reporting data",
        "local_police": "City/county crime statistics",
        "safewise": "Neighborhood safety scores",
        "spotcrime": "Real-time crime mapping"
    },
    "environmental": {
        "fema": "Flood risk and natural disasters",
        "epa": "Environmental hazards and superfund sites",
        "noaa": "Weather patterns and climate risks"
    },
    "economic": {
        "fred": "Federal Reserve economic data",
        "bls": "Bureau of Labor Statistics",
        "census": "Demographic and economic indicators"
    }
}
```

### 4. **Foot Traffic & Consumer Data**
```python
TRAFFIC_SOURCES = {
    "mobile_data": {
        "google_maps": "Popular times and visit duration",
        "foursquare": "Check-in data and venue popularity",
        "safegraph": "Foot traffic patterns and demographics"
    },
    "retail_intelligence": {
        "placer_ai": "Foot traffic analytics",
        "retail_next": "Consumer behavior insights",
        "nielsen": "Market research and demographics"
    },
    "transportation": {
        "transit_apis": "Public transportation access",
        "traffic_data": "Vehicle traffic patterns",
        "parking_data": "Parking availability and pricing"
    }
}
```

---

## 🏗️ **Enhanced System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  ├── Real Estate APIs (Crexi, LoopNet, Zillow)                │
│  ├── Market Data APIs (CoStar, CBRE, JLL)                     │
│  ├── Crime & Safety APIs (FBI, Local Police, SafeWise)        │
│  ├── Foot Traffic APIs (Google Maps, Foursquare, Placer.ai)   │
│  ├── Economic Data APIs (FRED, BLS, Census)                   │
│  └── Web Scrapers (Public Records, News, Social Media)        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  ├── ETL Pipelines (Apache Airflow)                           │
│  ├── Data Validation & Cleaning                               │
│  ├── Feature Engineering                                      │
│  ├── Geospatial Processing (PostGIS)                          │
│  └── Real-time Stream Processing (Kafka)                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ├── PostgreSQL (Property Data + Geospatial)                  │
│  ├── ClickHouse (Time Series Data)                            │
│  ├── Elasticsearch (Search & Analytics)                       │
│  ├── Redis (Caching)                                          │
│  └── S3/MinIO (Raw Data + ML Models)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS & ML LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ├── Market Analysis Engine                                   │
│  ├── Risk Assessment Models                                   │
│  ├── Predictive Analytics (Prophet, LSTM)                     │
│  ├── Competitive Intelligence                                  │
│  └── ROI Forecasting Models                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API & PRESENTATION LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│  ├── FastAPI Backend (Enhanced)                               │
│  ├── React Frontend (Dashboard)                               │
│  ├── Real-time WebSocket Updates                              │
│  ├── Interactive Maps (Mapbox/Leaflet)                        │
│  └── Data Visualization (D3.js, Chart.js)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 **Data Pipeline Implementation**

### 1. **Enhanced Database Schema**

```sql
-- Core Property Table (Enhanced)
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    name VARCHAR(255),
    property_type VARCHAR(100),
    sub_type VARCHAR(100),
    asking_price DECIMAL(15,2),
    last_sale_price DECIMAL(15,2),
    last_sale_date DATE,
    address JSONB,
    coordinates POINT,
    size_acres DECIMAL(10,2),
    building_sqft INTEGER,
    lot_sqft INTEGER,
    year_built INTEGER,
    zoning VARCHAR(100),
    status VARCHAR(50),
    listing_url TEXT,
    thumbnail_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market Data Table
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    date DATE,
    market_value DECIMAL(15,2),
    price_per_sqft DECIMAL(10,2),
    cap_rate DECIMAL(5,4),
    noi DECIMAL(15,2),
    occupancy_rate DECIMAL(5,4),
    market_trend VARCHAR(50),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crime Data Table
CREATE TABLE crime_data (
    id SERIAL PRIMARY KEY,
    location POINT,
    date DATE,
    crime_type VARCHAR(100),
    severity VARCHAR(50),
    description TEXT,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foot Traffic Data
CREATE TABLE foot_traffic (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    date DATE,
    hour INTEGER,
    visitor_count INTEGER,
    dwell_time INTEGER, -- in minutes
    peak_hours JSONB,
    demographics JSONB,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitor Analysis
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    property_id INTEGER REFERENCES properties(id),
    competitor_type VARCHAR(100), -- direct, indirect, potential
    market_share DECIMAL(5,4),
    pricing_strategy VARCHAR(100),
    last_activity DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Risk Assessment
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    assessment_date DATE,
    crime_risk_score INTEGER, -- 1-100
    environmental_risk_score INTEGER,
    market_risk_score INTEGER,
    overall_risk_score INTEGER,
    risk_factors JSONB,
    mitigation_strategies JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. **Data Ingestion Pipeline**

```python
# backend/data_pipeline/ingestion.py
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from sqlalchemy import create_engine
import logging

class RealEstateDataPipeline:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.logger = logging.getLogger(__name__)
    
    async def ingest_all_sources(self):
        """Main ingestion orchestrator"""
        tasks = [
            self.ingest_property_listings(),
            self.ingest_market_data(),
            self.ingest_crime_data(),
            self.ingest_foot_traffic(),
            self.ingest_competitor_data(),
            self.ingest_economic_data()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def ingest_property_listings(self):
        """Ingest from multiple property listing sources"""
        sources = {
            'crexi': self._ingest_crexi_data,
            'loopnet': self._ingest_loopnet_data,
            'zillow': self._ingest_zillow_data,
            'realtor': self._ingest_realtor_data
        }
        
        for source_name, ingest_func in sources.items():
            try:
                await ingest_func()
                self.logger.info(f"Successfully ingested {source_name} data")
            except Exception as e:
                self.logger.error(f"Failed to ingest {source_name}: {e}")
    
    async def _ingest_crexi_data(self):
        """Ingest Crexi commercial real estate data"""
        async with aiohttp.ClientSession() as session:
            # Crexi API integration
            url = "https://api.crexi.com/v1/properties"
            headers = {"Authorization": f"Bearer {CREXI_API_KEY}"}
            
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                
                # Process and store data
                properties = self._process_crexi_properties(data)
                await self._store_properties(properties)
    
    async def ingest_crime_data(self):
        """Ingest crime data from multiple sources"""
        sources = {
            'fbi_ucr': self._ingest_fbi_crime_data,
            'local_police': self._ingest_local_crime_data,
            'safewise': self._ingest_safewise_data
        }
        
        for source_name, ingest_func in sources.items():
            try:
                await ingest_func()
                self.logger.info(f"Successfully ingested {source_name} crime data")
            except Exception as e:
                self.logger.error(f"Failed to ingest {source_name} crime data: {e}")
    
    async def _ingest_fbi_crime_data(self):
        """Ingest FBI Uniform Crime Reporting data"""
        # FBI UCR API integration
        url = "https://api.usa.gov/crime/fbi/cde/arrest/state"
        params = {
            'api_key': FBI_API_KEY,
            'state': 'GA',
            'year': datetime.now().year
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                crime_records = self._process_fbi_crime_data(data)
                await self._store_crime_data(crime_records)
    
    async def ingest_foot_traffic(self):
        """Ingest foot traffic data from multiple sources"""
        sources = {
            'google_maps': self._ingest_google_maps_data,
            'foursquare': self._ingest_foursquare_data,
            'placer_ai': self._ingest_placer_ai_data
        }
        
        for source_name, ingest_func in sources.items():
            try:
                await ingest_func()
                self.logger.info(f"Successfully ingested {source_name} foot traffic data")
            except Exception as e:
                self.logger.error(f"Failed to ingest {source_name} foot traffic: {e}")
    
    async def _ingest_google_maps_data(self):
        """Ingest Google Maps Popular Times data"""
        # Google Places API integration
        for property in self._get_properties_with_coordinates():
            lat, lng = property['coordinates']
            
            # Get place details including popular times
            place_id = await self._get_place_id(lat, lng)
            if place_id:
                popular_times = await self._get_popular_times(place_id)
                await self._store_foot_traffic_data(property['id'], popular_times)
    
    async def ingest_competitor_data(self):
        """Ingest competitor analysis data"""
        # Web scraping and API integration for competitor data
        competitors = await self._identify_competitors()
        
        for competitor in competitors:
            competitor_data = await self._analyze_competitor(competitor)
            await self._store_competitor_data(competitor_data)
    
    def _process_crexi_properties(self, data: Dict) -> List[Dict]:
        """Process Crexi API response into standardized format"""
        properties = []
        
        for item in data.get('properties', []):
            property_data = {
                'external_id': f"crexi_{item['id']}",
                'name': item.get('name', ''),
                'property_type': item.get('propertyType', ''),
                'asking_price': item.get('askingPrice'),
                'address': {
                    'street': item.get('address', {}).get('street'),
                    'city': item.get('address', {}).get('city'),
                    'state': item.get('address', {}).get('state'),
                    'zip': item.get('address', {}).get('zipCode'),
                    'county': item.get('address', {}).get('county')
                },
                'coordinates': self._geocode_address(item.get('address')),
                'size_acres': item.get('acres'),
                'building_sqft': item.get('buildingSqFt'),
                'year_built': item.get('yearBuilt'),
                'zoning': item.get('zoning'),
                'status': item.get('status'),
                'listing_url': item.get('url'),
                'thumbnail_url': item.get('imageUrl'),
                'description': item.get('description')
            }
            properties.append(property_data)
        
        return properties
```

### 3. **Market Analysis Engine**

```python
# backend/analysis/market_analyzer.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import geopandas as gpd
from shapely.geometry import Point
import logging

class MarketAnalyzer:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.logger = logging.getLogger(__name__)
    
    def analyze_market_trends(self, property_id: int) -> Dict[str, Any]:
        """Comprehensive market analysis for a property"""
        
        # Get property data
        property_data = self._get_property_data(property_id)
        
        # Perform various analyses
        market_analysis = {
            'property_info': property_data,
            'pricing_analysis': self._analyze_pricing_trends(property_id),
            'competitor_analysis': self._analyze_competitors(property_id),
            'risk_assessment': self._assess_risks(property_id),
            'foot_traffic_analysis': self._analyze_foot_traffic(property_id),
            'market_forecast': self._forecast_market_trends(property_id),
            'investment_recommendation': self._generate_investment_recommendation(property_id)
        }
        
        return market_analysis
    
    def _analyze_pricing_trends(self, property_id: int) -> Dict[str, Any]:
        """Analyze pricing trends and market positioning"""
        
        # Get historical pricing data
        query = """
        SELECT date, market_value, price_per_sqft, cap_rate
        FROM market_data 
        WHERE property_id = %s 
        ORDER BY date DESC
        """
        
        df = pd.read_sql(query, self.engine, params=[property_id])
        
        if df.empty:
            return {'error': 'No pricing data available'}
        
        # Calculate trends
        pricing_analysis = {
            'current_value': df.iloc[0]['market_value'],
            'price_trend': self._calculate_trend(df['market_value']),
            'price_per_sqft_trend': self._calculate_trend(df['price_per_sqft']),
            'cap_rate_trend': self._calculate_trend(df['cap_rate']),
            'market_positioning': self._analyze_market_positioning(property_id),
            'price_volatility': df['market_value'].std(),
            'recommended_pricing': self._recommend_pricing(property_id)
        }
        
        return pricing_analysis
    
    def _analyze_competitors(self, property_id: int) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        
        property_data = self._get_property_data(property_id)
        property_type = property_data['property_type']
        location = property_data['coordinates']
        
        # Find nearby competitors
        competitors_query = """
        SELECT p.*, c.competitor_type, c.market_share, c.pricing_strategy
        FROM properties p
        JOIN competitors c ON p.id = c.property_id
        WHERE p.property_type = %s 
        AND ST_DWithin(p.coordinates, ST_Point(%s, %s), 5000) -- 5km radius
        AND p.id != %s
        """
        
        competitors_df = pd.read_sql(
            competitors_query, 
            self.engine, 
            params=[property_type, location.x, location.y, property_id]
        )
        
        competitor_analysis = {
            'total_competitors': len(competitors_df),
            'direct_competitors': len(competitors_df[competitors_df['competitor_type'] == 'direct']),
            'average_competitor_price': competitors_df['asking_price'].mean(),
            'price_advantage': self._calculate_price_advantage(property_data, competitors_df),
            'market_share_analysis': self._analyze_market_share(competitors_df),
            'competitive_threats': self._identify_competitive_threats(competitors_df),
            'opportunities': self._identify_opportunities(property_data, competitors_df)
        }
        
        return competitor_analysis
    
    def _assess_risks(self, property_id: int) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        # Get crime data
        crime_query = """
        SELECT crime_type, severity, date
        FROM crime_data 
        WHERE ST_DWithin(location, (SELECT coordinates FROM properties WHERE id = %s), 1000)
        AND date >= CURRENT_DATE - INTERVAL '1 year'
        """
        
        crime_df = pd.read_sql(crime_query, self.engine, params=[property_id])
        
        # Calculate crime risk score
        crime_risk_score = self._calculate_crime_risk(crime_df)
        
        # Get environmental risks
        environmental_risks = self._assess_environmental_risks(property_id)
        
        # Get market risks
        market_risks = self._assess_market_risks(property_id)
        
        risk_assessment = {
            'crime_risk_score': crime_risk_score,
            'environmental_risks': environmental_risks,
            'market_risks': market_risks,
            'overall_risk_score': self._calculate_overall_risk_score(
                crime_risk_score, environmental_risks, market_risks
            ),
            'risk_factors': self._identify_risk_factors(crime_df, environmental_risks, market_risks),
            'mitigation_strategies': self._recommend_mitigation_strategies(crime_risk_score, environmental_risks, market_risks)
        }
        
        return risk_assessment
    
    def _analyze_foot_traffic(self, property_id: int) -> Dict[str, Any]:
        """Analyze foot traffic patterns and consumer behavior"""
        
        # Get foot traffic data
        traffic_query = """
        SELECT date, hour, visitor_count, dwell_time, demographics
        FROM foot_traffic 
        WHERE property_id = %s 
        AND date >= CURRENT_DATE - INTERVAL '3 months'
        ORDER BY date, hour
        """
        
        traffic_df = pd.read_sql(traffic_query, self.engine, params=[property_id])
        
        if traffic_df.empty:
            return {'error': 'No foot traffic data available'}
        
        # Analyze patterns
        foot_traffic_analysis = {
            'average_daily_visitors': traffic_df['visitor_count'].mean(),
            'peak_hours': self._identify_peak_hours(traffic_df),
            'dwell_time_analysis': self._analyze_dwell_time(traffic_df),
            'demographic_breakdown': self._analyze_demographics(traffic_df),
            'traffic_trends': self._analyze_traffic_trends(traffic_df),
            'seasonal_patterns': self._analyze_seasonal_patterns(traffic_df),
            'competitor_traffic_comparison': self._compare_competitor_traffic(property_id)
        }
        
        return foot_traffic_analysis
    
    def _forecast_market_trends(self, property_id: int) -> Dict[str, Any]:
        """Predict future market trends using ML models"""
        
        # Get historical data
        historical_data = self._get_historical_market_data(property_id)
        
        # Prepare features for ML model
        features = self._prepare_ml_features(historical_data)
        
        # Train forecasting model
        forecast_model = self._train_forecasting_model(features)
        
        # Generate predictions
        predictions = self._generate_predictions(forecast_model, features)
        
        market_forecast = {
            'price_forecast': predictions['price_forecast'],
            'demand_forecast': predictions['demand_forecast'],
            'risk_forecast': predictions['risk_forecast'],
            'confidence_interval': predictions['confidence_interval'],
            'key_drivers': predictions['key_drivers'],
            'scenario_analysis': self._generate_scenario_analysis(predictions)
        }
        
        return market_forecast
    
    def _generate_investment_recommendation(self, property_id: int) -> Dict[str, Any]:
        """Generate comprehensive investment recommendation"""
        
        # Gather all analysis results
        market_analysis = self.analyze_market_trends(property_id)
        
        # Calculate investment metrics
        investment_metrics = self._calculate_investment_metrics(property_id)
        
        # Generate recommendation
        recommendation = {
            'investment_score': self._calculate_investment_score(market_analysis),
            'recommendation': self._generate_recommendation_text(market_analysis),
            'key_risks': market_analysis['risk_assessment']['risk_factors'],
            'key_opportunities': market_analysis['competitor_analysis']['opportunities'],
            'expected_roi': investment_metrics['expected_roi'],
            'payback_period': investment_metrics['payback_period'],
            'investment_timeline': self._recommend_investment_timeline(market_analysis),
            'action_items': self._generate_action_items(market_analysis)
        }
        
        return recommendation
```

### 4. **Enhanced API Endpoints**

```python
# backend/api/enhanced_endpoints.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import asyncio

router = APIRouter()

@router.get("/analysis/{property_id}")
async def get_property_analysis(property_id: int):
    """Get comprehensive property analysis"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        analysis = analyzer.analyze_market_trends(property_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitors/{property_id}")
async def get_competitor_analysis(property_id: int, radius: float = 5.0):
    """Get competitor analysis for a property"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        competitors = analyzer._analyze_competitors(property_id)
        return competitors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-assessment/{property_id}")
async def get_risk_assessment(property_id: int):
    """Get comprehensive risk assessment"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        risks = analyzer._assess_risks(property_id)
        return risks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/foot-traffic/{property_id}")
async def get_foot_traffic_analysis(property_id: int, days: int = 90):
    """Get foot traffic analysis"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        traffic = analyzer._analyze_foot_traffic(property_id)
        return traffic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-forecast/{property_id}")
async def get_market_forecast(property_id: int, months: int = 12):
    """Get market forecast for a property"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        forecast = analyzer._forecast_market_trends(property_id)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/investment-recommendation/{property_id}")
async def get_investment_recommendation(property_id: int):
    """Get investment recommendation"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        recommendation = analyzer._generate_investment_recommendation(property_id)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-intelligence")
async def get_market_intelligence(
    property_type: Optional[str] = None,
    location: Optional[str] = None,
    radius: float = 10.0
):
    """Get market intelligence for a specific area/type"""
    try:
        analyzer = MarketAnalyzer(DATABASE_URL)
        intelligence = analyzer.get_market_intelligence(property_type, location, radius)
        return intelligence
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5. **Enhanced Frontend Dashboard**

```jsx
// frontend/src/components/AnalysisDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './UI/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './UI/Tabs';
import { MarketAnalysis } from './Analysis/MarketAnalysis';
import { CompetitorAnalysis } from './Analysis/CompetitorAnalysis';
import { RiskAssessment } from './Analysis/RiskAssessment';
import { FootTrafficAnalysis } from './Analysis/FootTrafficAnalysis';
import { InvestmentRecommendation } from './Analysis/InvestmentRecommendation';

const AnalysisDashboard = ({ propertyId }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalysisData();
  }, [propertyId]);

  const fetchAnalysisData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analysis/${propertyId}`);
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Error fetching analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Investment Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {analysisData?.investment_recommendation?.investment_score || 0}/100
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {analysisData?.risk_assessment?.overall_risk_score || 0}/100
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Competitors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {analysisData?.competitor_analysis?.total_competitors || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Visitors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {analysisData?.foot_traffic_analysis?.average_daily_visitors || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="market">Market Analysis</TabsTrigger>
          <TabsTrigger value="competitors">Competitors</TabsTrigger>
          <TabsTrigger value="risks">Risk Assessment</TabsTrigger>
          <TabsTrigger value="traffic">Foot Traffic</TabsTrigger>
          <TabsTrigger value="investment">Investment</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MarketAnalysis data={analysisData?.pricing_analysis} />
            <RiskAssessment data={analysisData?.risk_assessment} />
          </div>
        </TabsContent>

        <TabsContent value="market">
          <MarketAnalysis data={analysisData?.pricing_analysis} />
        </TabsContent>

        <TabsContent value="competitors">
          <CompetitorAnalysis data={analysisData?.competitor_analysis} />
        </TabsContent>

        <TabsContent value="risks">
          <RiskAssessment data={analysisData?.risk_assessment} />
        </TabsContent>

        <TabsContent value="traffic">
          <FootTrafficAnalysis data={analysisData?.foot_traffic_analysis} />
        </TabsContent>

        <TabsContent value="investment">
          <InvestmentRecommendation data={analysisData?.investment_recommendation} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalysisDashboard;
```

---

## 🚀 **Implementation Roadmap**

### Phase 1: Data Infrastructure (Weeks 1-4)
- [ ] Set up enhanced database schema
- [ ] Implement data ingestion pipelines
- [ ] Integrate core data sources (Crexi, Zillow, etc.)
- [ ] Set up ETL processes with Apache Airflow

### Phase 2: Market Analysis Engine (Weeks 5-8)
- [ ] Build market analysis algorithms
- [ ] Implement competitor analysis
- [ ] Create risk assessment models
- [ ] Develop pricing trend analysis

### Phase 3: Advanced Analytics (Weeks 9-12)
- [ ] Implement foot traffic analysis
- [ ] Build predictive models
- [ ] Create investment recommendation engine
- [ ] Develop real-time monitoring

### Phase 4: Frontend Enhancement (Weeks 13-16)
- [ ] Build analysis dashboard
- [ ] Implement interactive maps
- [ ] Create data visualization components
- [ ] Add real-time updates

### Phase 5: Production & Optimization (Weeks 17-20)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Monitoring and alerting
- [ ] User testing and feedback

---

This comprehensive plan transforms your MIPA system into a sophisticated real estate analysis platform with competitive intelligence, risk assessment, and market forecasting capabilities. The system will provide actionable insights for real estate investment decisions based on comprehensive data analysis.
