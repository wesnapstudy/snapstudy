#!/usr/bin/env python3
"""
Validation Script: TRUE Agents Only (No Prompt-Based Reasoning)

This script validates that SnapStudy uses ONLY Bedrock Agents for autonomous
decision-making and has completely eliminated prompt-based reasoning patterns.
"""

import os
import re
import sys
from typing import List, Dict, Tuple

class TrueAgentValidator:
    """Validates that only TRUE Bedrock Agents are used (no prompt-based reasoning)."""
    
    def __init__(self):
        self.issues = []
        self.files_checked = 0
        self.prompt_patterns = [
            # Prompt-based reasoning patterns that should NOT exist
            r'_create_.*_prompt',
            r'_invoke_claude_reasoning',
            r'reasoning_prompt\s*=',
            r'system_prompt\s*=',
            r'prompt\s*=.*reasoning',
            r'bedrock_service\.invoke_claude.*prompt',
            r'You are an.*agent.*prompt',
            r'REASONING FRAMEWORK:',
            r'ANALYSIS FRAMEWORK:',
            r'Create a.*prompt for',
            r'structured.*prompt',
            r'prompt.*engineering'
        ]
        
        self.required_agent_patterns = [
            # Patterns that SHOULD exist for TRUE agents
            r'bedrock_agent_client\.invoke_agent',
            r'_invoke_learning_agent',
            r'_invoke_adaptive_agent',
            r'autonomous_decision.*True',
            r'agent_used.*True',
            r'learning_agent_id',
            r'adaptive_agent_id'
        ]
        
        self.files_to_check = [
            'backend/src/services/adaptive_agent.py',
            'backend/src/services/enhanced_chat_agent.py',
            'backend/src/services/chat_agent.py',
            'backend/src/agent_actions/agent_actions.py'
        ]
    
    def validate_all(self) -> Dict[str, any]:
        """Run complete validation of TRUE agent implementation."""
        print("🤖 Validating TRUE Agents Only (No Prompt-Based Reasoning)")
        print("=" * 70)
        
        results = {
            'files_checked': 0,
            'prompt_violations': [],
            'missing_agent_features': [],
            'agent_implementations': [],
            'overall_status': 'UNKNOWN'
        }
        
        # Check each file
        for file_path in self.files_to_check:
            if os.path.exists(file_path):
                print(f"\n🔍 Checking: {file_path}")
                file_results = self.validate_file(file_path)
                results['files_checked'] += 1
                
                if file_results['prompt_violations']:
                    results['prompt_violations'].extend(file_results['prompt_violations'])
                    
                if file_results['missing_agent_features']:
                    results['missing_agent_features'].extend(file_results['missing_agent_features'])
                    
                results['agent_implementations'].extend(file_results['agent_implementations'])
            else:
                print(f"⚠️  File not found: {file_path}")
        
        # Generate overall assessment
        results['overall_status'] = self.assess_overall_status(results)
        
        # Print summary
        self.print_validation_summary(results)
        
        return results
    
    def validate_file(self, file_path: str) -> Dict[str, List]:
        """Validate a single file for TRUE agent usage."""
        results = {
            'prompt_violations': [],
            'missing_agent_features': [],
            'agent_implementations': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for prompt-based reasoning violations
            for i, line in enumerate(lines, 1):
                for pattern in self.prompt_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results['prompt_violations'].append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'pattern': pattern,
                            'severity': 'HIGH'
                        })
            
            # Check for required agent implementations
            agent_features_found = []
            for pattern in self.required_agent_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    agent_features_found.append({
                        'pattern': pattern,
                        'matches': len(matches),
                        'file': file_path
                    })
            
            results['agent_implementations'] = agent_features_found
            
            # Check for specific TRUE agent methods
            required_methods = [
                '_invoke_learning_agent',
                '_invoke_adaptive_agent',
                'autonomous_adapt_learning_path',
                'get_autonomous_recommendation'
            ]
            
            for method in required_methods:
                if method not in content:
                    results['missing_agent_features'].append({
                        'file': file_path,
                        'missing_method': method,
                        'severity': 'MEDIUM'
                    })
            
            # Print file-specific results
            violations = len(results['prompt_violations'])
            implementations = len(results['agent_implementations'])
            
            if violations == 0 and implementations > 0:
                print(f"  ✅ CLEAN: No prompt-based reasoning, {implementations} agent features found")
            elif violations == 0:
                print(f"  ⚠️  PARTIAL: No violations but limited agent features ({implementations})")
            else:
                print(f"  ❌ VIOLATIONS: {violations} prompt-based patterns found")
                
        except Exception as e:
            print(f"  ❌ ERROR: Could not validate {file_path}: {e}")
            results['prompt_violations'].append({
                'file': file_path,
                'line': 0,
                'content': f'File validation error: {e}',
                'pattern': 'file_error',
                'severity': 'HIGH'
            })
        
        return results
    
    def assess_overall_status(self, results: Dict) -> str:
        """Assess overall validation status."""
        violations = len(results['prompt_violations'])
        implementations = len(results['agent_implementations'])
        
        if violations == 0 and implementations >= 10:
            return 'TRUE_AGENTS_ONLY'
        elif violations == 0 and implementations >= 5:
            return 'MOSTLY_TRUE_AGENTS'
        elif violations <= 2 and implementations >= 5:
            return 'MIXED_IMPLEMENTATION'
        else:
            return 'PROMPT_BASED_DETECTED'
    
    def print_validation_summary(self, results: Dict):
        """Print comprehensive validation summary."""
        print("\n" + "=" * 70)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 70)
        
        status = results['overall_status']
        violations = len(results['prompt_violations'])
        implementations = len(results['agent_implementations'])
        
        print(f"\nFiles Checked: {results['files_checked']}")
        print(f"Prompt Violations: {violations}")
        print(f"Agent Implementations: {implementations}")
        
        # Status assessment
        if status == 'TRUE_AGENTS_ONLY':
            print("\n🎉 STATUS: TRUE AGENTS ONLY ✅")
            print("   ✅ No prompt-based reasoning detected")
            print("   ✅ Strong agent implementation found")
            print("   ✅ Genuine autonomous AI confirmed")
            
        elif status == 'MOSTLY_TRUE_AGENTS':
            print("\n⚠️  STATUS: MOSTLY TRUE AGENTS")
            print("   ✅ No prompt-based reasoning detected")
            print("   ⚠️  Limited agent implementations")
            print("   📝 Consider adding more agent features")
            
        elif status == 'MIXED_IMPLEMENTATION':
            print("\n⚠️  STATUS: MIXED IMPLEMENTATION")
            print("   ❌ Some prompt-based reasoning detected")
            print("   ✅ Agent implementations present")
            print("   🔧 Needs cleanup to be TRUE agents only")
            
        else:
            print("\n❌ STATUS: PROMPT-BASED DETECTED")
            print("   ❌ Significant prompt-based reasoning found")
            print("   ❌ Not TRUE autonomous AI")
            print("   🚨 Requires major refactoring")
        
        # Detailed violations
        if violations > 0:
            print(f"\n🚨 PROMPT-BASED VIOLATIONS ({violations}):")
            for violation in results['prompt_violations'][:10]:  # Show first 10
                print(f"   ❌ {violation['file']}:{violation['line']}")
                print(f"      Pattern: {violation['pattern']}")
                print(f"      Code: {violation['content'][:80]}...")
        
        # Agent implementations
        if implementations > 0:
            print(f"\n✅ AGENT IMPLEMENTATIONS FOUND ({implementations}):")
            for impl in results['agent_implementations'][:5]:  # Show first 5
                print(f"   ✅ {impl['pattern']}: {impl['matches']} matches in {impl['file']}")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if status == 'TRUE_AGENTS_ONLY':
            print("   🎯 Perfect! Deploy with confidence")
            print("   📊 Monitor agent performance in production")
            print("   📈 Consider adding more autonomous features")
            
        elif violations > 0:
            print("   🔧 Remove all prompt-based reasoning methods")
            print("   🤖 Replace with TRUE Bedrock Agent invocations")
            print("   ✅ Re-run validation after fixes")
            
        else:
            print("   🚀 Add more autonomous agent features")
            print("   📚 Implement agent memory and planning")
            print("   🎯 Enhance agent decision-making capabilities")
        
        print("\n" + "=" * 70)


def main():
    """Run the TRUE agents validation."""
    validator = TrueAgentValidator()
    results = validator.validate_all()
    
    # Exit with appropriate code
    if results['overall_status'] == 'TRUE_AGENTS_ONLY':
        print("\n🎉 SUCCESS: SnapStudy uses TRUE Agents Only!")
        sys.exit(0)
    elif len(results['prompt_violations']) == 0:
        print("\n⚠️  WARNING: Mostly clean but could be improved")
        sys.exit(1)
    else:
        print("\n❌ FAILURE: Prompt-based reasoning detected")
        sys.exit(2)


if __name__ == "__main__":
    main()