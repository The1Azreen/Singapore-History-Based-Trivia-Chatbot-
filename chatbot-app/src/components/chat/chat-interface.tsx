'use client';


import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot } from 'lucide-react';
import Link from 'next/link'; 



interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Scroll to bottom whenever messages change
  useEffect(() => {
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage.trim()
    };

    try {
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      setIsLoading(true);

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gray-50">
      {/* Chat header */}
      <div className="flex items-center justify-between bg-white border-b px-6 py-4">
        <Link href="/">
          <h1 className="text-xl font-semibold hover:text-blue-600 transition-colors cursor-pointer">
            AI Chat Assistant
          </h1>
        </Link>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            Start a conversation by typing a message below.
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex items-start gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-blue-600" />
              </div>
            )}
            
            <div
              className={`relative max-w-2xl rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border shadow-sm'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input form */}
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;