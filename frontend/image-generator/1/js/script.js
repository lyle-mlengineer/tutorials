const API_KEY = ''; // Paste your API Key
const API_URL = 'http://0.0.0.0:8000/generate-image';

const imageContainer = document.getElementById('imageContainer');
const imageResultElement = document.getElementById('imageResult');

// Function to generate the image
function generateImage() {
    const prompt = document.getElementById('prompt').value;
    const size = document.getElementById('dropdownSize').value;
    const color = document.getElementById('dropdownColors').value;
    const format = document.getElementById('dropdownFormats').value;

    // If prompt is empty
    if (prompt === '') {
        alert('Please enter a prompt');
        return;
    }

    setLoadingState(true)

    // Prepare form data for api request
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('size', size);
    formData.append('color', color);
    formData.append('format', format);

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
            return response.blob();
        })
        .then((blob) => {
            const url = URL.createObjectURL(blob);
            const imageElement = document.createElement('img');
            imageElement.src = url;
            imageElement.onload = () => {
                imageContainer.innerHTML = '';
                imageContainer.appendChild(imageElement);
                setLoadingState(false);
            };
        })
        .catch((error) => {
            console.error(error);
            setLoadingState(false);
        });
}

function setLoadingState(isLoading) {
    if(isLoading){
        imageResultElement.style.display = 'none';
        imageContainer.classList.add('loading');
    }else{
        imageResultElement.style.display = 'block';
        imageContainer.classList.remove('loading');
    }
}

function downloadImage() {


}