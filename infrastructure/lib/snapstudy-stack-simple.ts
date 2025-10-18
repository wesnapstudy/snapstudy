import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class SnapStudyStack extends cdk.Stack {
  public usersTable: dynamodb.Table;
  public lessonsTable: dynamodb.Table;
  public microLessonsTable: dynamodb.Table;
  public quizzesTable: dynamodb.Table;
  public userEngagementTable: dynamodb.Table;
  public chatHistoryTable: dynamodb.Table;
  public contentBucket: s3.Bucket;
  public userPool: cognito.UserPool;
  public userPoolClient: cognito.UserPoolClient;
  public restApi: apigateway.RestApi;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create DynamoDB Tables
    this.createDynamoDBTables();
    
    // Create S3 Bucket for content storage
    this.createS3Bucket();
    
    // Create Cognito User Pool and Identity Pool
    this.createCognitoResources();
    
    // Create API Gateway
    this.createApiGateway();
    
    // Create IAM roles
    this.createIAMRoles();
    
    // Create CloudWatch Log Groups
    this.createCloudWatchResources();
    
    // Output important values
    this.createOutputs();
  }

  private createDynamoDBTables() {
    // Users Table
    this.usersTable = new dynamodb.Table(this, 'UsersTable', {
      tableName: 'SnapStudy-Users',
      partitionKey: {
        name: 'user_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED
    });

    // Add GSI for email lookup
    this.usersTable.addGlobalSecondaryIndex({
      indexName: 'EmailIndex',
      partitionKey: {
        name: 'email',
        type: dynamodb.AttributeType.STRING
      }
    });

    // Lessons Table
    this.lessonsTable = new dynamodb.Table(this, 'LessonsTable', {
      tableName: 'SnapStudy-Lessons',
      partitionKey: {
        name: 'lesson_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      timeToLiveAttribute: 'ttl'
    });

    // Add GSI for user lessons lookup
    this.lessonsTable.addGlobalSecondaryIndex({
      indexName: 'UserLessonsIndex',
      partitionKey: {
        name: 'user_id',
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'created_at',
        type: dynamodb.AttributeType.STRING
      }
    });

    // MicroLessons Table
    this.microLessonsTable = new dynamodb.Table(this, 'MicroLessonsTable', {
      tableName: 'SnapStudy-MicroLessons',
      partitionKey: {
        name: 'micro_lesson_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED
    });

    // Add GSI for lesson micro-lessons lookup
    this.microLessonsTable.addGlobalSecondaryIndex({
      indexName: 'LessonMicroLessonsIndex',
      partitionKey: {
        name: 'lesson_id',
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'sequence_number',
        type: dynamodb.AttributeType.NUMBER
      }
    });

    // Quizzes Table
    this.quizzesTable = new dynamodb.Table(this, 'QuizzesTable', {
      tableName: 'SnapStudy-Quizzes',
      partitionKey: {
        name: 'quiz_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED
    });

    // Add GSI for micro-lesson quizzes lookup
    this.quizzesTable.addGlobalSecondaryIndex({
      indexName: 'MicroLessonQuizzesIndex',
      partitionKey: {
        name: 'micro_lesson_id',
        type: dynamodb.AttributeType.STRING
      }
    });

    // UserEngagement Table
    this.userEngagementTable = new dynamodb.Table(this, 'UserEngagementTable', {
      tableName: 'SnapStudy-UserEngagement',
      partitionKey: {
        name: 'engagement_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      timeToLiveAttribute: 'ttl'
    });

    // Add GSI for user analytics
    this.userEngagementTable.addGlobalSecondaryIndex({
      indexName: 'UserEngagementIndex',
      partitionKey: {
        name: 'user_id',
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'timestamp',
        type: dynamodb.AttributeType.STRING
      }
    });

    // ChatHistory Table
    this.chatHistoryTable = new dynamodb.Table(this, 'ChatHistoryTable', {
      tableName: 'SnapStudy-ChatHistory',
      partitionKey: {
        name: 'session_id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      timeToLiveAttribute: 'ttl'
    });

    // Add GSI for user chat history lookup
    this.chatHistoryTable.addGlobalSecondaryIndex({
      indexName: 'UserChatHistoryIndex',
      partitionKey: {
        name: 'user_id',
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'created_at',
        type: dynamodb.AttributeType.STRING
      }
    });
  }

  private createS3Bucket() {
    this.contentBucket = new s3.Bucket(this, 'ContentBucket', {
      bucketName: `snapstudy-content-${this.account}-${this.region}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      lifecycleRules: [
        {
          id: 'DeleteIncompleteMultipartUploads',
          abortIncompleteMultipartUploadAfter: cdk.Duration.days(7)
        },
        {
          id: 'TransitionToIA',
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30)
            }
          ]
        }
      ],
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.POST, s3.HttpMethods.PUT],
          allowedOrigins: ['*'], // TODO: Restrict to actual domain in production
          allowedHeaders: ['*'],
          maxAge: 3000
        }
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });
  }

  private createCognitoResources() {
    // User Pool
    this.userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: 'SnapStudy-UserPool',
      selfSignUpEnabled: true,
      signInAliases: {
        email: true
      },
      autoVerify: {
        email: true
      },
      standardAttributes: {
        email: {
          required: true,
          mutable: true
        },
        fullname: {
          required: true,
          mutable: true
        }
      },
      customAttributes: {
        profession: new cognito.StringAttribute({ mutable: true }),
        education_level: new cognito.StringAttribute({ mutable: true }),
        country: new cognito.StringAttribute({ mutable: true }),
        learning_style: new cognito.StringAttribute({ mutable: true }),
        attention_span: new cognito.NumberAttribute({ mutable: true }),
        difficulty_level: new cognito.StringAttribute({ mutable: true })
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // User Pool Client
    this.userPoolClient = new cognito.UserPoolClient(this, 'UserPoolClient', {
      userPool: this.userPool,
      userPoolClientName: 'SnapStudy-WebClient',
      generateSecret: false,
      authFlows: {
        userSrp: true,
        userPassword: false,
        adminUserPassword: false
      },
      oAuth: {
        flows: {
          authorizationCodeGrant: true
        },
        scopes: [
          cognito.OAuthScope.EMAIL,
          cognito.OAuthScope.OPENID,
          cognito.OAuthScope.PROFILE
        ],
        callbackUrls: ['http://localhost:3000/auth/callback'], // TODO: Update for production
        logoutUrls: ['http://localhost:3000/auth/logout']
      },
      preventUserExistenceErrors: true,
      refreshTokenValidity: cdk.Duration.days(30),
      accessTokenValidity: cdk.Duration.hours(1),
      idTokenValidity: cdk.Duration.hours(1)
    });
  }

  private createApiGateway() {
    // REST API Gateway
    this.restApi = new apigateway.RestApi(this, 'RestApi', {
      restApiName: 'SnapStudy-RestApi',
      description: 'REST API for SnapStudy platform',
      endpointConfiguration: {
        types: [apigateway.EndpointType.REGIONAL]
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS, // TODO: Restrict in production
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token'
        ]
      },
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true
      }
    });
  }

  private createIAMRoles() {
    // Lambda execution role for authentication functions
    new iam.Role(this, 'AuthLambdaRole', {
      roleName: 'SnapStudy-AuthLambdaRole',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      inlinePolicies: {
        CognitoAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'cognito-idp:AdminCreateUser',
                'cognito-idp:AdminSetUserPassword',
                'cognito-idp:AdminInitiateAuth',
                'cognito-idp:AdminGetUser',
                'cognito-idp:AdminUpdateUserAttributes'
              ],
              resources: [this.userPool.userPoolArn]
            })
          ]
        }),
        DynamoDBAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'dynamodb:GetItem',
                'dynamodb:PutItem',
                'dynamodb:UpdateItem',
                'dynamodb:Query',
                'dynamodb:Scan'
              ],
              resources: [
                this.usersTable.tableArn,
                `${this.usersTable.tableArn}/index/*`
              ]
            })
          ]
        })
      }
    });
  }

  private createCloudWatchResources() {
    // Create log groups for different services
    new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: '/aws/apigateway/SnapStudy-RestApi',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    new logs.LogGroup(this, 'LambdaLogGroup', {
      logGroupName: '/aws/lambda/SnapStudy',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }

  private createOutputs() {
    // Cognito outputs
    new cdk.CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
      description: 'Cognito User Pool ID',
      exportName: 'SnapStudy-UserPoolId'
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: this.userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
      exportName: 'SnapStudy-UserPoolClientId'
    });

    // API Gateway outputs
    new cdk.CfnOutput(this, 'RestApiUrl', {
      value: this.restApi.url,
      description: 'REST API Gateway URL',
      exportName: 'SnapStudy-RestApiUrl'
    });

    // S3 outputs
    new cdk.CfnOutput(this, 'ContentBucketName', {
      value: this.contentBucket.bucketName,
      description: 'S3 Content Bucket Name',
      exportName: 'SnapStudy-ContentBucketName'
    });

    // DynamoDB table outputs
    new cdk.CfnOutput(this, 'UsersTableName', {
      value: this.usersTable.tableName,
      description: 'Users DynamoDB Table Name',
      exportName: 'SnapStudy-UsersTableName'
    });

    new cdk.CfnOutput(this, 'LessonsTableName', {
      value: this.lessonsTable.tableName,
      description: 'Lessons DynamoDB Table Name',
      exportName: 'SnapStudy-LessonsTableName'
    });

    new cdk.CfnOutput(this, 'MicroLessonsTableName', {
      value: this.microLessonsTable.tableName,
      description: 'MicroLessons DynamoDB Table Name',
      exportName: 'SnapStudy-MicroLessonsTableName'
    });

    new cdk.CfnOutput(this, 'QuizzesTableName', {
      value: this.quizzesTable.tableName,
      description: 'Quizzes DynamoDB Table Name',
      exportName: 'SnapStudy-QuizzesTableName'
    });

    new cdk.CfnOutput(this, 'UserEngagementTableName', {
      value: this.userEngagementTable.tableName,
      description: 'UserEngagement DynamoDB Table Name',
      exportName: 'SnapStudy-UserEngagementTableName'
    });

    new cdk.CfnOutput(this, 'ChatHistoryTableName', {
      value: this.chatHistoryTable.tableName,
      description: 'ChatHistory DynamoDB Table Name',
      exportName: 'SnapStudy-ChatHistoryTableName'
    });
  }
}