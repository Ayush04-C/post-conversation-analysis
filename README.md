# Conversation Analyser - Django REST API

A Django-based REST API application for managing and analyzing conversations. The application features automated daily analysis tasks scheduled via Celery Beat, Redis as a message broker, and SQLite for data persistence.

## Features

- **RESTful API** for conversation management and analysis
- **Automated Daily Analysis** using Celery Beat cron jobs (runs every night at midnight)
- **Sentiment Analysis** using VADER Sentiment
- **Conversation Metrics** including clarity, empathy, accuracy, relevance, and more
- **SQLite Database** for storing conversations and analysis results
- **Django REST Framework** for API endpoints
- **Redis** as Celery message broker

## Tech Stack

- **Django 3.2.6** - Web framework
- **Django REST Framework** - RESTful API toolkit
- **Celery 5.3.4** - Distributed task queue
- **Redis** - Message broker for Celery
- **SQLite** - Database
- **VADER Sentiment** - Sentiment analysis
- **Textstat** - Text readability metrics

## Project Structure

```
convo_analyser/
├── analysis/                   # Main Django app
│   ├── migrations/            # Database migrations
│   ├── celery.py              # Celery tasks (daily analysis)
│   ├── models.py              # Data models
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # API routes
│   ├── utils.py               # Analysis utility functions
│   └── views.py               # API views
├── convo_analyser/            # Project configuration
│   ├── celery.py              # Celery app configuration
│   ├── settings.py            # Django settings
│   └── urls.py                # Main URL configuration
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Docker (for running Redis)
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd convo_analyser
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

Run migrations to create the SQLite database:

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Setup Redis (Message Broker)

Run Redis using Docker:

```bash
docker run -d -p 6379:6379 redis
```

This starts Redis in detached mode on port 6379.

To verify Redis is running:

```bash
docker ps
```

## Running the Application

You need to run **three separate terminals** to start all components:

### Terminal 1: Django Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### Terminal 2: Celery Worker

**On Windows** (requires `--pool=solo` flag):

```bash
celery -A convo_analyser worker --pool=solo -l info
```

**On Linux/Mac**:

```bash
celery -A convo_analyser worker -l info
```

The worker processes background tasks from the Celery queue.

### Terminal 3: Celery Beat (Scheduler)

```bash
celery -A convo_analyser beat -l info
```

Celery Beat schedules the `run_daily_analysis` task to run every night at **00:00 (midnight)**.

## Automated Daily Analysis Configuration

The daily analysis cron job is configured in `convo_analyser/settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'run-daily-analysis-midnight': {
        'task': 'analysis.tasks.run_daily_analysis',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
}
```

### How It Works

1. **Celery Beat** triggers the `run_daily_analysis` task at midnight
2. The task finds all conversations without analysis
3. Each conversation is analyzed for:
   - Sentiment (positive/negative/neutral)
   - Clarity score
   - Empathy level
   - Accuracy
   - Relevance
   - Resolution status
   - Fallback count
   - Overall quality score
4. Analysis results are saved to the database

### Manual Task Execution (Testing)

To manually trigger the daily analysis task:

```python
from analysis.celery import run_daily_analysis
run_daily_analysis.delay()
```

Or using Celery shell:

```bash
python manage.py shell
>>> from analysis.celery import run_daily_analysis
>>> run_daily_analysis.delay()
```

## API Documentation

Base URL: `http://127.0.0.1:8000/api/`

### 1. Create Conversation

Creates a new conversation with messages.

**Endpoint:** `POST /api/conversations/`

**Request Body:**

```json
{
  "messages": [
    {
      "sender": "user",
      "text": "Hello, I need help with my account"
    },
    {
      "sender": "bot",
      "text": "Hello! I'd be happy to help you with your account. What seems to be the issue?"
    },
    {
      "sender": "user",
      "text": "I can't login to my account"
    },
    {
      "sender": "bot",
      "text": "I understand your frustration. Let me help you reset your password. Please check your email."
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "conversation_id": 1
}
```

**Example using cURL:**

```bash
curl -X POST http://127.0.0.1:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"sender": "user", "text": "Hello, I need help"},
      {"sender": "bot", "text": "How can I assist you today?"}
    ]
  }'
```

### 2. Analyse Conversation

Analyzes a specific conversation and returns metrics.

**Endpoint:** `POST /api/analyse/`

**Request Body:**

```json
{
  "conversation_id": 1
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "title": "Hello, I need help with my account",
  "conversation_id": 1,
  "sentiment": "positive",
  "clarity": 0.75,
  "empathy": 0.5,
  "relevance": 0.82,
  "resolution": false,
  "fallback_count": 0,
  "overall": 0.68,
  "created_at": "2025-11-10T19:24:35.123456Z"
}
```

**Response (404 Not Found):**

```json
{
  "error": "Conversation not found"
}
```

**Example using cURL:**

```bash
curl -X POST http://127.0.0.1:8000/api/analyse/ \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1}'
```

### 3. Get All Reports

Retrieves all conversation analysis reports, ordered by most recent first.

**Endpoint:** `GET /api/reports/`

**Response (200 OK):**

```json
[
  {
    "id": 2,
    "title": "I'm having trouble with checkout",
    "conversation_id": 2,
    "sentiment": "negative",
    "clarity": 0.82,
    "empathy": 0.65,
    "relevance": 0.78,
    "resolution": true,
    "fallback_count": 1,
    "overall": 0.71,
    "created_at": "2025-11-10T20:15:22.987654Z"
  },
  {
    "id": 1,
    "title": "Hello, I need help with my account",
    "conversation_id": 1,
    "sentiment": "positive",
    "clarity": 0.75,
    "empathy": 0.5,
    "relevance": 0.82,
    "resolution": false,
    "fallback_count": 0,
    "overall": 0.68,
    "created_at": "2025-11-10T19:24:35.123456Z"
  }
]
```

**Example using cURL:**

```bash
curl http://127.0.0.1:8000/api/reports/
```

## Analysis Metrics Explained

| Metric | Description | Range |
|--------|-------------|-------|
| **sentiment** | Overall conversation tone (positive/negative/neutral) | categorical |
| **clarity** | How clear and readable the conversation is | 0.0 - 1.0 |
| **empathy** | Level of empathetic language used | 0.0 - 1.0 |
| **accuracy** | Presence of definitive answers vs vague responses | 0.0 - 1.0 |
| **relevance** | How on-topic the conversation stays | 0.0 - 1.0 |
| **resolution** | Whether the issue was explicitly resolved | true/false |
| **fallback_count** | Number of times uncertain/fallback responses occurred | integer |
| **overall** | Weighted average quality score | 0.0 - 1.0 |
| **completeness** | Conversation length, greetings, and closings | 0.0 - 1.0 |
| **escalation_need** | Whether human escalation is needed | true/false |

## Data Models

### Conversation

```python
{
  "id": Integer,
  "created_at": DateTime
}
```

### Message

```python
{
  "id": Integer,
  "conversation": ForeignKey(Conversation),
  "sender": String (max 10 chars),
  "text": TextField
}
```

### ConversationAnalysis

```python
{
  "id": Integer,
  "title": String (max 255 chars),
  "conversation": OneToOne(Conversation),
  "sentiment": String (max 10 chars),
  "clarity": Float,
  "empathy": Float,
  "accuracy": Float,
  "relevance": Float,
  "escalation_need": Boolean,
  "completeness": Float,
  "resolution": Boolean,
  "fallback_count": Integer,
  "overall": Float,
  "created_at": DateTime
}
```

## Testing the Application

### Using Python Requests

```python
import requests

# Create a conversation
response = requests.post(
    'http://127.0.0.1:8000/api/conversations/',
    json={
        'messages': [
            {'sender': 'user', 'text': 'Hello'},
            {'sender': 'bot', 'text': 'Hi! How can I help you?'}
        ]
    }
)
conversation_id = response.json()['conversation_id']

# Analyse the conversation
analysis = requests.post(
    'http://127.0.0.1:8000/api/analyse/',
    json={'conversation_id': conversation_id}
)
print(analysis.json())

# Get all reports
reports = requests.get('http://127.0.0.1:8000/api/reports/')
print(reports.json())
```

### Using Django Admin Panel

1. Start the Django server
2. Navigate to `http://127.0.0.1:8000/admin/`
3. Login with your superuser credentials
4. View and manage Conversations, Messages, and Analysis records

## Celery Configuration

The Celery configuration in `settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
```

## Troubleshooting

### Redis Connection Error

If you see `Error connecting to Redis`:

1. Ensure Docker is running
2. Verify Redis container is active: `docker ps`
3. Restart Redis: `docker restart <container-id>`

### Celery Worker Not Processing Tasks

- Ensure Redis is running
- Check Celery worker logs for errors
- Verify task is registered: `celery -A convo_analyser inspect registered`

### Database Migration Issues

```bash
# Reset migrations (development only)
python manage.py migrate analysis zero
python manage.py migrate
```

### Port Already in Use

If port 8000 is busy:

```bash
python manage.py runserver 8080
```

## Development Notes

- The application uses SQLite for development (not recommended for production)
- Secret key is exposed in `settings.py` - **change this in production**
- `DEBUG = True` should be set to `False` in production
- Consider using PostgreSQL or MySQL for production environments
- Add proper authentication/authorization for production APIs

## License

[Add your license information here]

## Contributing

[Add contributing guidelines here]

## Contact

[Add contact information here]
