# 🚀 Quick Deployment Guide

## For Windows Users

### **Option 1: Using PowerShell (Recommended)**

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)"

2. **Navigate to Project Directory**
   ```powershell
   cd D:\repo\hackathon\study
   ```

3. **Run Deployment Script**
   ```powershell
   .\deploy.ps1
   ```

4. **Follow the Prompts**
   - Enter your AWS Access Key ID
   - Enter your AWS Secret Access Key
   - Select region (press Enter for us-east-1)
   - Confirm Bedrock access
   - Confirm deployment
   - Optionally create test user
   - Optionally setup frontend

### **Option 2: Using Command Prompt**

1. **Open Command Prompt as Administrator**
   - Press `Win + R`
   - Type `cmd`
   - Press `Ctrl + Shift + Enter`

2. **Navigate to Project Directory**
   ```cmd
   cd D:\repo\hackathon\study
   ```

3. **Run Deployment Script**
   ```cmd
   deploy.bat
   ```

---

## For macOS/Linux Users

1. **Open Terminal**

2. **Navigate to Project Directory**
   ```bash
   cd /path/to/snapstudy
   ```

3. **Make Script Executable**
   ```bash
   chmod +x deploy.sh
   ```

4. **Run Deployment Script**
   ```bash
   ./deploy.sh
   ```

5. **Follow the Prompts**
   - Enter your AWS Access Key ID
   - Enter your AWS Secret Access Key
   - Select region (press Enter for us-east-1)
   - Confirm Bedrock access
   - Confirm deployment
   - Optionally create test user
   - Optionally setup frontend

---

## 📋 What You'll Need Before Running

### **1. AWS Account**
- Sign up at https://aws.amazon.com if you don't have one

### **2. AWS Access Keys**

**How to Get Access Keys:**

1. Go to AWS Console: https://console.aws.amazon.com
2. Click your username (top right) → Security credentials
3. Scroll to "Access keys"
4. Click "Create access key"
5. Select "Command Line Interface (CLI)"
6. Check the confirmation box
7. Click "Create access key"
8. **SAVE BOTH:**
   - Access key ID (looks like: `AKIAIOSFODNN7EXAMPLE`)
   - Secret access key (looks like: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)

⚠️ **Important:** The secret key is only shown once! Save it immediately.

### **3. Amazon Bedrock Access**

**After running the script**, when prompted about Bedrock access:

1. Open https://console.aws.amazon.com/bedrock
2. Select region: **us-east-1** (top right)
3. Click "Model access" (left sidebar)
4. Click "Request model access" (orange button)
5. Find **Anthropic Claude 3.5 Sonnet**
6. Click "Request model access"
7. Wait for "Access granted" (usually instant)

---

## ⏱️ Deployment Timeline

| Step | Time | What's Happening |
|------|------|------------------|
| **Prerequisites Check** | 30 sec | Verifying Python, Node.js, AWS CLI installed |
| **AWS Configuration** | 1 min | Setting up credentials |
| **Bedrock Check** | 1 min | Verifying model access |
| **Backend Setup** | 2 min | Installing Python dependencies |
| **CDK Bootstrap** | 2 min | First-time AWS CDK setup (only once) |
| **Infrastructure Deploy** | 5-8 min | Creating Lambda, DynamoDB, S3, API Gateway, etc. |
| **Testing** | 30 sec | Verifying deployment |
| **Frontend Setup** | 2 min | Installing and building React app (optional) |
| **Total** | **15-20 min** | Complete deployment |

---

## 📊 What Gets Deployed

### **AWS Resources Created:**

| Service | Resource | Purpose |
|---------|----------|---------|
| **Lambda** | SnapStudyStack-ApiLambda | Backend API logic |
| **API Gateway** | SnapStudy-RestApi | REST API endpoint |
| **DynamoDB** | 6 tables | User data, lessons, quizzes, analytics |
| **S3** | snapstudy-content-* | PDF/video storage |
| **Cognito** | SnapStudy-UserPool | User authentication |
| **CloudWatch** | SnapStudy-Metrics | Monitoring dashboard |
| **WAF** | SnapStudyApiWaf | Security firewall |

### **Estimated Monthly Cost:**

| Usage Level | Cost |
|-------------|------|
| **Development** (testing) | $0-5 |
| **Light Production** (100 users) | $20-30 |
| **Medium Production** (1000 users) | $50-100 |

💡 Most services have free tier!

---

## ✅ After Deployment

### **You'll Receive:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
User Pool ID: us-east-1_ABC123XYZ
User Pool Client ID: 1a2b3c4d5e6f7g8h9i0j1k2l3m
Content Bucket: snapstudy-content-123456789012-us-east-1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Save these values!** You'll need them for frontend configuration.

### **Test Your Deployment:**

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "https://YOUR-API-URL/health"
```

**Command Prompt (with curl):**
```cmd
curl https://YOUR-API-URL/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T14:30:00Z"
}
```

---

## 🎨 Running the Frontend

### **Option 1: Local Development**

```bash
cd frontend
npm start
```

Opens http://localhost:3000 in your browser.

### **Option 2: Deploy to Vercel (Free)**

```bash
cd frontend
npm install -g vercel
vercel
```

Follow prompts, then get a public URL like: `https://snapstudy.vercel.app`

---

## 🔍 Troubleshooting

### **Problem: "AWS credentials not configured"**

**Solution:**
```bash
aws configure
```
Enter your Access Key ID and Secret Access Key.

---

### **Problem: "Bedrock model access denied"**

**Solution:**
1. Go to AWS Console → Bedrock
2. Select **us-east-1** region (top right)
3. Model access → Request access
4. Enable **Claude 3.5 Sonnet**

---

### **Problem: "CDK bootstrap failed"**

**Solution:**
```bash
cd backend/infrastructure
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

Replace `YOUR-ACCOUNT-ID` with your 12-digit AWS account ID.

---

### **Problem: "npm not found" or "python not found"**

**Solution:**

**Install Python:**
- Windows: https://www.python.org/downloads/
- macOS: `brew install python3`
- Linux: `sudo apt-get install python3`

**Install Node.js:**
- Windows/macOS/Linux: https://nodejs.org/

Then restart your terminal and try again.

---

### **Problem: Deployment stuck or slow**

**This is normal!** CDK deployment takes 5-8 minutes because it's creating:
- 6 DynamoDB tables
- Lambda function
- API Gateway
- S3 bucket
- Cognito user pool
- CloudWatch dashboard
- WAF rules

Be patient and wait for "✅ Deployment completed successfully!"

---

## 🧹 Cleanup (Delete Everything)

**To delete all AWS resources:**

### **Windows PowerShell:**
```powershell
cd D:\repo\hackathon\study\backend\infrastructure
cdk destroy
```

### **macOS/Linux:**
```bash
cd backend/infrastructure
cdk destroy
```

Type `y` to confirm deletion.

⚠️ **Warning:** This deletes all data permanently!

---

## 🆘 Need Help?

### **Check Logs:**

**PowerShell:**
```powershell
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow --region us-east-1
```

**Bash:**
```bash
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow --region us-east-1
```

### **Common Commands:**

| Task | Command |
|------|---------|
| **Check AWS credentials** | `aws sts get-caller-identity` |
| **List CloudFormation stacks** | `aws cloudformation list-stacks` |
| **View API Gateway endpoints** | `aws apigateway get-rest-apis` |
| **List DynamoDB tables** | `aws dynamodb list-tables` |

---

## 📞 Support

**Before asking for help:**

1. ✅ Check `DEPLOYMENT_SUMMARY.txt` (created after deployment)
2. ✅ Read error messages carefully
3. ✅ Check CloudWatch logs
4. ✅ Verify AWS credentials: `aws sts get-caller-identity`
5. ✅ Verify Bedrock access in AWS Console

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] API health check returns `{"status":"healthy"}`
- [ ] CloudWatch dashboard visible in AWS Console
- [ ] DynamoDB tables created (6 tables)
- [ ] S3 bucket created
- [ ] Cognito user pool created
- [ ] Test user login works (if created)
- [ ] Frontend connects to API (if deployed)

---

**You're ready to deploy! Run the script and follow the prompts.** 🚀
