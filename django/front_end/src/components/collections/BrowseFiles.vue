
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
      :async="loadTreeDataAsync"
    ></v-jstree>
  </div>
</template>

<script>
import VJstree from "vue-jstree";
import FileManagerApi from '@/services/apiV1/FileManager'
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
      },
      basePath:{
        //The base path of the file browse
        required: true,
        type: String
      },
      storageType:{
        //The storage type to access
        required: true,
        type: String
      }
    },
    data(){
      return{
        treeData: []
      }
    },
    methods:{
      loadTreeDataAsync(oriNode, resolve){
        let path = (oriNode.data.path ? oriNode.data.path : this.basePath)
        FileManagerApi.listDir(path,this.storageType)
        .then((data) => {
          resolve(data)}
        )
      },
      changed(node, item, e){
        let set = (item) => {
          if(item.isLeaf){
            this.$set(this.selectedFiles, item.text, item)
          }
          item.children.forEach((i) => {set(i)})
        }
        let del = (item) => {
          if(item.isLeaf){
            this.$delete(this.selectedFiles, item.text)
          }
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
