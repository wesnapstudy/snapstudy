# SnapStudy AWS Architecture Documentation

## Overview
SnapStudy is a serverless, AI-powered adaptive learning platform built on AWS. The architecture follows AWS Well-Architected Framework principles with emphasis on scalability, security, and cost optimization.

## Architecture Components

### 🌐 Frontend Layer
- **Technology**: React SPA (Single Page Application)
- **Hosting**: Amazon S3 + CloudFront (Static Website Hosting)
- **Domain**: `snapstudy-frontend-054037102331-us-east-1.s3-website-us-east-1.amazonaws.com`
- **Features**: 
  - Responsive design
  - Progressive Web App capabilities
  - Offline content caching

### 🛡️ Security Layer
- **AWS WAF**: Web Application Firewall
  - Rate limiting (1000 req/5min per IP)
  - SQL injection protection
  - Common attack patterns blocking
  - Known bad inputs filtering
- **Amazon Cognito**: User authentication and authorization
  - User Pool for identity management
  - JWT token-based authentication
  - Custom user attributes for learning preferences

### 🚪 API Layer
- **Amazon API Gateway**: RESTful API management
  - Regional endpoint configuration
  - CORS enabled for cross-origin requests
  - Request/response logging
  - Throttling and usage plans
  - Custom domain support (configurable)

### ⚡ Compute Layer
- **AWS Lambda**: Serverless compute
  - **Runtime**: Python 3.11
  - **Framework**: FastAPI with Mangum adapter
  - **Memory**: 512 MB
  - **Timeout**: 30 seconds
  - **Concurrency**: Auto-scaling based on demand
  - **Environment Variables**: 
    - Database table names
    - S3 bucket names
    - Cognito configuration
    - AWS region settings

### 🗄️ Database Layer
- **Amazon DynamoDB**: NoSQL database (6 tables)

#### Table Specifications:

1. **SnapStudy-Users**
   - **Primary Key**: `user_id` (String)
   - **GSI**: `EmailIndex` on `email`
   - **Attributes**: Profile, preferences, learning style
   - **Features**: Point-in-time recovery, encryption

2. **SnapStudy-Lessons**
   - **Primary Key**: `lesson_id` (String)
   - **GSI**: `UserLessonsIndex` on `user_id` + `created_at`
   - **Attributes**: Content, metadata, difficulty level
   - **Features**: TTL enabled, streams for real-time updates

3. **SnapStudy-MicroLessons**
   - **Primary Key**: `micro_lesson_id` (String)
   - **GSI**: `LessonMicroLessonsIndex` on `lesson_id` + `sequence_number`
   - **Attributes**: Bite-sized content, progress tracking
   - **Features**: Ordered sequences, adaptive content

4. **SnapStudy-Quizzes**
   - **Primary Key**: `quiz_id` (String)
   - **GSI**: `MicroLessonQuizzesIndex` on `micro_lesson_id`
   - **Attributes**: Questions, answers, scoring logic
   - **Features**: AI-generated content, difficulty adaptation

5. **SnapStudy-UserEngagement**
   - **Primary Key**: `engagement_id` (String)
   - **GSI**: `UserEngagementIndex` on `user_id` + `timestamp`
   - **Attributes**: Learning analytics, time spent, interactions
   - **Features**: TTL (365 days), analytics aggregation

6. **SnapStudy-ChatHistory**
   - **Primary Key**: `session_id` (String)
   - **GSI**: `UserChatHistoryIndex` on `user_id` + `created_at`
   - **Attributes**: Conversation history, context
   - **Features**: TTL (30 days), conversation continuity

7. **SnapStudy-VideoContent**
   - **Primary Key**: `video_id` (String)
   - **GSI**: `LessonVideosIndex` on `lesson_id` + `created_at`
   - **GSI**: `UserVideoPreferencesIndex` on `user_id` + `video_type`
   - **Attributes**: Video metadata, user preferences, generated content
   - **Features**: TTL enabled, video tracking

8. **SnapStudy-VideoJobs**
   - **Primary Key**: `job_id` (String)
   - **GSI**: `UserJobsIndex` on `user_id` + `created_at`
   - **Attributes**: Job status, processing details, results
   - **Features**: TTL (30 days), job tracking

### 📦 Storage Layer
- **Amazon S3**: Object storage
  - **Content Bucket**: `snapstudy-content-054037102331-us-east-1`
  - **Features**:
    - Server-side encryption (AES-256)
    - Versioning enabled
    - Lifecycle policies (IA after 30 days)
    - CORS configuration
    - Public access blocked (secure access only)

### 🤖 AI/ML Services

#### Amazon Bedrock
- **Model**: Claude 3 (Anthropic)
- **Use Cases**:
  - Intelligent chat tutoring
  - Adaptive quiz generation
  - Content summarization
  - Learning path optimization
- **Features**:
  - Streaming responses
  - Context-aware conversations
  - Guardrails for safe AI interactions

#### Amazon Textract
- **Purpose**: Document processing and text extraction
- **Supported Formats**: PDF, PNG, JPEG, TIFF
- **Features**:
  - OCR (Optical Character Recognition)
  - Form data extraction
  - Table detection and extraction

#### Amazon Transcribe
- **Purpose**: Audio and video content processing
- **Features**:
  - Speech-to-text conversion
  - Multiple language support
  - Timestamp generation
  - Speaker identification

#### Amazon Nova Reel
- **Purpose**: AI-powered video generation from text
- **Features**:
  - Text-to-video conversion
  - Educational video styles
  - Customizable duration and quality
  - User preference-based generation

#### Amazon MediaConvert
- **Purpose**: Video processing and snippet creation
- **Features**:
  - Video format conversion
  - Lecture snippet extraction
  - Quality optimization
  - Batch processing capabilities

#### Amazon Rekognition
- **Purpose**: Video content analysis
- **Features**:
  - Scene detection for optimal cut points
  - Content moderation
  - Object and activity recognition
  - Timestamp-based analysis

### 📊 Monitoring & Analytics

#### Amazon CloudWatch
- **Dashboards**: Real-time metrics visualization
- **Alarms**: Proactive monitoring
  - Lambda error rates
  - API Gateway 5XX errors
  - Lambda duration (performance)
  - DynamoDB throttling
- **Logs**: Centralized logging for debugging
- **Metrics**: Custom business metrics

#### Key Performance Indicators (KPIs)
- API response times
- User engagement rates
- Learning completion rates
- Error rates and availability
- Cost per active user

## Data Flow Architecture

### 1. User Registration & Authentication
```
User → Frontend → API Gateway → Lambda → Cognito → DynamoDB (Users)
```

### 2. Content Upload & Processing
```
Educator → Frontend → API Gateway → Lambda → S3 → Textract/Transcribe → DynamoDB (Lessons)
```

### 3. Adaptive Learning Flow
```
Student → Frontend → API Gateway → Lambda → Bedrock → DynamoDB (Analytics) → Personalized Content
```

### 4. Chat Tutoring System
```
Student → Frontend → WebSocket/API → Lambda → Bedrock → DynamoDB (ChatHistory) → Real-time Response
```

### 5. AI Video Generation
```
User → Frontend → API Gateway → Lambda → Nova Reel → S3 (Video Storage) → DynamoDB (VideoContent)
```

### 6. Lecture Snippet Creation
```
Educator → Upload Video → Lambda → MediaConvert + Rekognition → Video Snippets → S3 → DynamoDB (VideoJobs)
```

### 5. Progress Analytics
```
Learning Activity → Lambda → DynamoDB (UserEngagement) → CloudWatch → Analytics Dashboard
```

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Cognito Integration**: Centralized identity management
- **Role-Based Access**: Different permissions for students/educators
- **API Key Management**: Secure service-to-service communication

### Data Protection
- **Encryption at Rest**: All DynamoDB tables and S3 objects
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Protection**: NoSQL database eliminates SQL injection risks

### Network Security
- **WAF Rules**: Application-layer protection
- **VPC Integration**: Optional for enhanced network isolation
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: DDoS protection and fair usage

## Scalability & Performance

### Auto-Scaling Components
- **Lambda**: Automatic concurrency scaling (up to 1000 concurrent executions)
- **DynamoDB**: On-demand billing with automatic scaling
- **API Gateway**: Built-in scaling and throttling
- **S3**: Unlimited storage capacity

### Performance Optimizations
- **DynamoDB GSIs**: Optimized query patterns
- **Lambda Cold Start Mitigation**: Provisioned concurrency for critical functions
- **CloudFront CDN**: Global content delivery for frontend
- **Connection Pooling**: Efficient database connections

### Cost Optimization
- **Serverless Architecture**: Pay-per-use pricing model
- **DynamoDB On-Demand**: No pre-provisioned capacity
- **S3 Lifecycle Policies**: Automatic cost optimization
- **Lambda Right-Sizing**: Optimal memory allocation

## Disaster Recovery & Backup

### Data Backup
- **DynamoDB**: Point-in-time recovery enabled
- **S3**: Cross-region replication (configurable)
- **Lambda**: Code stored in version control
- **Infrastructure**: Infrastructure as Code (CDK)

### High Availability
- **Multi-AZ Deployment**: DynamoDB and Lambda automatically distributed
- **Regional Failover**: API Gateway regional endpoints
- **Health Checks**: CloudWatch alarms for proactive monitoring

## Deployment Architecture

### Infrastructure as Code
- **AWS CDK**: Python-based infrastructure definitions
- **Version Control**: Git-based infrastructure versioning
- **Automated Deployment**: CI/CD pipeline ready
- **Environment Separation**: Dev/Staging/Production environments

### Deployment Process
1. **Code Commit**: Developer pushes code changes
2. **Build Process**: Lambda deployment packages created
3. **Infrastructure Update**: CDK deploys infrastructure changes
4. **Application Deployment**: Lambda functions updated
5. **Health Checks**: Automated testing and validation
6. **Rollback Capability**: Quick rollback on issues

## Integration Points

### External Services
- **Anthropic Claude**: Via Amazon Bedrock
- **AWS Services**: Native AWS SDK integration
- **Third-party APIs**: Configurable webhook support
- **Analytics Platforms**: CloudWatch integration

### API Endpoints
- **Authentication**: `/api/v1/auth/*`
- **User Management**: `/api/v1/users/*`
- **Content Management**: `/api/v1/content/*`
- **Learning**: `/api/v1/lessons/*`
- **Chat**: `/api/v1/chat/*`
- **Analytics**: `/api/v1/analytics/*`

## Future Enhancements

### Planned Features
- **Amazon Q Developer**: Code assistance integration
- **Multi-language Support**: I18n implementation
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: Machine learning insights
- **Real-time Collaboration**: WebSocket-based features

### Scalability Roadmap
- **Global Deployment**: Multi-region architecture
- **CDN Integration**: CloudFront for API caching
- **Database Sharding**: Advanced DynamoDB patterns
- **Microservices**: Service decomposition for scale

## Cost Estimation

### Monthly Cost Breakdown (Estimated for 1000 active users)
- **Lambda**: $20-50 (based on usage)
- **DynamoDB**: $25-75 (on-demand pricing)
- **API Gateway**: $10-25 (per million requests)
- **S3**: $5-15 (storage and requests)
- **Bedrock**: $50-200 (AI model usage)
- **CloudWatch**: $5-15 (monitoring)
- **Total**: ~$115-380/month

### Cost Optimization Strategies
- **Reserved Capacity**: For predictable workloads
- **Spot Instances**: For batch processing (future)
- **Data Lifecycle**: Automated archival policies
- **Usage Monitoring**: Real-time cost tracking

---

## Quick Start Commands

### Deploy the Architecture
```bash
# Install dependencies
cd backend
pip install -r requirements.txt
pip install -r infrastructure/requirements.txt

# Deploy infrastructure
python deploy.py

# Or manual deployment
cd infrastructure
cdk bootstrap
cdk deploy
```

### Generate Architecture Diagram
```bash
# Install diagram library
pip install diagrams

# Generate diagrams
python create_architecture_diagram.py
```

### Monitor the System
```bash
# Check deployment status
aws cloudformation describe-stacks --stack-name SnapStudyStack

# View logs
aws logs tail /aws/lambda/SnapStudy-ApiLambda --follow

# Check metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations
```

---

*This architecture documentation is maintained alongside the codebase and updated with each major release.*