# Chatbot Application for Interview Management

## Overview

This project is a chatbot-based system designed to assist in interview management and candidate evaluation. The application comprises a backend API built with FastAPI and a frontend interface using modern JavaScript frameworks. It supports functionalities like conducting chat-based interactions, managing interview records, and generating candidate comparisons and recommendations.

---

## Features

### Backend (`chat_api.py`)
- **Interview Management**:
  - Fetch a list of all interviews.
  - Compare interviews based on evaluation scores and generate recommendations.
  
- **Chatbot Processing**:
  - Handles candidate information and chat messages.
  - Generates chatbot responses tailored to interview scenarios.

- **Evaluation and Scoring**:
  - Processes interview messages to calculate evaluation scores.
  - Supports decision-making with automated recommendations.

---

### Frontend (`chat-store.js` and `Home.js`)
- **State Management**:
  - `chat-store.js` manages the state of chatbot interactions and interview data.
  - Synchronizes data with the backend through API calls.

- **User Interface**:
  - `Home.js` renders the chat interface.
  - Displays chatbot responses, user messages, and candidate information dynamically.

- **API Integration**:
  - Frontend communicates with the backend to fetch interview data (`/interviews`) and compare candidates (`/compare`).

---

## Setup Instructions

### Prerequisites
- **Backend**:
  - Python 3.8+
  - FastAPI
- **Frontend**:
  - Node.js 14+
  - npm or yarn
  

## Usage

1. Use the chatbot interface to:
   - Input candidate information.
   - Engage in chat-based mock interviews.
   - Fetch and compare interview records.
2. Backend ChatBot is live at `https://amra.databutton.app/talent-scout-chatbot`.

---

## API Endpoints

### GET `/interviews`
- Fetches a list of all recorded interviews.

### POST `/compare`
- Accepts a list of interview IDs and returns:
  - Comparison of evaluation scores.
  - Recommendations for each candidate.

---

## Future Enhancements
- Add support for real-time chat using WebSockets.
- Enhance the scoring mechanism with machine learning models.
- Improve frontend UI/UX for better user engagement.

---
