const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
    btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

const formButton = document.getElementById('formButton');
formButton.addEventListener('click', async () => {

    const debug = document.getElementById('debug');
    const input = document.getElementById('translation')

    if (formButton.innerText === 'Translate' && input.value != '') {

        const response = await fetch('/written_translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'text': input.value}),
        });

        const data = await response.json();
        debug.innerText = data['text'];
        formButton.innerText = 'Clear';

    } else {
        formButton.innerText = 'Translate';
        input.value = '';
        debug.innerText = 'No translation occuring...';
    }
});

let audioChunks = [];
let mediaRecorder;
let stream;

const recordButton = document.getElementById('recordButton');
recordButton.addEventListener('click', async () => {
    if (recordButton.innerText === 'Record') {
        stream = await navigator.mediaDevices.getUserMedia({audio: true});
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable(event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, {type: 'audio/wav'});
            const formData = new FormData();
            formData.append('file', blob, 'audio.wav');
            document.getElementById('debug').innerText = 'Processing translation ...';
            
            const response = await fetch('/audio_translate', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            document.getElementById('debug').innerText = 'Translation: ' + data.text; // debug thing to see if the audio came well

            const audioPlayback = document.getElementById('audioPlayback');
            audioPlayback.src = data.audio_url;
            audioPlayback.style.display = 'block'; // to see if it's there            
            audioPlayback.play();
        };

        mediaRecorder.start();
        recordButton.innerText = 'Stop';
    } else {
        mediaRecorder.stop();
        recordButton.innerText = 'Record';

        await fetch('/delete_audio', {
            method: 'DELETE',
        });

        document.getElementById('debug').innerText = 'No translation occuring ...';
        }
    }
);