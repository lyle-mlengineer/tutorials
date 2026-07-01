const imageTagsInput = document.getElementById('imageTagsInput');
const imageTagsList = document.getElementById('imageTagsList');
const imageTags = document.querySelectorAll('.image-tag');
const tagsList = document.querySelector('.image-container__image-tags');

const fileList = document.querySelector(".file-list");
const fileBrowseButton = document.querySelector(".file-browse-button");
const fileBrowseInput = document.querySelector(".file-browse-input");
const fileUploadBox = document.querySelector(".file-upload-box");
const fileCompletedStatus = document.querySelector(".file-completed-status");

const uploadModal = document.querySelector('.upload-modal');

let totalFiles = 0;
let completedFiles = 0;

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

// Function to create HTML for each file item
const createFileItemHTML = (file, uniqueIdentifier) => {
    // Extracting file name, size, and extension
    const {name, size} = file;
    const extension = name.split(".").pop();
    const formattedFileSize = size >= 1024 * 1024 ? `${(size / (1024 * 1024)).toFixed(2)} MB` : `${(size / 1024).toFixed(2)} KB`;
    // Generating HTML for file item
    return `<li class="file-item" id="file-item-${uniqueIdentifier}">
                <div class="file-extension">${extension}</div>
                <div class="file-content-wrapper">
                <div class="file-content">
                    <div class="file-details">
                    <h5 class="file-name">${name}</h5>
                    <div class="file-info">
                        <small class="file-size">0 MB / ${formattedFileSize}</small>
                        <small class="file-divider">•</small>
                        <small class="file-status">Uploading...</small>
                    </div>
                    </div>
                    <button class="cancel-button">
                    <i class="bx bx-x"></i>
                    </button>
                </div>
                <div class="file-progress-bar">
                    <div class="file-progress"></div>
                </div>
                </div>
            </li>`;
}
// Function to handle file uploading
const handleFileUploading = (file, uniqueIdentifier) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);
    // Adding progress event listener to the ajax request
    xhr.upload.addEventListener("progress", (e) => {
        // Updating progress bar and file size element
        const fileProgress = document.querySelector(`#file-item-${uniqueIdentifier} .file-progress`);
        const fileSize = document.querySelector(`#file-item-${uniqueIdentifier} .file-size`);
        // Formatting the uploading or total file size into KB or MB accordingly
        const formattedFileSize = file.size >= 1024 * 1024  ? `${(e.loaded / (1024 * 1024)).toFixed(2)} MB / ${(e.total / (1024 * 1024)).toFixed(2)} MB` : `${(e.loaded / 1024).toFixed(2)} KB / ${(e.total / 1024).toFixed(2)} KB`;
        const progress = Math.round((e.loaded / e.total) * 100);
        fileProgress.style.width = `${progress}%`;
        fileSize.innerText = formattedFileSize;
    });
    // Opening connection to the server API endpoint "api.php" and sending the form data
    xhr.open("POST", "http://0.0.0.0:8000/files/upload", true);
    xhr.send(formData);
    return xhr;
}
// Function to handle selected files
const handleSelectedFiles = ([...files]) => {
    if(files.length === 0) return; // Check if no files are selected
    totalFiles += files.length;
    files.forEach((file, index) => {
        const uniqueIdentifier = Date.now() + index;
        const fileItemHTML = createFileItemHTML(file, uniqueIdentifier);
        // Inserting each file item into file list
        fileList.insertAdjacentHTML("afterbegin", fileItemHTML);
        const currentFileItem = document.querySelector(`#file-item-${uniqueIdentifier}`);
        const cancelFileUploadButton = currentFileItem.querySelector(".cancel-button");
        const xhr = handleFileUploading(file, uniqueIdentifier);
        // Update file status text and change color of it 
        const updateFileStatus = (status, color) => {
            currentFileItem.querySelector(".file-status").innerText = status;
            currentFileItem.querySelector(".file-status").style.color = color;
        }
        xhr.addEventListener("readystatechange", () => {
            // Handling completion of file upload
            if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                completedFiles++;
                cancelFileUploadButton.remove();
                updateFileStatus("Completed", "#00B125");
                fileCompletedStatus.innerText = `${completedFiles} / ${totalFiles} files completed`;
            }
        });
        // Handling cancellation of file upload
        cancelFileUploadButton.addEventListener("click", () => {
            xhr.abort(); // Cancel file upload
            updateFileStatus("Cancelled", "#E3413F");
            cancelFileUploadButton.remove();
        });
        // Show Alert if there is any error occured during file uploading
        xhr.addEventListener("error", () => {
            updateFileStatus("Error", "#E3413F");
            alert("An error occurred during the file upload!");
        });
    });
    fileCompletedStatus.innerText = `${completedFiles} / ${totalFiles} files completed`;
    // uploadModal.classList.add('show');
}
// Function to handle file drop event
fileUploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    handleSelectedFiles(e.dataTransfer.files);
    fileUploadBox.classList.remove("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Drag files here or";
});
// Function to handle file dragover event
fileUploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    fileUploadBox.classList.add("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Release to upload or";
});
// Function to handle file dragleave event
fileUploadBox.addEventListener("dragleave", (e) => {
    e.preventDefault();
    fileUploadBox.classList.remove("active");
    fileUploadBox.querySelector(".file-instruction").innerText = "Drag files here or";
});
fileBrowseInput.addEventListener("change", (e) => handleSelectedFiles(e.target.files));
fileBrowseButton.addEventListener("click", () => fileBrowseInput.click());


function closeFileUploadModal(){
    uploadModal.classList.remove('show');
}

function openFileUploadModal(){
    uploadModal.classList.add('show');
}