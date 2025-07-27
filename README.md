# AI Image Generation Backend System

A scalable backend system for AI image generation with credit-based economy, built using Firebase Functions and Firestore.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)

## 🎯 Overview

This backend system provides:
- Credit-based AI image generation with two mock AI models
- User credit management with atomic deductions and refunds
- Configurable failure simulation for testing
- Weekly usage reporting with anomaly detection
- Comprehensive validation and error handling

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Firebase        │────▶│ Cloud Functions  │────▶│ Mock AI Models  │
│ Functions       │     │ - createRequest  │     │ - Model A       │
│ (HTTP Triggers) │     │ - getUserCredits │     │ - Model B       │
└─────────────────┘     │ - weeklyReport   │     └─────────────────┘
                        └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    Firestore     │
                        │ - users          │
                        │ - requests       │
                        │ - transactions   │
                        │ - reports        │
                        └──────────────────┘
```

## 📦 Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Firebase CLI (`npm install -g firebase-tools`)
- Google Cloud account with Firebase project

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-image-generation-backend
   ```

2. **Install Firebase CLI**
   ```bash
   npm install -g firebase-tools
   ```

3. **Install Python dependencies**
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

4. **Initialize Firebase project**
   ```bash
   firebase login
   firebase init
   # Select: Functions, Firestore, Emulators
   # Choose Python for functions
   ```

5. **Import initial data to emulator**
   ```bash
   firebase emulators:start --import=./emulator-data
   ```

## 📁 Project Structure

```
ai-image-generation-backend/
├── functions/
│   ├── main.py                 # Main entry point for Cloud Functions
│   ├── requirements.txt        # Python dependencies
│   ├── services/
│   │   ├── __init__.py
│   │   ├── credit_service.py   # Credit management logic
│   │   ├── generation_service.py # Image generation simulation
│   │   └── report_service.py   # Weekly reporting logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py         # Generation request model
│   │   └── transaction.py     # Credit transaction model
│   ├── validators/
│   │   ├── __init__.py
│   │   └── request_validator.py # Input validation
│   └── tests/
│       ├── test_credit_service.py
│       ├── test_report_service.py
│       ├── test_generation_service.py
│       └── test_validators.py
├── emulator-data/              # Initial data for Firebase emulator
│   ├── firestore_export/
│   └── auth_export/
├── firebase.json               # Firebase configuration
├── .firebaserc                # Firebase project configuration
└── README.md                  # This file
```

## 📡 API Documentation

### 1. Create Generation Request

**Endpoint:** `POST /createGenerationRequest`

**Request Body:**
```json
{
  "userId": "user123",
  "model": "Model A",
  "style": "realistic",
  "color": "vibrant",
  "size": "1024x1024",
  "prompt": "A beautiful sunset over mountains"
}
```

**Response:**
```json
{
  "generationRequestId": "req_abc123",
  "deductedCredits": 3,
  "imageUrl": "https://placeholder-model-a.com/image123.jpg"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input parameters
- `402 Payment Required`: Insufficient credits
- `500 Internal Server Error`: Generation failure

### 2. Get User Credits

**Endpoint:** `GET /getUserCredits?userId=user123`

**Response:**
```json
{
  "currentCredits": 47,
  "transactions": [
    {
      "id": "trans_xyz789",
      "type": "deduction",
      "credits": 3,
      "generationRequestId": "req_abc123",
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "id": "trans_def456",
      "type": "refund",
      "credits": 4,
      "generationRequestId": "req_failed789",
      "timestamp": "2025-01-14T15:45:00Z"
    }
  ]
}
```

### 3. Schedule Weekly Report

**Endpoint:** Triggered by Cloud Scheduler (every Monday at 00:00 UTC)

**Response:**
```json
{
  "reportStatus": "success"
}
```

## 💾 Database Schema

### Collections

#### 1. users
```javascript
{
  "userId": "user123",
  "email": "user@example.com",
  "credits": 50,
  "createdAt": Timestamp,
  "updatedAt": Timestamp
}
```

#### 2. generation_requests
```javascript
{
  "requestId": "req_abc123",
  "userId": "user123",
  "model": "Model A",
  "style": "realistic",
  "color": "vibrant",
  "size": "1024x1024",
  "prompt": "A beautiful sunset",
  "status": "completed", // pending, completed, failed
  "imageUrl": "https://...",
  "creditsCharged": 3,
  "createdAt": Timestamp,
  "completedAt": Timestamp
}
```

#### 3. credit_transactions
```javascript
{
  "transactionId": "trans_xyz789",
  "userId": "user123",
  "type": "deduction", // deduction, refund
  "credits": 3,
  "generationRequestId": "req_abc123",
  "reason": "Image generation",
  "timestamp": Timestamp
}
```

#### 4. weekly_reports
```javascript
{
  "reportId": "report_20250120",
  "weekStartDate": "2025-01-13",
  "weekEndDate": "2025-01-19",
  "totalRequests": 1523,
  "successfulRequests": 1447,
  "failedRequests": 76,
  "totalCreditsConsumed": 4569,
  "totalCreditsRefunded": 228,
  "requestsByModel": {
    "Model A": 823,
    "Model B": 700
  },
  "requestsBySize": {
    "512x512": 456,
    "1024x1024": 789,
    "1024x1792": 278
  },
  "requestsByStyle": {
    "realistic": 412,
    "anime": 367,
    // ...
  },
  "anomalies": [],
  "createdAt": Timestamp
}
```

#### 5. Configuration Collections
- **colors**: Valid color options
- **styles**: Valid style options  
- **sizes**: Size options with credit costs

## 🧪 Testing

### Running Tests

```bash
cd functions
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_credit_service.py

# Run tests with verbose output
python -m pytest -v
```

### Test Coverage

The test suite covers:
- ✅ Credit deduction and refund logic
- ✅ Input validation for all parameters
- ✅ Successful generation scenarios
- ✅ Failed generation with automatic refunds
- ✅ Concurrent request handling
- ✅ Weekly report generation
- ✅ Edge cases and error scenarios

### Running with Firebase Emulator

```bash
# Start emulator with test data
firebase emulators:start --import=./emulator-data

# In another terminal, run tests
python -m pytest
```


## 🔧 Configuration

### Credit Costs

| Image Size | Credit Cost |
|------------|-------------|
| 512x512    | 1           |
| 1024x1024  | 3           |
| 1024x1792  | 4           |

### Valid Options

**Styles:** realistic, anime, oil painting, sketch, cyberpunk, watercolor

**Colors:** vibrant, monochrome, pastel, neon, vintage

**Models:** Model A, Model B

## 📊 Monitoring

Weekly reports include:
- Total requests and success/failure rates
- Credit consumption and refund statistics
- Breakdown by model, style, size, and color
- Anomaly detection for unusual usage patterns
- Performance metrics
