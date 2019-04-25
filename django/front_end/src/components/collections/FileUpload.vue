
<template>
  <div>
    <table class="table table-hover">
        <thead>
          <tr>
            <th>#</th>
            <th>Thumb</th>
            <th>Name</th>
            <th>Size</th>
            <th>Speed</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>

          <tr v-if="!files.length">
            <td colspan="7">
              <div class="text-center p-5">
                <h4>Drop files anywhere to upload<br/>or</h4>
                <label :for="name" class="btn btn-lg btn-primary">Select Files</label>
              </div>
            </td>
          </tr>

          <tr v-for="(file, index) in files" :key="file.id">

            <td>{{index}}</td>

            <td>
              <img v-if="file.thumb" :src="file.thumb" width="40" height="auto" />
              <span v-else>No Image</span>
            </td>

            <td>
              <div class="filename">
                {{file.name}}
              </div>
              <div class="progress" v-if="file.active || file.progress !== '0.00'">
                <div :class="{'progress-bar': true, 'progress-bar-striped': true, 'bg-danger': file.error, 'progress-bar-animated': file.active}" role="progressbar" :style="{width: file.progress + '%'}">{{file.progress}}%</div>
              </div>
            </td>

            <td>{{file.size}}</td>

            <td>{{file.speed}}</td>

            <td v-if="file.error">{{file.error}}</td>
            <td v-else-if="file.success">success</td>
            <td v-else-if="file.active">active</td>
            <td v-else></td>

          </tr>
        </tbody>
      </table>

      <vue-upload
        class="btn btn-primary"
        v-model="files"
        :multiple="true"
        :headers="headers"
        postAction="/apis/v1/files/upload/"
        :data="{storage_type: storageType, path: path}"
        ref="upload"
        @input-file="inputFile">
          Add Files
      </vue-upload>
      <button type="button" class="btn btn-success ml-2" v-if="!$refs.upload || !$refs.upload.active" @click.prevent="$refs.upload.active = true">
        Start Upload
      </button>

  </div>
</template>

<script>
import FileManagerApi from '@/services/apiV1/FileManager'
import VueUpload from 'vue-upload-component'
import Auth from '@/services/apiV1/Auth'

export default {
    name: 'FileUpload',
    components:{
      VueUpload
    },
    props: ['storageType', 'path'],
    data(){
      return {
        files: [],
        name: 'file',
        headers:{
          "X-CSRFTOKEN": Auth.getCSRFToken()
        }
      }
    },
    methods:{
      inputFile: function(newFile, oldFile) {
        /**
         * Called whenever the this.files list is
         * modified (files added, files uploaded, etc)
         *
         * Used here to set the upload location of files and to add files to the
         * file tree after uploading
         **/

        // if File uploaded
        if (newFile && oldFile && !newFile.active && oldFile.active) {
          //Emit to parent
          this.$emit('fileUploaded',newFile.response)
        }
      }
    }
};
</script>
