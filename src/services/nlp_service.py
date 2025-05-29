import pytesseract
from PIL import Image
import whisper
import re
from typing import Dict, Any, Optional
import tempfile
import os

class NLPService:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
    
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        """Extract amount and payment method from an image using OCR."""
        try:
            # Open and process image
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            # Extract amount using regex
            amount_pattern = r'\$?\d+(?:\.\d{2})?'
            amounts = re.findall(amount_pattern, text)
            amount = float(amounts[0].replace('$', '')) if amounts else None
            
            # Look for common payment methods
            payment_methods = ['cash', 'credit', 'debit', 'transfer', 'paypal']
            found_method = None
            for method in payment_methods:
                if method.lower() in text.lower():
                    found_method = method
                    break
            
            return {
                "amount": amount,
                "payment_method": found_method,
                "full_text": text
            }
        except Exception as e:
            return {
                "error": str(e),
                "amount": None,
                "payment_method": None,
                "full_text": None
            }
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file to text using Whisper."""
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_path)
            
            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": None,
                "language": None,
                "segments": None
            } 