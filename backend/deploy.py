#!/usr/bin/env python3
"""Deployment script for SnapStudy backend."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        return False
    
    print(result.stdout)
    return True

def main():
    """Main deployment function."""
    print("🚀 Starting SnapStudy backend deployment...")
    
    # Get the current directory
    backend_dir = Path(__file__).parent
    infrastructure_dir = backend_dir / "infrastructure"
    
    # Check if we're in the right directory
    if not infrastructure_dir.exists():
        print("❌ Infrastructure directory not found!")
        sys.exit(1)
    
    # Install Python dependencies for infrastructure
    print("📦 Installing CDK dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=infrastructure_dir):
        print("❌ Failed to install CDK dependencies")
        sys.exit(1)
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        print("❌ Failed to install backend dependencies")
        sys.exit(1)
    
    # Bootstrap CDK (if needed)
    print("🔧 Bootstrapping CDK...")
    run_command("cdk bootstrap", cwd=infrastructure_dir)
    
    # Synthesize the stack
    print("🔨 Synthesizing CDK stack...")
    if not run_command("cdk synth", cwd=infrastructure_dir):
        print("❌ Failed to synthesize CDK stack")
        sys.exit(1)
    
    # Deploy the stack
    print("🚀 Deploying CDK stack...")
    if not run_command("cdk deploy --require-approval never", cwd=infrastructure_dir):
        print("❌ Failed to deploy CDK stack")
        sys.exit(1)
    
    print("✅ Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Check the AWS Console to verify all resources are created")
    print("2. Note down the API Gateway URL from the outputs")
    print("3. Configure your frontend to use the new API endpoint")

if __name__ == "__main__":
    main()