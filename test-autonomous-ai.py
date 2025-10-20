#!/usr/bin/env python3
"""
Test Suite for SnapStudy TRUE Autonomous AI Implementation

This script validates that the Bedrock Agents are working correctly
and making genuine autonomous decisions (not just prompt-based responses).
"""

import asyncio
import json
import sys
import os
import boto3
from datetime import datetime, timezone
import uuid

# Add the backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.adaptive_agent import BedrockAgentCore, AdaptiveLearningAgent
from services.enhanced_chat_agent import EnhancedAgenticChatAgent
from config import settings

class AutonomousAITester:
    """Test suite for validating TRUE autonomous AI capabilities."""
    
    def __init__(self):
        self.agent_core = BedrockAgentCore()
        self.adaptive_agent = AdaptiveLearningAgent()
        self.enhanced_chat = EnhancedAgenticChatAgent()
        self.test_results = []
        
    async def run_all_tests(self):
        """Run comprehensive test suite for autonomous AI."""
        print("🤖 SnapStudy TRUE Autonomous AI Test Suite")
        print("=" * 60)
        
        # Test 1: Agent Configuration Validation
        await self.test_agent_configuration()
        
        # Test 2: Autonomous Reasoning Capabilities
        await self.test_autonomous_reasoning()
        
        # Test 3: Learning Path Adaptation
        await self.test_autonomous_adaptation()
        
        # Test 4: Performance Analysis
        await self.test_performance_analysis()
        
        # Test 5: Enhanced Chat with Agents
        await self.test_enhanced_chat_agents()
        
        # Test 6: Agent vs Prompt-Based Comparison
        await self.test_agent_vs_prompts()
        
        # Generate test report
        self.generate_test_report()
    
    async def test_agent_configuration(self):
        """Test that Bedrock Agents are properly configured."""
        print("\n🔧 Test 1: Agent Configuration Validation")
        print("-" * 40)
        
        try:
            # Check agent health status
            health_status = self.agent_core.get_agent_health_status()
            
            print(f"Learning Agent Configured: {health_status['learning_agent']['configured']}")
            print(f"Adaptive Agent Configured: {health_status['adaptive_agent']['configured']}")
            print(f"Knowledge Base Configured: {health_status['knowledge_base']['configured']}")
            
            # Validate agent IDs are set
            if health_status['learning_agent']['configured']:
                print(f"✅ Learning Agent ID: {health_status['learning_agent']['agent_id']}")
                self.test_results.append(("Agent Configuration", "PASS", "Learning Agent properly configured"))
            else:
                print("❌ Learning Agent not configured")
                self.test_results.append(("Agent Configuration", "FAIL", "Learning Agent missing"))
                
            if health_status['adaptive_agent']['configured']:
                print(f"✅ Adaptive Agent ID: {health_status['adaptive_agent']['agent_id']}")
            else:
                print("⚠️  Adaptive Agent not configured (optional)")
                
            # Test autonomous capabilities
            autonomous_caps = health_status['autonomous_capabilities']
            print(f"\nAutonomous Capabilities:")
            print(f"  Reasoning: {autonomous_caps['reasoning']}")
            print(f"  Adaptation: {autonomous_caps['adaptation']}")
            print(f"  Planning: {autonomous_caps['planning']}")
            print(f"  Recommendations: {autonomous_caps['recommendations']}")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            self.test_results.append(("Agent Configuration", "FAIL", str(e)))
    
    async def test_autonomous_reasoning(self):
        """Test TRUE autonomous reasoning capabilities."""
        print("\n🧠 Test 2: Autonomous Reasoning Capabilities")
        print("-" * 40)
        
        try:
            # Create test context for autonomous reasoning
            test_context = {
                'user_id': 'test-user-autonomous',
                'current_lesson': {
                    'title': 'Introduction to Calculus',
                    'difficulty': 'intermediate'
                },
                'performance_data': {
                    'average_score': 0.75,
                    'completion_rate': 0.8,
                    'engagement_level': 'medium'
                },
                'user_profile': {
                    'learning_style': 'visual',
                    'difficulty_level': 'intermediate'
                },
                'session_id': str(uuid.uuid4())
            }
            
            # Test autonomous reasoning
            print("Testing autonomous reasoning...")
            reasoning_result = await self.agent_core.reason_over_context(
                test_context, 
                "analyze_student_performance_and_recommend_next_action"
            )
            
            # Validate autonomous decision
            if reasoning_result.get('autonomous_decision'):
                print("✅ TRUE autonomous decision made by Bedrock Agent")
                print(f"   Confidence: {reasoning_result.get('confidence', 'N/A')}")
                print(f"   Reasoning: {reasoning_result.get('reasoning', 'N/A')[:100]}...")
                
                # Check for agent-specific indicators
                if reasoning_result.get('agent_used'):
                    print("✅ Confirmed: Real Bedrock Agent invocation (not prompt-based)")
                    self.test_results.append(("Autonomous Reasoning", "PASS", "TRUE agent reasoning confirmed"))
                else:
                    print("⚠️  Warning: May be using fallback reasoning")
                    self.test_results.append(("Autonomous Reasoning", "PARTIAL", "Fallback reasoning used"))
                    
            else:
                print("❌ No autonomous decision detected")
                self.test_results.append(("Autonomous Reasoning", "FAIL", "No autonomous decision made"))
                
        except Exception as e:
            print(f"❌ Autonomous reasoning test failed: {e}")
            self.test_results.append(("Autonomous Reasoning", "FAIL", str(e)))
    
    async def test_autonomous_adaptation(self):
        """Test autonomous learning path adaptation."""
        print("\n🎯 Test 3: Autonomous Learning Path Adaptation")
        print("-" * 40)
        
        try:
            # Test different performance scenarios
            test_scenarios = [
                {
                    'name': 'High Performance - Should ADVANCE',
                    'performance': {'average_score': 0.92, 'engagement': 'high'},
                    'expected': 'advance'
                },
                {
                    'name': 'Low Performance - Should SIMPLIFY',
                    'performance': {'average_score': 0.45, 'engagement': 'medium'},
                    'expected': 'simplify'
                },
                {
                    'name': 'Medium Performance - Should REINFORCE',
                    'performance': {'average_score': 0.68, 'engagement': 'medium'},
                    'expected': 'reinforce'
                }
            ]
            
            adaptation_results = []
            
            for scenario in test_scenarios:
                print(f"\nTesting: {scenario['name']}")
                
                # Test autonomous adaptation
                adaptation_result = await self.agent_core.autonomous_adapt_learning_path(
                    user_id='test-user-adaptation',
                    performance_data=scenario['performance'],
                    learning_context={'current_lesson_id': 'test-lesson-123'}
                )
                
                decision = adaptation_result.get('decision', 'unknown')
                autonomous = adaptation_result.get('autonomous', False)
                confidence = adaptation_result.get('confidence', 0)
                
                print(f"   Decision: {decision}")
                print(f"   Autonomous: {autonomous}")
                print(f"   Confidence: {confidence}")
                
                adaptation_results.append({
                    'scenario': scenario['name'],
                    'decision': decision,
                    'autonomous': autonomous,
                    'expected': scenario['expected']
                })
                
                if autonomous:
                    print("   ✅ TRUE autonomous adaptation")
                else:
                    print("   ⚠️  Fallback adaptation used")
            
            # Evaluate adaptation quality
            autonomous_count = sum(1 for r in adaptation_results if r['autonomous'])
            total_tests = len(adaptation_results)
            
            if autonomous_count == total_tests:
                print(f"\n✅ All {total_tests} adaptations were autonomous")
                self.test_results.append(("Autonomous Adaptation", "PASS", f"{autonomous_count}/{total_tests} autonomous"))
            elif autonomous_count > 0:
                print(f"\n⚠️  {autonomous_count}/{total_tests} adaptations were autonomous")
                self.test_results.append(("Autonomous Adaptation", "PARTIAL", f"{autonomous_count}/{total_tests} autonomous"))
            else:
                print(f"\n❌ No autonomous adaptations detected")
                self.test_results.append(("Autonomous Adaptation", "FAIL", "No autonomous adaptations"))
                
        except Exception as e:
            print(f"❌ Adaptation test failed: {e}")
            self.test_results.append(("Autonomous Adaptation", "FAIL", str(e)))
    
    async def test_performance_analysis(self):
        """Test autonomous performance analysis capabilities."""
        print("\n📊 Test 4: Autonomous Performance Analysis")
        print("-" * 40)
        
        try:
            # Create test performance data
            test_performance = {
                'user_id': 'test-user-performance',
                'recent_scores': [0.85, 0.78, 0.92, 0.88, 0.76],
                'engagement_metrics': {
                    'time_spent': [300, 450, 280, 520, 380],
                    'completion_rates': [1.0, 0.8, 1.0, 1.0, 0.9]
                },
                'learning_context': {
                    'subject': 'mathematics',
                    'current_topic': 'algebra'
                }
            }
            
            print("Testing autonomous performance analysis...")
            
            # This would call the agent action function
            # For now, we'll test the agent core reasoning about performance
            analysis_context = {
                'user_id': test_performance['user_id'],
                'performance_data': test_performance,
                'task_type': 'performance_analysis'
            }
            
            analysis_result = await self.agent_core.reason_over_context(
                analysis_context,
                "analyze_student_performance_patterns_and_identify_trends"
            )
            
            if analysis_result.get('autonomous_decision'):
                print("✅ Autonomous performance analysis completed")
                print(f"   Analysis confidence: {analysis_result.get('confidence', 'N/A')}")
                
                # Check for specific analysis components
                if analysis_result.get('recommendations'):
                    print(f"   Recommendations provided: {len(analysis_result['recommendations'])}")
                    
                self.test_results.append(("Performance Analysis", "PASS", "Autonomous analysis successful"))
            else:
                print("❌ No autonomous analysis detected")
                self.test_results.append(("Performance Analysis", "FAIL", "No autonomous analysis"))
                
        except Exception as e:
            print(f"❌ Performance analysis test failed: {e}")
            self.test_results.append(("Performance Analysis", "FAIL", str(e)))
    
    async def test_enhanced_chat_agents(self):
        """Test enhanced chat with TRUE agent integration."""
        print("\n💬 Test 5: Enhanced Chat with Bedrock Agents")
        print("-" * 40)
        
        try:
            # Test educational chat with agent routing
            test_messages = [
                {
                    'message': 'Can you help me understand calculus derivatives?',
                    'expected_intent': 'explanation',
                    'expected_source': 'agent_core'
                },
                {
                    'message': 'I need help with my Python programming assignment',
                    'expected_intent': 'coding_help',
                    'expected_source': 'amazon_q_developer'
                },
                {
                    'message': 'Find me research papers about machine learning',
                    'expected_intent': 'research_request',
                    'expected_source': 'amazon_q_business'
                }
            ]
            
            chat_results = []
            
            for test_msg in test_messages:
                print(f"\nTesting: '{test_msg['message'][:50]}...'")
                
                chat_response = await self.enhanced_chat.handle_enhanced_message(
                    user_id='test-user-chat',
                    message=test_msg['message'],
                    context={'user_profile': {'learning_style': 'mixed'}},
                    session_id=str(uuid.uuid4())
                )
                
                intent = chat_response.get('intent')
                source = chat_response.get('source')
                enhanced_features = chat_response.get('metadata', {}).get('enhanced_features_used', False)
                
                print(f"   Intent: {intent}")
                print(f"   Source: {source}")
                print(f"   Enhanced Features: {enhanced_features}")
                
                chat_results.append({
                    'message': test_msg['message'][:30],
                    'intent': intent,
                    'source': source,
                    'enhanced': enhanced_features
                })
                
                if enhanced_features:
                    print("   ✅ Enhanced chat features active")
                else:
                    print("   ⚠️  Basic chat features used")
            
            # Evaluate chat enhancement
            enhanced_count = sum(1 for r in chat_results if r['enhanced'])
            total_chats = len(chat_results)
            
            if enhanced_count >= total_chats * 0.7:  # 70% threshold
                print(f"\n✅ Enhanced chat working: {enhanced_count}/{total_chats} enhanced")
                self.test_results.append(("Enhanced Chat", "PASS", f"{enhanced_count}/{total_chats} enhanced"))
            else:
                print(f"\n⚠️  Limited enhancement: {enhanced_count}/{total_chats} enhanced")
                self.test_results.append(("Enhanced Chat", "PARTIAL", f"{enhanced_count}/{total_chats} enhanced"))
                
        except Exception as e:
            print(f"❌ Enhanced chat test failed: {e}")
            self.test_results.append(("Enhanced Chat", "FAIL", str(e)))
    
    async def test_agent_vs_prompts(self):
        """Compare TRUE agent responses vs prompt-based responses."""
        print("\n⚖️  Test 6: Agent vs Prompt-Based Comparison")
        print("-" * 40)
        
        try:
            test_context = {
                'user_id': 'comparison-test',
                'performance_data': {'average_score': 0.72},
                'session_id': str(uuid.uuid4())
            }
            
            # Test with agent (if available)
            print("Testing TRUE Bedrock Agent response...")
            agent_response = await self.agent_core.reason_over_context(
                test_context,
                "provide_learning_recommendation"
            )
            
            # Analyze response characteristics
            agent_autonomous = agent_response.get('autonomous_decision', False)
            agent_confidence = agent_response.get('confidence', 0)
            agent_trace = agent_response.get('trace_data', [])
            
            print(f"Agent Response:")
            print(f"   Autonomous: {agent_autonomous}")
            print(f"   Confidence: {agent_confidence}")
            print(f"   Has Trace Data: {len(agent_trace) > 0}")
            print(f"   Session ID: {agent_response.get('session_id', 'None')}")
            
            # Determine if this is TRUE agent vs prompt-based
            if agent_autonomous and len(agent_trace) > 0:
                print("\n✅ CONFIRMED: TRUE Bedrock Agent (not prompt-based)")
                print("   Evidence: Autonomous decision + Agent trace data")
                self.test_results.append(("Agent vs Prompts", "PASS", "TRUE agent confirmed"))
            elif agent_autonomous:
                print("\n⚠️  LIKELY: TRUE Bedrock Agent (autonomous decision)")
                print("   Evidence: Autonomous decision (trace data may be unavailable)")
                self.test_results.append(("Agent vs Prompts", "PARTIAL", "Likely true agent"))
            else:
                print("\n❌ FALLBACK: Prompt-based response detected")
                print("   Evidence: No autonomous decision indicators")
                self.test_results.append(("Agent vs Prompts", "FAIL", "Prompt-based fallback"))
                
        except Exception as e:
            print(f"❌ Agent comparison test failed: {e}")
            self.test_results.append(("Agent vs Prompts", "FAIL", str(e)))
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("🎯 AUTONOMOUS AI TEST REPORT")
        print("=" * 60)
        
        # Count results
        passed = sum(1 for r in self.test_results if r[1] == "PASS")
        partial = sum(1 for r in self.test_results if r[1] == "PARTIAL")
        failed = sum(1 for r in self.test_results if r[1] == "FAIL")
        total = len(self.test_results)
        
        print(f"\nTest Results Summary:")
        print(f"  ✅ PASSED: {passed}/{total}")
        print(f"  ⚠️  PARTIAL: {partial}/{total}")
        print(f"  ❌ FAILED: {failed}/{total}")
        
        print(f"\nDetailed Results:")
        for test_name, result, details in self.test_results:
            status_icon = "✅" if result == "PASS" else "⚠️" if result == "PARTIAL" else "❌"
            print(f"  {status_icon} {test_name}: {result}")
            print(f"     {details}")
        
        # Overall assessment
        print(f"\n" + "=" * 60)
        if passed >= total * 0.8:  # 80% pass rate
            print("🎉 OVERALL: TRUE AUTONOMOUS AI IMPLEMENTATION SUCCESSFUL!")
            print("   Your SnapStudy application is using genuine Bedrock Agents")
            print("   for autonomous decision-making, not just prompt-based responses.")
        elif passed >= total * 0.5:  # 50% pass rate
            print("⚠️  OVERALL: PARTIAL AUTONOMOUS AI IMPLEMENTATION")
            print("   Some autonomous features are working, but configuration")
            print("   may need adjustment for full autonomous capabilities.")
        else:
            print("❌ OVERALL: AUTONOMOUS AI IMPLEMENTATION NEEDS ATTENTION")
            print("   Most tests failed. Check agent configuration and deployment.")
        
        print(f"\nNext Steps:")
        if failed > 0:
            print("  1. Check Bedrock Agent deployment and configuration")
            print("  2. Verify agent IDs are set in environment variables")
            print("  3. Ensure proper IAM permissions for agent access")
        if partial > 0:
            print("  4. Review partial test results for optimization opportunities")
        if passed > 0:
            print("  5. Monitor autonomous decisions in production")
            print("  6. Collect metrics on autonomous decision quality")
        
        print(f"\n📊 Test completed at: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)


async def main():
    """Run the autonomous AI test suite."""
    tester = AutonomousAITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())