import os
import logging
import tempfile
from openai import OpenAI
from flask import current_app
import boto3
from botocore.exceptions import NoCredentialsError
import hashlib

class TTSService:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
        self.model = 'tts-1'  # or 'tts-1-hd' for higher quality
        
        # Setup S3/Wasabi for audio storage
        self.s3_client = None
        if all([
            os.environ.get('WASABI_ACCESS_KEY'),
            os.environ.get('WASABI_SECRET_KEY'),
            os.environ.get('WASABI_ENDPOINT'),
            os.environ.get('WASABI_BUCKET')
        ]):
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=os.environ.get('WASABI_ENDPOINT'),
                    aws_access_key_id=os.environ.get('WASABI_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('WASABI_SECRET_KEY'),
                    region_name=os.environ.get('WASABI_REGION', 'us-east-1')
                )
                self.bucket_name = os.environ.get('WASABI_BUCKET')
            except Exception as e:
                logging.warning(f"Failed to initialize S3 client: {e}")

    def optimize_text_for_speech(self, text):
        """
        Optimize text for better speech synthesis since OpenAI TTS doesn't support SSML.
        Uses punctuation and formatting for natural pauses and flow.
        """
        if not text or not text.strip():
            return ""
            
        # Clean up the text
        optimized = text.strip()
        
        # Add chapter breaks with longer pauses
        optimized = optimized.replace('\n\n\n', '.\n\n')
        
        # Ensure proper sentence endings
        optimized = optimized.replace('\n', '. ')
        
        # Add pauses after chapter markers
        optimized = optimized.replace('Chapter ', '... Chapter ')
        
        # Ensure proper punctuation for natural pauses
        lines = optimized.split('. ')
        lines = [line.strip() + '.' if line.strip() and not line.strip().endswith(('.', '!', '?')) else line.strip() for line in lines]
        optimized = ' '.join(lines)
        
        return optimized

    def generate_audio(self, text, voice='alloy', project_id=None, chapter_id=None):
        """
        Generate audio from text using OpenAI TTS API
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text content is required for audio generation")
            
            if voice not in self.voices:
                voice = 'alloy'  # Default voice
            
            # Optimize text for better speech synthesis
            optimized_text = self.optimize_text_for_speech(text)
            
            # Generate audio using OpenAI TTS
            logging.info(f"Generating audio with voice '{voice}' for {len(optimized_text)} characters")
            
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=optimized_text,
                response_format='mp3'
            )
            
            # Create a unique filename
            text_hash = hashlib.md5(optimized_text.encode()).hexdigest()[:8]
            filename = f"audio_{project_id}_{chapter_id}_{text_hash}.mp3" if chapter_id else f"audio_{project_id}_{text_hash}.mp3"
            
            # Save to temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Upload to S3/Wasabi if configured
            audio_url = None
            if self.s3_client:
                try:
                    s3_key = f"audio/{filename}"
                    self.s3_client.upload_file(temp_file_path, self.bucket_name, s3_key)
                    audio_url = f"{os.environ.get('WASABI_ENDPOINT')}/{self.bucket_name}/{s3_key}"
                    logging.info(f"Audio uploaded to S3: {audio_url}")
                except Exception as e:
                    logging.error(f"Failed to upload to S3: {e}")
            
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            return {
                'success': True,
                'audio_url': audio_url,
                'filename': filename,
                'duration_estimate': len(optimized_text) / 150,  # Rough estimate: 150 chars per minute
                'voice': voice,
                'text_length': len(optimized_text)
            }
            
        except Exception as e:
            logging.error(f"TTS generation error: {e}")
            return {
                'success': False,
                'error': 'Failed to generate audio. Please try again later.'
            }

    def get_available_voices(self):
        """Get list of available voices"""
        return self.voices

    def estimate_cost(self, text):
        """
        Estimate cost for TTS generation
        OpenAI TTS-1: $15.00 per 1M characters
        """
        if not text:
            return 0
        
        char_count = len(text)
        cost_per_char = 15.00 / 1_000_000  # $15 per million characters
        estimated_cost = char_count * cost_per_char
        
        return {
            'character_count': char_count,
            'estimated_cost_usd': round(estimated_cost, 4),
            'estimated_duration_minutes': char_count / 150  # Rough estimate
        }

# Global TTS service instance
tts_service = TTSService()