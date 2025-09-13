import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Square, TrendingUp, Eye } from 'lucide-react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { cn } from '../../lib/utils';

interface PropertyCardProps {
  property: {
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
  };
  index?: number;
}

export const PropertyCard: React.FC<PropertyCardProps> = ({ property, index = 0 }) => {
  const formatPrice = (price?: number) => {
    if (!price) return 'Price on request';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getPropertyTypeColor = (type?: string) => {
    const typeColors = {
      'commercial': 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
      'residential': 'bg-green-500/10 text-green-600 dark:text-green-400',
      'industrial': 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
      'retail': 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
      'office': 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400',
    };
    return typeColors[type?.toLowerCase() as keyof typeof typeColors] || 'bg-gray-500/10 text-gray-600 dark:text-gray-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay: index * 0.1,
        ease: [0.25, 0.25, 0, 1]
      }}
      whileHover={{ y: -8 }}
      className="group"
    >
      <Card className="overflow-hidden transition-all duration-300 hover:shadow-xl dark:hover:shadow-2xl border-0 bg-gradient-to-br from-background to-muted/20">
        {/* Property Image */}
        <div className="relative h-48 overflow-hidden bg-gradient-to-br from-primary/20 to-primary/10">
          {property.thumbnail_url ? (
            <img
              src={property.thumbnail_url}
              alt={property.name || 'Property'}
              className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
              onError={(e) => {
                // Hide image if it fails to load
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          
          {/* Fallback placeholder */}
          <div className={`flex items-center justify-center h-full ${property.thumbnail_url ? 'hidden' : ''}`}>
            <div className="text-center space-y-2">
              <div className="p-4 rounded-full bg-primary/10 mx-auto w-fit">
                <TrendingUp className="h-8 w-8 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground font-medium">Investment Property</p>
            </div>
          </div>
          
          {/* Property Type Badge */}
          {property.property_type && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className={cn(
                'absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-sm',
                getPropertyTypeColor(property.property_type)
              )}
            >
              {property.property_type}
            </motion.div>
          )}

          {/* Overlay gradient */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        <CardContent className="p-6 space-y-4">
          {/* Property Name */}
          <div>
            <h3 className="text-lg font-semibold line-clamp-2 group-hover:text-primary transition-colors">
              {property.name || 'Untitled Property'}
            </h3>
            
            {/* Address */}
            {property.address && (
              <div className="flex items-start gap-1 mt-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span className="line-clamp-2">
                  {property.address.fullAddress || 
                   [property.address.street, property.address.city, property.address.state]
                    .filter(Boolean)
                    .join(', ') || 
                   'Address not available'}
                </span>
              </div>
            )}
          </div>

          {/* Price */}
          <div className="text-2xl font-bold text-primary">
            {formatPrice(property.asking_price)}
          </div>

          {/* Property Stats */}
          <div className="grid grid-cols-1 gap-3">
            {property.size_acres && (
              <div className="text-center p-3 rounded-lg bg-muted/50">
                <Square className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
                <div className="text-sm font-semibold">{property.size_acres.toFixed(2)} acres</div>
                <div className="text-xs text-muted-foreground">Size</div>
              </div>
            )}
          </div>

          {/* Description */}
          {property.description && (
            <div className="text-sm text-muted-foreground line-clamp-2">
              {property.description}
            </div>
          )}

          {/* Status */}
          {property.status && (
            <div className="text-sm text-muted-foreground">
              <span className="font-medium">Status:</span> {property.status}
            </div>
          )}

          {/* Action Button */}
          <Button 
            className="w-full group-hover:bg-primary group-hover:text-primary-foreground"
            variant="outline"
            onClick={() => {
              if (property.listing_url) {
                window.open(property.listing_url, '_blank', 'noopener,noreferrer');
              } else {
                // Fallback: redirect to Crexi search for this property
                const searchQuery = encodeURIComponent(property.name || property.address?.fullAddress || 'property');
                window.open(`https://www.crexi.com/search?query=${searchQuery}`, '_blank', 'noopener,noreferrer');
              }
            }}
          >
            <Eye className="h-4 w-4 mr-2" />
            View Details
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
};