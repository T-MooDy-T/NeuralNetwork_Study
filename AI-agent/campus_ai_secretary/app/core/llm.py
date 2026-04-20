"""千问 LLM 服务封装

使用阿里云 DashScope SDK 调用 Qwen 模型
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import dashscope
from dashscope import Generation
import httpx


class QwenAPIError(Exception):
    """Qwen API 调用异常"""
    pass


class QwenLLM:
    """千问大语言模型服务"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-plus"):
        """初始化 LLM 服务
        
        Args:
            api_key: DashScope API Key，默认从环境变量读取
            model: 模型名称，如 qwen-plus, qwen-max 等
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 未配置")
        
        # 自定义 API endpoint 支持
        self.custom_endpoint = os.getenv("QWEN_API_ENDPOINT")
        
        dashscope.api_key = self.api_key
        self.model = model
        self.http_client = httpx.Client(timeout=30.0)
        logger.info(f"QwenLLM 初始化完成，模型：{model}")
        if self.custom_endpoint:
            logger.info(f"使用自定义 API endpoint：{self.custom_endpoint}")
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             system_prompt: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: int = 2048) -> str:
        """发送聊天请求
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数 (0-2)
            max_tokens: 最大输出 token 数
        
        Returns:
            模型回复文本
        """
        try:
            # 如果有自定义 endpoint，使用 HTTP 直接调用
            if self.custom_endpoint:
                return self._chat_with_custom_endpoint(
                    messages, system_prompt, temperature, max_tokens
                )
            
            # 构建消息
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                logger.error(f"Qwen API 请求失败：{response.code} - {response.message}")
                return f"抱歉，服务暂时不可用（错误码：{response.code}）"
        
        except Exception as e:
            logger.exception(f"LLM 调用异常：{e}")
            return "抱歉，处理您的请求时出现了问题，请稍后重试。"
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """从文本中提取日程实体
        
        Args:
            text: 用户输入的文本
        
        Returns:
            提取的实体字典
        """
        system_prompt = """你是一个校园日程助手，擅长从自然语言中提取日程信息。
请从用户输入中提取以下信息，以 JSON 格式返回：
- event_name: 事件名称（字符串）
- start_time: 开始时间（字符串，保持原文）
- end_time: 结束时间（字符串，可选）
- location: 地点（字符串，可选）
- priority: 优先级（high/medium/low）
- description: 详细描述（字符串）

如果某些信息无法提取，对应字段设为 null。
只返回 JSON，不要其他内容。"""
        
        messages = [{"role": "user", "content": text}]
        response = self.chat(messages, system_prompt, temperature=0.3)
        
        try:
            # 尝试解析 JSON
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]
            elif json_str.startswith("```"):
                json_str = json_str[3:-3]
            
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"JSON 解析失败：{e}, 原始响应：{response}")
            return {
                "event_name": None,
                "start_time": None,
                "end_time": None,
                "location": None,
                "priority": "medium",
                "description": text
            }
    
    def answer_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """回答用户问题
        
        Args:
            question: 用户问题
            context: 相关上下文（知识库检索结果）
        
        Returns:
            包含回答和元数据的字典
        """
        system_prompt = """你是校园 AI 秘书，负责回答校园相关问题。
- 语气友好、简洁、专业
- 基于提供的参考信息回答
- 如果参考信息不足，明确告知用户
- 如果问题涉及日程创建，在回答末尾说明可以帮用户创建日程
"""
        
        user_content = question
        if context:
            user_content = f"""【参考信息】
{context}

【用户问题】
{question}

请基于参考信息回答用户问题。"""
        
        messages = [{"role": "user", "content": user_content}]
        response = self.chat(messages, system_prompt, temperature=0.5)
        
        return {
            "answer": response,
            "confidence": 0.8 if context else 0.5
        }
