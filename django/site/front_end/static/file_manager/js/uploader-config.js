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
    auto: false,
    onNewFile: function(id, file){
      // When a new file is added using the file selector or the DnD area
      ui_multi_add_file(id, file);
    },
    onBeforeUpload: function(id){
     // about tho start uploading a file
     ui_multi_update_file_status(id, 'uploading', 'Uploading...');
     ui_multi_update_file_progress(id, 0, '', true);
    },
    onUploadCanceled: function(id) {
     // Happens when a file is directly canceled by the user.
     ui_multi_update_file_status(id, 'warning', 'Canceled by User');
     ui_multi_update_file_progress(id, 0, 'warning', false);
    },
    onUploadProgress: function(id, percent){
     // Updating file progress
     ui_multi_update_file_progress(id, percent);
    },
    onUploadSuccess: function(id, data){
     // A file was successfully uploaded
     ui_multi_update_file_status(id, 'success', 'Upload Complete');
     ui_multi_update_file_progress(id, 100, 'success', false);
    },
    onUploadError: function(id, xhr, status, message){
     ui_multi_update_file_status(id, 'danger', message);
     ui_multi_update_file_progress(id, 0, 'danger', false);
    },
  });
})
