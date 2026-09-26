import os
from google import genai


def repair_code(code, vulnerability, cwe, line):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "GEMINI_API_KEY is not configured."
        }

    try:

        client = genai.Client(
            api_key=api_key
        )

        prompt = f"""
You are a secure code repair agent.

Vulnerability:
{vulnerability}

CWE:
{cwe}

Vulnerable line:
{line}

Source code:
{code}

Your task:
1. Identify the security vulnerability.
2. Fix the vulnerability.
3. Preserve the original functionality.
4. Return the complete repaired Python source code.
5. Do not include markdown code fences.
6. Return only the repaired source code.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        repaired_code = response.text.strip()

        return {
            "success": True,
            "code": repaired_code
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }