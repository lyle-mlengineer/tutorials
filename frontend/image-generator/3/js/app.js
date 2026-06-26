const imageTagsInput = document.getElementById('imageTagsInput');
const imageTagsList = document.getElementById('imageTagsList');
const imageTags = document.querySelectorAll('.image-tag');

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