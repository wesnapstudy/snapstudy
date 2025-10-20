# 🎯 Deploy SnapStudy NOW - Step-by-Step Guide

## Your Current Location: `D:\repo\hackathon\study`

Follow these exact steps to deploy SnapStudy to AWS in the next 20 minutes.

---

## 🚦 STEP-BY-STEP INSTRUCTIONS

### **STEP 1: Open PowerShell** ⏱️ 10 seconds

1. Press `Win + X` on your keyboard
2. Click **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**
3. If prompted, click **"Yes"** to allow

---

### **STEP 2: Navigate to Your Project** ⏱️ 5 seconds

Copy and paste this command:

```powershell
cd D:\repo\hackathon\study
```

Press `Enter`

---

### **STEP 3: Run the Deployment Script** ⏱️ 2 seconds

Copy and paste this command:

```powershell
.\deploy.ps1
```

Press `Enter`

**You'll see:**
```
╔═══════════════════════════════════════════════════════════════╗
║              SnapStudy AWS Deployment Script                  ║
╚═══════════════════════════════════════════════════════════════╝

[INFO] Checking Prerequisites...
```

---

### **STEP 4: Enter AWS Credentials** ⏱️ 2 minutes

The script will prompt you for AWS credentials.

#### **If you DON'T have AWS Access Keys yet:**

**4a. Open a new browser tab:** https://console.aws.amazon.com

**4b. Login to AWS Console**

**4c. Click your username (top right corner)**

**4d. Click "Security credentials"**

**4e. Scroll down to "Access keys" section**

**4f. Click "Create access key"**

**4g. Select "Command Line Interface (CLI)"**

**4h. Check the box "I understand..."**

**4i. Click "Create access key"**

**4j. IMPORTANT:** You'll see two values:
- **Access key ID**: Starts with `AKIA...`
- **Secret access key**: Long random string

**4k. Click "Download .csv file"** (backup)

**4l. COPY both values** (you'll paste them next)

---

#### **Back in PowerShell:**

**When prompted:**
```
AWS Access Key ID:
```
**Paste your Access Key ID** (right-click to paste in PowerShell)
Press `Enter`

**When prompted:**
```
AWS Secret Access Key:
```
**Paste your Secret Access Key**
Press `Enter`

**When prompted:**
```
AWS Region [us-east-1]:
```
**Just press `Enter`** (use default us-east-1)

**You'll see:**
```
[SUCCESS] AWS credentials configured successfully
[SUCCESS] AWS Account ID: 123456789012
[SUCCESS] AWS Region: us-east-1
```

---

### **STEP 5: Enable Bedrock Model Access** ⏱️ 2 minutes

**The script will check if you have Bedrock access.**

**If you DON'T have access yet, you'll see:**
```
[ERROR] Claude 3.5 Sonnet model access not found
[WARNING] You need to request model access in AWS Console:
1. Go to AWS Console → Amazon Bedrock
2. Select region: us-east-1
...
Press Enter after you've enabled model access...
```

**DO THIS:**

**5a. Open new browser tab:** https://console.aws.amazon.com/bedrock

**5b. IMPORTANT:** Check top-right corner - must be **"US East (N. Virginia)"**
   - If not, click region dropdown and select **"US East (N. Virginia)"**

**5c. Click "Model access"** in the left sidebar

**5d. Click orange button "Request model access"**

**5e. Scroll down to find:**
   ```
   Anthropic
     └─ Claude 3.5 Sonnet
   ```

**5f. Check the box next to "Claude 3.5 Sonnet"**

**5g. Scroll to bottom, click "Request model access"**

**5h. Wait 5-10 seconds**

**5i. Refresh the page**

**5j. You should see "Access granted" in green next to Claude 3.5 Sonnet**

---

#### **Back in PowerShell:**

Press `Enter`

**You'll see:**
```
[SUCCESS] Model access confirmed!
```

---

### **STEP 6: Let the Script Run** ⏱️ 10-15 minutes

**The script will now automatically:**

✅ Install Python dependencies (2 min)
✅ Bootstrap AWS CDK (2 min) - first time only
✅ Install CDK dependencies (1 min)
✅ Generate CloudFormation template (30 sec)
✅ **Deploy infrastructure to AWS** (5-8 min) ⬅️ **This is the longest step**

**You'll see progress like:**
```
[INFO] Installing Python dependencies...
[SUCCESS] Python dependencies installed

[INFO] Bootstrapping CDK...
[SUCCESS] CDK bootstrap completed

[INFO] Starting deployment...
SnapStudyStack: deploying...
[████████████████████░░░░] (80%)
```

**☕ Take a coffee break!** The deployment takes 5-8 minutes.

**When deployment is DONE, you'll see:**
```
[SUCCESS] Infrastructure deployed successfully!
```

---

### **STEP 7: Save Deployment Outputs** ⏱️ 10 seconds

**The script automatically saves outputs and shows:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deployment Outputs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
User Pool ID: us-east-1_ABC123XYZ
User Pool Client ID: 1a2b3c4d5e6f7g8h9i0j1k2l3m
Content Bucket: snapstudy-content-123456789012-us-east-1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**📝 COPY THESE VALUES** - You'll need them!

Also saved automatically to: `D:\repo\hackathon\study\deployment-outputs.json`

---

### **STEP 8: Test Deployment** ⏱️ 30 seconds

**The script will test automatically and show:**

```
[INFO] Testing API health endpoint...
[SUCCESS] API is healthy!
Response: {"status":"healthy","timestamp":"2025-10-20T14:30:00Z"}
```

**✅ If you see this, your deployment is successful!**

---

### **STEP 9: Create Test User** ⏱️ 1 minute

**The script will ask:**
```
Do you want to create a test user? (y/n):
```

**Type:** `y` and press `Enter`

**When prompted:**
```
Test user email [test@example.com]:
```
**Just press `Enter`** (use default)

**When prompted:**
```
Test user password [TestPassword123!]:
```
**Just press `Enter`** (use default)

**You'll see:**
```
[SUCCESS] Test user created successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test User Credentials:
Email: test@example.com
Password: TestPassword123!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**📝 Save these credentials!**

---

### **STEP 10: Frontend Setup** ⏱️ 3 minutes

**The script will ask:**
```
Do you want to set up the frontend? (y/n):
```

**Type:** `y` and press `Enter`

**The script will:**
- Install React dependencies (1 min)
- Create configuration file
- Build frontend (2 min)

**You'll see:**
```
[INFO] Installing frontend dependencies...
[SUCCESS] Frontend dependencies installed

[INFO] Building frontend...
[SUCCESS] Frontend build completed
[INFO] Build files located in: frontend\build\
```

---

### **STEP 11: Deployment Complete!** 🎉

**You'll see the final summary:**

```
🎉 DEPLOYMENT COMPLETE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    SnapStudy Deployment Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Backend Infrastructure:
   API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
   Region: us-east-1
   Account: 123456789012

✅ Cognito Authentication:
   User Pool ID: us-east-1_ABC123XYZ
   Client ID: 1a2b3c4d5e6f7g8h9i0j1k2l3m

✅ Storage:
   S3 Bucket: snapstudy-content-123456789012-us-east-1

📝 Next Steps:
   1. Test the API: curl https://YOUR-API-URL/health
   2. View CloudWatch Dashboard: AWS Console → CloudWatch → Dashboards
   3. Check WAF Rules: AWS Console → WAF & Shield
   4. Deploy frontend: cd frontend && npm start

[SUCCESS] Deployment script completed successfully! 🎉
```

**Summary also saved to:** `DEPLOYMENT_SUMMARY.txt`

---

## 🎯 VERIFY YOUR DEPLOYMENT

### **Test 1: API Health Check**

**In PowerShell, run:**
```powershell
Invoke-RestMethod -Uri "https://YOUR-API-URL/health"
```
(Replace YOUR-API-URL with actual URL from outputs)

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T14:30:00Z"
}
```

---

### **Test 2: View CloudWatch Dashboard**

1. Go to: https://console.aws.amazon.com/cloudwatch
2. Select region: **US East (N. Virginia)**
3. Click **"Dashboards"** in left sidebar
4. Click **"SnapStudy-Metrics"**
5. You should see graphs for Lambda, API Gateway, DynamoDB

---

### **Test 3: Check AWS WAF**

1. Go to: https://console.aws.amazon.com/wafv2
2. Select region: **US East (N. Virginia)**
3. Click **"Web ACLs"** in left sidebar
4. You should see **"SnapStudyApiWaf"**

---

### **Test 4: Run Frontend**

**In a NEW PowerShell window:**

```powershell
cd D:\repo\hackathon\study\frontend
npm start
```

**Your browser will automatically open:** http://localhost:3000

**You should see the SnapStudy login page!**

**Login with:**
- Email: `test@example.com`
- Password: `TestPassword123!`

---

## ✅ SUCCESS CHECKLIST

Mark each item as you verify:

- [ ] PowerShell script completed without errors
- [ ] Received deployment outputs (API URL, User Pool ID, etc.)
- [ ] `deployment-outputs.json` file created
- [ ] `DEPLOYMENT_SUMMARY.txt` file created
- [ ] API health check returns `{"status":"healthy"}`
- [ ] CloudWatch dashboard visible in AWS Console
- [ ] AWS WAF web ACL created
- [ ] Frontend runs on http://localhost:3000
- [ ] Can login with test user credentials

---

## 🚨 TROUBLESHOOTING

### **Script Stops with Error**

**Read the error message!** It will tell you what's wrong.

**Common errors:**

1. **"Python not found"**
   - Install Python: https://www.python.org/downloads/
   - Restart PowerShell

2. **"AWS credentials invalid"**
   - Check Access Key ID and Secret Key
   - Run: `aws sts get-caller-identity`

3. **"Bedrock access denied"**
   - Follow Step 5 again
   - Make sure region is **us-east-1**

4. **"CDK bootstrap failed"**
   - Open AWS Console
   - Check if you have IAM permissions
   - You need AdministratorAccess or PowerUser role

---

### **Deployment Takes Too Long**

**Is it stuck at:**
```
SnapStudyStack: deploying...
```

**This is NORMAL!** Wait 5-8 minutes.

CloudFormation is creating:
- 6 DynamoDB tables ✅
- Lambda function ✅
- API Gateway ✅
- Cognito User Pool ✅
- CloudWatch Dashboard ✅
- AWS WAF ✅

**Be patient!**

---

### **Still Having Issues?**

**Check logs:**

```powershell
aws logs tail /aws/lambda/SnapStudyStack-ApiLambda --follow --region us-east-1
```

**View CloudFormation events:**

```powershell
aws cloudformation describe-stack-events --stack-name SnapStudyStack --region us-east-1
```

---

## 📞 READY TO DEPLOY?

**Open PowerShell NOW and run:**

```powershell
cd D:\repo\hackathon\study
.\deploy.ps1
```

**Good luck! You've got this! 🚀**

---

## ⏱️ QUICK REFERENCE

| Step | Time | Command |
|------|------|---------|
| Open PowerShell | 10 sec | Win+X → PowerShell (Admin) |
| Navigate | 5 sec | `cd D:\repo\hackathon\study` |
| Deploy | 15 min | `.\deploy.ps1` |
| Test | 30 sec | `Invoke-RestMethod -Uri "API-URL/health"` |
| Run Frontend | 1 min | `cd frontend && npm start` |

**Total Time: ~20 minutes**

---

**NOW GO DEPLOY! The script will guide you through everything! 🎉**
