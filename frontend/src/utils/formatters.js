export const formatPrice = (price) => {
    if (price >= 1000000) {
        return `$${(price / 1000000).toFixed(2)}M`;
    } else if (price >= 1000) {
        return `$${(price / 1000).toFixed(0)}K`;
    }
    return `$${price.toFixed(2)}`;
};

export const formatAddress = (address) => {
    try {
        const addr = JSON.parse(address);
        return `${addr.street}, ${addr.city}, ${addr.county} ${addr.zip}`;
    } catch (error) {
        return address; // Fallback to raw address if parsing fails
    }
};

export const formatSize = (sizeAcres, sizeSqft) => {
    const sizeInfo = [];
    if (sizeAcres > 0) {
        sizeInfo.push(`${sizeAcres} acres`);
    }
    if (sizeSqft > 0) {
        sizeInfo.push(`${sizeSqft.toLocaleString()} sqft`);
    }
    return sizeInfo.join(' • ');
};