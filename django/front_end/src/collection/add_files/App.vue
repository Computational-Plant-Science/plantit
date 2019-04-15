<template>
  <div id="app">
    <div class="flex-row" style="width: 100%">
      <!-- File Browser -->
      <div class="flex-box content-column">
        <h3>Add Files To Collection From Server</h3>
        <button><i class="fas fa-folder-plus"></i></button>
        <button><i class="fas fa-upload"></i></button>

        <v-jstree
          :data="treeData"
          ref="tree"
          :async="loadData"
          show-checkbox
          multiple
          allow-batch
          whole-row
          class="file-browser"
        ></v-jstree>

        <div class="button-nav">
          <button v-on:click="addSelected">Add Selected</button>
          <button v-on:click="refreshTree">Refresh</button>
        </div>
      </div>

      <!-- File Upload -->
      <div class="flex-box content-column">
        <h3>Upload Files To Server</h3>
        <table style="margin: 0 auto">
          <thead>
            <tr>
              <th>#</th>
              <th>Thumb</th>
              <th>Name</th>
              <th>Size</th>
              <th>Speed</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!files.length">
              <td colspan="5">
                <div class="text-center p-5">
                  Click "Add Files" or drag here to begin
                </div>
              </td>
            </tr>
            <tr v-for="(file, index) in files" :key="file.id">
              <td>{{ index }}</td>
              <td>
                <img
                  v-if="file.thumb"
                  :src="file.thumb"
                  width="40"
                  height="auto"
                />
                <span v-else>No Image</span>
              </td>
              <td>
                <div class="filename">
                  {{ file.name }}
                </div>
                <div
                  class="progress"
                  v-if="file.active || file.progress !== '0.00'"
                >
                  <div
                    :class="{
                      'progress-bar': true,
                      'progress-bar-striped': true,
                      'bg-danger': file.error,
                      'progress-bar-animated': file.active
                    }"
                    role="progressbar"
                    :style="{ width: file.progress + '%' }"
                  >
                    {{ file.progress }}%
                  </div>
                </div>
              </td>
              <td>{{ file.size | formatSize }}</td>
              <td>{{ file.speed | formatSize }}</td>
            </tr>
          </tbody>
        </table>

        <file-upload
          ref="upload"
          v-model="files"
          :post-action="uploadURL"
          data="uploadData"
          multiple="true"
          :headers="uploadHeaders"
          @input-file="inputFile"
        >
        </file-upload>
        <label
          class="btn btn-success"
          v-if="!$refs.upload || !$refs.upload.active"
          @click.prevent="$refs.upload.active = true"
        >
          <i class="fa fa-arrow-up" aria-hidden="true"></i>
          Start Upload
        </label>
        <label for="file" class="btn btn-primary">Add Files</label>
      </div>
    </div>
  </div>
</template>

<script>
import VJstree from "vue-jstree";
import VueUploadComponent from "vue-upload-component";
import {
  Collection,
  Files,
  getCSRFToken
} from "../../vue_components/PlantITAPI";

export default {
  name: "app",
  props: ["collection", "referrer"],
  components: {
    "v-jstree": VJstree,
    "file-upload": VueUploadComponent
  },
  data() {
    return {
      treeData: [],
      // File Tree
      files: [],
      // File upload files
      uploadHeaders: { "X-CSRFToken": getCSRFToken() },
      collection: {},
      //Information about the collection, populated in main.js
      referrer: "",
      //URL of the referring page, populated in main.js
      uploadURL: Files.uploadURL(this.collection.storage_type)
      //API url to upload the files to
    };
  },
  methods: {
    loadData: function(oriNode, resolve) {
      /**
       * Load branches of the file tree async via the PlantIT Files API
       **/
      Files.listDir(
        oriNode.data.path ? oriNode.data.path : this.collection.base_dir,
        this.collection.storage_type
      )
        .then(data => {
          resolve(data);
        })
        .catch(e => {
          console.log(e);
        });
    },
    addSelected: function() {
      /**
       * Add the selected files to the collection and return to the referrer page
       **/
      let samples = [];
      this.$refs.tree.handleRecursionNodeChilds(this.$refs.tree, node => {
        if (node.model && node.model.selected) {
          //Root Node has no model
          samples.push({
            name: node.model.value,
            path: node.model.path
          });
        }
      });
      Collection.addSamples(samples, this.collection.pk).then(
        function() {
          window.location.assign(this.referrer);
        }.bind(this)
      );
    },
    refreshTree: async function() {
      /**
       * Reload the tree
       **/
      this.treeData = [this.$refs.tree.initializeLoading()];
      this.$refs.tree.handleAsyncLoad(this.treeData, this.$refs.tree);
    },
    inputFile: function(newFile, oldFile) {
      /**
       * Called whenever the this.files list is
       * modified (files added, files uploaded, etc)
       *
       * Used here to set the upload location of files and to add files to the
       * file tree after uploading
       **/
      //File queued for upload
      if (newFile && !oldFile) {
        //Set the upload location (See api.file_manger.views.uplaod)
        this.$refs.upload.update(newFile, {
          data: { pwd: this.collection.base_dir }
        });
      }

      // if File uploaded
      if (newFile && oldFile && !newFile.active && oldFile.active) {
        //Add file to the file tree
        newFile.response.forEach(file => {
          this.treeData.push(
            this.$refs.tree.initializeDataItem({
              text: file,
              size: 0,
              path: file,
              isLeaf: true,
              icon: "far fa-file"
            })
          );
        });
      }
    }
  }
};
</script>

<style lang="scss">
.file-browser {
  overflow: auto;
  height: 400px;
}
.button-nav {
  padding: 10px;
}
</style>
