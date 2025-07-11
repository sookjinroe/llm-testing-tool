#!/usr/bin/env python3
"""
모델 정보 조회 스크립트
OpenAI와 Anthropic의 실제 모델 정보를 조회합니다.
"""

import os
from dotenv import load_dotenv
import anthropic
import openai

load_dotenv()

print("=== API 키 확인 ===")
print(f"OpenAI API Key: {'설정됨' if os.getenv('OPENAI_API_KEY') else '설정되지 않음'}")
print(f"Anthropic API Key: {'설정됨' if os.getenv('ANTHROPIC_API_KEY') else '설정되지 않음'}")
print()

print("=== Anthropic 모델 목록 ===")
try:
    anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    models = anthropic_client.models.list()
    print("사용 가능한 Anthropic 모델:")
    for model in models.data:
        print(f"- {model.id}")
    print()
except Exception as e:
    print(f"Anthropic 모델 조회 실패: {e}")
    print()

print("=== OpenAI 모델 목록 ===")
try:
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    models = openai_client.models.list()
    print("사용 가능한 OpenAI 모델:")
    for model in models.data:
        print(f"- {model.id}")
    print()
except Exception as e:
    print(f"OpenAI 모델 조회 실패: {e}")
    print() 