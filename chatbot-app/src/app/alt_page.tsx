'use client';

import React, { useState } from 'react';
import axios from 'axios';

export default function ChatPage() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await axios.post('http://172.31.84.135:11434/api/generate', {
        model: "phi3:mini",
        prompt: prompt,
        stream: false
      });

      setResponse(result.data.response);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error occurred while fetching response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Chat Interface</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full p-2 border rounded-lg"
            rows={4}
            placeholder="Enter your prompt..."
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>

        {response && (
          <div className="mt-4 p-4 bg-white rounded-lg shadow">
            <h2 className="font-bold mb-2">Response:</h2>
            <p className="whitespace-pre-wrap">{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}