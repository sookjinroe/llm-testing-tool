"""
프롬프트 처리 서비스
변수 치환 및 프롬프트 전처리 기능을 담당
"""

import re
from typing import Dict, List, Optional
from loguru import logger

class PromptProcessor:
    """프롬프트 처리 및 변수 치환 서비스"""
    
    @staticmethod
    def replace_variables(prompt: str, variables: Dict[str, str]) -> str:
        """
        프롬프트 내 변수를 실제 값으로 치환
        
        Args:
            prompt: 원본 프롬프트
            variables: 변수 키-값 쌍
            
        Returns:
            str: 변수가 치환된 프롬프트
        """
        if not variables:
            return prompt
        
        try:
            # {{변수명}} 형태의 변수를 찾아서 치환
            for var_name, var_value in variables.items():
                # 정규식으로 정확한 변수 패턴 매칭
                pattern = r'\{\{\s*' + re.escape(var_name) + r'\s*\}\}'
                prompt = re.sub(pattern, str(var_value), prompt)
            
            logger.debug(f"변수 치환 완료: {len(variables)}개 변수 처리")
            return prompt
            
        except Exception as e:
            logger.error(f"변수 치환 중 오류: {str(e)}")
            return prompt
    
    @staticmethod
    def extract_variables(prompt: str) -> List[str]:
        """
        프롬프트에서 사용된 변수명들을 추출
        
        Args:
            prompt: 프롬프트 문자열
            
        Returns:
            List[str]: 변수명 목록
        """
        try:
            # {{변수명}} 형태의 변수를 찾아서 추출
            pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
            variables = re.findall(pattern, prompt)
            
            # 중복 제거하고 정렬
            unique_variables = sorted(list(set(variables)))
            logger.debug(f"프롬프트에서 {len(unique_variables)}개 변수 추출: {unique_variables}")
            
            return unique_variables
            
        except Exception as e:
            logger.error(f"변수 추출 중 오류: {str(e)}")
            return []
    
    @staticmethod
    def validate_variables(prompt: str, provided_variables: Dict[str, str]) -> Dict[str, str]:
        """
        프롬프트에 필요한 변수와 제공된 변수를 검증
        
        Args:
            prompt: 프롬프트 문자열
            provided_variables: 제공된 변수들
            
        Returns:
            Dict[str, str]: 누락된 변수들 (키만 포함, 값은 빈 문자열)
        """
        required_variables = set(PromptProcessor.extract_variables(prompt))
        provided_variable_names = set(provided_variables.keys())
        
        # 누락된 변수들 찾기
        missing_variables = required_variables - provided_variable_names
        
        missing_dict = {var: "" for var in missing_variables}
        
        if missing_variables:
            logger.warning(f"누락된 변수들: {list(missing_variables)}")
        
        return missing_dict
    
    @staticmethod
    def process_messages_with_variables(
        messages: List[Dict[str, str]], 
        variables: Optional[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        메시지 목록의 모든 메시지에 변수 치환 적용
        
        Args:
            messages: 메시지 목록
            variables: 변수 키-값 쌍
            
        Returns:
            List[Dict[str, str]]: 변수가 치환된 메시지 목록
        """
        if not variables:
            return messages
        
        processed_messages = []
        
        for message in messages:
            processed_message = message.copy()
            if 'content' in processed_message:
                processed_message['content'] = PromptProcessor.replace_variables(
                    processed_message['content'], 
                    variables
                )
            processed_messages.append(processed_message)
        
        logger.debug(f"{len(messages)}개 메시지에 변수 치환 적용")
        return processed_messages
    
    @staticmethod
    def create_variable_template(prompt: str) -> Dict[str, str]:
        """
        프롬프트에서 변수 템플릿 생성
        
        Args:
            prompt: 프롬프트 문자열
            
        Returns:
            Dict[str, str]: 변수명과 기본값(빈 문자열)의 딕셔너리
        """
        variables = PromptProcessor.extract_variables(prompt)
        return {var: "" for var in variables}
    
    @staticmethod
    def format_prompt_with_examples(prompt: str, examples: Dict[str, str]) -> str:
        """
        예시와 함께 프롬프트 포맷팅
        
        Args:
            prompt: 원본 프롬프트
            examples: 변수 예시 값들
            
        Returns:
            str: 예시가 포함된 포맷된 프롬프트
        """
        if not examples:
            return prompt
        
        # 예시 섹션 추가
        examples_section = "\n\n사용 가능한 변수들:\n"
        for var_name, example_value in examples.items():
            examples_section += f"- {var_name}: {example_value}\n"
        
        return prompt + examples_section 