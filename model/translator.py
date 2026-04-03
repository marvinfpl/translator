from transformers import pipeline, MarianMTModel, MarianTokenizer
import torch
import torchaudio

text2speech = pipeline('text-to-speech', model='facebook/mms-tts-fra')
speech2text = pipeline('automatic-speech-recognition', model='openai/whisper-base')

model_name = 'Helsinki-NLP/opus-mt-en-fr'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)


def audio_to_text(audio_path: str) -> str:
    text = speech2text(audio_path)[0]['text']
    return text
    
def translator_model(text: str) -> str:
    inputs = tokenizer(text, return_tensors='pt')
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)


# output_path = '/audio/audio_trad.wav'
def text_to_audio(text: str, output_path: str) -> None:
    result = text2speech(text)[0]
    audio = result['audio']
    sr = result['sampling_rate']
    
    torchaudio.save(output_path, torch.tensor(audio).unsqueeze(0), sr)

if __name__ == '__main__':
    text = "I will be the next Tony Stark!"
    print(translator_model(text))