import { ChatResponse } from '@/types/chat';

export async function sendMessage(message: string): Promise<ChatResponse> {
  try {
    const response = await fetch('http://[ECS-IP]:11434/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "phi3:mini",
        prompt: message,
        stream: false
      }),
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    return {
      response: 'Sorry, there was an error processing your request.',
    };
  }
}