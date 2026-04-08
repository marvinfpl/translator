from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from model.translator import translator_model, audio_to_text, text_to_audio, convert_webm_to_wav, convert_flac_to_wav
import uvicorn
import os
import logging
from config import AUDIO_DIR

logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s.')
log = logging.getLogger('server.log')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/logger')
async def logger(request: Request):
    response = await request.json()
    text = response['log']
    log_type = response['type']

    if log_type == 'info':
        log.info(text)
    elif log_type == 'debug':
        log.debug(text)
    elif log_type == 'warning':
        log.warning(text)
    elif log_type == 'error':
        log.error(text)
    elif log_type == 'critical':
        log.critical(text)
    else:
        return {'status': 'log type is not recognized'}

    return {'status': 'log registered'}

@app.get('/jarvis', response_class=HTMLResponse)
async def render_jarvis():
    with open('main.html') as f:
        return f.read()
    
app.post('/audio_test')
async def audio_test():
    output_wav = AUDIO_DIR / 'test.wav'
    test_flac = AUDIO_DIR / 'test/121123/84-121123-0000.flac'

    convert_flac_to_wav(test_flac, output_wav)

    try:
        text = audio_to_text(output_wav)
        translation = translator_model(text)

        output_path = AUDIO_DIR / 'output.wav'
        text_to_audio(translation, output_path)

    except Exception as e:
        raise e 


    return {'text': translation, 'audio_url': output_path}
    
@app.post('/audio_translate')
async def audio_translate(file: UploadFile = File(...)):
    input_webm = AUDIO_DIR / 'input.webm'
    output_wav = AUDIO_DIR / 'input.wav'
    
    with open(input_webm, 'wb') as buffer:
        buffer.write(await file.read())
    
    log.info('input.webm has been written')

    if os.path.getsize(input_webm) == 0:
        log.error('input.webm is empty')
        return {'error': 'empty file'}

    convert_webm_to_wav(input_webm, output_wav)
    log.info('input.wav has been written')

    try:
        text = audio_to_text(output_wav)
        translation = translator_model(text)

        log.info(f'text: {text}, translation: {translation}')

        output_path = AUDIO_DIR / 'output.wav'
        text_to_audio(translation, output_path)

        log.info('text to audio is done')

    except Exception as e:
        log.error(f'pipeline error: {e}')
        raise
    
    return {'text': translation, 'audio_url': output_path}


@app.delete('/delete_audio')
async def audio_delete():
    path = AUDIO_DIR / 'output.wav'
    if os.path.exists(path):
        os.remove(path)
    return {"status": "deleted"}

@app.post('/written_translate')
async def written_translate(request: Request):
    response = await request.json()
    text = response['text'] 

    translation = translator_model(text)

    return {'text': translation}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)