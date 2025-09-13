import React, { useState } from 'react';

const AddressDetailsMode = () => {
    const [address, setAddress] = useState('');
    const [propertyDetails, setPropertyDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFetchDetails = async () => {
        if (!address.trim()) return;

        setIsLoading(true);
        
        // TODO: Connect to backend API
        setTimeout(() => {
            setPropertyDetails({
                address: address,
                type: 'Commercial Property',
                price: '$450,000',
                size: '2.5 acres',
                zoning: 'C-2 Commercial',
                details: 'Sample property details. Backend integration coming soon!'
            });
            setIsLoading(false);
        }, 1500);
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
                    <p>Fetching property details...</p>
                </div>
            )}

            {propertyDetails && !isLoading && (
                <div className="property-details">
                    <h4>Property Information</h4>
                    <div className="details-grid">
                        <div className="detail-item">
                            <strong>Address:</strong> {propertyDetails.address}
                        </div>
                        <div className="detail-item">
                            <strong>Type:</strong> {propertyDetails.type}
                        </div>
                        <div className="detail-item">
                            <strong>Price:</strong> {propertyDetails.asking_price}
                        </div>
                        <div className="detail-item">
                            <strong>Size:</strong> {propertyDetails.size}
                        </div>
                        <div className="detail-item">
                            <strong>Zoning:</strong> {propertyDetails.zoning}
                        </div>
                        <div className="detail-item">
                            <strong>Details:</strong> {propertyDetails.details}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AddressDetailsMode;