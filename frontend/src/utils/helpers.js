function formatAddress(address) {
    if (!address) return 'N/A';
    return `${address.street}, ${address.city}, ${address.state} ${address.zip}`;
}

function formatPrice(price) {
    if (price >= 1000000) {
        return `$${(price / 1000000).toFixed(2)}M`;
    } else if (price >= 1000) {
        return `$${(price / 1000).toFixed(0)}K`;
    }
    return `$${price.toFixed(2)}`;
}

function formatSize(size, unit) {
    return size ? `${size} ${unit}` : 'N/A';
}

function getPropertyType(property) {
    return property.property_type || 'Unknown Type';
}

function getPropertySubtype(property) {
    return property.property_subtype || 'Unknown Subtype';
}

export {
    formatAddress,
    formatPrice,
    formatSize,
    getPropertyType,
    getPropertySubtype
};