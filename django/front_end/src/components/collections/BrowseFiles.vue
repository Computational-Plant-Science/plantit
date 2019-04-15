
<template>
  <div>
    <button @click="$refs['uploadModal'].show()">Upload Files</i></button>

    <b-modal ref="uploadModal">
      Upload your files here <br/>
      (someday, we are still in alpha after all...)
    </b-modal>

    <v-jstree
      :data="treeData"
      @item-click="changed"
      ref="tree"
      show-checkbox
      multiple
      allow-batch
      whole-row
      class="file-browser"
    ></v-jstree>
  </div>
</template>

<script>
import VJstree from "vue-jstree";

export default {
    name: 'BrowseFiles',
    components: {
      VJstree,
    },
    props: {
      selectedFiles:{
        //Object to place the selected items in.
        // selected[item.text] = item
        required: true,
        type: Object
      }
    },
    data(){
      return{
        treeData: [
          {
            "text": "file1.txt",
            "size": 10
          },
          {
            "text": "file2.txt",
            "size": 4
          },
          {
            "text": "file3.txt",
            "size": 12,
            children: [
              {
                "text": "child file 1.txt",
                "size": 11
              }
            ]
          },
          {
            "text": "file4.txt",
            "size": 15
          }
        ]
      }
    },
    methods:{
      changed(node, item, e){
        let set = (item) => {
          this.$set(this.selectedFiles, item.text, item)
          item.children.forEach((i) => {set(i)})
        }
        let del = (item) => {
          this.$delete(this.selectedFiles, item.text)
          item.children.forEach((i) => {del(i)})
        }
        if(item.selected){
          set(item)
        }else{
          del(item)
        }
      }
    }
};
</script>
