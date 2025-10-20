#!/usr/bin/env python3
"""
SnapStudy AWS Architecture Diagram Generator
Run this script to generate a professional AWS architecture diagram.

Prerequisites:
pip install diagrams

Usage:
python create_architecture_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.database import DynamodbTable
from diagrams.aws.storage import S3
from diagrams.aws.security import Cognito, WAF
from diagrams.aws.ml import Bedrock, Textract, Transcribe
from diagrams.aws.management import Cloudwatch
from diagrams.aws.analytics import Quicksight
from diagrams.onprem.client import Users
from diagrams.programming.framework import React

def create_snapstudy_architecture():
    """Create the SnapStudy AWS architecture diagram."""
    
    with Diagram("SnapStudy - AWS Serverless Architecture", 
                 filename="snapstudy_architecture", 
                 show=False,
                 direction="TB"):
        
        # Users
        users = Users("Students & Educators")
        
        with Cluster("Frontend Layer"):
            frontend = React("React Frontend")
            frontend_s3 = S3("Frontend Hosting\n(S3 + CloudFront)")
            
        with Cluster("API Layer"):
            waf = WAF("AWS WAF\n(Security)")
            api_gateway = APIGateway("API Gateway\n(REST API)")
            
        with Cluster("Compute Layer"):
            lambda_api = Lambda("Main API\n(FastAPI)")
            
        with Cluster("Authentication"):
            cognito = Cognito("Cognito\nUser Pool")
            
        with Cluster("Database Layer"):
            with Cluster("DynamoDB Tables"):
                users_table = DynamodbTable("Users")
                lessons_table = DynamodbTable("Lessons")
                micro_lessons_table = DynamodbTable("MicroLessons")
                quizzes_table = DynamodbTable("Quizzes")
                engagement_table = DynamodbTable("UserEngagement")
                chat_table = DynamodbTable("ChatHistory")
                
        with Cluster("Storage Layer"):
            content_s3 = S3("Content Storage\n(Documents, Media)")
            
        with Cluster("AI/ML Services"):
            bedrock = Bedrock("Amazon Bedrock\n(Claude 3)")
            textract = Textract("Amazon Textract\n(Document Processing)")
            transcribe = Transcribe("Amazon Transcribe\n(Audio/Video)")
            
        with Cluster("Monitoring & Analytics"):
            cloudwatch = Cloudwatch("CloudWatch\n(Monitoring & Alarms)")
            
        # User flow
        users >> Edge(label="HTTPS") >> frontend
        frontend >> Edge(label="Static Assets") >> frontend_s3
        
        # API flow
        frontend >> Edge(label="API Calls") >> waf
        waf >> Edge(label="Filtered Requests") >> api_gateway
        api_gateway >> Edge(label="Lambda Proxy") >> lambda_api
        
        # Authentication flow
        frontend >> Edge(label="Auth") >> cognito
        lambda_api >> Edge(label="User Management") >> cognito
        
        # Database operations
        lambda_api >> Edge(label="CRUD Operations") >> [
            users_table,
            lessons_table,
            micro_lessons_table,
            quizzes_table,
            engagement_table,
            chat_table
        ]
        
        # Storage operations
        lambda_api >> Edge(label="File Operations") >> content_s3
        
        # AI/ML operations
        lambda_api >> Edge(label="Chat & Quiz Generation") >> bedrock
        lambda_api >> Edge(label="Document Processing") >> textract
        lambda_api >> Edge(label="Audio Processing") >> transcribe
        
        # Monitoring
        lambda_api >> Edge(label="Metrics & Logs") >> cloudwatch
        api_gateway >> Edge(label="API Metrics") >> cloudwatch

def create_detailed_flow_diagram():
    """Create a detailed data flow diagram."""
    
    with Diagram("SnapStudy - Detailed Data Flow", 
                 filename="snapstudy_data_flow", 
                 show=False,
                 direction="LR"):
        
        # User interactions
        student = Users("Student")
        educator = Users("Educator")
        
        with Cluster("Frontend Application"):
            react_app = React("React SPA")
            
        with Cluster("API Gateway + Security"):
            waf_security = WAF("WAF Rules")
            api_gw = APIGateway("REST API")
            
        with Cluster("Backend Services"):
            auth_service = Lambda("Auth Service")
            content_service = Lambda("Content Service")
            lesson_service = Lambda("Lesson Service")
            chat_service = Lambda("Chat Service")
            analytics_service = Lambda("Analytics Service")
            
        with Cluster("Data Persistence"):
            user_data = DynamodbTable("User Profiles")
            lesson_data = DynamodbTable("Lesson Content")
            progress_data = DynamodbTable("Learning Progress")
            
        with Cluster("AI Processing"):
            ai_bedrock = Bedrock("Claude 3\n(Chat & Generation)")
            doc_processing = Textract("Document Analysis")
            
        with Cluster("Content Storage"):
            media_storage = S3("Media Files")
            
        # Flow connections
        student >> react_app
        educator >> react_app
        
        react_app >> waf_security >> api_gw
        
        api_gw >> auth_service >> user_data
        api_gw >> content_service >> [lesson_data, media_storage]
        api_gw >> lesson_service >> [lesson_data, progress_data]
        api_gw >> chat_service >> ai_bedrock
        api_gw >> analytics_service >> progress_data
        
        content_service >> doc_processing >> media_storage

if __name__ == "__main__":
    print("🎨 Creating SnapStudy AWS Architecture Diagrams...")
    
    try:
        # Create main architecture diagram
        create_snapstudy_architecture()
        print("✅ Main architecture diagram created: snapstudy_architecture.png")
        
        # Create detailed flow diagram
        create_detailed_flow_diagram()
        print("✅ Data flow diagram created: snapstudy_data_flow.png")
        
        print("\n📋 Diagram files created:")
        print("- snapstudy_architecture.png")
        print("- snapstudy_data_flow.png")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please install the required library: pip install diagrams")
        print("Note: You may also need Graphviz installed on your system")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")