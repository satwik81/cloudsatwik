import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import os
import textwrap

def save_tts_chunk(text, filename, voice_id=None, rate=120, volume=1.0):
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)

    engine.save_to_file(text, filename)
    engine.runAndWait()

def save_tts_chunks(text, filename_prefix="chunk", max_chars=5000, voice_id=None):
    chunks = textwrap.wrap(text, max_chars)
    files = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"{filename_prefix}_{i}.wav"
        save_tts_chunk(chunk, chunk_file, voice_id=voice_id)
        files.append(chunk_file)

    return files

def concatenate_audio(files, output_file="output.wav"):
    combined = AudioSegment.empty()

    for file in files:
        segment = AudioSegment.from_file(file)
        combined += segment

    combined.export(output_file, format="wav")

#Fetch available voices and select a male voice
engine = pyttsx3.init()
voices = engine.getProperty('voices')
male_voice_id = None
for voice in voices:
    if "male" in voice.name.lower():
        male_voice_id = voice.id
        break

if not male_voice_id:
    print("Male voice not found, using default voice.")

text = """Hello User., 
Nice meeting You......."""



#Save TTS chunks with larger chunk size
tts_files = save_tts_chunks(text, max_chars=5000, voice_id=male_voice_id)

#Concatenate audio files
output_file = "old_man_voice.wav"
concatenate_audio(tts_files, output_file)

#Check if the file was saved successfully
if os.path.exists(output_file):
    print(f"File {output_file} created successfully.")
else:
    print(f"Failed to create file {output_file}.")
    exit()

#Load the concatenated WAV file
try:
    sound = AudioSegment.from_file(output_file)
    print(f"Loaded {output_file} successfully.")
except Exception as e:
    print(f"Error loading {output_file}: {e}")
    exit()
    