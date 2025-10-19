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
)
from constructs import Construct


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
        
        # Add Bedrock permissions
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