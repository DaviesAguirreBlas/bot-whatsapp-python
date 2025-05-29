# WhatsApp Sales Bot

A WhatsApp bot for managing sales, processing receipts, and providing business insights using LangChain and OpenAI.

## Features

- Process text messages using LangChain agents
- Register sales with amount, payment method, and seller information
- View sales history and daily summaries
- Get business insights and KPIs
- Extract information from receipt images using OCR
- Transcribe audio messages to text
- Persistent chat history using Redis
- PostgreSQL database for sales data

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.11+

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://postgres:postgres@db:5432/salesbot
DEBUG=False
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bot-whatsapp-python.git
cd bot-whatsapp-python
```

2. Build and start the services:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Text Messages
```http
POST /webhook
Content-Type: application/json

{
    "customer_phone": "1234567890",
    "content": "Register sale: $100 paid with credit card by John",
    "type": "text"
}
```

### Image Processing
```http
POST /upload/image
Content-Type: multipart/form-data

customer_phone: "1234567890"
file: receipt.jpg
```

### Audio Processing
```http
POST /upload/audio
Content-Type: multipart/form-data

customer_phone: "1234567890"
file: message.mp3
```

## Project Structure

```
bot-whatsapp-python/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── main.py                 # FastAPI application
    ├── config.py              # Configuration management
    ├── db.py                  # Database connection
    ├── models.py              # SQLAlchemy models
    ├── agents/                # LangChain agents
    ├── memory/                # Chat history management
    ├── services/              # Business logic
    ├── templates/             # Prompt templates
    └── tools/                 # Agent tools
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 