import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Building2, 
  DollarSign, 
  Users, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  MapPin
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/UI/Card.tsx';
import { Button } from '../components/UI/Button.tsx';
import Chatbot from '../components/Chatbot/Chatbot';
import { PropertyGallery } from '../components/PropertyGallery/PropertyGallery';

const Dashboard = () => {
  const stats = [
    {
      title: 'Total Properties',
      value: '1,234',
      change: '+12.5%',
      trend: 'up',
      icon: Building2,
      color: 'text-blue-600 dark:text-blue-400'
    },
    {
      title: 'Active Listings',
      value: '567',
      change: '+8.2%',
      trend: 'up',
      icon: Activity,
      color: 'text-green-600 dark:text-green-400'
    },
    {
      title: 'Closed Deals',
      value: '89',
      change: '-2.1%',
      trend: 'down',
      icon: TrendingUp,
      color: 'text-orange-600 dark:text-orange-400'
    },
    {
      title: 'Revenue',
      value: '$2.1M',
      change: '+15.3%',
      trend: 'up',
      icon: DollarSign,
      color: 'text-purple-600 dark:text-purple-400'
    }
  ];

  const recentActivities = [
    {
      id: 1,
      type: 'new_listing',
      title: 'New commercial property listed',
      location: '123 Business Ave, Downtown',
      time: '2 hours ago',
      value: '$850,000'
    },
    {
      id: 2,
      type: 'deal_closed',
      title: 'Deal closed successfully',
      location: '456 Trade Center, Midtown',
      time: '5 hours ago',
      value: '$1.2M'
    },
    {
      id: 3,
      type: 'inquiry',
      title: 'New client inquiry',
      location: '789 Corporate Plaza',
      time: '1 day ago',
      value: '$950,000'
    }
  ];

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Georgia Properties Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Welcome back! Here's what's happening with your properties.
            </p>
          </div>
          <Button className="mt-4 sm:mt-0">
            <TrendingUp className="mr-2 h-4 w-4" />
            View Analytics
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="relative overflow-hidden hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <IconComponent className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <div className="flex items-center text-xs">
                    {stat.trend === 'up' ? (
                      <ArrowUpRight className="h-4 w-4 text-green-500 mr-1" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-red-500 mr-1" />
                    )}
                    <span className={stat.trend === 'up' ? 'text-green-500' : 'text-red-500'}>
                      {stat.change}
                    </span>
                    <span className="text-muted-foreground ml-1">from last month</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="grid grid-cols-1 xl:grid-cols-2 gap-8"
      >
        {/* Chatbot Section */}
        <Card className="p-6">
          <CardHeader className="px-0 pt-0">
            <CardTitle className="flex items-center">
              <Users className="mr-2 h-5 w-5" />
              AI Property Assistant
            </CardTitle>
          </CardHeader>
          <CardContent className="px-0">
            <Chatbot />
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="mr-2 h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                  </div>
                  <div className="flex-grow min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {activity.title}
                    </p>
                    <div className="flex items-center text-xs text-muted-foreground mt-1">
                      <MapPin className="h-3 w-3 mr-1" />
                      {activity.location}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <div className="text-sm font-semibold text-foreground">
                      {activity.value}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {activity.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Property Gallery */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card className="p-6">
          <CardHeader className="px-0 pt-0">
            <CardTitle className="flex items-center">
              <Building2 className="mr-2 h-5 w-5" />
              Property Portfolio
            </CardTitle>
          </CardHeader>
          <CardContent className="px-0">
            <PropertyGallery />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Dashboard;