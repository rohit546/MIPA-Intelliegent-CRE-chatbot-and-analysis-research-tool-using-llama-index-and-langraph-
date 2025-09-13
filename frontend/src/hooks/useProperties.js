import { useState, useEffect } from 'react';
import { fetchProperties } from '../services/propertyService';

const useProperties = () => {
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadProperties = async () => {
            try {
                setLoading(true);
                const data = await fetchProperties();
                setProperties(data);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        loadProperties();
    }, []);

    return { properties, loading, error };
};

export default useProperties;