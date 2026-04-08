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
const stopButton = document.getElementById('stopButton');

recordButton.onclick = async () => {

    if (mediaRecorder && mediaRecorder.state === "recording") return;

    if (!stream) {
        stream = await navigator.mediaDevices.getUserMedia({audio: true});
        sendLogs('stream ready: '+ stream, 'debug');
    }

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
        sendLogs('chunk reçu'+ event.data.size , 'debug');
    };

    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm; codecs=opus' });
        sendLogs('blob size: '+ blob.size+ 'blob type: '+ blob.type, 'debug');
        if (blob.size == 0) {
            document.getElementById('debug').innerText = 'No audio captured ...';
        }

        const formData = new FormData();
        formData.append('file', blob, 'audio.webm');

        document.getElementById('debug').innerText = 'Processing translation...';

        const response = await fetch('/audio_translate', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        sendLogs(data, 'debug');

        document.getElementById('debug').innerText = 'Translation: ' + data.text;

        const audioPlayback = document.getElementById('audioPlayback');
        audioPlayback.src = data.audio_url;
        audioPlayback.style.display = 'block';
        audioPlayback.play();
    };

    mediaRecorder.start();
    recordButton.innerText = "Recording...";
};

stopButton.onclick = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        recordButton.innerText = "Record";
        sendLogs('media recorder stopped', 'debug');
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        sendLogs('microphone stopped', 'debug');
    }
};

async function sendLogs(text, log_type) {
    await fetch('/logger', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'log': text, 'type': log_type}),
    });
}