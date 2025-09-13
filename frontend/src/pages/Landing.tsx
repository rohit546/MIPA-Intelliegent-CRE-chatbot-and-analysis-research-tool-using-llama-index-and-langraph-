import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Search, BarChart3, Zap, Shield, Users } from 'lucide-react';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { Card } from '../components/UI/Card';

const Landing: React.FC = () => {
  const features = [
    {
      icon: TrendingUp,
      title: 'Investment Analysis',
      description: 'AI-powered insights to identify profitable investment opportunities and market trends.',
    },
    {
      icon: BarChart3,
      title: 'Market Intelligence',
      description: 'Comprehensive market data and analytics to make informed investment decisions.',
    },
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'Get instant notifications about new properties and market changes.',
    },
    {
      icon: Shield,
      title: 'Risk Assessment',
      description: 'Advanced risk analysis tools to protect and optimize your investment portfolio.',
    },
    {
      icon: Users,
      title: 'Expert Network',
      description: 'Connect with verified agents, brokers, and investment professionals.',
    },
    {
      icon: Search,
      title: 'Smart Search',
      description: 'Find properties that match your exact investment criteria with AI-powered search.',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background gradients */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-muted/20" />
        <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 relative">
          <div className="text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary via-primary/80 to-accent bg-clip-text text-transparent leading-tight">
                Mighty Investment Property Analyzer
              </h1>
              
              <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
                AI-Powered Commercial Property Intelligence Platform with advanced analytics and investment insights.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
                <Button size="lg" className="text-lg px-8 py-4">
                  <TrendingUp className="mr-2 h-5 w-5" />
                  Start Analyzing
                </Button>
                <Button size="lg" variant="outline" className="text-lg px-8 py-4">
                  <BarChart3 className="mr-2 h-5 w-5" />
                  View Properties
                </Button>
              </div>
            </motion.div>
          </div>

          {/* Quick Search */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-16 max-w-2xl mx-auto"
          >
            <Card className="p-6">
              <div className="text-center mb-4">
                <h3 className="text-lg font-semibold">Quick Property Search</h3>
                <p className="text-muted-foreground">Find your next investment opportunity</p>
              </div>
              <div className="flex gap-2">
                <Input 
                  placeholder="Enter location, property type, or budget..."
                  className="flex-1"
                  icon={<Search className="h-4 w-4" />}
                />
                <Button>Search</Button>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything you need for smart property investment
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our comprehensive platform combines AI, market data, and expert insights 
              to help you make profitable investment decisions.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="h-full p-6 hover:shadow-lg transition-shadow">
                    <div className="text-center space-y-4">
                      <div className="p-3 rounded-full bg-primary/10 w-fit mx-auto">
                        <IconComponent className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold">{feature.title}</h3>
                      <p className="text-muted-foreground">{feature.description}</p>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center max-w-2xl mx-auto"
          >
            <Card className="p-8 bg-gradient-to-br from-primary/5 to-accent/5">
              <h2 className="text-3xl font-bold mb-4">
                Ready to start investing smarter?
              </h2>
              <p className="text-xl text-muted-foreground mb-8">
                Join thousands of investors who trust our platform 
                to identify profitable opportunities.
              </p>
              <div className="space-y-4">
                <Button size="lg" className="text-lg px-8 py-4">
                  Get Started Free
                </Button>
                <p className="text-sm text-muted-foreground">
                  No credit card required • Free forever plan available
                </p>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;