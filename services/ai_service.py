import os
import json
import logging
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_content_suggestions(text, suggestion_type='improve'):
    """
    Get AI-powered content suggestions for audiobook manuscripts
    """
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    try:
        if suggestion_type == 'improve':
            prompt = f"""
            As an expert audiobook editor, please improve the following text for better readability and engagement when spoken aloud.
            Focus on:
            - Natural speech patterns and flow
            - Clear transitions between ideas
            - Engaging narrative voice
            - Proper pacing for audio consumption
            
            Original text: {text}
            
            Please provide your improved version and explain the key changes made.
            Respond in JSON format with 'improved_text' and 'explanation' fields.
            """
        elif suggestion_type == 'expand':
            prompt = f"""
            As an audiobook content expert, please expand the following text with additional details, examples, or narrative elements that would enhance the listening experience.
            
            Original text: {text}
            
            Provide an expanded version that maintains the original meaning while adding value for audio listeners.
            Respond in JSON format with 'expanded_text' and 'additions' fields.
            """
        elif suggestion_type == 'summarize':
            prompt = f"""
            Please create a concise summary of the following text that captures the key points while being suitable for audiobook format.
            
            Original text: {text}
            
            Provide a summary that maintains the essential information in a clear, spoken-friendly format.
            Respond in JSON format with 'summary' and 'key_points' fields.
            """
        else:
            raise ValueError(f"Invalid suggestion type: {suggestion_type}")
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert audiobook editor and content creator. Provide helpful, professional suggestions that enhance the listening experience."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        result = json.loads(response.choices[0].message.content or '{}')
        return result
        
    except Exception as e:
        logging.error(f"AI suggestions error: {e}")
        raise Exception("Failed to generate AI suggestions. Please check your API configuration and try again.")

def improve_text(text):
    """
    Specifically improve text for audiobook narration
    """
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    try:
        prompt = f"""
        Improve this text specifically for audiobook narration. Focus on:
        1. Natural speech rhythm and flow
        2. Clear pronunciation cues
        3. Appropriate pacing markers
        4. Engaging storytelling elements
        5. Listener-friendly language
        
        Text to improve: {text}
        
        Provide the improved text along with specific notes about changes made for audio performance.
        Respond in JSON format with 'improved_text', 'narration_notes', and 'key_improvements' fields.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional audiobook editor specializing in optimizing text for spoken performance. Consider pacing, clarity, and listener engagement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1200
        )
        
        result = json.loads(response.choices[0].message.content or '{}')
        return result
        
    except Exception as e:
        logging.error(f"Text improvement error: {e}")
        raise Exception("Failed to improve text. Please check your API configuration and try again.")

def analyze_audiobook_readiness(content):
    """
    Analyze content for audiobook production readiness
    """
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    try:
        prompt = f"""
        Analyze this audiobook manuscript for production readiness. Evaluate:
        1. Narrative flow and pacing
        2. Clarity for spoken delivery
        3. Chapter structure and transitions
        4. Pronunciation challenges
        5. Overall listening experience
        
        Content: {content[:3000]}...
        
        Provide detailed feedback and a readiness score (1-10).
        Respond in JSON format with 'readiness_score', 'strengths', 'areas_for_improvement', and 'recommendations' fields.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an audiobook production specialist who evaluates manuscripts for recording readiness."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content or '{}')
        return result
        
    except Exception as e:
        logging.error(f"Readiness analysis error: {e}")
        raise Exception("Failed to analyze content. Please check your API configuration and try again.")
