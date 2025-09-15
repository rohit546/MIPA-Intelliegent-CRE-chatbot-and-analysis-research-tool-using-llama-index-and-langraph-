import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { PropertyCard } from './PropertyCard';
import { PropertyCardSkeleton } from '../UI/Skeleton';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';
import { Card, CardContent, CardHeader, CardTitle } from '../UI/Card';
import { fetchProperties } from '../../services/api';

interface Property {
  id: number;
  name?: string;
  property_type?: string;
  asking_price?: number;
  size_acres?: number;
  address?: {
    fullAddress?: string;
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
  };
  thumbnail_url?: string;
  description?: string;
  status?: string;
  listing_url?: string;
  zoning?: string;
}

interface Pagination {
  current_page: number;
  total_pages: number;
  total_count: number;
  has_next: boolean;
  has_prev: boolean;
}

const PropertyGallery: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<Pagination>({
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    has_next: false,
    has_prev: false,
  });

  const propertyTypes = ['all', 'commercial', 'residential', 'industrial', 'retail', 'office', 'land'];

  const loadProperties = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetchProperties({
        page: currentPage,
        limit: 20,
        property_type: filter === 'all' ? undefined : filter,
        search: searchQuery || undefined,
        min_price: minPrice,
        max_price: maxPrice
      });
      setProperties(response.properties || []);
      setPagination(response.pagination || {});
    } catch (error) {
      console.error('Error loading properties:', error);
      setError('Failed to load properties. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, filter, searchQuery, minPrice, maxPrice]);

  useEffect(() => {
    loadProperties();
  }, [loadProperties]);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRetry = () => {
    loadProperties();
  };

  // Since we're now filtering on the backend, we don't need client-side filtering
  const displayedProperties = properties;

  if (error) {
    return (
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md mx-auto"
        >
          <Card className="border-destructive/20">
            <CardContent className="pt-8 pb-6">
              <div className="p-3 rounded-full bg-destructive/10 w-fit mx-auto mb-4">
                <AlertCircle className="h-6 w-6 text-destructive" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Something went wrong</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={handleRetry} variant="outline">
                Try Again
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Investment Properties
            </CardTitle>
            <p className="text-muted-foreground mt-2">
              {pagination.total_count > 0 ? (
                <>Showing {pagination.total_count} investment opportunities</>
              ) : (
                <>Discover your next investment opportunity</>
              )}
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search Bar */}
            <div className="max-w-md mx-auto">
              <Input
                placeholder="Search properties..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={<Search className="h-4 w-4" />}
              />
            </div>

            {/* Filter Controls */}
            <div className="space-y-4">
              {/* Property Type Filters */}
              <div className="flex flex-wrap justify-center gap-2">
                {propertyTypes.map((type) => (
                  <Button
                    key={type}
                    variant={filter === type ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => {setFilter(type); setCurrentPage(1);}}
                    className="capitalize"
                  >
                    {type === 'all' ? 'All Types' : type}
                  </Button>
                ))}
              </div>
              
              {/* Price Range Filters */}
              <div className="flex flex-wrap justify-center gap-4 max-w-2xl mx-auto">
                <div className="min-w-32">
                  <Input
                    type="number"
                    placeholder="Min Price"
                    value={minPrice || ''}
                    onChange={(e) => {
                      setMinPrice(e.target.value ? parseFloat(e.target.value) : undefined);
                      setCurrentPage(1);
                    }}
                  />
                </div>
                <div className="min-w-32">
                  <Input
                    type="number"
                    placeholder="Max Price"
                    value={maxPrice || ''}
                    onChange={(e) => {
                      setMaxPrice(e.target.value ? parseFloat(e.target.value) : undefined);
                      setCurrentPage(1);
                    }}
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setMinPrice(undefined);
                    setMaxPrice(undefined);
                    setSearchQuery('');
                    setFilter('all');
                    setCurrentPage(1);
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Properties Grid */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {[...Array(9)].map((_, i) => (
              <PropertyCardSkeleton key={i} />
            ))}
          </motion.div>
        ) : displayedProperties.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center py-16"
          >
            <Card className="max-w-md mx-auto">
              <CardContent className="pt-8 pb-6">
                <div className="p-4 rounded-full bg-muted w-fit mx-auto mb-4">
                  <Search className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No properties found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search criteria or filters.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key="properties"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {displayedProperties.map((property: Property, index: number) => (
              <PropertyCard 
                key={property.id} 
                property={property} 
                index={index}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pagination */}
      {!isLoading && pagination.total_pages > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardContent className="flex items-center justify-center gap-4 py-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={!pagination.has_prev}
              >
                <ChevronLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>
              
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted">
                <span className="text-sm font-medium">
                  Page {pagination.current_page} of {pagination.total_pages}
                </span>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={!pagination.has_next}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export { PropertyGallery };
export default PropertyGallery;