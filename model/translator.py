from transformers import pipeline, MarianMTModel, MarianTokenizer, WhisperFeatureExtractor
import torch
import soundfile as sf
import subprocess
import numpy as np

device = 0 if torch.backends.mps.is_available() else -1

text2speech = pipeline('text-to-speech', model='facebook/mms-tts-fra', device=device)

feature_extractor = WhisperFeatureExtractor(sampling_rate=16000)
speech2text = pipeline('automatic-speech-recognition', model='openai/whisper-base', chunk_length_s=30, device=device, feature_extractor=feature_extractor)

model_name = 'Helsinki-NLP/opus-mt-en-fr'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name).to('mps')


#llm_name = 'mpt-7b-instruct'
#llm = pipeline('text-generation', model=llm_name, device=device)
#answer = llm("", max_length, do_sample=True, device=device)
#answer[0]['generated_text']

def audio_to_text(audio_path: str) -> str:
    text = speech2text(audio_path)['text']
    return text
    
def translator_model(text: str) -> str:
    text = ">>fr<< " + text
    inputs = tokenizer(text, return_tensors='pt').to('mps')
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# output_path = '/audio/audio_trad.wav'
def text_to_audio(text: str, output_path: str) -> None:
    chunks = chunk_text(text)
    audios = []
    sr = None
    for chunk in chunks:
        result = text2speech(chunk)
        audios.append(result['audio'])
        sr = result['sampling_rate']
    audio_concat = np.concatenate(audios)

    sf.write(output_path, audio_concat, sr)

def convert_webm_to_wav(input_path: str, output_path: str) -> None:
    subprocess.run([
        'ffmpeg',
        '-i', input_path,
        '-ar', '16000',    
        '-ac', '1',        
        '-c:a', 'pcm_s16le', 
        output_path
    ], check=True)

def convert_flac_to_wav(input_path: str, output_path: str) -> None:
    subprocess.run([
        'ffmpeg',
        '-i', input_path,
        '-ar', '16000',
        '-ac', '1',
        output_path,
    ], check=True)

def chunk_text(text: str, max_len=200):
    words = text.split()
    chunks = []
    current = []
    for w in words:
        current.append(w)
        if len(''.join(current)) >= max_len:
            chunks.append(''.join(current))
            current = []
    if current:
        chunks.append(''.join(current))
        return chunks

if __name__ == '__main__':
    text = "I will be the next Tony Stark!"

    translated = translator_model(text)
    print('translation: ', translated)

    text_to_audio(translated, 'static/audio/test.wav')