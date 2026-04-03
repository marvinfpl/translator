from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from model.translator import speech2text, text2speech, translator_model
import uvicorn
import shutil
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/jarvis', response_class=HTMLResponse)
async def render_jarvis():
    with open('main.html') as f:
        return f.read()
    
    
@app.post('/audio_translate')
async def audio_translate():
    return {'text': 'actually nothing'}

@app.delete('/delete_audio')
async def audio_delete():
    path = '/static/audio/output.wav'
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