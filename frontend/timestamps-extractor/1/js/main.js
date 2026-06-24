const API_KEY = '1234'; // Paste your API Key
const API_URL = 'http://0.0.0.0:8002/api/v1/extract';

const timestampsPre = document.getElementById('timestampsPre');
const imageResult = document.getElementById('imageResult');

function extractTimestamps(){
    const urlInput = document.getElementById('videoUrl').value.trim();

    if(!urlInput){
        alert('Please enter a YouTube video URL.');
        return
    }

    const formData = new FormData();
    formData.append('videourl', urlInput);

    fetch(API_URL, {
        method: 'POST',
        headers: {
            'X-API-KEY': API_KEY,
        },
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            const timestamps = data.timestamps;
            console.log(timestamps);
            imageResult.src = data.thumbnail_url; // Set the thumbnail image
            timestampsPre.textContent = JSON.stringify(data.timestamps, null, 2); // Display timestamps in the pre element
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function copyTimestamps(){
    const timestampsText = timestampsPre.textContent;

    navigator.clipboard.writeText(timestampsText)
    .then(() => {
        alert('Timestamps copied to clipboard!');
    })
    .catch(err => {
        console.error('Failed to copy timestamps: ', err);
    });
}

function downloadTimestamps() {
    const timestampsText = timestampsPre.textContent;
    const blob = new Blob([timestampsText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'timestamps.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}