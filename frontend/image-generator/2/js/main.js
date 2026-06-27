const API_KEY = '12345'; // Paste your API Key
const API_URL = 'http://0.0.0.0:8000/generate-image';

const imageContainer = document.getElementById('imageContainer');
const imageResultElement = document.getElementById('imageResult');

// Function to generate the image
function generateImage() {

    setLoadingState(true)
    setErrorState(false)

    fetch(API_URL, {
        method: 'GET',
        headers: {
            'X-API-KEY': API_KEY,
        }
    })
        .then((response) => {
            if (!response.ok) {
                console.log('Network response was not ok');
                setLoadingState(false);
                setErrorState(true)
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then((blob) => {
            const url = URL.createObjectURL(blob);
            imageResultElement.src = url;
            setLoadingState(false);
        })
        .catch((error) => {
            console.error(error);
            // setLoadingState(false);
            // setErrorState(true);
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

function setErrorState(isError) {
    if(isError){
        imageResultElement.style.display = 'none';
        console.log('error');
        imageContainer.classList.add('error');
    }else{
        imageResultElement.style.display = 'block';
        imageContainer.classList.remove('error');
    }
}

function downloadImage() {
    const imageUrl = imageResultElement.src;
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = 'image.png';
    link.click();
}