import React from 'react';
import { Book } from 'react-feather';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const RAGButton = () => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Link
        to="/support-rag"
        className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl font-semibold text-lg shadow-lg hover:shadow-indigo-500/30 transition-all duration-300 flex items-center gap-2 text-white"
      >
        <Book className="w-5 h-5" />
        Support RAG
      </Link>
    </motion.div>
  );
};

export default RAGButton;