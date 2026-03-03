# app/services/transcriber.py
from faster_whisper import WhisperModel
import os
from typing import Dict, List, Tuple

class TranscriberService:
    def __init__(self):
        self.device = "cpu"
        self.model = WhisperModel("small", device=self.device, compute_type="int8")

    def transcribe_file(self, file_path: str) -> Tuple[List[Dict], str, str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Transcribing {file_path}...")
        
        segments, info = self.model.transcribe(file_path, beam_size=5, vad_filter=True)
        
        transcript_results = []
        full_text_parts = []
        
        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }
            transcript_results.append(segment_data)
            full_text_parts.append(segment.text)
        
        full_text = " ".join(full_text_parts)
        
        # Create preview (first 30 words)
        words = full_text.split()
        preview_words = words[:30]
        preview = " ".join(preview_words)
        if len(words) > 30:
            preview += "..."
            
        return transcript_results, full_text, preview