# Amazon Bedrock AgentCore Integration

This document explains how SnapStudy's Adaptive Learning Agent uses Amazon Bedrock AgentCore primitives for true autonomous reasoning and decision-making.

## Overview

The SnapStudy Adaptive Learning Agent is now powered by **Amazon Bedrock AgentCore primitives**, providing:

- **Autonomous Reasoning**: Context-aware decision making using agent reasoning capabilities
- **Memory Management**: Persistent learning patterns and user context across sessions  
- **Function Invocation**: Structured calling of learning functions (content generation, evaluation)
- **Planning**: Multi-step learning sequence planning
- **State Management**: Continuous learning state updates and context preservation

## AgentCore Architecture

### BedrockAgentCore Class

The `BedrockAgentCore` class implements the core agent primitives:

```python
class BedrockAgentCore:
    def __init__(self):
        self.bedrock_agent_client = boto3.client('bedrock-agent-runtime')
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.agent_id = settings.bedrock_agent_id
        self.agent_alias_id = settings.bedrock_agent_alias_id
```

### Core Primitives

#### 1. Reasoning Over Context
```python
async def reason_over_context(self, context: Dict[str, Any], goal: str) -> Dict[str, Any]:
    """
    Use Bedrock Agent reasoning capabilities to analyze context and make decisions.
    This is the core autonomous reasoning function.
    """
```

**Features:**
- Analyzes comprehensive learner context (performance, engagement, preferences)
- Makes autonomous decisions about learning path adaptation
- Provides structured reasoning with confidence scores
- Fallback to Claude reasoning if Bedrock Agent unavailable

#### 2. Memory Management
```python
async def update_memory(self, user_id: str, experience: Dict[str, Any]) -> None:
async def retrieve_memory(self, user_id: str) -> Dict[str, Any]:
```

**Features:**
- Stores learning experiences and patterns for each user
- Maintains performance history and adaptation decisions
- Identifies learning patterns over time
- Provides context for future decision making

#### 3. Function Invocation
```python
async def invoke_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
```

**Supported Functions:**
- `generate_micro_lesson`: Create personalized learning content
- `generate_quiz`: Generate adaptive assessments
- `evaluate_answer`: Intelligent answer evaluation with partial credit
- `analyze_performance`: Performance analysis for adaptation decisions

#### 4. Planning Capabilities
```python
async def plan_learning_sequence(self, context: Dict[str, Any], objective: str) -> List[Dict[str, Any]]:
```

**Features:**
- Creates multi-step learning sequences
- Plans content difficulty progression
- Sets assessment checkpoints
- Defines adaptation triggers

## Integration with Adaptive Learning Agent

### Decision Making Flow

1. **Context Gathering**: Collect user profile, performance history, engagement metrics
2. **Memory Retrieval**: Get agent memory for this user's learning patterns
3. **Autonomous Reasoning**: Use AgentCore to reason over context and make decisions
4. **Function Invocation**: Generate content using AgentCore function calls
5. **Memory Update**: Store decision and outcomes for future reasoning
6. **State Management**: Update learning state in DynamoDB

### Example Usage

```python
class AdaptiveLearningAgent:
    def __init__(self):
        self.agent_core = BedrockAgentCore()
    
    async def _make_adaptation_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Retrieve agent memory
        user_id = context.get('user_profile', {}).get('user_id')
        memory = await self.agent_core.retrieve_memory(user_id)
        context['agent_memory'] = memory
        
        # Use AgentCore reasoning
        decision_data = await self.agent_core.reason_over_context(
            context=context,
            goal="optimize_learning_path_based_on_performance_and_engagement"
        )
        
        # Update agent memory
        await self.agent_core.update_memory(user_id, {
            'decision': decision_data['decision'],
            'reasoning': decision_data['reasoning'],
            'context_summary': context
        })
        
        return decision_data
```

## Configuration

### Environment Variables

```bash
# Bedrock Agents Configuration
BEDROCK_AGENT_ID=your-agent-id-here
BEDROCK_AGENT_ALIAS_ID=TSTALIASID
BEDROCK_KNOWLEDGE_BASE_ID=your-knowledge-base-id
```

### AWS Permissions

The following IAM permissions are required:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeAgent",
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:agent/*",
                "arn:aws:bedrock:*:*:knowledge-base/*"
            ]
        }
    ]
}
```

## Fallback Mechanisms

### Agent Unavailable
If Bedrock Agent is not configured or unavailable, the system falls back to:
- Direct Claude invocation with agent-like reasoning prompts
- Structured decision making with safety constraints
- Local memory management using in-memory storage

### Function Invocation Fallback
If AgentCore function invocation fails:
- Direct calls to Bedrock service methods
- Error handling with graceful degradation
- Logging for debugging and monitoring

## Benefits of AgentCore Integration

### 1. True Autonomy
- **Reasoning**: Makes intelligent decisions based on comprehensive context
- **Memory**: Learns from past interactions and adapts over time
- **Planning**: Creates multi-step learning sequences autonomously

### 2. Consistency
- **Structured Decisions**: All decisions follow consistent reasoning patterns
- **State Management**: Maintains coherent learning state across sessions
- **Function Calls**: Standardized approach to content generation and evaluation

### 3. Scalability
- **Session Management**: Handles multiple concurrent learning sessions
- **Memory Efficiency**: Optimized memory storage with automatic cleanup
- **Performance**: Efficient agent invocation with proper error handling

### 4. Observability
- **Decision Tracking**: All autonomous decisions are logged and traceable
- **Performance Monitoring**: Agent reasoning performance metrics
- **Memory Analysis**: Learning pattern identification and analysis

## Testing AgentCore Integration

### Unit Tests
```python
async def test_agent_reasoning():
    agent_core = BedrockAgentCore()
    context = {...}  # Test context
    decision = await agent_core.reason_over_context(context, "optimize_learning")
    assert decision['decision'] in ['advance', 'review', 'reinforce']
```

### Integration Tests
```python
async def test_adaptive_agent_with_agentcore():
    agent = AdaptiveLearningAgent()
    result = await agent.get_next_micro_lesson(session_id, user_id, performance)
    assert 'adaptation_info' in result
    assert result['adaptation_info']['reasoning']  # AgentCore reasoning
```

## Monitoring and Debugging

### Logging
- All AgentCore operations are logged with structured data
- Decision reasoning is captured for analysis
- Memory updates are tracked for pattern identification

### Metrics
- Agent invocation success/failure rates
- Decision consistency across similar contexts
- Memory retrieval and update performance

### Debugging
- Fallback mechanism activation tracking
- JSON parsing error handling
- Context validation and sanitization

## Future Enhancements

### Knowledge Base Integration
- Connect to Bedrock Knowledge Base for domain-specific learning content
- Retrieve relevant educational materials based on learning context
- Enhance reasoning with educational best practices

### Advanced Planning
- Multi-session learning path planning
- Prerequisite dependency management
- Learning objective optimization

### Collaborative Agents
- Multiple specialized agents for different learning aspects
- Agent coordination for complex learning scenarios
- Distributed decision making across agent network

## Conclusion

The AgentCore integration transforms SnapStudy's Adaptive Learning Agent from a rule-based system into a truly autonomous, reasoning-capable AI agent. This provides:

- **Superior Learning Outcomes**: Intelligent adaptation based on comprehensive context
- **Scalable Architecture**: Handles complex learning scenarios autonomously  
- **Production Readiness**: Robust error handling and fallback mechanisms
- **Future Extensibility**: Foundation for advanced agent capabilities

The agent now operates as a true autonomous learning companion, making intelligent decisions that optimize each learner's educational journey.