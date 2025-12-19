"""List available Gemini models."""

import os
import google.generativeai as genai  # type: ignore
from google.generativeai import list_models  # type: ignore

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")
genai.configure(api_key=api_key)  # type: ignore

print("📋 Modelos Gemini Disponíveis:")
print("=" * 70)

for model in list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"\n✅ {model.name}")
        print(f"   Descrição: {model.display_name}")
        print(f"   Métodos: {', '.join(model.supported_generation_methods)}")
