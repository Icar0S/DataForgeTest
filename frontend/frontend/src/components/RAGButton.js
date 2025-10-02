import React from 'react';
import { Book } from 'react-feather';
import { Link } from 'react-router-dom';

const RAGButton = () => {
  return (
    <Link
      to="/support-rag"
      className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl font-semibold shadow-lg hover:shadow-indigo-500/30 transition-all duration-300 flex items-center gap-2 text-white"
    >
      <Book className="w-5 h-5" />
      Support RAG
    </Link>
  );
};

export default RAGButton;