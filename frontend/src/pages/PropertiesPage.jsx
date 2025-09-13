import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  SortAsc, 
  Map, 
  Grid, 
  List,
  MapPin,
  DollarSign,
  Square,
  Calendar
} from 'lucide-react';
import { Button } from '../components/UI/Button.tsx';
import { Input } from '../components/UI/Input.tsx';
import { Card, CardContent, CardHeader, CardTitle } from '../components/UI/Card.tsx';
import { PropertyGallery } from '../components/PropertyGallery/PropertyGallery';

const PropertiesPage = () => {
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const filters = [
    { label: 'Property Type', options: ['Office', 'Retail', 'Industrial', 'Mixed Use'] },
    { label: 'Price Range', options: ['$0 - $500K', '$500K - $1M', '$1M - $5M', '$5M+'] },
    { label: 'Location', options: ['Downtown', 'Midtown', 'Suburbs', 'Waterfront'] },
    { label: 'Status', options: ['Available', 'Under Contract', 'Sold'] }
  ];

  const quickStats = [
    { label: 'Total Properties', value: '1,234', icon: Square },
    { label: 'Available', value: '567', icon: Calendar },
    { label: 'Avg. Price', value: '$2.1M', icon: DollarSign },
    { label: 'Locations', value: '12', icon: MapPin }
  ];

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Properties</h1>
            <p className="text-muted-foreground mt-1">
              Browse our comprehensive collection of commercial properties.
            </p>
          </div>
          
          {/* View Toggle */}
          <div className="flex items-center gap-2 mt-4 lg:mt-0">
            <div className="flex items-center border rounded-lg p-1">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className="h-8 px-2"
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                className="h-8 px-2"
              >
                <List className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'map' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('map')}
                className="h-8 px-2"
              >
                <Map className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {quickStats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <Card key={stat.label} className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <IconComponent className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-lg font-semibold">{stat.value}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card className="p-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by location, property type, or price..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                  className="w-full"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center"
                >
                  <Filter className="mr-2 h-4 w-4" />
                  Filters
                </Button>
                <Button variant="outline" className="flex items-center">
                  <SortAsc className="mr-2 h-4 w-4" />
                  Sort
                </Button>
              </div>
            </div>

            {/* Expandable Filters */}
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t"
              >
                {filters.map((filter) => (
                  <div key={filter.label} className="space-y-2">
                    <label className="text-sm font-medium text-foreground">
                      {filter.label}
                    </label>
                    <select className="w-full p-2 border rounded-lg bg-background text-foreground">
                      <option value="">All {filter.label}</option>
                      {filter.options.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </motion.div>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Properties Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        {viewMode === 'map' ? (
          <Card className="p-6">
            <div className="h-96 bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center space-y-2">
                <Map className="h-16 w-16 text-muted-foreground mx-auto" />
                <h3 className="text-lg font-semibold">Map View</h3>
                <p className="text-muted-foreground">
                  Interactive map with property locations coming soon
                </p>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="p-6">
            <CardHeader className="px-0 pt-0">
              <CardTitle className="flex items-center justify-between">
                <span>Property Listings</span>
                <span className="text-sm font-normal text-muted-foreground">
                  Showing 567 properties
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="px-0">
              <PropertyGallery viewMode={viewMode} />
            </CardContent>
          </Card>
        )}
      </motion.div>
    </div>
  );
};

export default PropertiesPage;