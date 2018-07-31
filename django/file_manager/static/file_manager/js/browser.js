/**
 Implements the javascript required for the ajax file browser
 **/

function cd(dir){
  /**
    Repopulate #file_table with the files and dirs from directory dir by
    asking the server via the "ls" ajax view

    :param dir: (String) directory to list in the #file_table table
  **/
  pwd = $("#pwd").text()

  if (dir == './') {
    dir = './'
  }else{
    dir = pwd + dir + "/"
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
    }
  });
  $.ajax({
      type: "POST",
      url: "ajax/browse/",
      dataType: "json",
      data: { "dir": dir,

      },
      success: function(data) {
        if(dir.slice(-4) == '..//'){
          pwd = pwd.substr(0, pwd.slice(0,-1).lastIndexOf("/") + 1)
        }else{
          pwd = dir
        }
        $("#pwd").text(pwd)

        $("#file_table tr").not(function(){ return !!$(this).has('th').length; }).remove();
        if(dir != "./"){
          $('<tr>').append(
            $('<td></td>'),
            $('<td>').html("<a href=\"javascript:cd('./')\" >./</a>"),
          ).appendTo('#file_table');
          $('<tr>').append(
              $('<td></td>'),
              $('<td>').html("<a href=\"javascript:cd('../')\" >../</a>")
          ).appendTo('#file_table');
        }

        list_dirs(data.dirs)
        list_files(data.files,pwd)
      }
  });
}

function list_dirs(dirs){
  /**
    Populate #file_table with the directories listed in dirs

    :param dirs: list of directory name strings
  **/
  $.each(dirs, function(i,dir) {
    $('<tr>').append(
        $('<td></td>'),
        $('<td>').html("<a href=\"javascript:cd('" + dir + "')\" >" + dir + "</a>")
    ).appendTo('#file_table');
  });
}

function list_files(files,pwd){
  /**
    Populate #file_table with the files in files

    :param files: list of file objects, each file object has:
      file.name the name of the file
      file.size the size of the file
  **/
  $.each(files, function(i,file) {
    $('<tr>').append(
        $('<td>').html("<input type='checkbox' value='"+ pwd + file.name + "' class='selectFileCheckBox' name='files'>"),
        $('<td>').text(file.name),
        $('<td>').text(file.size)
    ).appendTo('#file_table');
  });
}

$(document).ready(function() {
  /**
   init
   **/
  cd('./');

  $("#drop-area").dmUploader({
    url: "ajax/upload/",
    //... More settings here...
    extraData: function(){
      return {
        "pwd" : $("#pwd").text()
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
