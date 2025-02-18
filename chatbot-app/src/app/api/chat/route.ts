import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { message } = await request.json();

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate`, {
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

    const data = await response.json();

    return NextResponse.json({ response: data.response });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}