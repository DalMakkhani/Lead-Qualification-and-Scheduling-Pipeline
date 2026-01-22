import os
import sys
import time
import vlc
import re
import tempfile
import atexit
import json
import requests
from groq import Groq
from dotenv import load_dotenv
import shutil
import pyaudio
import threading
import wave
import io
import webrtcvad
from database import MongoDBManager

# Load environment variables
load_dotenv()

# Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
DEEPGRAM_VOICE = "aura-luna-en"

# Audio configuration
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000  # 0.5 seconds of audio

# Lead data storage: {lead_name: json_data}
lead_data_storage = {}

# Temp directory for audio files
TEMP_DIR = tempfile.mkdtemp(prefix="bot_audio_")

def cleanup_temp_dir():
    """Clean up temp directory on exit"""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

atexit.register(cleanup_temp_dir)

def load_system_prompt(lead_name: str = "", company_name: str = "") -> str:
    """Load system prompt from prompt.md and inject lead_name and company_name"""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # Replace placeholders if provided
    if lead_name:
        prompt = prompt.replace("{lead_name}", lead_name)
    if company_name:
        prompt = prompt.replace("{company_name}", company_name)
    
    return prompt

def deepgram_tts_to_wav(text: str, output_file: str, return_audio_data: bool = False):
    """Generate speech using Deepgram Aura"""
    # Add pause before question marks for better intonation
    if text.strip().endswith('?'):
        text = text.strip()[:-1] + '...?'
    
    url = f"https://api.deepgram.com/v1/speak?model={DEEPGRAM_VOICE}"
    headers = {
        "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    
    audio_content = response.content
    
    with open(output_file, "wb") as f:
        f.write(audio_content)
    
    if return_audio_data:
        return audio_content
    return output_file

def play_audio(path: str):
    """Play audio file and wait for completion"""
    player = vlc.MediaPlayer(path)
    player.play()

    while player.get_state() not in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
        time.sleep(0.05)
    
    player.stop()
    player.release()
    time.sleep(0.1)

def clean_text_for_tts(text: str) -> str:
    """Remove markdown, prefixes, and stage directions"""
    text = re.sub(r'\([^)]*\)', '', text)  # Remove (stage directions)
    text = re.sub(r'\[[^\]]*\]', '', text)  # Remove [notes]
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove *italic*
    text = re.sub(r'^(\*\*)?Priya(\*\*)?:\s*', '', text, flags=re.IGNORECASE)  # Remove "Priya:"
    text = re.sub(r'^(Bot|Assistant|AI):\s*', '', text, flags=re.IGNORECASE)  # Remove other prefixes
    text = re.sub(r'\.\s+', '.', text)  # Remove space after period for natural TTS flow
    text = re.sub(r'\s+', ' ', text)  # Clean whitespace
    return text.strip()

def is_json_output(text: str) -> bool:
    """Check if text contains JSON qualification data"""
    # Check for JSON code blocks
    if '```json' in text.lower() or ('```' in text and '{' in text):
        return True
    # Check if text contains JSON object (can be anywhere in text)
    if '{' in text and '}' in text:
        # Try to extract and parse JSON
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                json.loads(json_match.group(0))
                return True
        except:
            pass
    return False

def extract_and_store_json(text: str, lead_name: str, conversation_history: list, 
                          db_manager: MongoDBManager, audio_file_path: str = None):
    """Extract JSON data and store in MongoDB with full conversation history and call recording"""
    try:
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            json_data = json.loads(json_match.group(0))
            
            # Add lead_name to JSON if not present
            if "lead_name" not in json_data:
                json_data["lead_name"] = lead_name or "unknown_lead"
            
            # Store in MongoDB with conversation history and audio recording
            db_manager.store_lead(json_data, conversation_history, audio_file_path)
            
            # Also keep in memory for backward compatibility
            lead_data_storage[lead_name or "unknown_lead"] = json_data
            print(f"\n[Data stored in MongoDB for {lead_name or 'unknown_lead'}]")
            return True
    except Exception as e:
        print(f"\n[Storage error: {e}]")
    return False

def listen_for_speech(timeout: int = 30, return_audio: bool = False) -> tuple:
    """Listen to microphone and transcribe speech using Deepgram STT (REST API) with WebRTC VAD
    
    Args:
        timeout: Maximum time to wait for speech (seconds)
        return_audio: If True, return (transcript, audio_frames) tuple
    
    Returns:
        If return_audio=True: (transcript, audio_frames) tuple
        Otherwise: transcript string
    """
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_key:
        raise RuntimeError("Set DEEPGRAM_API_KEY")
    
    try:
        # Initialize WebRTC VAD (aggressive mode 3 = most aggressive)
        vad = webrtcvad.Vad(2)  # Mode 2 = balanced (0=least aggressive, 3=most)
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=AUDIO_FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("[Listening... Speak now]")
        
        # VAD parameters
        frames = []
        start_time = time.time()
        speech_frames = 0
        silence_frames = 0
        silence_threshold = 2  # 1 second of silence (0.5s per chunk * 2 = 1s)
        speech_detected = False
        min_speech_frames = 2  # Need 1 second of speech before considering it real
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"\r[Timeout after {elapsed:.1f}s]" + " " * 30)
                break
            
            # Read audio chunk
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(audio_data)
            
            # Check if this frame contains speech
            # WebRTC VAD requires 10, 20, or 30ms frames at 8000, 16000, 32000, or 48000 Hz
            # Our CHUNK is 8000 samples at 16000 Hz = 500ms, so we need to split it
            is_speech = False
            frame_length = 480  # 30ms at 16000 Hz
            
            for i in range(0, len(audio_data), frame_length * 2):  # *2 because 16-bit samples
                frame = audio_data[i:i + frame_length * 2]
                if len(frame) == frame_length * 2:
                    try:
                        if vad.is_speech(frame, RATE):
                            is_speech = True
                            break
                    except:
                        pass
            
            if is_speech:
                speech_frames += 1
                silence_frames = 0
                
                if not speech_detected and speech_frames >= min_speech_frames:
                    speech_detected = True
                    print(f"\r[Speaking detected... Recording]" + " " * 20, end="", flush=True)
            else:
                if speech_detected:
                    silence_frames += 1
                    
                    # Show progress
                    silence_duration = silence_frames * 0.5
                    print(f"\r[Recording... {silence_duration:.1f}s silence]", end="", flush=True)
                    
                    # Stop if we have enough silence after detecting speech
                    if silence_frames >= silence_threshold:
                        print(f"\r[Speech ended after silence]" + " " * 30)
                        break
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        if not speech_detected:
            print("\n[No speech detected]")
            return ""
        
        print(f"\r[Recording complete - transcribing...]" + " " * 50, end="", flush=True)
        
        # Convert frames to WAV format in memory
        wav_buffer = io.BytesIO()
        wf = wave.open(wav_buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Send to Deepgram REST API
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
        headers = {
            "Authorization": f"Token {deepgram_key}",
            "Content-Type": "audio/wav"
        }
        
        response = requests.post(url, headers=headers, data=wav_buffer.getvalue(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript'].strip()
        
        if transcript:
            print(f"\r[Transcribed: {transcript}]" + " " * 50)
        else:
            print(f"\r[No speech detected]" + " " * 50)
        
        if return_audio:
            return transcript, frames
        return transcript, []
        
    except Exception as e:
        print(f"\n[STT error: {e}]")
        import traceback
        traceback.print_exc()
        if return_audio:
            return "", []
        return "", []

def main(lead_name: str = "", company_name: str = "", voice_mode: bool = False):
    """Main conversation loop
    
    Args:
        lead_name: Optional lead name to personalize the conversation
        company_name: Optional company name (if known)
        voice_mode: If True, use microphone input (STT). If False, use text input
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise RuntimeError("Set GROQ_API_KEY")

    # Initialize MongoDB
    db_manager = MongoDBManager()
    call_start_time = time.time()
    
    # Initialize call recording
    recording_frames = []  # Store all audio frames for full call recording
    recording_active = voice_mode  # Only record in voice mode

    client = Groq(api_key=groq_key)
    
    # Load system prompt with lead name and company
    system_prompt = load_system_prompt(lead_name, company_name)

    history = [{"role": "system", "content": system_prompt}]
    
    if lead_name:
        print(f"Ready. Conversation prepared for lead: {lead_name}")
        if company_name:
            print(f"Company: {company_name}")
    
    if voice_mode:
        print("\n=== VOICE MODE ENABLED ===")
        print("Bot will speak and listen. Say 'goodbye' or 'exit' to end call.\n")
    else:
        print("Type messages. Use /exit to quit.\n")

    # Bot initiates the conversation
    first_turn = True

    while True:
        if first_turn:
            # Pre-generate opening greeting immediately (no LLM wait)
            print("\nBot: ", end="", flush=True)
            if lead_name:
                opening_text = f"Hello, I am Priya. Am I speaking with {lead_name}?"
            else:
                opening_text = "Hello, I am Priya. May I know who I am speaking with?"
            
            print(opening_text)
            
            # Generate audio for opening
            temp_file = os.path.join(TEMP_DIR, "opening_greeting.wav")
            try:
                deepgram_tts_to_wav(opening_text, temp_file)
                
                # Play audio first (blocking)
                play_audio(temp_file)
                os.remove(temp_file)
                
                if voice_mode:
                    # In voice mode: NOW start listening (after audio finished)
                    print()  # New line after audio
                    user_message, audio_frames = listen_for_speech(timeout=15, return_audio=recording_active)
                    recording_frames.extend(audio_frames)  # Add to full recording
                    
                    if not user_message:
                        print("\n[No response detected. Ending call.]")
                        break
                    
                    # Check for exit phrases
                    if any(word in user_message.lower() for word in ['goodbye', 'bye', 'exit', 'hang up', 'end call']):
                        print("\n[Call ended by user]")
                        break
                    
                    print(f"\nYou: {user_message}")
                else:
                    # Text mode: continue to next iteration for user input
                    print()
                    first_turn = False
                    # Add to history
                    history.append({"role": "assistant", "content": opening_text})
                    continue
                    
            except Exception as e:
                print(f"\n[Audio error: {e}]")
                if voice_mode:
                    break
            
            # Add to history as if bot said it
            history.append({"role": "assistant", "content": opening_text})
            print()
            first_turn = False
        else:
            # User's turn to respond
            if voice_mode:
                # Use microphone input with STT
                user_message, audio_frames = listen_for_speech(timeout=15, return_audio=recording_active)
                recording_frames.extend(audio_frames)  # Add to full recording
                
                if not user_message:
                    print("\n[No response detected. Ending call.]")
                    break
                
                # Check for exit phrases
                if any(word in user_message.lower() for word in ['goodbye', 'bye', 'exit', 'hang up', 'end call']):
                    print("\n[Call ended by user]")
                    break
                
                print(f"\nYou: {user_message}")
            else:
                # Use text input
                user = input("You: ").strip()
                if user.lower() == "/exit":
                    break
                if not user:
                    continue
                user_message = user

        history.append({"role": "user", "content": user_message})

        print("\nBot: ", end="", flush=True)
        
        # Collect full response from LLM
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=history,
            temperature=0.4,
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print("\n")
        
        # Check if response contains JSON - don't speak it
        if is_json_output(full_response.strip()):
            # Save full call recording if we have frames
            recording_path = None
            if recording_frames and voice_mode:
                recording_path = os.path.join(TEMP_DIR, f"call_recording_{lead_name}_{int(time.time())}.wav")
                try:
                    import pyaudio
                    audio = pyaudio.PyAudio()
                    wf = wave.open(recording_path, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(recording_frames))
                    wf.close()
                    audio.terminate()
                    print(f"[Call recording saved: {len(recording_frames)} frames]")
                except Exception as e:
                    print(f"[Recording save error: {e}]")
            
            # Store in MongoDB with recording
            extract_and_store_json(full_response.strip(), lead_name, history, db_manager, recording_path)
            print("\n[Qualification complete - JSON data stored in MongoDB, not spoken]")
            
            # Cleanup recording file after upload
            if recording_path and os.path.exists(recording_path):
                try:
                    os.remove(recording_path)
                except:
                    pass
            
            # Close DB connection before exiting
            db_manager.close()
            print("\n[Call ended automatically after qualification]\n")
            break
        else:
            # Split into sentences and generate/play audio sequentially
            sentences = re.split(r'([.!?]+)', full_response)
            sentence_count = 0
            
            i = 0
            while i < len(sentences):
                if i + 1 < len(sentences) and sentences[i+1] in ['.', '!', '?', '..', '...']:
                    sentence = (sentences[i] + sentences[i+1]).strip()
                    i += 2
                else:
                    sentence = sentences[i].strip()
                    i += 1
                
                if sentence and not is_json_output(sentence):
                    clean_sentence = clean_text_for_tts(sentence)
                    if clean_sentence:
                        temp_file = os.path.join(TEMP_DIR, f"temp_audio_{sentence_count}.wav")
                        try:
                            # Get TTS audio and add to recording
                            tts_audio_data = deepgram_tts_to_wav(clean_sentence, temp_file, return_audio_data=voice_mode)
                            if voice_mode and tts_audio_data and recording_active:
                                # Convert bytes to list of bytes for consistency with recording format
                                recording_frames.append(tts_audio_data)
                            play_audio(temp_file)
                            os.remove(temp_file)
                        except Exception as e:
                            print(f"[Audio error: {e}]")
                        sentence_count += 1

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python groqEleveLabsTalker_VAD.py <lead_name> <company_name> [--voice|-v]")
        sys.exit(1)
    
    lead_name = sys.argv[1]
    company_name = sys.argv[2]
    voice_mode = "--voice" in sys.argv or "-v" in sys.argv
    
    main(lead_name, company_name, voice_mode)
