function add_checkbox_listeners(elements,checked) {
  /**
   * toggle all checkboxes within the parent element of the event listener
   *
   * Args:
   *   element: element to attached evenet listener to
   *   check (bool): what to set check boxes to on click
   **/
   for(var i = 0; i < elements.length; i++){
     elements[i].addEventListener('click',function(){
       checkboxes = this.parentNode.querySelectorAll('input[type=checkbox]')
       for(var j=0; j < checkboxes.length; j++) {
         checkboxes[j].checked = checked;
       }
     })
   }
}

document.addEventListener('DOMContentLoaded', function () {
    checkall = document.querySelectorAll(".field-group .check-all");
    add_checkbox_listeners(checkall,true)
    uncheckall = document.querySelectorAll(".field-group .uncheck-all");
    add_checkbox_listeners(uncheckall,false)
});
