# SnapStudy Deployment Checklist

Use this checklist to ensure a smooth and safe deployment of the SnapStudy infrastructure.

## Pre-Deployment Checklist

### 🔧 Environment Setup
- [ ] Node.js 18+ installed
- [ ] AWS CLI installed and configured
- [ ] AWS CDK 2.87.0+ installed globally
- [ ] jq installed (for JSON processing)
- [ ] Git repository cloned and up to date

### 🔐 AWS Account Preparation
- [ ] AWS account has sufficient permissions
- [ ] AWS credentials configured (`aws configure` or environment variables)
- [ ] Target region supports all required services:
  - [ ] DynamoDB
  - [ ] S3
  - [ ] Cognito
  - [ ] API Gateway
  - [ ] Lambda
  - [ ] Bedrock (Claude models)
  - [ ] CloudWatch
  - [ ] IAM

### 📋 Service Limits Check
- [ ] DynamoDB table limit (default: 256 per region)
- [ ] S3 bucket limit (default: 100 per account)
- [ ] API Gateway limit (default: 600 per region)
- [ ] Lambda concurrent executions limit
- [ ] CloudWatch log groups limit

### 🔍 Pre-Deployment Validation
- [ ] Run pre-deployment check: `make pre-deploy`
- [ ] All tests pass: `make test`
- [ ] Code builds successfully: `make build`
- [ ] Configuration files are valid
- [ ] Environment-specific settings reviewed

## Deployment Process

### 🚀 Development Environment
- [ ] Set environment: `ENV=dev`
- [ ] Run: `make deploy-dev`
- [ ] Validate deployment: `make validate`
- [ ] Test basic functionality
- [ ] Check CloudWatch logs

### 🧪 Staging Environment
- [ ] Set environment: `ENV=staging`
- [ ] Set AWS profile if needed: `PROFILE=staging-profile`
- [ ] Run: `make deploy-staging`
- [ ] Validate deployment: `make validate`
- [ ] Run integration tests
- [ ] Performance testing
- [ ] Security testing

### 🏭 Production Environment
- [ ] **STOP**: Ensure all previous environments are working
- [ ] Set environment: `ENV=prod`
- [ ] Set AWS profile: `PROFILE=production-profile`
- [ ] Set alert email: `--alert-email admin@company.com`
- [ ] Review production configuration
- [ ] Notify team about deployment
- [ ] Run: `make deploy-prod`
- [ ] Monitor deployment progress
- [ ] Validate deployment: `make validate`
- [ ] Run smoke tests
- [ ] Monitor for 30 minutes post-deployment

## Post-Deployment Checklist

### ✅ Immediate Validation
- [ ] All stack resources created successfully
- [ ] CloudFormation stack status: `CREATE_COMPLETE` or `UPDATE_COMPLETE`
- [ ] No failed resources in stack events
- [ ] All outputs available and correct
- [ ] CloudWatch dashboards accessible
- [ ] SNS topic configured for alerts

### 🔍 Functional Testing
- [ ] DynamoDB tables accessible and properly configured
- [ ] S3 bucket accessible with correct permissions
- [ ] Cognito User Pool and Identity Pool working
- [ ] API Gateway endpoints responding
- [ ] WebSocket API functional
- [ ] IAM roles have correct permissions
- [ ] CloudWatch logging working

### 📊 Monitoring Setup
- [ ] CloudWatch alarms configured and active
- [ ] SNS notifications working
- [ ] Dashboard showing metrics
- [ ] Log groups receiving data
- [ ] Metric filters working

### 🔒 Security Validation
- [ ] All data encrypted at rest
- [ ] HTTPS/TLS for all communications
- [ ] CORS configured correctly
- [ ] S3 bucket public access blocked
- [ ] IAM roles follow least privilege
- [ ] No hardcoded secrets in code

### 📝 Documentation Update
- [ ] Record deployment details
- [ ] Update configuration documentation
- [ ] Note any issues encountered
- [ ] Update runbooks if needed

## Environment-Specific Checklists

### Development Environment
- [ ] CORS allows localhost origins
- [ ] Reduced throttling limits for testing
- [ ] Shorter log retention (7 days)
- [ ] Test data can be safely deleted

### Staging Environment
- [ ] Production-like configuration
- [ ] HTTPS URLs only
- [ ] Realistic throttling limits
- [ ] Longer log retention (14 days)
- [ ] Load testing completed

### Production Environment
- [ ] **CRITICAL**: No wildcard CORS origins
- [ ] **CRITICAL**: HTTPS URLs only
- [ ] **CRITICAL**: Alert email configured
- [ ] **CRITICAL**: Backup strategy in place
- [ ] High throttling limits configured
- [ ] Long log retention (90 days)
- [ ] Monitoring and alerting active
- [ ] Incident response plan ready

## Rollback Checklist

### When to Rollback
- [ ] Critical functionality broken
- [ ] Security vulnerability introduced
- [ ] Performance significantly degraded
- [ ] Data corruption detected
- [ ] Monitoring shows system instability

### Rollback Process
- [ ] Identify the issue requiring rollback
- [ ] Notify team about rollback decision
- [ ] Run: `make rollback ENV=<environment>`
- [ ] Monitor rollback progress
- [ ] Validate system functionality post-rollback
- [ ] Document rollback reason and process
- [ ] Plan fix for the original issue

## Troubleshooting Common Issues

### Deployment Failures
- [ ] Check CloudFormation events for error details
- [ ] Verify AWS service limits not exceeded
- [ ] Ensure IAM permissions are sufficient
- [ ] Check for resource naming conflicts
- [ ] Validate configuration syntax

### Permission Issues
- [ ] Verify AWS credentials are current
- [ ] Check IAM user/role permissions
- [ ] Ensure MFA requirements are met
- [ ] Validate cross-account access if applicable

### Service Availability
- [ ] Check AWS service health dashboard
- [ ] Verify services available in target region
- [ ] Confirm Bedrock model access enabled
- [ ] Check for regional service outages

### Configuration Issues
- [ ] Validate JSON syntax in config files
- [ ] Check environment variable values
- [ ] Verify URL formats and protocols
- [ ] Ensure required fields are present

## Emergency Procedures

### Critical Production Issue
1. [ ] **IMMEDIATE**: Assess impact and severity
2. [ ] **IMMEDIATE**: Notify incident response team
3. [ ] **IMMEDIATE**: Consider rollback if safe
4. [ ] Document all actions taken
5. [ ] Implement temporary workarounds if possible
6. [ ] Schedule post-incident review

### Data Loss Risk
1. [ ] **STOP**: Do not proceed with destructive actions
2. [ ] **IMMEDIATE**: Enable point-in-time recovery if not already
3. [ ] **IMMEDIATE**: Create manual backups if possible
4. [ ] Consult with data team before proceeding
5. [ ] Document all recovery actions

### Security Incident
1. [ ] **IMMEDIATE**: Isolate affected resources
2. [ ] **IMMEDIATE**: Notify security team
3. [ ] **IMMEDIATE**: Review access logs
4. [ ] Change all relevant credentials
5. [ ] Implement additional security measures
6. [ ] Document incident for compliance

## Sign-off

### Development Deployment
- [ ] Developer: _________________ Date: _________
- [ ] Code Review: ______________ Date: _________

### Staging Deployment
- [ ] Developer: _________________ Date: _________
- [ ] QA Lead: __________________ Date: _________
- [ ] DevOps: ___________________ Date: _________

### Production Deployment
- [ ] Developer: _________________ Date: _________
- [ ] QA Lead: __________________ Date: _________
- [ ] DevOps: ___________________ Date: _________
- [ ] Tech Lead: ________________ Date: _________
- [ ] Product Owner: ____________ Date: _________

## Notes

Use this section to record any deployment-specific notes, issues encountered, or deviations from the standard process:

```
Date: ___________
Environment: ___________
Deployed by: ___________

Notes:
_________________________________
_________________________________
_________________________________
```

---

**Remember**: When in doubt, don't deploy to production. It's better to delay and ensure safety than to rush and cause issues.