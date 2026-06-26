const API_URL = "http://0.0.0.0:8000/images/label/";
const API_KEY = "1234";

const imageTagsInput = document.getElementById('imageTagsInput');
const imageTagsList = document.getElementById('imageTagsList');
const imageTags = document.querySelectorAll('.image-tag');
const tagsList = document.querySelector('.image-container__image-tags');

// Show dropdown list when the input field is focused
imageTagsInput.addEventListener('focus', () => {
  imageTagsList.classList.remove('hidden');
});

// // Hide list if the input field is not focused
// imageTagsInput.addEventListener('blur', () => {
//   imageTagsList.classList.add('hidden');
// });

// Update input value on selection and hide list
imageTags.forEach(imageTag => {
  imageTag.addEventListener('click', (e) => {
    imageTagsInput.value = e.target.textContent;
    imageTagsList.classList.add('hidden');
  });
});

// Filter options as the user types
imageTagsInput.addEventListener('input', (e) => {
  const filter = e.target.value.toLowerCase();
  let hasVisibleOptions = false;

  imageTags.forEach(imageTag => {
    const text = imageTag.textContent.toLowerCase();
    if (text.includes(filter)) {
      imageTag.classList.remove('hidden');
      hasVisibleOptions = true;
    } else {
      imageTag.classList.add('hidden');
    }
  });

  // Hide the list container completely if no items match
  if (hasVisibleOptions) {
    imageTagsInput.classList.remove('hidden');
  } else {
    imageTagsInput.classList.add('hidden');
  }
});

// Close dropdown if user clicks completely outside of the element
document.addEventListener('click', (e) => {
  if (!e.target.closest('.tags')) {
    imageTagsList.classList.add('hidden');
  }
});


function openTagModal(){
    const tagModal = document.querySelector('.tag-modal');
    tagModal.classList.add('show');
}

function closeTagModal(){
    const tagModal = document.querySelector('.tag-modal');
    tagModal.classList.remove('show');
}

function addTag(){
    const selectedTag = document.getElementById('imageTagsInput').value;
    console.log(selectedTag);
    let currentTags = []
    const imageTags = document.querySelectorAll(".image-tags__tag")
    imageTags.forEach((imageTag) => {
        currentTags.push(imageTag.textContent.toLowerCase().trim());
    })
    if(!currentTags.includes(selectedTag.toLowerCase())){
        const newTag = document.createElement('div');
        newTag.classList.add('image-tags__tag');
        newTag.textContent = selectedTag;
        const tagsList = document.querySelector('.image-container__image-tags');
        tagsList.appendChild(newTag);
    }
    const tagModal = document.querySelector('.tag-modal');
    tagModal.classList.remove('show');
}

//delete tag
tagsList.addEventListener('click', (e) => {
    if (e.target.classList.contains('image-tags__tag')) {
        e.target.remove();
    }
})

function submit(){
  const prompt = document.getElementById('prompt').value;
  if (prompt === '') {
    alert('Please enter a valid image description!');
    return;
  }
  const gender = document.getElementById('dropdownGender').value;
  const imageId = document.querySelector('.image-container__image-result').getAttribute('data-image-id');
  const rawTags = document.querySelectorAll('.image-tags__tag');
  let tags = [];
  rawTags.forEach((rawTag) => {
    tags.push(rawTag.textContent.trim());
  })
  fetch(API_URL + imageId, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': API_KEY
    },
    body: JSON.stringify({description: prompt, gender: gender, tags: tags}),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
    window.location.reload();
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}