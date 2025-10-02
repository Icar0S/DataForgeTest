import React, { useState } from 'react';
import { MessageCircle } from 'react-feather';
import ChatWindow from './ChatWindow';

const SupportButton = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 p-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full shadow-lg hover:shadow-purple-500/30 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all duration-300"
        aria-label="Open support chat"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {isChatOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-[#1a1a2e]/95 via-[#16213e]/95 to-[#1a1a2e]/95 backdrop-blur-sm">
          <div className="w-full max-w-4xl h-[80vh] m-4">
            <ChatWindow onClose={() => setIsChatOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
};

export default SupportButton;