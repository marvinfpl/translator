const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
    btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

const record = document.getElementById('record');
const audioPlayback = document.getElementById("audioPlayback");
let audioChunks = [];
let mediaRecorder = MediaRecorder();
record.addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable(event => {
            let arrayBuffer = event.data.arrayBuffer();
            audioChunks.push(arrayBuffer);
        })
    } else {
        mediaRecorder.stop();
        const blob = Blob('blob', audioChunks, )
        const response = await fetch('/audio', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: blob,
        });

        const data = await response.json();
        document.getElementById("debug").innerText = "Translation: " + data.translation;

        const audioURL = URL.createObjectURL(blob)
        audioPlayback.src = audioURL;
        audioPlayback.display = "block";
    }
});