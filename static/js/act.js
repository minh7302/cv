function displayImage() {
  var input = document.getElementById('imageInput');
  var uploadedImage = document.getElementById('uploadedImage');
  
  var reader = new FileReader();
  reader.onload = function (e) {
      uploadedImage.src = e.target.result;
      updateDisplayedImage();
      
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