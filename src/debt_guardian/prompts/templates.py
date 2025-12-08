"""
Prompt templates for Technical Debt detection.

Implements various prompting strategies from the paper:
- Zero-shot prompting
- Few-shot prompting
- Batch prompting
- Granular prompting
"""
from typing import List, Dict, Optional
from debt_guardian.schemas.td_schema import TechnicalDebtType


class PromptTemplates:
    """
    Collection of prompt templates for TD detection.
    """
    
    # System prompt for TD detection
    SYSTEM_PROMPT = """You are an expert software engineer specializing in code quality analysis and technical debt detection.

Your task is to analyze code changes and identify technical debt instances. Technical debt refers to suboptimal design or implementation choices that may hinder future maintenance, quality, or performance.

You should identify the following types of technical debt:
- DESIGN: Poor architectural decisions, code smells, violations of design principles
- DOCUMENTATION: Missing or inadequate documentation, comments, or explanations
- DEFECT: Bugs, errors, or potential issues in the code
- TEST: Missing tests, inadequate test coverage, or poor test quality
- COMPATIBILITY: Issues with backward/forward compatibility or deprecated APIs
- BUILD: Problems with build configuration, dependencies, or deployment
- REQUIREMENT: Missing or incomplete implementation of requirements

Be precise and specific in your analysis. Focus on actionable issues."""

    @staticmethod
    def zero_shot_single_type(
        code_diff: str,
        file_path: str,
        td_type: str
    ) -> str:
        """
        Zero-shot prompt for detecting a single TD type.
        
        Args:
            code_diff: The code change to analyze
            file_path: Path to the file
            td_type: Type of TD to detect
            
        Returns:
            Formatted prompt
        """
        return f"""Analyze the following code change for {td_type.upper()} technical debt.

File: {file_path}

Code Change:
```
{code_diff}
```

Identify any {td_type} technical debt in this code change. For each instance found, provide:
1. The exact line numbers where the debt exists
2. A clear description of the symptom or problem
3. The severity (low, medium, high, or critical)
4. A suggested remediation approach

Return your analysis as a JSON array with this structure:
{{
  "debts": [
    {{
      "debt_type": "{td_type}",
      "symptom": "description of the problem",
      "location": {{
        "file_path": "{file_path}",
        "start_line": <line_number>,
        "end_line": <line_number>
      }},
      "severity": "medium",
      "confidence": 0.85,
      "suggested_remediation": "how to fix it",
      "code_snippet": "the problematic code"
    }}
  ]
}}

If no {td_type} debt is found, return: {{"debts": []}}"""

    @staticmethod
    def zero_shot_batch(
        code_diff: str,
        file_path: str,
        td_types: List[str]
    ) -> str:
        """
        Zero-shot batch prompt for detecting multiple TD types.
        
        Args:
            code_diff: The code change to analyze
            file_path: Path to the file
            td_types: List of TD types to detect
            
        Returns:
            Formatted prompt
        """
        types_str = ", ".join(td_types)
        
        return f"""Analyze the following code change for ALL types of technical debt: {types_str}.

File: {file_path}

Code Change:
```
{code_diff}
```

Identify any technical debt in this code change across all the specified types. For each instance found, provide:
1. The debt type (one of: {types_str})
2. The exact line numbers where the debt exists
3. A clear description of the symptom or problem
4. The severity (low, medium, high, or critical)
5. A suggested remediation approach

Return your analysis as a JSON array with this structure:
{{
  "debts": [
    {{
      "debt_type": "<type>",
      "symptom": "description of the problem",
      "location": {{
        "file_path": "{file_path}",
        "start_line": <line_number>,
        "end_line": <line_number>
      }},
      "severity": "medium",
      "confidence": 0.85,
      "suggested_remediation": "how to fix it",
      "code_snippet": "the problematic code"
    }}
  ]
}}

If no debt is found, return: {{"debts": []}}"""

    @staticmethod
    def few_shot_single_type(
        code_diff: str,
        file_path: str,
        td_type: str,
        examples: Optional[List[Dict]] = None
    ) -> str:
        """
        Few-shot prompt with examples for a single TD type.
        
        Args:
            code_diff: The code change to analyze
            file_path: Path to the file
            td_type: Type of TD to detect
            examples: Optional list of example detections
            
        Returns:
            Formatted prompt
        """
        examples_section = ""
        
        if examples:
            examples_section = "\n\nHere are some examples of " + td_type + " technical debt:\n\n"
            for i, ex in enumerate(examples, 1):
                examples_section += f"Example {i}:\n"
                examples_section += f"Code:\n```\n{ex.get('code', '')}\n```\n"
                examples_section += f"Issue: {ex.get('issue', '')}\n"
                examples_section += f"Severity: {ex.get('severity', 'medium')}\n\n"
        
        return f"""Analyze the following code change for {td_type.upper()} technical debt.
{examples_section}
Now analyze this code:

File: {file_path}

Code Change:
```
{code_diff}
```

Identify any {td_type} technical debt similar to the examples. For each instance found, provide:
1. The exact line numbers where the debt exists
2. A clear description of the symptom or problem
3. The severity (low, medium, high, or critical)
4. A suggested remediation approach

Return your analysis as a JSON array with this structure:
{{
  "debts": [
    {{
      "debt_type": "{td_type}",
      "symptom": "description of the problem",
      "location": {{
        "file_path": "{file_path}",
        "start_line": <line_number>,
        "end_line": <line_number>
      }},
      "severity": "medium",
      "confidence": 0.85,
      "suggested_remediation": "how to fix it",
      "code_snippet": "the problematic code"
    }}
  ]
}}

If no {td_type} debt is found, return: {{"debts": []}}"""

    @staticmethod
    def get_examples_for_type(td_type: str) -> List[Dict]:
        """
        Get predefined examples for few-shot prompting.
        
        Args:
            td_type: Type of technical debt
            
        Returns:
            List of example dictionaries
        """
        examples = {
            "design": [
                {
                    "code": "def process_data(data):\n    # God method that does everything\n    filtered = []\n    for item in data:\n        if item > 0:\n            filtered.append(item)\n    sorted_data = sorted(filtered)\n    result = sum(sorted_data) / len(sorted_data)\n    return result",
                    "issue": "Single method doing too many responsibilities (filtering, sorting, calculating). Violates Single Responsibility Principle.",
                    "severity": "medium"
                },
                {
                    "code": "class User:\n    def __init__(self):\n        self.db = Database()  # Tight coupling\n        self.cache = Cache()  # Tight coupling",
                    "issue": "Hard-coded dependencies create tight coupling. Should use dependency injection.",
                    "severity": "high"
                }
            ],
            "documentation": [
                {
                    "code": "def calc(x, y, z):\n    return (x * y) / z if z != 0 else None",
                    "issue": "Complex calculation without docstring explaining parameters, return value, or edge cases.",
                    "severity": "medium"
                },
                {
                    "code": "# TODO: Fix this later\nresult = data.process()",
                    "issue": "Vague TODO comment without context, assignee, or deadline.",
                    "severity": "low"
                }
            ],
            "test": [
                {
                    "code": "def critical_payment_processor(amount, account):\n    # No tests exist for this critical function\n    account.balance -= amount\n    return account.save()",
                    "issue": "Critical business logic without any unit tests.",
                    "severity": "critical"
                },
                {
                    "code": "def test_user_creation():\n    user = User('test')\n    assert user  # Weak assertion",
                    "issue": "Test exists but assertions are too weak to catch real issues.",
                    "severity": "medium"
                }
            ],
            "defect": [
                {
                    "code": "result = data / count  # count can be zero",
                    "issue": "Potential division by zero error without validation.",
                    "severity": "high"
                },
                {
                    "code": "user_input = request.args.get('id')\nquery = f'SELECT * FROM users WHERE id={user_input}'",
                    "issue": "SQL injection vulnerability - using unsanitized user input directly in query.",
                    "severity": "critical"
                }
            ]
        }
        
        return examples.get(td_type, [])
