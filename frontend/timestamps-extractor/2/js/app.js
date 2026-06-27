const typeDropdown = document.querySelector("#typeDropdown");
const input = document.querySelector("#linkInput");

typeDropdown.addEventListener('change', updateLinkText);

function updateLinkText(event){
    const selectedOption = event.target.value;
    console.log(selectedOption);
    input.setAttribute('placeholder', selectedOption);
}

