/**
 Implements the javascript required for the ajax file browser

 This code assumes the following global variables are set:
  - storage_type (String): the storage type identifier. Must be one of
      the implmented file_manger.storage.permissions.STOARGE_TYPES
  - base_path (String): The path from the root folder on the webserver to the
      "root folder" shown to the user. base_path is prefixed to all paths when
      querying the web server. It is hidden from the user.


  These can be set within the template using:

  .. code:: html
    <script type="text/javascript">
      var storage_type = "{{ storage_type }}"
      var base_path = "{{ path }}"
      var urls = {
                  browse: "{% url 'file_manager:ajax' command='browse' %}",
                  upload: "{% url 'file_manager:ajax' command='upload' %}"
                }
    </script>

 **/

function cd(dir){
  /**
    Repopulate #file_table with the files and dirs from directory dir by
    asking the server via the "ls" ajax view

    Args:
      dir (String): directory path to list in the #file_table table.
        path is relative to base_path
  **/

  //Remove extra /'s in the dir string
  folders = dir.split("/")
  folders = folders.filter(function(n){ return n != "" })
  dir = folders.join("/")

  path = base_path + dir;

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
    }
  });
  $.ajax({
      type: "POST",
      url: urls.browse,
      dataType: "json",
      data: { "dir": path,
             "storage_type": storage_type
      },
      success: function(data) {
        $("#pwd").text("/" + dir)

        $("#file_table tr").not(function(){ return !!$(this).has('th').length; }).remove();
        if(dir != ""){
          $('<tr>').append(
            $('<td></td>'),
            $('<td>').html("<a href=\"javascript:cd('')\" >./</a>"),
          ).appendTo('#file_table');
          $('<tr>').append(
              $('<td></td>'),
              $('<td>').html("<a href=\"javascript:up_dir()\" >../</a>")
          ).appendTo('#file_table');
        }

        list_dirs(data.dirs,dir)
        list_files(data.files,dir)
      }
  });
}

function up_dir(){
  /**
    cd into the parent directory
  **/
  folders = $("#pwd").text().split("/")
  cd(folders.slice(0,folders.length - 1).join("/"))
}

function list_dirs(dirs,pwd){
  /**
    Populate #file_table with the directories listed in dirs

    Args:
      dirs: list of directory name strings
      pwd: the path from the basepath to the current folder
  **/
  $.each(dirs, function(i,dir) {
    $('<tr>').append(
        $('<td></td>'),
        $('<td>').html("<a href=\"javascript:cd('" + pwd + "/" + dir + "')\" >" + dir + "</a>")
    ).appendTo('#file_table');
  });
}

function list_files(files,pwd){
  /**
    Populate #file_table with the files in files

    Args:
      files: list of file objects, each file object has:
        file.name the name of the file
        file.size the size of the file
      pwd: the path from the basepath to the current folder
  **/
  $.each(files, function(i,file) {
    $('<tr>').append(
        $('<td>').html("<input type='checkbox' value='"+ pwd + "/" + file.name + "' class='selectFileCheckBox' name='file'>"),
        $('<td>').text(file.name),
        $('<td>').text(file.size)
    ).appendTo('#file_table');
  });
}

$(document).ready(function() {
  /**
   init
   **/
  cd($("#pwd").text());

  $("#drop-area").dmUploader({
    url: urls.upload,
    //... More settings here...
    extraData: function(){
      return {
        "dir": path,
        "storage_type": storage_type
      };
    },

    onComplete: function(){
      cd($("#pwd").text());
    }
    // ... More callbacks
  });

  /**
    Select all files
   **/
  $("#ckbCheckAll").click(function () {
    $(".selectFileCheckBox").prop('checked', $(this).prop('checked'));
  });


})
