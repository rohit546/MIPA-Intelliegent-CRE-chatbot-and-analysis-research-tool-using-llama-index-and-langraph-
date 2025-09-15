import requests
import logging
from typing import Optional, Dict, List, Any
import json

class SmartyAddressAnalyzer:
    def __init__(self, auth_id: str, auth_token: str):
        """Initialize the Smarty Street Address Analyzer"""
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.base_url = "https://us-enrichment.api.smarty.com"
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _validate_address(self, address: str) -> Optional[Dict]:
        """Validate address using property lookup (which also validates)"""
        try:
            url = f"{self.base_url}/lookup/search/property/principal"
            params = {
                "freeform": address,
                "auth-id": self.auth_id,
                "auth-token": self.auth_token
            }
            
            self.logger.info(f"Making request to: {url}")
            self.logger.info(f"With params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            
            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                self.logger.error("Authentication failed - check credentials")
                return None
                
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except Exception as e:
            self.logger.error(f"Address validation error: {str(e)}")
            return None

    def analyze_address(self, address: str) -> Dict[str, Any]:
        """Main method to analyze an address and return comprehensive results"""
        try:
            self.logger.info(f"Analyzing address: {address}")
            
            # First validate the address
            validated_address = self._validate_address(address)
            if not validated_address:
                return {
                    "formatted_address": address,
                    "city": "",
                    "state": "",
                    "zip_code": "",
                    "county": None,
                    "property_info": None,
                    "financial_info": None,
                    "risk_analysis": None,
                    "investment_analysis": {
                        "investment_score": 0,
                        "analysis": "ADDRESS VALIDATION FAILED\n\nThe address could not be validated. Please check:\n- Street number and name\n- City and state\n- ZIP code\n\nExample: '123 Main St, Atlanta, GA 30309'"
                    }
                }
            
            # Get enrichment data from Smarty API
            property_data = self._get_property_data(address)
            risk_data = self._get_risk_data(address)
            
            # Parse the response data
            parsed_data = self._parse_smarty_response(property_data, risk_data, address)
            
            # Extract address components from validated data
            matched_address = validated_address.get('matched_address', {})
            
            return {
                "formatted_address": f"{matched_address.get('street', '')} {matched_address.get('city', '')} {matched_address.get('state', '')} {matched_address.get('zipcode', '')}".strip(),
                "city": matched_address.get('city', ''),
                "state": matched_address.get('state', ''),
                "zip_code": matched_address.get('zipcode', ''),
                "county": parsed_data.get('location_info', {}).get('county', ''),
                "property_info": parsed_data.get('property_info', {}),
                "financial_info": parsed_data.get('financial_info', {}),
                "location_info": parsed_data.get('location_info', {}),
                "investment_analysis": {
                    "investment_score": parsed_data.get('investment_score', 0),
                    "analysis": self._format_analysis_results(address, parsed_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Address analysis error: {str(e)}")
            return {
                "formatted_address": address,
                "city": "",
                "state": "",
                "zip_code": "",
                "county": None,
                "property_info": None,
                "financial_info": None,
                "risk_analysis": None,
                "investment_analysis": {
                    "investment_score": 0,
                    "analysis": f"ADDRESS ANALYSIS ERROR\n\nWe couldn't analyze this address. This might be because:\n- The address format is incomplete or invalid\n- The property data is not available in our database\n- There was a temporary service issue\n\nPlease try:\n- Double-checking the address format\n- Including city and state\n- Trying a different address\n\nError details: {str(e)}"
                }
            }

    def _get_property_data(self, address: str) -> Optional[Dict]:
        """Get property enrichment data from Smarty API"""
        try:
            url = f"{self.base_url}/lookup/search/property/principal"
            params = {
                "freeform": address,
                "auth-id": self.auth_id,
                "auth-token": self.auth_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except Exception as e:
            self.logger.error(f"Property data error: {str(e)}")
            return None

    def _get_risk_data(self, address: str) -> Optional[Dict]:
        """Get risk assessment data from Smarty API"""
        try:
            url = f"{self.base_url}/lookup/search/risk"
            params = {
                "freeform": address,
                "auth-id": self.auth_id,
                "auth-token": self.auth_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except Exception as e:
            self.logger.error(f"Risk data error: {str(e)}")
            return None

    def _parse_smarty_response(self, property_data: Optional[Dict], risk_data: Optional[Dict], address: str) -> Dict[str, Any]:
        """Parse Smarty API response data into structured format"""
        parsed = {
            "address": address,
            "property_info": {},
            "financial_info": {},
            "investment_score": 50
        }

        # Parse property data - using actual field names from Smarty API
        if property_data and 'attributes' in property_data:
            attributes = property_data['attributes']
            
            # Comprehensive Property information
            parsed["property_info"] = {
                "owner_name": attributes.get('deed_owner_full_name', attributes.get('owner_full_name', 'Not available')),
                "property_type": attributes.get('land_use_standard', attributes.get('land_use_group', 'Not available')),
                "land_use": attributes.get('land_use_code', 'Not available'),
                "building_sqft": self._format_number(attributes.get('building_sqft')),
                "gross_sqft": self._format_number(attributes.get('gross_sqft')),
                "lot_sqft": self._format_number(attributes.get('lot_sqft')),
                "acres": attributes.get('acres', 'Not available'),
                "year_built": attributes.get('year_built', 'Not available'),
                "zoning": attributes.get('zoning', 'Not available'),
                "fireplace": attributes.get('fireplace', 'Not available'),
                "fireplace_number": attributes.get('fireplace_number', 'Not available'),
                "heat": attributes.get('heat', 'Not available'),
                "parking_spaces": attributes.get('parking_spaces', 'Not available'),
                "elevation_feet": attributes.get('elevation_feet', 'Not available'),
                "width_linear_footage": attributes.get('width_linear_footage', 'Not available'),
                "parcel_number": attributes.get('parcel_raw_number', 'Not available'),
                "legal_description": attributes.get('legal_description', 'Not available'),
                "neighborhood_code": attributes.get('neighborhood_code', 'Not available'),
                "company_flag": attributes.get('company_flag', 'Not available'),
                "ownership_type": attributes.get('ownership_type', 'Not available'),
                "owner_occupancy_status": attributes.get('owner_occupancy_status', 'Not available')
            }
            
            # Financial information with actual field names
            parsed["financial_info"] = {
                "market_value": self._safe_currency(attributes.get('total_market_value')),
                "assessed_value": self._safe_currency(attributes.get('assessed_value')),
                "assessed_improvement_value": self._safe_currency(attributes.get('assessed_improvement_value')),
                "assessed_land_value": self._safe_currency(attributes.get('assessed_land_value')),
                "market_improvement_value": self._safe_currency(attributes.get('market_improvement_value')),
                "market_land_value": self._safe_currency(attributes.get('market_land_value')),
                "sale_amount": self._safe_currency(attributes.get('sale_amount')),
                "sale_date": attributes.get('sale_date', 'Not available'),
                "deed_sale_price": self._safe_currency(attributes.get('deed_sale_price')),
                "deed_sale_date": attributes.get('deed_sale_date', 'Not available'),
                "prior_sale_amount": self._safe_currency(attributes.get('prior_sale_amount')),
                "prior_sale_date": attributes.get('prior_sale_date', 'Not available'),
                "transfer_amount": self._safe_currency(attributes.get('transfer_amount')),
                "tax_billed_amount": self._safe_currency(attributes.get('tax_billed_amount')),
                "tax_assess_year": attributes.get('tax_assess_year', 'Not available'),
                "tax_fiscal_year": attributes.get('tax_fiscal_year', 'Not available'),
                "mortgage_amount": self._safe_currency(attributes.get('mortgage_amount')),
                "mortgage_due_date": attributes.get('mortgage_due_date', 'Not available'),
                "mortgage_lender_code": attributes.get('mortgage_lender_code', 'Not available'),
                "lender_name": attributes.get('lender_name', 'Not available'),
                "mortgage_recording_date": attributes.get('mortgage_recording_date', 'Not available'),
                "mortgage_term": attributes.get('mortgage_term', 'Not available'),
                "mortgage_term_type": attributes.get('mortgage_term_type', 'Not available'),
                "mortgage_type": attributes.get('mortgage_type', 'Not available'),
                "assessed_improvement_percent": attributes.get('assessed_improvement_percent', 'Not available'),
                "market_improvement_percent": attributes.get('market_improvement_percent', 'Not available')
            }

            # Location and Administrative data
            parsed["location_info"] = {
                "latitude": attributes.get('latitude', 'Not available'),
                "longitude": attributes.get('longitude', 'Not available'),
                "fips_code": attributes.get('fips_code', 'Not available'),
                "county": attributes.get('situs_county', 'Not available'),
                "state": attributes.get('situs_state', 'Not available'),
                "census_tract": attributes.get('census_tract', 'Not available'),
                "census_block": attributes.get('census_block', 'Not available'),
                "census_block_group": attributes.get('census_block_group', 'Not available'),
                "congressional_district": attributes.get('congressional_district', 'Not available'),
                "cbsa_code": attributes.get('cbsa_code', 'Not available'),
                "cbsa_name": attributes.get('cbsa_name', 'Not available'),
                "msa_code": attributes.get('msa_code', 'Not available'),
                "msa_name": attributes.get('msa_name', 'Not available'),
                "combined_statistical_area": attributes.get('combined_statistical_area', 'Not available'),
                "minor_civil_division_name": attributes.get('minor_civil_division_name', 'Not available')
            }

        return parsed

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        try:
            return int(float(str(value).replace(',', '').replace('$', '')))
        except (ValueError, TypeError):
            return None

    def _safe_currency(self, value) -> Optional[str]:
        """Safely format currency value"""
        if value is None or value == '':
            return None
        try:
            amount = int(float(str(value).replace(',', '').replace('$', '')))
            return f"${amount:,}"
        except (ValueError, TypeError):
            return str(value) if value else None

    def _format_number(self, value) -> str:
        """Format number with commas"""
        if value is None or value == '':
            return 'Not available'
        try:
            number = int(float(str(value).replace(',', '')))
            return f"{number:,}"
        except (ValueError, TypeError):
            return str(value) if value else 'Not available'

    def _get_risk_level(self, risk_data) -> str:
        """Get risk level from risk data"""
        if not risk_data:
            return "Not available"
        
        if isinstance(risk_data, dict):
            level = risk_data.get('risk_level', 'Unknown')
            return f"{level} ({risk_data.get('risk_score', 'N/A')})"
        
        return str(risk_data)

    def _calculate_investment_score(self, data: Dict[str, Any]) -> int:
        """Calculate investment potential score (1-100)"""
        score = 50  # Base score
        
        financial = data.get("financial_info", {})
        property_info = data.get("property_info", {})
        risks = data.get("risk_assessment", {})
        
        # Adjust based on financial data
        if financial.get("market_value") and financial.get("assessed_value"):
            if financial["market_value"] > financial["assessed_value"]:
                score += 10
        
        if financial.get("last_sale_price") and financial.get("market_value"):
            if financial["market_value"] > financial["last_sale_price"]:
                score += 15
        
        # Adjust based on property characteristics
        year_built = property_info.get("year_built")
        if year_built and str(year_built).isdigit():
            if int(year_built) > 2000:
                score += 10
            elif int(year_built) > 1980:
                score += 5
        
        # Adjust based on risk factors
        for risk_type, risk_level in risks.items():
            if "low" in str(risk_level).lower():
                score += 2
            elif "high" in str(risk_level).lower():
                score -= 5
        
        return max(1, min(100, score))

    def _format_analysis_results(self, address: str, data: Dict[str, Any]) -> str:
        """Format analysis results into readable text"""
        sections = []
        
        # Header
        sections.append(f"PROPERTY ANALYSIS RESULTS\n\nAddress: {address}")
        
        # Property Information
        if data.get("property_info"):
            prop_info = data["property_info"]
            sections.append("PROPERTY DETAILS")
            sections.append(f"Owner: {prop_info.get('owner_name', 'Not available')}")
            sections.append(f"Property Type: {prop_info.get('property_type', 'Not available')}")
            sections.append(f"Year Built: {prop_info.get('year_built', 'Not available')}")
            sections.append(f"Building Area: {prop_info.get('building_sqft', 'Not available')} sq ft")
            sections.append(f"Lot Size: {prop_info.get('lot_sqft', 'Not available')} sq ft")
            sections.append(f"Acres: {prop_info.get('acres', 'Not available')}")
            sections.append(f"Zoning: {prop_info.get('zoning', 'Not available')}")
        
        # Financial Information
        if data.get("financial_info"):
            fin_info = data["financial_info"]
            sections.append("\nFINANCIAL OVERVIEW")
            if fin_info.get("market_value"):
                sections.append(f"Market Value: {fin_info['market_value']}")
            if fin_info.get("assessed_value"):
                sections.append(f"Assessed Value: {fin_info['assessed_value']}")
            if fin_info.get("deed_sale_price"):
                sections.append(f"Last Sale Price: {fin_info['deed_sale_price']}")
            if fin_info.get("deed_sale_date"):
                sections.append(f"Last Sale Date: {fin_info['deed_sale_date']}")
            if fin_info.get("tax_billed_amount"):
                sections.append(f"Annual Taxes: {fin_info['tax_billed_amount']}")
            if fin_info.get("mortgage_amount"):
                sections.append(f"Mortgage Amount: {fin_info['mortgage_amount']}")
            if fin_info.get("lender_name"):
                sections.append(f"Lender: {fin_info['lender_name']}")
        
        # Location Information
        if data.get("location_info"):
            loc_info = data["location_info"]
            sections.append("\nLOCATION DETAILS")
            if loc_info.get("county"):
                sections.append(f"County: {loc_info['county']}")
            if loc_info.get("cbsa_name"):
                sections.append(f"Metro Area: {loc_info['cbsa_name']}")
            if loc_info.get("latitude") and loc_info.get("longitude"):
                sections.append(f"Coordinates: {loc_info['latitude']}, {loc_info['longitude']}")
        
        # Investment Score
        score = data.get("investment_score", 50)
        sections.append(f"\nINVESTMENT SCORE: {score}/100")
        
        if score >= 70:
            sections.append("✓ Strong investment potential")
        elif score >= 50:
            sections.append("~ Moderate investment potential")
        else:
            sections.append("⚠ Lower investment potential - review carefully")
        
        return "\n".join(sections)
