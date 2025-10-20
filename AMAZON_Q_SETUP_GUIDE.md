# Amazon Q Integration Setup Guide for SnapStudy

This guide walks you through setting up Amazon Q Business and Bedrock Guardrails to enhance the SnapStudy chatbot with advanced educational features and content safety.

## 🎯 Overview

The enhanced SnapStudy chatbot integrates:
- **Amazon Q Business**: Educational knowledge base and research assistance
- **Amazon Q Developer**: Coding help and programming assistance (when available)
- **Bedrock Guardrails**: Content safety and educational appropriateness filtering

## 📋 Prerequisites

- AWS Account with appropriate permissions
- SnapStudy backend deployed and running
- Access to AWS Console
- Basic understanding of AWS services

## 🚀 Step 1: Set Up Amazon Q Business

### 1.1 Create Q Business Application

1. **Navigate to Amazon Q Business Console**
   ```
   https://console.aws.amazon.com/q/business
   ```

2. **Create New Application**
   - Click "Create application"
   - Choose "Create with quick start" for faster setup
   - Application name: `SnapStudy-Educational-Assistant`
   - Description: `Educational knowledge base for SnapStudy learning platform`

3. **Configure Application Settings**
   - **Access management**: Choose "AWS IAM Identity Center" or "SAML 2.0"
   - **Encryption**: Use AWS managed keys (default)
   - **Service role**: Let AWS create a new role

### 1.2 Set Up Knowledge Base

1. **Add Data Sources**
   - Click "Add data source" in your Q Business application
   - Choose appropriate connectors:
     - **Web Crawler**: For educational websites and online resources
     - **SharePoint**: If you have educational documents in SharePoint
     - **S3**: For uploaded educational materials
     - **Confluence**: For internal knowledge base

2. **Configure Web Crawler (Recommended)**
   - **Data source name**: `Educational-Web-Resources`
   - **Starting URLs**: Add educational websites like:
     ```
     https://www.khanacademy.org/
     https://www.coursera.org/
     https://ocw.mit.edu/
     https://www.edx.org/
     ```
   - **Crawl depth**: 2-3 levels
   - **Content filters**: Include only educational content
   - **Sync schedule**: Daily or weekly

3. **Upload Educational Documents (Optional)**
   - Create S3 bucket: `snapstudy-educational-content`
   - Upload textbooks, research papers, study guides
   - Configure S3 data source in Q Business

### 1.3 Configure User Access

1. **Set Up User Groups**
   - Create group: `SnapStudy-Students`
   - Create group: `SnapStudy-Educators`
   - Assign appropriate permissions

2. **Configure Application Access**
   - Enable programmatic access for the SnapStudy application
   - Note the **Application ID** (you'll need this later)

## 🛡️ Step 2: Set Up Bedrock Guardrails

### 2.1 Create Educational Content Guardrail

1. **Navigate to Bedrock Console**
   ```
   https://console.aws.amazon.com/bedrock
   ```

2. **Create New Guardrail**
   - Go to "Guardrails" in the left sidebar
   - Click "Create guardrail"
   - **Name**: `SnapStudy-Educational-Content-Filter`
   - **Description**: `Content safety and educational appropriateness filter for SnapStudy`

### 2.2 Configure Content Filters

1. **Harmful Content Filters**
   - **Hate speech**: High strength (input and output)
   - **Insults**: High strength (input and output)
   - **Sexual content**: High strength (input and output)
   - **Violence**: High strength (input and output)
   - **Misconduct**: High strength (input and output)

2. **Denied Topics**
   - Add topic: "Non-educational content"
   - Definition: "Content that is not related to learning, education, or academic subjects"
   - Examples: "Entertainment gossip, sports scores, personal relationships"

3. **Word Filters**
   - Add inappropriate words and phrases
   - Include academic dishonesty terms: "cheat", "plagiarize", "copy homework"

4. **Sensitive Information Filters**
   - **Personal identifiers**: Medium strength
   - **Financial information**: High strength
   - **Health information**: Medium strength

### 2.3 Test and Deploy Guardrail

1. **Test Guardrail**
   - Use the test interface to validate filters
   - Test with educational content (should pass)
   - Test with inappropriate content (should block)

2. **Create Version**
   - Create a working version of the guardrail
   - Note the **Guardrail ID** and **Version**

## ⚙️ Step 3: Configure SnapStudy Backend

### 3.1 Update Environment Variables

Edit your `.env` file in the backend directory:

```bash
# Amazon Q Configuration
Q_BUSINESS_APPLICATION_ID=your-q-business-app-id-here
Q_BUSINESS_INDEX_ID=your-q-business-index-id-here
Q_DEVELOPER_ENABLED=false

# Bedrock Guardrails Configuration
BEDROCK_GUARDRAIL_ID=your-guardrail-id-here
BEDROCK_GUARDRAIL_VERSION=1

# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
CONTENT_SAFETY_LEVEL=strict
```

### 3.2 Update IAM Permissions

Ensure your Lambda execution role has these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "qbusiness:ChatSync",
                "qbusiness:Chat",
                "qbusiness:ListConversations",
                "qbusiness:GetConversation",
                "qbusiness:ListMessages"
            ],
            "Resource": "arn:aws:qbusiness:*:*:application/your-app-id/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:ApplyGuardrail",
                "bedrock:GetGuardrail"
            ],
            "Resource": "arn:aws:bedrock:*:*:guardrail/your-guardrail-id"
        }
    ]
}
```

## 🧪 Step 4: Test the Integration

### 4.1 Run Test Suite

```bash
cd backend
python test_enhanced_chat_system.py
```

### 4.2 Test Chat Endpoints

1. **Test Basic Chat**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Explain photosynthesis",
       "lesson_context": {"title": "Biology Basics"}
     }'
   ```

2. **Test Research Resources**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/research" \
     -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "machine learning algorithms"
     }'
   ```

3. **Test Coding Help**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/coding-help" \
     -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "How do I create a Python function?",
       "programming_language": "python"
     }'
   ```

4. **Check Service Health**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/chat/q-services/health" \
     -H "Authorization: Bearer your-jwt-token"
   ```

## 📊 Step 5: Monitor and Optimize

### 5.1 Monitor Q Business Usage

1. **CloudWatch Metrics**
   - Monitor Q Business API calls
   - Track response times and success rates
   - Set up alarms for failures

2. **Q Business Analytics**
   - Review conversation analytics in Q Business console
   - Analyze user query patterns
   - Identify knowledge gaps

### 5.2 Monitor Content Safety

1. **Guardrail Metrics**
   - Track blocked content attempts
   - Monitor false positives/negatives
   - Adjust filter sensitivity as needed

2. **Content Quality**
   - Review chat logs for inappropriate content
   - Validate educational appropriateness
   - Update guardrail rules based on findings

## 🔧 Troubleshooting

### Common Issues

1. **Q Business Access Denied**
   - Verify IAM permissions
   - Check application ID configuration
   - Ensure user has access to the Q Business application

2. **Guardrail Not Working**
   - Verify guardrail ID and version
   - Check IAM permissions for Bedrock
   - Test guardrail independently in Bedrock console

3. **Poor Response Quality**
   - Review knowledge base content
   - Add more relevant educational sources
   - Adjust Q Business retrieval settings

4. **High Latency**
   - Monitor Q Business response times
   - Consider caching frequently requested content
   - Optimize knowledge base indexing

### Debug Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# List Q Business applications
aws qbusiness list-applications --region us-east-1

# List Bedrock guardrails
aws bedrock list-guardrails --region us-east-1

# Test guardrail
aws bedrock apply-guardrail \
  --guardrail-identifier your-guardrail-id \
  --guardrail-version 1 \
  --source INPUT \
  --content '[{"text":{"text":"Test content"}}]'
```

## 🎯 Best Practices

### Content Management

1. **Curate Knowledge Base**
   - Regularly update educational content
   - Remove outdated or incorrect information
   - Add diverse learning resources

2. **Monitor Content Quality**
   - Review AI responses for accuracy
   - Implement feedback mechanisms
   - Update guardrails based on user reports

### Security and Safety

1. **Regular Guardrail Updates**
   - Review and update content filters monthly
   - Add new inappropriate terms as discovered
   - Test guardrails with edge cases

2. **Access Control**
   - Implement proper user authentication
   - Use least-privilege IAM policies
   - Monitor access logs regularly

### Performance Optimization

1. **Caching Strategy**
   - Cache frequently requested educational content
   - Implement response caching for common queries
   - Use CDN for static educational resources

2. **Cost Management**
   - Monitor Q Business usage costs
   - Implement query rate limiting
   - Optimize knowledge base size

## 📈 Success Metrics

Track these metrics to measure success:

- **User Engagement**: Chat session duration and frequency
- **Content Quality**: User satisfaction ratings
- **Safety Effectiveness**: Blocked inappropriate content percentage
- **Educational Value**: Learning outcome improvements
- **Response Accuracy**: Correct and helpful response rate

## 🔮 Future Enhancements

Consider these future improvements:

1. **Advanced Analytics**
   - Learning pattern analysis
   - Personalized content recommendations
   - Predictive learning assistance

2. **Multi-modal Support**
   - Image and document analysis
   - Voice interaction capabilities
   - Video content integration

3. **Collaborative Features**
   - Peer learning assistance
   - Group study support
   - Educator oversight tools

## 📞 Support and Resources

- **AWS Documentation**: [Amazon Q Business User Guide](https://docs.aws.amazon.com/amazonq/latest/business-use-dg/)
- **Bedrock Guardrails**: [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- **SnapStudy Support**: Contact your development team for application-specific issues

---

**Note**: This setup enables advanced educational features in SnapStudy. The basic chat functionality works without Amazon Q, but these enhancements provide significantly better educational assistance and content safety.