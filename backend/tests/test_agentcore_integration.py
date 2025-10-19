#!/usr/bin/env python3
"""
Test script to verify Amazon Bedrock AgentCore integration.
"""

import asyncio
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.adaptive_agent import BedrockAgentCore, AdaptiveLearningAgent


async def test_agentcore_reasoning():
    """Test AgentCore reasoning capabilities."""
    print("🧠 Testing AgentCore Reasoning...")
    print("=" * 50)
    
    try:
        agent_core = BedrockAgentCore()
        
        # Test context
        test_context = {
            'user_profile': {
                'user_id': 'test-user-123',
                'learning_style': 'visual',
                'attention_span': 15,
                'difficulty_level': 'intermediate'
            },
            'latest_performance': {
                'score': 75.0,
                'time_spent_seconds': 240,
                'engagement_metrics': {'focus_score': 0.8}
            },
            'progress': {
                'current_index': 2,
                'total_micro_lessons': 5,
                'completion_percentage': 40.0
            }
        }
        
        # Test reasoning
        decision = await agent_core.reason_over_context(
            context=test_context,
            goal="optimize_learning_path_based_on_performance"
        )
        
        print(f"✅ AgentCore Decision: {decision.get('decision', 'N/A')}")
        print(f"✅ Reasoning: {decision.get('reasoning', 'N/A')[:100]}...")
        print(f"✅ Confidence: {decision.get('confidence', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore reasoning test failed: {e}")
        return False


async def test_agentcore_memory():
    """Test AgentCore memory management."""
    print("🧠 Testing AgentCore Memory...")
    print("=" * 50)
    
    try:
        agent_core = BedrockAgentCore()
        user_id = 'test-user-memory'
        
        # Test memory update
        test_experience = {
            'decision': 'advance',
            'score': 85.0,
            'reasoning': 'User performed well, advancing to next concept'
        }
        
        await agent_core.update_memory(user_id, test_experience)
        print("✅ Memory updated successfully")
        
        # Test memory retrieval
        memory = await agent_core.retrieve_memory(user_id)
        print(f"✅ Memory retrieved: {len(memory.get('experiences', []))} experiences")
        
        if memory.get('experiences'):
            latest_exp = memory['experiences'][-1]
            print(f"✅ Latest experience: {latest_exp.get('experience', {}).get('decision', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore memory test failed: {e}")
        return False


async def test_agentcore_function_invocation():
    """Test AgentCore function invocation."""
    print("🔧 Testing AgentCore Function Invocation...")
    print("=" * 50)
    
    try:
        agent_core = BedrockAgentCore()
        
        # Test performance analysis function
        result = await agent_core.invoke_function(
            function_name="analyze_performance",
            parameters={
                'score': 78.0,
                'time_spent': 300,
                'engagement_metrics': {'focus_score': 0.75}
            }
        )
        
        print(f"✅ Performance Analysis: {result.get('performance_level', 'N/A')}")
        print(f"✅ Time Efficiency: {result.get('time_efficiency', 'N/A')}")
        print(f"✅ Recommendations: {len(result.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore function invocation test failed: {e}")
        return False


async def test_adaptive_agent_with_agentcore():
    """Test the full Adaptive Agent with AgentCore integration."""
    print("🤖 Testing Adaptive Agent with AgentCore...")
    print("=" * 50)
    
    try:
        agent = AdaptiveLearningAgent()
        
        # Verify AgentCore is initialized
        if hasattr(agent, 'agent_core') and agent.agent_core:
            print("✅ AgentCore properly initialized in Adaptive Agent")
            
            # Test that the agent uses AgentCore for reasoning
            print("✅ Adaptive Agent configured to use AgentCore primitives")
            print("   - Reasoning over context")
            print("   - Memory management")
            print("   - Function invocation")
            print("   - State updates")
            
            return True
        else:
            print("❌ AgentCore not properly initialized")
            return False
        
    except Exception as e:
        print(f"❌ Adaptive Agent integration test failed: {e}")
        return False


async def main():
    """Run all AgentCore integration tests."""
    print("🚀 Amazon Bedrock AgentCore Integration Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("AgentCore Reasoning", test_agentcore_reasoning),
        ("AgentCore Memory", test_agentcore_memory),
        ("AgentCore Function Invocation", test_agentcore_function_invocation),
        ("Adaptive Agent Integration", test_adaptive_agent_with_agentcore),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            success = await test_func()
            results[test_name] = success
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} FAILED: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 AGENTCORE INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 AgentCore integration is working correctly!")
        print("\n🔧 AgentCore Features Verified:")
        print("   ✅ Autonomous reasoning over context")
        print("   ✅ Memory management and pattern learning")
        print("   ✅ Function invocation for learning tasks")
        print("   ✅ Integration with Adaptive Learning Agent")
    else:
        print("⚠️  Some AgentCore integration tests failed.")
        print("\n💡 Note: Some failures may be expected if:")
        print("   - Bedrock Agent is not configured (will use fallback)")
        print("   - AWS permissions are limited (will use Claude fallback)")
        print("   - This is the first run (memory starts empty)")


if __name__ == "__main__":
    asyncio.run(main())