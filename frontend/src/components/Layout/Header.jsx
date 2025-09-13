import React from 'react';
import { BarChart3, Activity } from 'lucide-react';
import { ThemeToggle } from '../UI/ThemeToggle.tsx';
import { motion } from 'framer-motion';

const Header = () => {
    return (
        <motion.header 
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50"
        >
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <motion.div 
                        className="flex items-center space-x-4"
                        initial={{ x: -50, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                    >
                        <div className="flex items-center space-x-2">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                <BarChart3 className="h-6 w-6" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                                    Mighty Property Analyzer
                                </h1>
                                <p className="text-xs text-muted-foreground hidden sm:block">
                                    AI-Powered Commercial Property Intelligence
                                </p>
                            </div>
                        </div>
                    </motion.div>

                    <motion.nav 
                        className="flex items-center space-x-4"
                        initial={{ x: 50, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        <div className="hidden sm:flex items-center space-x-2 px-3 py-2 rounded-full bg-green-500/10 text-green-600 dark:text-green-400">
                            <Activity className="h-4 w-4 animate-pulse" />
                            <span className="text-sm font-medium">System Online</span>
                        </div>
                        <ThemeToggle />
                    </motion.nav>
                </div>
            </div>
        </motion.header>
    );
};

export default Header;