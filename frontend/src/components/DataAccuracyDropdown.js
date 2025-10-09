import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Database, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DataAccuracyDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const timeoutRef = useRef(null);

  // Handle mouse enter
  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsOpen(true);
  };

  // Handle mouse leave
  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setIsOpen(false);
    }, 200);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setIsOpen(!isOpen);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const dropdownVariants = {
    hidden: { 
      opacity: 0, 
      y: -10,
      scale: 0.95
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    exit: { 
      opacity: 0, 
      y: -10,
      scale: 0.95,
      transition: {
        duration: 0.15
      }
    }
  };

  return (
    <div 
      ref={dropdownRef}
      className="relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Main Button */}
      <button
        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl font-semibold text-lg shadow-lg hover:shadow-blue-500/30 transition-all duration-300 flex items-center gap-2"
        aria-label="Data Accuracy Menu"
        aria-expanded={isOpen}
        aria-haspopup="true"
        onKeyDown={handleKeyDown}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Database className="w-5 h-5" />
        Data Accuracy
        <ChevronDown 
          className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={dropdownVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="absolute top-full left-0 mt-2 w-64 bg-gray-800/95 backdrop-blur-sm rounded-xl shadow-xl border border-gray-700/50 overflow-hidden z-50"
          >
            <Link
              to="/data-accuracy"
              className="block px-6 py-3 text-white hover:bg-blue-600/20 transition-colors duration-200 border-b border-gray-700/50"
              onClick={() => setIsOpen(false)}
              onFocus={() => setIsOpen(true)}
            >
              <div className="font-medium">Compare Datasets</div>
              <div className="text-sm text-gray-400 mt-1">
                Compare GOLD vs TARGET datasets
              </div>
            </Link>
            <Link
              to="/data-accuracy/test-gold"
              className="block px-6 py-3 text-white hover:bg-blue-600/20 transition-colors duration-200 border-b border-gray-700/50"
              onClick={() => setIsOpen(false)}
              onFocus={() => setIsOpen(true)}
            >
              <div className="font-medium">Test Dataset GOLD</div>
              <div className="text-sm text-gray-400 mt-1">
                Clean and validate a single dataset
              </div>
            </Link>
            <Link
              to="/data-accuracy/metrics"
              className="block px-6 py-3 text-white hover:bg-blue-600/20 transition-colors duration-200"
              onClick={() => setIsOpen(false)}
              onFocus={() => setIsOpen(true)}
            >
              <div className="font-medium">Dataset Metrics</div>
              <div className="text-sm text-gray-400 mt-1">
                Analyze data quality metrics
              </div>
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DataAccuracyDropdown;
