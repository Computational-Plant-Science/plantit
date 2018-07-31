$(document).ready(function() {
  /**
   init
   **/
   $.ajaxSetup({
     beforeSend: function(xhr, settings) {
       xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
     }
   });

  $("#drop-area").dmUploader({
    url: "",
  });
})
