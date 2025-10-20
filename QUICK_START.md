# SnapStudy - Quick Start Guide

## 🚀 Deploy in 2 Commands

### Prerequisites
- AWS Account with "hackathon" profile configured
- Bedrock access to Claude 3.5 Sonnet (us-east-1)
- Python 3.11+, Node.js 18+, AWS CLI

### Step 1: Deploy Core System (10-15 minutes)

```powershell
cd D:\repo\hackathon\study
.\deploy-complete.ps1
```

**What gets deployed:**
- ✅ Backend API (Lambda + API Gateway)
- ✅ Frontend Website (S3 static hosting)
- ✅ Database (6 DynamoDB tables)
- ✅ Authentication (Cognito User Pool)
- ✅ AI Services (Bedrock Claude 3.5 Sonnet)
- ✅ Security (AWS WAF with 4 rules)
- ✅ Monitoring (CloudWatch Dashboard + 3 alarms)

**Cost:** ~$41/month + Bedrock usage (~$300/month for 100k conversations)

### Step 2: Enable Enhanced AI (Optional, 20-30 minutes)

```powershell
.\setup-amazon-q.ps1
```

**What gets enabled:**
- ✅ Amazon Q Business for educational resources
- ✅ Bedrock Guardrails for content safety
- ✅ Enhanced chat with multi-AI orchestration
- ✅ Research assistance endpoints
- ✅ Coding help with validation

**Additional Cost:** ~$30-105/month (depending on usage)

---

## 📊 What You Get

### Backend API Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/me` - Get current user profile

**Lessons:**
- `POST /api/v1/lessons/upload` - Upload educational content
- `GET /api/v1/lessons/{lesson_id}` - Get lesson details
- `GET /api/v1/lessons/user/{user_id}` - Get user's lessons
- `GET /api/v1/lessons/{lesson_id}/micro-lessons` - Get micro-lessons

**Enhanced Chat:**
- `WS /api/v1/chat/ws/{user_id}` - WebSocket chat
- `POST /api/v1/chat/message` - REST chat message
- `POST /api/v1/chat/research` - Educational research
- `POST /api/v1/chat/coding-help` - Programming assistance
- `GET /api/v1/chat/health` - Chat service health
- `GET /api/v1/chat/q-services/health` - Amazon Q health

**Progress Tracking:**
- `POST /api/v1/progress/track` - Track learning activity
- `GET /api/v1/progress/{user_id}` - Get user progress
- `GET /api/v1/progress/{user_id}/analytics` - Learning analytics

### Frontend Features

**User Interface:**
- Login/Registration page
- Dashboard with lesson library
- Lesson viewer with micro-lesson progression
- Interactive quiz interface
- Real-time AI chat assistant
- Progress tracking visualizations
- Profile management

**Responsive Design:**
- Desktop, tablet, mobile support
- Touch-friendly interactions
- Adaptive layouts

---

## 🧪 Testing Your Deployment

### 1. Test Backend API

```powershell
# Health check
Invoke-RestMethod -Uri "YOUR-API-URL/health"

# Chat service health
Invoke-RestMethod -Uri "YOUR-API-URL/api/v1/chat/health"

# Amazon Q services health (if configured)
Invoke-RestMethod -Uri "YOUR-API-URL/api/v1/chat/q-services/health"
```

### 2. Test Frontend Website

Open browser to: `YOUR-FRONTEND-URL`

**Test with default user:**
- Email: `test@example.com`
- Password: `TestPassword123!`

### 3. Test Enhanced Chat

```powershell
# Test research endpoint
$body = @{
    topic = "machine learning"
    resource_type = "tutorial"
    difficulty_level = "beginner"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR-API-URL/api/v1/chat/research" `
    -Method POST `
    -Headers @{"Authorization"="Bearer YOUR-JWT-TOKEN"; "Content-Type"="application/json"} `
    -Body $body
```

```powershell
# Test coding help
$body = @{
    message = "How do I implement a binary search in Python?"
    programming_language = "python"
    skill_level = "intermediate"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR-API-URL/api/v1/chat/coding-help" `
    -Method POST `
    -Headers @{"Authorization"="Bearer YOUR-JWT-TOKEN"; "Content-Type"="application/json"} `
    -Body $body
```

### 4. Monitor Performance

**CloudWatch Dashboard:**
1. Go to: https://console.aws.amazon.com/cloudwatch
2. Region: US East (N. Virginia)
3. Dashboards → SnapStudy-Metrics

**Metrics to watch:**
- Lambda invocations, errors, duration
- API Gateway requests, latency, errors
- DynamoDB read/write capacity

**AWS WAF:**
1. Go to: https://console.aws.amazon.com/wafv2
2. Region: US East (N. Virginia)
3. Web ACLs → SnapStudyApiWaf

---

## 🏗️ System Architecture (Simplified)

```
User Browser
     │
     ├──────────────┬──────────────┐
     │              │              │
     v              v              v
┌─────────┐  ┌──────────┐  ┌──────────┐
│S3 Static│  │   API    │  │ Cognito  │
│ Website │  │ Gateway  │  │UserPool  │
└─────────┘  │ (+WAF)   │  └──────────┘
             └─────┬────┘
                   │
                   v
             ┌──────────┐
             │ Lambda   │
             │ FastAPI  │
             └─────┬────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     v             v             v
┌─────────┐  ┌──────────┐  ┌──────────┐
│DynamoDB │  │ Bedrock  │  │ Amazon Q │
│6 Tables │  │ Claude   │  │(Optional)│
└─────────┘  └──────────┘  └──────────┘
     │
     v
┌──────────┐
│CloudWatch│
│Dashboard │
└──────────┘
```

---

## 💡 Key Features

### 🎓 Adaptive Learning
- AI analyzes user performance in real-time
- Automatically adjusts difficulty level
- Personalized micro-lessons (5-7 min each)
- Progressive learning paths

### 🤖 Multi-AI Chat System
- **Bedrock Claude 3.5 Sonnet**: General conversation
- **Amazon Q Business**: Educational resources (optional)
- **Agent Core**: Autonomous reasoning
- **Fallback Mechanism**: Always available

### 🛡️ 5-Layer Content Safety
1. **Bedrock Guardrails**: AWS-managed filtering (optional)
2. **Educational Appropriateness**: Keyword scoring
3. **Age Appropriateness**: Level-based validation
4. **Harmful Content**: Pattern detection
5. **Academic Integrity**: Plagiarism prevention

### 📊 Analytics & Insights
- Learning time tracking
- Quiz performance analytics
- Engagement heatmaps
- Progress visualizations

---

## 🎯 Common Use Cases

### 1. Upload Educational Content

```javascript
// Frontend (React)
const uploadLesson = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', 'Introduction to Python');
  formData.append('description', 'Learn Python basics');

  const response = await fetch(`${API_URL}/api/v1/lessons/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  const lesson = await response.json();
  console.log('Lesson created:', lesson);
};
```

### 2. Chat with AI Assistant

```javascript
// WebSocket Chat
const ws = new WebSocket(`wss://YOUR-API-URL/api/v1/chat/ws/${userId}?token=${jwt}`);

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Explain quantum entanglement in simple terms",
    session_id: "session-123"
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('AI:', response.message);
  console.log('Intent:', response.intent);
  console.log('Source:', response.metadata.service_used);
};
```

### 3. Get Educational Resources

```javascript
// Research Assistance
const getResources = async (topic) => {
  const response = await fetch(`${API_URL}/api/v1/chat/research`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic: topic,
      resource_type: 'tutorial',
      difficulty_level: 'intermediate'
    })
  });

  const data = await response.json();
  console.log('Resources:', data.resources);
};
```

### 4. Track Learning Progress

```javascript
// Track Engagement
const trackProgress = async (activityData) => {
  const response = await fetch(`${API_URL}/api/v1/progress/track`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      lesson_id: lessonId,
      activity_type: 'quiz_completion',
      score: 85,
      time_spent: 420 // seconds
    })
  });

  const result = await response.json();
  console.log('Progress tracked:', result);
};
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
JWT_SECRET_KEY=your-secret-key

# Amazon Q (Optional)
Q_BUSINESS_APPLICATION_ID=app-123abc
Q_BUSINESS_INDEX_ID=idx-456def
Q_DEVELOPER_ENABLED=false

# Bedrock Guardrails (Optional)
BEDROCK_GUARDRAIL_ID=guardrail-789ghi
BEDROCK_GUARDRAIL_VERSION=DRAFT

# Enhanced Chat
ENHANCED_CHAT_ENABLED=true
CONTENT_SAFETY_LEVEL=strict  # strict, moderate, permissive
```

### Frontend Configuration (.env.production)

```bash
REACT_APP_AWS_REGION=us-east-1
REACT_APP_USER_POOL_ID=us-east-1_ABC123
REACT_APP_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j1k
REACT_APP_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

---

## 🆘 Troubleshooting

### Deployment Issues

**"Bedrock access denied"**
→ Enable Claude 3.5 Sonnet in Bedrock console (us-east-1)

**"CDK bootstrap failed"**
→ Check IAM permissions (need AdministratorAccess)

**"Frontend build failed"**
→ Check Node.js version (need 18+), delete node_modules and reinstall

### Runtime Issues

**"API returning 401 Unauthorized"**
→ Check JWT token is included in Authorization header
→ Verify token hasn't expired (1 hour validity)

**"Chat not responding"**
→ Check CloudWatch logs: `/aws/lambda/SnapStudyStack-ApiLambda`
→ Verify Bedrock permissions in Lambda role

**"Amazon Q service not available"**
→ Expected if Q Business not configured (optional feature)
→ Run `.\setup-amazon-q.ps1` to enable

### Performance Issues

**"API is slow"**
→ Check Lambda duration in CloudWatch
→ Increase Lambda memory if needed
→ Verify DynamoDB isn't throttling

**"Chat responses delayed"**
→ Bedrock may be rate-limited
→ Check CloudWatch metrics for throttling
→ Consider implementing response caching

---

## 📚 Additional Resources

### Documentation
- **Complete Architecture**: `COMPLETE_ARCHITECTURE.md`
- **Deployment Guide**: `COMPLETE_DEPLOYMENT.md`
- **Amazon Q Setup**: `AMAZON_Q_SETUP_GUIDE.md`
- **Hackathon Submission**: `SUBMISSION.md`

### AWS Console Links
- **CloudWatch Dashboard**: https://console.aws.amazon.com/cloudwatch
- **Lambda Functions**: https://console.aws.amazon.com/lambda
- **DynamoDB Tables**: https://console.aws.amazon.com/dynamodb
- **Cognito User Pools**: https://console.aws.amazon.com/cognito
- **AWS WAF**: https://console.aws.amazon.com/wafv2
- **Bedrock**: https://console.aws.amazon.com/bedrock

### Support
- GitHub Issues: (your-repo-url)
- AWS Support: https://console.aws.amazon.com/support

---

## 🎉 Next Steps

1. ✅ Deploy basic system: `.\deploy-complete.ps1`
2. ✅ Test frontend and API
3. ✅ Create test user and login
4. ✅ Upload sample educational content
5. ✅ Try AI chat assistant
6. ⭐ (Optional) Enable Amazon Q: `.\setup-amazon-q.ps1`
7. ⭐ (Optional) Configure Bedrock Guardrails
8. 📹 Record demo video for hackathon
9. 📝 Finalize README and documentation
10. 🚀 Submit to AWS AI Agent Global Hackathon!

---

**Good luck with your hackathon submission! 🏆**
