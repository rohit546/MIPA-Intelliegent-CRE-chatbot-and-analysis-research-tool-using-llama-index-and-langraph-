import React, { useState } from 'react';

const AddressDetailsMode = () => {
    const [address, setAddress] = useState('');
    const [propertyDetails, setPropertyDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFetchDetails = async () => {
        if (!address.trim()) return;

        setIsLoading(true);
        setError(null);
        setPropertyDetails(null);

        try {
            const response = await fetch('http://localhost:8003/address-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ address: address }),
            });

            const data = await response.json();

            if (response.ok) {
                setPropertyDetails(data);
            } else {
                setError(data.detail || 'Failed to analyze address');
            }
        } catch (err) {
            setError('Network error. Please check if the backend is running.');
            console.error('Address analysis error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="address-mode">
            <div className="address-input-section">
                <h3>Property Address Lookup</h3>
                <div className="address-input">
                    <input
                        type="text"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        placeholder="Enter property address..."
                        onKeyPress={(e) => e.key === 'Enter' && handleFetchDetails()}
                    />
                    <button onClick={handleFetchDetails} disabled={!address.trim()}>
                        Get Details
                    </button>
                </div>
            </div>

            {isLoading && (
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Analyzing address with Smarty API...</p>
                </div>
            )}

            {error && (
                <div className="error-message">
                    <h4>Error</h4>
                    <p>{error}</p>
                </div>
            )}

            {propertyDetails && !isLoading && (
                <div className="property-details">
                    <h4>Address Analysis Results</h4>
                    
                    {/* Basic Address Information */}
                    <div className="address-section">
                        <h5>Verified Address</h5>
                        <div className="detail-item">
                            <strong>Address:</strong> {propertyDetails.formatted_address}
                        </div>
                        <div className="detail-item">
                            <strong>City:</strong> {propertyDetails.city}
                        </div>
                        <div className="detail-item">
                            <strong>State:</strong> {propertyDetails.state}
                        </div>
                        <div className="detail-item">
                            <strong>ZIP Code:</strong> {propertyDetails.zip_code}
                        </div>
                        <div className="detail-item">
                            <strong>County:</strong> {propertyDetails.county}
                        </div>
                    </div>

                    {/* Property Information */}
                    {propertyDetails.property_info && (
                        <div className="property-section">
                            <h5>Property Details</h5>
                            
                            {/* Owner Information */}
                            {propertyDetails.property_info.owner_name && propertyDetails.property_info.owner_name !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Owner:</strong> {propertyDetails.property_info.owner_name}
                                </div>
                            )}
                            {propertyDetails.property_info.ownership_type && propertyDetails.property_info.ownership_type !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Ownership Type:</strong> {propertyDetails.property_info.ownership_type}
                                </div>
                            )}
                            {propertyDetails.property_info.owner_occupancy_status && propertyDetails.property_info.owner_occupancy_status !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Owner Occupancy:</strong> {propertyDetails.property_info.owner_occupancy_status}
                                </div>
                            )}
                            
                            {/* Property Type and Use */}
                            {propertyDetails.property_info.property_type && propertyDetails.property_info.property_type !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Property Type:</strong> {propertyDetails.property_info.property_type}
                                </div>
                            )}
                            {propertyDetails.property_info.land_use && propertyDetails.property_info.land_use !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Land Use Code:</strong> {propertyDetails.property_info.land_use}
                                </div>
                            )}
                            {propertyDetails.property_info.zoning && propertyDetails.property_info.zoning !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Zoning:</strong> {propertyDetails.property_info.zoning}
                                </div>
                            )}
                            
                            {/* Building Information */}
                            {propertyDetails.property_info.year_built && propertyDetails.property_info.year_built !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Year Built:</strong> {propertyDetails.property_info.year_built}
                                </div>
                            )}
                            {propertyDetails.property_info.building_sqft && propertyDetails.property_info.building_sqft !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Building Area:</strong> {propertyDetails.property_info.building_sqft} sq ft
                                </div>
                            )}
                            {propertyDetails.property_info.gross_sqft && propertyDetails.property_info.gross_sqft !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Gross Area:</strong> {propertyDetails.property_info.gross_sqft} sq ft
                                </div>
                            )}
                            
                            {/* Lot Information */}
                            {propertyDetails.property_info.lot_sqft && propertyDetails.property_info.lot_sqft !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Lot Size:</strong> {propertyDetails.property_info.lot_sqft} sq ft
                                </div>
                            )}
                            {propertyDetails.property_info.acres && propertyDetails.property_info.acres !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Acres:</strong> {propertyDetails.property_info.acres}
                                </div>
                            )}
                            {propertyDetails.property_info.width_linear_footage && propertyDetails.property_info.width_linear_footage !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Width:</strong> {propertyDetails.property_info.width_linear_footage} ft
                                </div>
                            )}
                            
                            {/* Features */}
                            {propertyDetails.property_info.fireplace && propertyDetails.property_info.fireplace !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Fireplace:</strong> {propertyDetails.property_info.fireplace}
                                    {propertyDetails.property_info.fireplace_number && propertyDetails.property_info.fireplace_number !== 'Not available' && 
                                        ` (${propertyDetails.property_info.fireplace_number})`
                                    }
                                </div>
                            )}
                            {propertyDetails.property_info.heat && propertyDetails.property_info.heat !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Heating:</strong> {propertyDetails.property_info.heat}
                                </div>
                            )}
                            {propertyDetails.property_info.parking_spaces && propertyDetails.property_info.parking_spaces !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Parking Spaces:</strong> {propertyDetails.property_info.parking_spaces}
                                </div>
                            )}
                            
                            {/* Administrative */}
                            {propertyDetails.property_info.parcel_number && propertyDetails.property_info.parcel_number !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Parcel Number:</strong> {propertyDetails.property_info.parcel_number}
                                </div>
                            )}
                            {propertyDetails.property_info.elevation_feet && propertyDetails.property_info.elevation_feet !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Elevation:</strong> {propertyDetails.property_info.elevation_feet} ft
                                </div>
                            )}
                            {propertyDetails.property_info.legal_description && propertyDetails.property_info.legal_description !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Legal Description:</strong> {propertyDetails.property_info.legal_description}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Financial Information */}
                    {propertyDetails.financial_info && (
                        <div className="financial-section">
                            <h5>Financial Information</h5>
                            
                            {/* Market Values */}
                            {propertyDetails.financial_info.market_value && (
                                <div className="detail-item">
                                    <strong>Total Market Value:</strong> {propertyDetails.financial_info.market_value}
                                </div>
                            )}
                            {propertyDetails.financial_info.market_improvement_value && (
                                <div className="detail-item">
                                    <strong>Market Improvement Value:</strong> {propertyDetails.financial_info.market_improvement_value}
                                </div>
                            )}
                            {propertyDetails.financial_info.market_land_value && (
                                <div className="detail-item">
                                    <strong>Market Land Value:</strong> {propertyDetails.financial_info.market_land_value}
                                </div>
                            )}
                            
                            {/* Assessed Values */}
                            {propertyDetails.financial_info.assessed_value && (
                                <div className="detail-item">
                                    <strong>Assessed Value:</strong> {propertyDetails.financial_info.assessed_value}
                                </div>
                            )}
                            {propertyDetails.financial_info.assessed_improvement_value && (
                                <div className="detail-item">
                                    <strong>Assessed Improvement Value:</strong> {propertyDetails.financial_info.assessed_improvement_value}
                                </div>
                            )}
                            {propertyDetails.financial_info.assessed_land_value && (
                                <div className="detail-item">
                                    <strong>Assessed Land Value:</strong> {propertyDetails.financial_info.assessed_land_value}
                                </div>
                            )}
                            
                            {/* Sale History */}
                            {propertyDetails.financial_info.deed_sale_price && (
                                <div className="detail-item">
                                    <strong>Latest Sale Price:</strong> {propertyDetails.financial_info.deed_sale_price}
                                </div>
                            )}
                            {propertyDetails.financial_info.deed_sale_date && propertyDetails.financial_info.deed_sale_date !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Latest Sale Date:</strong> {propertyDetails.financial_info.deed_sale_date}
                                </div>
                            )}
                            {propertyDetails.financial_info.prior_sale_amount && (
                                <div className="detail-item">
                                    <strong>Prior Sale Price:</strong> {propertyDetails.financial_info.prior_sale_amount}
                                </div>
                            )}
                            {propertyDetails.financial_info.prior_sale_date && propertyDetails.financial_info.prior_sale_date !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Prior Sale Date:</strong> {propertyDetails.financial_info.prior_sale_date}
                                </div>
                            )}
                            
                            {/* Tax Information */}
                            {propertyDetails.financial_info.tax_billed_amount && (
                                <div className="detail-item">
                                    <strong>Annual Tax Bill:</strong> {propertyDetails.financial_info.tax_billed_amount}
                                </div>
                            )}
                            {propertyDetails.financial_info.tax_assess_year && propertyDetails.financial_info.tax_assess_year !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Tax Assessment Year:</strong> {propertyDetails.financial_info.tax_assess_year}
                                </div>
                            )}
                            
                            {/* Mortgage Information */}
                            {propertyDetails.financial_info.mortgage_amount && (
                                <div className="detail-item">
                                    <strong>Mortgage Amount:</strong> {propertyDetails.financial_info.mortgage_amount}
                                </div>
                            )}
                            {propertyDetails.financial_info.lender_name && propertyDetails.financial_info.lender_name !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Lender:</strong> {propertyDetails.financial_info.lender_name}
                                </div>
                            )}
                            {propertyDetails.financial_info.mortgage_due_date && propertyDetails.financial_info.mortgage_due_date !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Mortgage Due Date:</strong> {propertyDetails.financial_info.mortgage_due_date}
                                </div>
                            )}
                            {propertyDetails.financial_info.mortgage_type && propertyDetails.financial_info.mortgage_type !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Mortgage Type:</strong> {propertyDetails.financial_info.mortgage_type}
                                </div>
                            )}
                            {propertyDetails.financial_info.mortgage_term && propertyDetails.financial_info.mortgage_term !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Mortgage Term:</strong> {propertyDetails.financial_info.mortgage_term} {propertyDetails.financial_info.mortgage_term_type}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Location Information */}
                    {propertyDetails.location_info && (
                        <div className="location-section">
                            <h5>Location & Demographics</h5>
                            
                            {/* Geographic Coordinates */}
                            {propertyDetails.location_info.latitude && propertyDetails.location_info.latitude !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Coordinates:</strong> {propertyDetails.location_info.latitude}, {propertyDetails.location_info.longitude}
                                </div>
                            )}
                            
                            {/* Administrative Areas */}
                            {propertyDetails.location_info.county && propertyDetails.location_info.county !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>County:</strong> {propertyDetails.location_info.county}
                                </div>
                            )}
                            {propertyDetails.location_info.congressional_district && propertyDetails.location_info.congressional_district !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Congressional District:</strong> {propertyDetails.location_info.congressional_district}
                                </div>
                            )}
                            {propertyDetails.location_info.minor_civil_division_name && propertyDetails.location_info.minor_civil_division_name !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Municipality:</strong> {propertyDetails.location_info.minor_civil_division_name}
                                </div>
                            )}
                            
                            {/* Census Data */}
                            {propertyDetails.location_info.census_tract && propertyDetails.location_info.census_tract !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Census Tract:</strong> {propertyDetails.location_info.census_tract}
                                </div>
                            )}
                            {propertyDetails.location_info.census_block && propertyDetails.location_info.census_block !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Census Block:</strong> {propertyDetails.location_info.census_block}
                                </div>
                            )}
                            
                            {/* Metropolitan Areas */}
                            {propertyDetails.location_info.cbsa_name && propertyDetails.location_info.cbsa_name !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Metro Area:</strong> {propertyDetails.location_info.cbsa_name}
                                </div>
                            )}
                            {propertyDetails.location_info.msa_name && propertyDetails.location_info.msa_name !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>MSA:</strong> {propertyDetails.location_info.msa_name}
                                </div>
                            )}
                            {propertyDetails.location_info.combined_statistical_area && propertyDetails.location_info.combined_statistical_area !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>Combined Statistical Area:</strong> {propertyDetails.location_info.combined_statistical_area}
                                </div>
                            )}
                            
                            {/* Codes */}
                            {propertyDetails.location_info.fips_code && propertyDetails.location_info.fips_code !== 'Not available' && (
                                <div className="detail-item">
                                    <strong>FIPS Code:</strong> {propertyDetails.location_info.fips_code}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Investment Analysis */}
                    {propertyDetails.investment_analysis && (
                        <div className="investment-section">
                            <h5>Investment Analysis</h5>
                            {propertyDetails.investment_analysis.investment_score !== undefined && (
                                <div className="detail-item">
                                    <strong>Investment Score:</strong> {propertyDetails.investment_analysis.investment_score}/10
                                </div>
                            )}
                            {propertyDetails.investment_analysis.rental_potential && (
                                <div className="detail-item">
                                    <strong>Rental Potential:</strong> {propertyDetails.investment_analysis.rental_potential}
                                </div>
                            )}
                            {propertyDetails.investment_analysis.appreciation_potential && (
                                <div className="detail-item">
                                    <strong>Appreciation Potential:</strong> {propertyDetails.investment_analysis.appreciation_potential}
                                </div>
                            )}
                            {propertyDetails.investment_analysis.liquidity && (
                                <div className="detail-item">
                                    <strong>Liquidity:</strong> {propertyDetails.investment_analysis.liquidity}
                                </div>
                            )}
                            {propertyDetails.investment_analysis.analysis && (
                                <div className="detail-item analysis-text">
                                    <strong>Analysis:</strong>
                                    <pre>{propertyDetails.investment_analysis.analysis}</pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AddressDetailsMode;