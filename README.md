# 🏥 AI Medical Clinic Phone Call Agent

A sophisticated voice-based AI phone call agent for medical clinic reception using CrewAI, FastAPI, and React. Simulates a real phone conversation with voice-only interaction, no typing or UI buttons required.

## 🎯 Features

✅ **Phone Call Simulation** - Single "Call Clinic" button, entire interaction through voice
✅ **Full-Duplex Conversation** - Natural back-and-forth dialogue with AI agent
✅ **Voice Activity Detection (VAD)** - Automatic silence detection to know when user stops speaking
✅ **Speech-to-Text** - Continuous voice transcription using Whisper
✅ **Text-to-Speech** - Natural, calm, clinic-appropriate voice responses
✅ **CrewAI Backend** - YAML-based agent architecture with professional medical receptionist behavior
✅ **LLaMA 3.2 Integration** - Deterministic, context-aware AI reasoning
✅ **Session Memory** - Conversation context preservation
✅ **Service Management** - Browse clinics services and check availability
✅ **Appointment Booking** - Voice-based booking with confirmation
✅ **Medical Safety** - Emergency escalation protocols and disclaimers

## 🏗️ Architecture

```
ai-medical-clinic-phone-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── api/
│   │   │   └── call.py             # WebSocket call endpoints
│   │   ├── crew/
│   │   │   ├── crew.py             # CrewAI initialization
│   │   │   ├── agents/
│   │   │   │   └── medical_call_agent.yaml
│   │   │   ├── tasks/
│   │   │   │   └── patient_call_flow.yaml
│   │   │   └── tools/
│   │   │       ├── service_lookup.yaml
│   │   │       ├── availability_checker.yaml
│   │   │       └── reservation_creator.yaml
│   │   ├── audio/
│   │   │   ├── vad.py              # Voice Activity Detection
│   │   │   ├── speech_to_text.py   # Whisper integration
│   │   │   ├── text_to_speech.py   # TTS with ffmpeg
│   │   │   ├── audio_stream.py     # Audio pipeline management
│   │   │   └── utils.py            # Audio utilities
│   │   ├── data/
│   │   │   ├── services.json       # Available services database
│   │   │   └── reservations.json   # Booking storage
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   └── config.py               # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   └── Dockerfile                  # Docker configuration
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main React component
│   │   ├── components/
│   │   │   ├── CallButton.jsx      # Single "Call Clinic" button
│   │   │   ├── CallStatus.jsx      # Call status indicator
│   │   │   └── AudioVisualizer.jsx # Real-time audio visualization
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js     # WebSocket connection hook
│   │   │   └── useAudioRecorder.js # Audio recording hook
│   │   ├── services/
│   │   │   └── callService.js      # Call service logic
│   │   ├── styles/
│   │   │   ├── App.css
│   │   │   └── index.css
│   │   └── index.jsx               # React entry point
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml              # Multi-container orchestration
├── .gitignore
└── setup.sh                        # Automated setup script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- ffmpeg (`apt-get install ffmpeg`)
- Git

### Backend Setup

```bash
# 1. Clone and navigate
git clone https://github.com/lukacerovic/ai-medical-clinic-phone-agent.git
cd ai-medical-clinic-phone-agent/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys and settings

# 5. Download LLaMA 3.2 model (one-time)
ollama pull llama2  # or appropriate model version

# 6. Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env
# Update REACT_APP_API_URL if needed

# 4. Start development server
npm start
```

Access the application at `http://localhost:3000`

### Docker Setup (All-in-One)

```bash
# From repository root
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📞 How It Works

### Call Flow

1. **User presses "Call Clinic"** button
2. **Microphone activates** - Browser requests microphone permission
3. **AI speaks first** - Clinic greeting and introduction
4. **Full-duplex loop begins:**
   - System listens continuously
   - VAD detects when user stops speaking (1-1.5s silence)
   - Audio chunk sent to backend
   - Whisper transcribes to text
   - CrewAI agent reasons and generates response
   - TTS converts response to audio
   - Audio played back to user
   - Loop continues until call ends

### Example Conversation

```
AI: "Good afternoon, welcome to Central Medical Clinic. 
     How can I help you today?"

User: "I'd like to book an appointment"

AI: "Of course! What type of service are you interested in? 
     We offer general consultations, dental cleaning, 
     blood tests, and eye exams."

User: "I need a general consultation"

AI: "Perfect. General consultations are 30 minutes and cost $50.
     What date and time work best for you?"

User: "Next Friday at 2 PM"

AI: "Just checking availability... Yes, we have an opening at 2 PM 
     on Friday, January 10th. Before I confirm, may I get your 
     full name and date of birth?"

User: "John Smith, born March 15, 1985"

AI: "Thank you John. So to confirm: 
     General consultation, Friday January 10th at 2 PM. 
     Your date of birth is March 15, 1985. Is everything correct?"

User: "Yes, that's right"

AI: "Excellent! Your appointment is confirmed. You'll receive a 
     confirmation email shortly. Is there anything else I can help 
     with today?"

User: "No, thank you"

AI: "Thank you for calling Central Medical Clinic. Have a great day!"
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
# Model & API
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENAI_API_KEY=your_key_for_whisper  # For Whisper API
ELEVENLABS_API_KEY=your_key  # Optional: for premium TTS

# Audio Settings
VAD_SILENCE_THRESHOLD=1.5
VAD_MIN_SPEECH_LENGTH=0.5
SAMPLE_RATE=16000
CHUNK_SIZE=1024

# Server
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000"]

# Database
SERVICES_JSON_PATH=./data/services.json
RESERVATIONS_JSON_PATH=./data/reservations.json
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 🎙️ Audio Pipeline Details

### Speech-to-Text (Whisper)

- Continuous microphone input
- VAD-based chunking (silence detection)
- Whisper transcription
- Automatic language detection
- Confidence scoring

### Text-to-Speech (TTS)

- Backend options:
  - **gTTS** (free, Google)
  - **ElevenLabs** (premium, natural voices)
  - **Coqui TTS** (open-source, local)
- ffmpeg processing for audio normalization
- Pacing/breaks for natural conversation

### Voice Activity Detection (VAD)

- PyAudio + WebRTC VAD algorithm
- Configurable silence threshold (1-1.5s default)
- Real-time detection
- Automatic recording stop

## 🧠 CrewAI Agent Design

### Agent Profile: Medical Receptionist

**Personality:**
- Polite and professional
- Calm and reassuring
- Detail-oriented
- Patient and understanding

**Capabilities:**
- Service information lookup
- Availability checking
- Appointment booking
- Context memory (remembers patient preferences)
- Escalation protocols for emergencies

### Tools Available

1. **ServiceLookup** - Browse available medical services
2. **AvailabilityChecker** - Check appointment slots
3. **ReservationCreator** - Book appointments
4. **PatientInfoValidator** - Validate patient details

## 🛡️ Safety & Medical Compliance

### Built-in Safeguards

- ✅ AI explicitly states it's a virtual assistant
- ✅ No diagnosis or medical advice provided
- ✅ Emergency detection and escalation
- ✅ Conversation logging for audit trail
- ✅ Session isolation and privacy
- ✅ Input sanitization

### Emergency Keywords

System automatically escalates if user mentions:
- Chest pain, difficulty breathing
- Severe bleeding
- Loss of consciousness
- Severe allergic reactions
- Any life-threatening symptoms

## 📊 Data Schema

### services.json
```json
[
  {
    "id": "general-consultation",
    "name": "General Consultation",
    "durationMinutes": 30,
    "price": 50,
    "description": "Initial consultation with a general practitioner",
    "whatIsIncluded": "Medical history review, vital signs, general examination",
    "howItsDone": "In-person at clinic or video call",
    "specialPreparation": null
  }
]
```

### reservations.json
```json
[
  {
    "id": "RES001",
    "serviceId": "general-consultation",
    "date": "2026-01-10",
    "time": "14:00",
    "patientName": "John Smith",
    "patientDOB": "1985-03-15",
    "status": "confirmed",
    "createdAt": "2026-01-03T12:13:00Z"
  }
]
```

## 📝 API Endpoints

### WebSocket
- `ws://localhost:8000/ws/call/{session_id}` - Voice call endpoint

### REST
- `POST /api/call/start` - Initialize call session
- `GET /api/call/status/{session_id}` - Get call status
- `POST /api/call/end` - Terminate call
- `GET /api/services` - List available services
- `GET /api/availability` - Check appointment slots
- `GET /api/reservations` - Get user's reservations

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing
1. Open `http://localhost:3000`
2. Press "Call Clinic"
3. Allow microphone access
4. Speak naturally with the AI agent
5. Complete a test booking

## 🚧 Development Tips

### Debugging Audio
```python
# In backend/app/audio/vad.py, enable debug logging:
DEBUG = True  # Logs VAD decisions
```

### Testing CrewAI Flow
```bash
cd backend
python -m app.crew.crew  # Run CrewAI in isolation
```

### Frontend Console Logs
```javascript
// In frontend/src/services/callService.js:
const DEBUG = true;  // Enable verbose logging
```

## 📦 Dependencies

### Backend
- fastapi - Web framework
- python-multipart - File uploads
- websockets - WebSocket support
- crewai - Agent framework
- ollama - LLaMA model integration
- openai-whisper - Speech-to-text
- gtts - Text-to-speech
- pyaudio - Audio I/O
- webrtcvad - Voice activity detection
- pydantic - Data validation
- python-dotenv - Environment config
- uvicorn - ASGI server

### Frontend
- react - UI framework
- react-dom - React DOM
- axios - HTTP client
- ws - WebSocket client

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙋 Support & Issues

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Provide detailed reproduction steps

## 🔐 Security

- Never commit `.env` files
- Use environment variables for all secrets
- Validate and sanitize all user input
- Log sensitive data minimally
- Keep dependencies updated

## 📚 References

- [CrewAI Documentation](https://docs.crewai.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [WebRTC VAD](https://github.com/wiseman/py-webrtcvad)
- [React Documentation](https://react.dev/)

---

**Built with ❤️ for modern medical clinic communication**
