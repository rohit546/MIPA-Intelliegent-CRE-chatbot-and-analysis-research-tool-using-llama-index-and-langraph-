import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MessageCircle,
  Bot,
  Building,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Button } from '../components/UI/Button.tsx';
import { Card, CardContent, CardHeader, CardTitle } from '../components/UI/Card.tsx';
import { PropertyCard } from '../components/PropertyGallery/PropertyCard.tsx';
import Chatbot from '../components/Chatbot/Chatbot';

const ChatPage = () => {
  const [chatProperties, setChatProperties] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [showProperties, setShowProperties] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const propertiesPerPage = 6;

  const handlePropertiesFound = (properties, query) => {
    setChatProperties(properties);
    setCurrentQuery(query);
    setShowProperties(true);
    setCurrentPage(1);
  };

  // Pagination logic
  const totalPages = Math.ceil(chatProperties.length / propertiesPerPage);
  const startIndex = (currentPage - 1) * propertiesPerPage;
  const endIndex = startIndex + propertiesPerPage;
  const currentProperties = chatProperties.slice(startIndex, endIndex);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
          
          <div className="space-y-6">
            <div className="text-center lg:text-left">
              <motion.h1 
                className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent mb-4"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                AI Property Search
              </motion.h1>
              <motion.p 
                className="text-muted-foreground text-lg"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                Ask natural language questions about Georgia commercial properties
              </motion.p>
            </div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="h-[600px] flex flex-col">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <Bot className="h-5 w-5 text-primary" />
                      AI Assistant
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm text-muted-foreground">Online</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 p-0">
                  <Chatbot onPropertiesFound={handlePropertiesFound} />
                </CardContent>
              </Card>
            </motion.div>
          </div>

          <div className="space-y-6">
            <div className="text-center lg:text-left">
              <motion.h2 
                className="text-2xl font-bold mb-2"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                {showProperties ? `Results for: "${currentQuery}"` : 'Property Results'}
              </motion.h2>
              <motion.p 
                className="text-muted-foreground"
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                {showProperties 
                  ? `Found ${chatProperties.length} matching properties (Page ${currentPage} of ${totalPages})`
                  : 'Ask a question to see property results here'
                }
              </motion.p>
            </div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="h-[600px] overflow-hidden rounded-lg border bg-card"
            >
              {showProperties && chatProperties.length > 0 ? (
                <div className="h-full flex flex-col">
                  <div className="flex-1 overflow-y-auto p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {currentProperties.map((property, index) => (
                        <PropertyCard 
                          key={property.id || index}
                          property={{
                            ...property,
                            price: property.asking_price,
                            address: property.address || { fullAddress: 'Address not available' }
                          }}
                          index={index}
                        />
                      ))}
                    </div>
                  </div>
                  
                  {/* Pagination Controls */}
                  {totalPages > 1 && (
                    <div className="border-t p-4">
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-muted-foreground">
                          Showing {startIndex + 1}-{Math.min(endIndex, chatProperties.length)} of {chatProperties.length} properties
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => goToPage(currentPage - 1)}
                            disabled={currentPage === 1}
                          >
                            <ChevronLeft className="h-4 w-4" />
                          </Button>
                          
                          <div className="flex items-center gap-1">
                            {Array.from({ length: totalPages }, (_, i) => i + 1)
                              .filter(page => 
                                page === 1 || 
                                page === totalPages || 
                                (page >= currentPage - 1 && page <= currentPage + 1)
                              )
                              .map((page, index, array) => (
                                <React.Fragment key={page}>
                                  {index > 0 && array[index - 1] !== page - 1 && (
                                    <span className="px-2 text-muted-foreground">...</span>
                                  )}
                                  <Button
                                    size="sm"
                                    variant={currentPage === page ? "default" : "outline"}
                                    onClick={() => goToPage(page)}
                                    className="w-8 h-8 p-0"
                                  >
                                    {page}
                                  </Button>
                                </React.Fragment>
                              ))}
                          </div>
                          
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => goToPage(currentPage + 1)}
                            disabled={currentPage === totalPages}
                          >
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <MessageCircle className="h-16 w-16 text-muted-foreground/50 mx-auto" />
                    <div>
                      <h3 className="font-semibold text-lg mb-2">No Results Yet</h3>
                      <p className="text-muted-foreground max-w-sm">
                        Ask the AI assistant a question about properties and the results will appear here
                      </p>
                    </div>
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <p><strong>Try asking:</strong></p>
                      <p>• "Show me gas stations under $500k"</p>
                      <p>• "Find retail properties in Atlanta"</p>
                      <p>• "Properties between 2-5 acres"</p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;