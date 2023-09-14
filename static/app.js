URL = window.URL || window.webkitURL;
var gumStream;
var rec;
var input;

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

recordButton.addEventListener("click", startRecording);

var formdata = new FormData();
var index = 0;

function startRecording() {
    var constraints = {
        audio: true,
        video: false
    }

    recordButton.disabled = true;
    stopButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        gumStream = stream;
        input = audioContext.createMediaStreamSource(stream);
        rec = new Recorder(input, {
            numChannels: 1
        })

        rec.record()
    }).catch(function (err) {

        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}

function sendRecording() {
    stopButton.disabled = true;
    recordButton.disabled = false;

    rec.stop();
    gumStream.getAudioTracks()[0].stop();

    rec.exportWAV(saveVoice);
}

function saveVoice(blob) {
    var reader = new window.FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function () {
        base64 = reader.result.toString();
        
        base64 += "=".repeat(base64%4);

        if (formdata.has("voice"))
            formdata.set("voice", base64)
        else
            formdata.append("voice", base64);
        alert('Record saved successfully!');
    }
}

function stopRecording() {
    stopButton.disabled = true;
    recordButton.disabled = false;
    
    rec.stop();
    gumStream.getAudioTracks()[0].stop();

    rec.exportWAV(createSelection);
}

function createSelection(blob) {
    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    var trash = document.createElement('button');

    au.controls = true;
    au.src = url;
    au.className = "align-text-bottom";

    li.style.color = "transparent";

    trash.innerText = "🗑";
    trash.className = "btn btn-light btn-lg align-text-bottom mx-2";


    stopButton.disabled = true;
    recordButton.disabled = true;
    
    li.className = "my-5 col-md-12 text-center";
    li.appendChild(au);
    li.appendChild(trash);
    li.id = "voice-" + index.toString();
    trash.addEventListener("click", (e) => {index--; stopButton.disabled = false; recordButton.disabled = false; formdata.delete("voice"); e.target.parentNode.remove();});

    document.getElementById("recordingsList").appendChild(li);
    index++;

    saveVoice(blob);
}