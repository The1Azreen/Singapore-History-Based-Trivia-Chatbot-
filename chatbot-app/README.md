# AI Chatbot with Next.js and Ollama

A modern chatbot interface built with Next.js, React, and integrated with Ollama's phi3:mini model. Features a clean, responsive UI similar to ChatGPT and Claude.

## Features

- Real-time chat interface
- Integration with Ollama API
- Responsive design
- Message history
- Loading states and animations
- Error handling
- Markdown support

## Tech Stack

- Frontend: Next.js 15.1.6 with TypeScript
- UI: React 19.0.0 with Tailwind CSS
- Icons: Lucide React
- Backend API Integration: Ollama Service (ECS with Fargate)

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Ollama service running and accessible

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chatbot-app
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file in the root directory:
```
NEXT_PUBLIC_API_URL=http://[Your-ECS-IP]:11434
```

## Running the Application

1. Development mode:
```bash
npm run dev
```
Access the application at `http://localhost:3000`

2. Production build:
```bash
npm run build
npm start
```

## API Configuration

The chatbot integrates with Ollama running on ECS. Configure the API endpoint in these locations:

1. `.env.local`:
```
NEXT_PUBLIC_API_URL=http://[Your-ECS-IP]:11434
```

2. Security Group Configuration:
- WebServer Security Group
- Ollama-ecs Security Group
- Ensure inbound traffic rules are properly configured

## API Endpoints

The application uses the following Ollama endpoints:

1. Model Check:
```bash
curl http://[ECS-IP]:11434/api/pull -d '{"name": "phi3:mini"}'
```

2. Generate Response:
```bash
curl -X POST http://[ECS-IP]:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

## Project Structure

```
src/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                  # Home page
│   ├── globals.css               # Global styles
│   ├── chat/
│   │   └── page.tsx             # Chat interface page
│   └── api/
│       └── chat/
│           └── route.ts         # API routes
├── components/
│   └── chat/
│       └── chat-interface.tsx   # Main chat component
├── lib/
│   └── api.ts                   # API utilities
└── types/
    └── chat.ts                  # TypeScript interfaces
```

## Security Considerations

1. API Security:
   - Ensure proper security group configurations
   - Limit inbound traffic to necessary ports
   - Configure CORS policies appropriately

2. Environment Variables:
   - Never commit `.env` files
   - Use proper environment variable handling
   - Follow security best practices for API keys

## Troubleshooting

1. API Connection Issues:
   - Verify ECS IP address is correct
   - Check security group configurations
   - Ensure Ollama service is running

2. Build Errors:
   - Ensure all dependencies are installed
   - Check for correct Node.js version
   - Verify TypeScript configurations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your License Choice]