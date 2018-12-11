function load_threshold_images(){
  var images = document.getElementsByClassName("threshold-img")

  for(var i = 0; i < images.length; i++) {
    var image = new Image();
    image.onload = function(){
        document.querySelector('.threshold-img[threshold="' + this.threshold + '"]').src = this.src;
    };
    image.src = "segment/?threshold=" + images[i].getAttribute("threshold");
    image.threshold = images[i].getAttribute("threshold");
  }
};

document.addEventListener('DOMContentLoaded', function () {
    load_threshold_images();
});
