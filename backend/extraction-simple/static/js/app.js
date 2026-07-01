let API_URL = "http://0.0.0.0:8000";
const API_KEY = "1234";

const typeDropdown = document.querySelector("#typeDropdown");
const input = document.querySelector("#linkInput");
const extractionModal = document.querySelector(".extraction-modal");
const formContainer = document.querySelector(".form-container");
const datasetCreationModal = document.querySelector(".dataset-creation-modal");
const imageResult = document.querySelector(".image-container__image-result-image");
const datasetDropdown = document.querySelector("#datasetDropdown");

typeDropdown.addEventListener('change', updateLinkText);

function updateLinkText(event){
    const selectedOption = event.target.value;
    if(selectedOption === 'video'){
        input.setAttribute('placeholder', 'Enter YouTube video URL...');
    }else if(selectedOption === 'playlist'){
        input.setAttribute('placeholder', 'Enter YouTube playlist URL...');
    }else{
        input.setAttribute('placeholder', 'Enter YouTube channel ID...');
    }
}

function setLoadingState(isLoading) {
    if(isLoading){
        formContainer.classList.add('show');
    }else{
        formContainer.classList.remove('show');
    }
}

function openExtractionModal(){
    extractionModal.style.display = 'flex';
}

function closeExtractionModal(){
    extractionModal.style.display = 'none';
    window.location.reload();
}

function findResource(){
    const linkInput = document.getElementById('linkInput').value.trim();
    if(linkInput === ''){
        alert('Please enter a valid video url or playlist url or channel id!');
        return
    }
    setLoadingState(true);
    // setTimeout(() => {
    //     setLoadingState(false);
    // }, 1000);
    findVideo();
    openExtractionModal();
}

function findVideo(){
    const linkInput = document.getElementById('linkInput').value.trim();
    const type = document.getElementById('typeDropdown').value;
    const dataset = document.getElementById('dataset').value;
    let body;
    
    if(type === 'video'){
        API_URL += '/extraction/video';
        body = JSON.stringify({url: linkInput, dataset: dataset});
        console.log(linkInput);
        console.log(dataset);
        console.log(API_URL);
    }else if(type === 'playlist'){
        API_URL += '/extraction/playlist';
        body = JSON.stringify({url: linkInput, dataset: dataset});
        console.log(linkInput);
        console.log(API_URL);
    }else{
        API_URL += '/extraction/channel';
        body = JSON.stringify({id: linkInput, dataset: dataset});
        console.log(linkInput);
        console.log(API_URL);
    }

    fetch(API_URL, {
        method: 'POST',
        headers: {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json'
        },
        body: body,
    })
        .then((response) => {
            if (!response.ok) {
                console.log('Network response was not ok');
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            console.log('Success:', data);
            console.log(data);
            imageResult.src = data.thumbnail_url;
        })
        .catch((error) => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function showDatasetCreationModel(){
    datasetCreationModal.style.display = 'flex';
}

function closeDatasetCreationModel(){
    datasetCreationModal.style.display = 'none';
}

function createDataset(){
    const nameInput = document.getElementById('nameInput').value.trim();
    if(nameInput === ''){
        alert('Please enter a valid dataset name!');
        return
    }
    const descriptionInput = document.getElementById('descriptionInput').value.trim();
    console.log('create dataset');
    console.log(nameInput);
    console.log(descriptionInput);
    API_URL += '/dataset';
    fetch(API_URL, {
        method: 'POST',
        headers: {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name: nameInput, description: descriptionInput}),
    })
        .then((response) => {
            if (!response.ok) {
                console.log('Network response was not ok');
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            console.log(data);
        })
        .catch((error) => {
            console.error('There was a problem with the fetch operation:', error);
        });
    closeDatasetCreationModel();
    window.location.reload();
}