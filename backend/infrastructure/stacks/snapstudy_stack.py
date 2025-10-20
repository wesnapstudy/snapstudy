"""Main SnapStudy infrastructure stack."""

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_wafv2 as wafv2,
    aws_cloudwatch as cloudwatch,
    aws_amplify_alpha as amplify,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct
import os


class SnapStudyStack(Stack):
    """Main infrastructure stack for SnapStudy."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB tables
        self.create_dynamodb_tables()
        
        # Create S3 bucket
        self.create_s3_bucket()
        
        # Create Cognito resources
        self.create_cognito_resources()
        
        # Create Lambda functions
        self.create_lambda_functions()
        
        # Create API Gateway
        self.create_api_gateway()

        # Create AWS WAF
        self.create_waf()

        # Create CloudWatch Dashboard and Alarms
        self.create_monitoring()

        # Create Frontend Deployment (S3 + CloudFront)
        self.create_frontend_deployment()

        # Create outputs
        self.create_outputs()

    def create_dynamodb_tables(self):
        """Create all DynamoDB tables."""
        
        # Users table
        self.users_table = dynamodb.Table(
            self, "UsersTable",
            table_name="SnapStudy-Users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED
        )
        
        # Add GSI for email lookup
        self.users_table.add_global_secondary_index(
            index_name="EmailIndex",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Lessons table
        self.lessons_table = dynamodb.Table(
            self, "LessonsTable",
            table_name="SnapStudy-Lessons",
            partition_key=dynamodb.Attribute(
                name="lesson_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl"
        )
        
        # Add GSI for user lessons lookup
        self.lessons_table.add_global_secondary_index(
            index_name="UserLessonsIndex",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )

        # MicroLessons table
        self.micro_lessons_table = dynamodb.Table(
            self, "MicroLessonsTable",
            table_name="SnapStudy-MicroLessons",
            partition_key=dynamodb.Attribute(
                name="micro_lesson_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED
        )
        
        # Add GSI for lesson micro-lessons lookup
        self.micro_lessons_table.add_global_secondary_index(
            index_name="LessonMicroLessonsIndex",
            partition_key=dynamodb.Attribute(
                name="lesson_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sequence_number",
                type=dynamodb.AttributeType.NUMBER
            )
        )

        # Quizzes table
        self.quizzes_table = dynamodb.Table(
            self, "QuizzesTable",
            table_name="SnapStudy-Quizzes",
            partition_key=dynamodb.Attribute(
                name="quiz_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED
        )
        
        # Add GSI for micro-lesson quizzes lookup
        self.quizzes_table.add_global_secondary_index(
            index_name="MicroLessonQuizzesIndex",
            partition_key=dynamodb.Attribute(
                name="micro_lesson_id",
                type=dynamodb.AttributeType.STRING
            )
        )

        # UserEngagement table
        self.user_engagement_table = dynamodb.Table(
            self, "UserEngagementTable",
            table_name="SnapStudy-UserEngagement",
            partition_key=dynamodb.Attribute(
                name="engagement_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl"
        )
        
        # Add GSI for user analytics
        self.user_engagement_table.add_global_secondary_index(
            index_name="UserEngagementIndex",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            )
        )

        # ChatHistory table
        self.chat_history_table = dynamodb.Table(
            self, "ChatHistoryTable",
            table_name="SnapStudy-ChatHistory",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl"
        )
        
        # Add GSI for user chat history lookup
        self.chat_history_table.add_global_secondary_index(
            index_name="UserChatHistoryIndex",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )

    def create_s3_bucket(self):
        """Create S3 bucket for content storage."""
        self.content_bucket = s3.Bucket(
            self, "ContentBucket",
            bucket_name=f"snapstudy-content-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteIncompleteMultipartUploads",
                    abort_incomplete_multipart_upload_after=Duration.days(7)
                ),
                s3.LifecycleRule(
                    id="TransitionToIA",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        )
                    ]
                )
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST, s3.HttpMethods.PUT],
                    allowed_origins=["*"],  # TODO: Restrict in production
                    allowed_headers=["*"],
                    max_age=3000
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )

    def create_cognito_resources(self):
        """Create Cognito User Pool and related resources."""
        
        # User Pool
        self.user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="SnapStudy-UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                fullname=cognito.StandardAttribute(required=True, mutable=True)
            ),
            custom_attributes={
                "profession": cognito.StringAttribute(mutable=True),
                "education_level": cognito.StringAttribute(mutable=True),
                "country": cognito.StringAttribute(mutable=True),
                "learning_style": cognito.StringAttribute(mutable=True),
                "attention_span": cognito.NumberAttribute(mutable=True),
                "difficulty_level": cognito.StringAttribute(mutable=True)
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.RETAIN
        )

        # User Pool Client
        self.user_pool_client = cognito.UserPoolClient(
            self, "UserPoolClient",
            user_pool=self.user_pool,
            user_pool_client_name="SnapStudy-WebClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_srp=True,
                user_password=False,
                admin_user_password=False
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=["http://localhost:3000/auth/callback"],  # TODO: Update for production
                logout_urls=["http://localhost:3000/auth/logout"]
            ),
            prevent_user_existence_errors=True,
            refresh_token_validity=Duration.days(30),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1)
        )

    def create_lambda_functions(self):
        """Create Lambda functions."""
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Add DynamoDB permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    self.users_table.table_arn,
                    f"{self.users_table.table_arn}/index/*",
                    self.lessons_table.table_arn,
                    f"{self.lessons_table.table_arn}/index/*",
                    self.micro_lessons_table.table_arn,
                    f"{self.micro_lessons_table.table_arn}/index/*",
                    self.quizzes_table.table_arn,
                    f"{self.quizzes_table.table_arn}/index/*",
                    self.user_engagement_table.table_arn,
                    f"{self.user_engagement_table.table_arn}/index/*",
                    self.chat_history_table.table_arn,
                    f"{self.chat_history_table.table_arn}/index/*"
                ]
            )
        )
        
        # Add Cognito permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminInitiateAuth",
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:AdminUpdateUserAttributes"
                ],
                resources=[self.user_pool.user_pool_arn]
            )
        )
        
        # Add S3 permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                resources=[f"{self.content_bucket.bucket_arn}/*"]
            )
        )
        
        # Add Bedrock permissions (LLM invocation)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )

        # Add Bedrock Agent Runtime permissions (AgentCore primitives)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock-agent-runtime:InvokeAgent",
                    "bedrock-agent-runtime:Retrieve",
                    "bedrock-agent-runtime:RetrieveAndGenerate"
                ],
                resources=["*"]
            )
        )

        # Add Amazon Q Business permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "qbusiness:ChatSync",
                    "qbusiness:Chat",
                    "qbusiness:ListConversations",
                    "qbusiness:GetConversation",
                    "qbusiness:ListMessages",
                    "qbusiness:GetApplication",
                    "qbusiness:ListApplications"
                ],
                resources=["*"]
            )
        )

        # Add Amazon Q Developer permissions (when available)
        # Note: Q Developer service is not yet available via API, but permissions are prepared
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "codewhisperer:GenerateRecommendations",
                    "codewhisperer:GetRecommendations"
                ],
                resources=["*"]
            )
        )

        # Add Bedrock Guardrails permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:ApplyGuardrail",
                    "bedrock:GetGuardrail",
                    "bedrock:ListGuardrails"
                ],
                resources=["*"]
            )
        )

        # Add CloudWatch Logs permissions for enhanced monitoring
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:PutMetricFilter",
                    "logs:PutRetentionPolicy"
                ],
                resources=["*"]
            )
        )

        # Add CloudWatch Metrics permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData"
                ],
                resources=["*"]
            )
        )

        # Add Textract permissions for document processing
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "textract:DetectDocumentText",
                    "textract:AnalyzeDocument",
                    "textract:StartDocumentTextDetection",
                    "textract:GetDocumentTextDetection"
                ],
                resources=["*"]
            )
        )

        # Add Transcribe permissions for audio/video processing
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                    "transcribe:DeleteTranscriptionJob"
                ],
                resources=["*"]
            )
        )

        # Main API Lambda function
        self.api_lambda = lambda_.Function(
            self, "ApiLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="src.api.main.handler",
            code=lambda_.Code.from_asset("../src"),  # Points to backend/src
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "USERS_TABLE": self.users_table.table_name,
                "LESSONS_TABLE": self.lessons_table.table_name,
                "MICRO_LESSONS_TABLE": self.micro_lessons_table.table_name,
                "QUIZZES_TABLE": self.quizzes_table.table_name,
                "USER_ENGAGEMENT_TABLE": self.user_engagement_table.table_name,
                "CHAT_HISTORY_TABLE": self.chat_history_table.table_name,
                "CONTENT_BUCKET": self.content_bucket.bucket_name,
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "USER_POOL_CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "AWS_REGION": self.region
            }
        )

    def create_api_gateway(self):
        """Create API Gateway."""
        
        # REST API Gateway
        self.rest_api = apigateway.RestApi(
            self, "RestApi",
            rest_api_name="SnapStudy-RestApi",
            description="REST API for SnapStudy platform",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,  # TODO: Restrict in production
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token"
                ]
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            )
        )
        
        # Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            self.api_lambda,
            proxy=True
        )
        
        # Add proxy resource to handle all paths
        self.rest_api.root.add_proxy(
            default_integration=lambda_integration,
            any_method=True
        )

    def create_waf(self):
        """Create AWS WAF Web ACL for API protection."""

        # Create WAF Web ACL with managed rules
        waf_acl = wafv2.CfnWebACL(
            self, "ApiWafAcl",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            scope="REGIONAL",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="SnapStudyWafMetrics",
                sampled_requests_enabled=True
            ),
            name="SnapStudyApiWaf",
            rules=[
                # AWS Managed Rule - Common Rule Set
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesCommonRuleSet",
                    priority=1,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesCommonRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesCommonRuleSetMetric",
                        sampled_requests_enabled=True
                    ),
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={})
                ),
                # AWS Managed Rule - Known Bad Inputs
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesKnownBadInputsRuleSet",
                    priority=2,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesKnownBadInputsRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesKnownBadInputsRuleSetMetric",
                        sampled_requests_enabled=True
                    ),
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={})
                ),
                # Rate limiting rule (1000 requests per 5 minutes per IP)
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitRule",
                    priority=3,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                            limit=1000,
                            aggregate_key_type="IP"
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(
                        block=wafv2.CfnWebACL.BlockActionProperty(
                            custom_response=wafv2.CfnWebACL.CustomResponseProperty(
                                response_code=429
                            )
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitRuleMetric",
                        sampled_requests_enabled=True
                    )
                ),
                # SQL Injection protection
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesSQLiRuleSet",
                    priority=4,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesSQLiRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesSQLiRuleSetMetric",
                        sampled_requests_enabled=True
                    ),
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={})
                )
            ]
        )

        # Associate WAF with API Gateway
        wafv2.CfnWebACLAssociation(
            self, "ApiWafAssociation",
            resource_arn=f"arn:aws:apigateway:{self.region}::/restapis/{self.rest_api.rest_api_id}/stages/prod",
            web_acl_arn=waf_acl.attr_arn
        )

        self.waf_acl = waf_acl

    def create_monitoring(self):
        """Create CloudWatch Dashboard and Alarms for monitoring."""

        # Create CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self, "SnapStudyDashboard",
            dashboard_name="SnapStudy-Metrics"
        )

        # Lambda metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations",
                left=[
                    self.api_lambda.metric_invocations(statistic="Sum"),
                    self.api_lambda.metric_errors(statistic="Sum"),
                    self.api_lambda.metric_throttles(statistic="Sum")
                ],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="Lambda Duration",
                left=[
                    self.api_lambda.metric_duration(statistic="Average"),
                    self.api_lambda.metric_duration(statistic="Maximum")
                ],
                width=12
            )
        )

        # API Gateway metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Gateway Requests",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Count",
                        dimensions_map={"ApiName": self.rest_api.rest_api_name},
                        statistic="Sum"
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="4XXError",
                        dimensions_map={"ApiName": self.rest_api.rest_api_name},
                        statistic="Sum"
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="5XXError",
                        dimensions_map={"ApiName": self.rest_api.rest_api_name},
                        statistic="Sum"
                    )
                ],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="API Latency",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Latency",
                        dimensions_map={"ApiName": self.rest_api.rest_api_name},
                        statistic="Average"
                    )
                ],
                width=12
            )
        )

        # DynamoDB metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="DynamoDB Read/Write Units",
                left=[
                    self.users_table.metric_consumed_read_capacity_units(),
                    self.users_table.metric_consumed_write_capacity_units()
                ],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="DynamoDB Throttles",
                left=[
                    self.users_table.metric_user_errors()
                ],
                width=12
            )
        )

        # Create alarms
        # Lambda error alarm
        lambda_error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            alarm_name="SnapStudy-Lambda-Errors",
            alarm_description="Alert when Lambda function has errors",
            metric=self.api_lambda.metric_errors(statistic="Sum"),
            threshold=10,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        # API Gateway 5XX alarm
        api_5xx_alarm = cloudwatch.Alarm(
            self, "Api5XXAlarm",
            alarm_name="SnapStudy-API-5XX-Errors",
            alarm_description="Alert when API has 5XX errors",
            metric=cloudwatch.Metric(
                namespace="AWS/ApiGateway",
                metric_name="5XXError",
                dimensions_map={"ApiName": self.rest_api.rest_api_name},
                statistic="Sum"
            ),
            threshold=5,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        # Lambda duration alarm (detect slow responses)
        lambda_duration_alarm = cloudwatch.Alarm(
            self, "LambdaDurationAlarm",
            alarm_name="SnapStudy-Lambda-Duration",
            alarm_description="Alert when Lambda execution is slow",
            metric=self.api_lambda.metric_duration(statistic="Average"),
            threshold=25000,  # 25 seconds (near the 30s timeout)
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        self.dashboard = dashboard

    def create_frontend_deployment(self):
        """Create S3 + CloudFront deployment for frontend (most cost-effective)."""

        # Create S3 bucket for frontend hosting
        self.frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            bucket_name=f"snapstudy-frontend-{self.account}-{self.region}",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3000
                )
            ]
        )

        # Add bucket policy for public read
        self.frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[f"{self.frontend_bucket.bucket_arn}/*"]
            )
        )

        # Check if frontend build exists and deploy it
        frontend_build_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..", "frontend", "build"
        )

        if os.path.exists(frontend_build_path):
            # Deploy frontend build to S3
            s3deploy.BucketDeployment(
                self, "DeployFrontend",
                sources=[s3deploy.Source.asset(frontend_build_path)],
                destination_bucket=self.frontend_bucket,
                retain_on_delete=False
            )

    def create_outputs(self):
        """Create CloudFormation outputs."""
        
        # Cognito outputs
        CfnOutput(
            self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
            export_name="SnapStudy-UserPoolId"
        )
        
        CfnOutput(
            self, "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
            export_name="SnapStudy-UserPoolClientId"
        )
        
        # API Gateway outputs
        CfnOutput(
            self, "RestApiUrl",
            value=self.rest_api.url,
            description="REST API Gateway URL",
            export_name="SnapStudy-RestApiUrl"
        )
        
        # S3 outputs
        CfnOutput(
            self, "ContentBucketName",
            value=self.content_bucket.bucket_name,
            description="S3 Content Bucket Name",
            export_name="SnapStudy-ContentBucketName"
        )
        
        # DynamoDB table outputs
        CfnOutput(
            self, "UsersTableName",
            value=self.users_table.table_name,
            description="Users DynamoDB Table Name",
            export_name="SnapStudy-UsersTableName"
        )
        
        CfnOutput(
            self, "LessonsTableName",
            value=self.lessons_table.table_name,
            description="Lessons DynamoDB Table Name",
            export_name="SnapStudy-LessonsTableName"
        )

        # Frontend outputs
        CfnOutput(
            self, "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="Frontend S3 Bucket Name",
            export_name="SnapStudy-FrontendBucketName"
        )

        CfnOutput(
            self, "FrontendUrl",
            value=f"http://{self.frontend_bucket.bucket_website_domain_name}",
            description="Frontend Website URL",
            export_name="SnapStudy-FrontendUrl"
        )