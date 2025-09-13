import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Bot, TrendingUp, Home, Building2, Settings, CheckCircle, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils.ts';

const Sidebar = () => {
    const location = useLocation();
    
    const menuItems = [
        { id: 'home', label: 'Home', icon: Home, path: '/' },
        { id: 'dashboard', label: 'Dashboard', icon: TrendingUp, path: '/dashboard' },
        { id: 'properties', label: 'Properties', icon: Building2, path: '/properties' },
        { id: 'chat', label: 'AI Assistant', icon: Bot, path: '/chat' },
        { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
    ];

    const features = [
        { label: 'AI Investment Analysis', status: 'active' },
        { label: 'Property Intelligence', status: 'active' },
        { label: 'Market Insights', status: 'active' },
        { label: 'ROI Calculator', status: 'active' },
        { label: 'Backend Integration', status: 'coming' },
    ];

    return (
        <motion.aside 
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-64 border-r bg-background/50 backdrop-blur-sm h-screen overflow-y-auto sticky top-0"
        >
            <div className="p-6 h-full flex flex-col">
                <nav className="flex-1 space-y-2">
                    <AnimatePresence>
                        {menuItems.map((item, index) => {
                            const IconComponent = item.icon;
                            const isActive = location.pathname === item.path;
                            
                            return (
                                <motion.div
                                    key={item.id}
                                    initial={{ x: -50, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ duration: 0.3, delay: index * 0.1 }}
                                >
                                    <NavLink
                                        to={item.path}
                                        className={({ isActive: linkActive }) =>
                                            cn(
                                                'w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 hover:translate-x-1',
                                                linkActive
                                                    ? 'bg-primary text-primary-foreground shadow-sm'
                                                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                                            )
                                        }
                                    >
                                        <IconComponent className="h-5 w-5 flex-shrink-0" />
                                        <span className="truncate">{item.label}</span>
                                        {isActive && (
                                            <motion.div
                                                layoutId="activeIndicator"
                                                className="ml-auto w-2 h-2 rounded-full bg-primary-foreground"
                                            />
                                        )}
                                    </NavLink>
                                </motion.div>
                            );
                        })}
                    </AnimatePresence>
                </nav>
                
                <motion.div 
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 }}
                    className="mt-8 p-4 rounded-lg bg-muted/50"
                >
                    <h4 className="text-sm font-semibold mb-3 text-foreground">Features</h4>
                    <div className="space-y-2">
                        {features.map((feature, index) => (
                            <motion.div
                                key={feature.label}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: 0.9 + index * 0.1 }}
                                className="flex items-center space-x-2 text-xs"
                            >
                                {feature.status === 'active' ? (
                                    <CheckCircle className="h-3 w-3 text-green-500 flex-shrink-0" />
                                ) : (
                                    <Clock className="h-3 w-3 text-orange-500 flex-shrink-0" />
                                )}
                                <span className={cn(
                                    'truncate',
                                    feature.status === 'active' 
                                        ? 'text-foreground' 
                                        : 'text-muted-foreground'
                                )}>
                                    {feature.label}
                                </span>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </motion.aside>
    );
};

export default Sidebar;