const API_KEY = '1234'; // Paste your API Key
const API_URL = 'http://0.0.0.0:8002/api/v1/extract';

const timestampsPre = document.getElementById('timestampsPre');

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
            timestampsPre.textContent = JSON.stringify(data.timestamps, null, 2); // Display timestamps in the pre element
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}