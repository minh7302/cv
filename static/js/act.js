function displayImage() {
  var input = document.getElementById('imageInput');
  var uploadedImage = document.getElementById('uploadedImage');
  
  var reader = new FileReader();
  reader.onload = function (e) {
      uploadedImage.src = e.target.result;
      updateDisplayedImage();  // Update the displayed image when a new image is uploaded
      
      // Send the uploaded file to the server
      var formData = new FormData();
      formData.append("file", input.files[0]);

      fetch('/uploadfile/', {
          method: 'POST',
          body: formData
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error));
  };
  
  reader.readAsDataURL(input.files[0]);
}

function get_img(img) {
  displayedImageLow.src = img.src;
  displayedImageHigh.src = '';
}

document.getElementById('folderListBottom').onclick = function(){
  document.getElementById('folderListBottom').style.display = 'none';
  document.getElementById('hide_content').style.display = '';
  document.querySelector('.image-container').innerHTML = '';
}