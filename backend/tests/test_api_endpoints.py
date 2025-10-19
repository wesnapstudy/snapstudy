#!/usr/bin/env python3
"""
HTTP test script for AI services API endpoints.
Run this after starting the FastAPI server to test the endpoints.
"""

import requests
import json
import time


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_endpoint(self):
        """Test the basic health endpoint."""
        print("🏥 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False
    
    def test_ai_health_check(self):
        """Test AI services health check."""
        print("🔍 Testing AI Services Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ai/health-check")
            if response.status_code == 200:
                data = response.json()
                print("✅ AI Health Check working")
                print(f"   Overall Status: {data.get('status', 'unknown')}")
                
                services = data.get('services', {})
                for service, info in services.items():
                    status = "✅" if info.get('has_permissions') else "❌"
                    print(f"   {service}: {status}")
                
                return True
            else:
                print(f"❌ AI Health Check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ AI Health Check error: {e}")
            return False
    
    def test_bedrock_service(self):
        """Test Bedrock service."""
        print("🤖 Testing Bedrock Service...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/test-bedrock",
                params={"test_prompt": "Hello, please respond with 'API test successful'"}
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Bedrock test working")
                print(f"   Response: {data.get('response', 'No response')}")
                return True
            else:
                print(f"❌ Bedrock test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Bedrock test error: {e}")
            return False
    
    def test_content_analysis(self):
        """Test content analysis."""
        print("📝 Testing Content Analysis...")
        try:
            test_content = "Python is a high-level programming language known for its simplicity and readability."
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/test-content-analysis",
                params={"content": test_content}
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Content Analysis working")
                analysis = data.get('analysis', {})
                print(f"   Title: {analysis.get('title', 'N/A')}")
                print(f"   Difficulty: {analysis.get('difficulty_level', 'N/A')}")
                print(f"   Key Concepts: {analysis.get('key_concepts', [])}")
                return True
            else:
                print(f"❌ Content Analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Content Analysis error: {e}")
            return False
    
    def test_micro_lesson_generation(self):
        """Test micro-lesson generation."""
        print("📚 Testing Micro-Lesson Generation...")
        try:
            response = self.session.post(f"{self.base_url}/api/v1/ai/test-micro-lesson-generation")
            if response.status_code == 200:
                data = response.json()
                print("✅ Micro-Lesson Generation working")
                lesson = data.get('generated_lesson', {})
                print(f"   Title: {lesson.get('title', 'N/A')}")
                print(f"   Duration: {lesson.get('estimated_duration_minutes', 'N/A')} minutes")
                print(f"   Key Concepts: {lesson.get('key_concepts', [])}")
                return True
            else:
                print(f"❌ Micro-Lesson Generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Micro-Lesson Generation error: {e}")
            return False
    
    def test_quiz_generation(self):
        """Test quiz generation."""
        print("❓ Testing Quiz Generation...")
        try:
            response = self.session.post(f"{self.base_url}/api/v1/ai/test-quiz-generation")
            if response.status_code == 200:
                data = response.json()
                print("✅ Quiz Generation working")
                quiz = data.get('generated_quiz', {})
                print(f"   Questions: {quiz.get('total_questions', 0)}")
                print(f"   Total Points: {quiz.get('total_points', 0)}")
                
                questions = quiz.get('questions', [])
                if questions:
                    print(f"   Sample Question: {questions[0].get('question_text', 'N/A')}")
                
                return True
            else:
                print(f"❌ Quiz Generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Quiz Generation error: {e}")
            return False
    
    def test_service_capabilities(self):
        """Test individual service capabilities."""
        print("🛠️ Testing Service Capabilities...")
        
        services = ['s3', 'textract', 'transcribe']
        results = {}
        
        for service in services:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/ai/test-{service}")
                if response.status_code == 200:
                    print(f"✅ {service.upper()} capabilities test passed")
                    results[service] = True
                else:
                    print(f"❌ {service.upper()} capabilities test failed: {response.status_code}")
                    results[service] = False
            except Exception as e:
                print(f"❌ {service.upper()} capabilities test error: {e}")
                results[service] = False
        
        return all(results.values())
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 SnapStudy AI Services API Test Suite")
        print("=" * 60)
        print()
        
        # Check if server is running
        print("🔌 Checking if server is running...")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code != 200:
                print("❌ Server not responding. Please start the FastAPI server first.")
                print("   Run: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
                return
        except Exception as e:
            print("❌ Cannot connect to server. Please start the FastAPI server first.")
            print("   Run: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
            print(f"   Error: {e}")
            return
        
        print("✅ Server is running!")
        print()
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("AI Health Check", self.test_ai_health_check),
            ("Service Capabilities", self.test_service_capabilities),
            ("Bedrock Service", self.test_bedrock_service),
            ("Content Analysis", self.test_content_analysis),
            ("Micro-Lesson Generation", self.test_micro_lesson_generation),
            ("Quiz Generation", self.test_quiz_generation),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            try:
                result = test_func()
                results[test_name] = result
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                results[test_name] = False
                print(f"❌ {test_name} failed with exception: {e}")
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 API TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All API tests passed! Your AI services API is working correctly.")
        else:
            print("⚠️  Some API tests failed. Check the server logs for more details.")


def main():
    """Main function."""
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Testing API at: {base_url}")
    print()
    
    tester = APITester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()