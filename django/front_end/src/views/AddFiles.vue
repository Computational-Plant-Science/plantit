<template>
    <div>
      <PageNavigation>
        <template v-slot:buttons>
            <b-button
              @click="addSelected"
            >
                Add Selected
            </b-button>
            <b-button
              @click="$router.push({name: 'collection', query: { pk: pk }})"
            >
                Cancel
            </b-button>
        </template>
      </PageNavigation>

      <b-container>
        <b-row>
          <b-col class="content-box center-container p-5 m-3">
            <h3>Add Files To Collection From Server</h3>
            <BrowseFiles
              v-if="collection.base_file_path"
              :basePath="collection.base_file_path"
              :storageType="collection.storage_type"
              :selectedFiles="selectedFiles"
            >
            </BrowseFiles>
          </b-col>
          <b-col class="content-box center-container p-5 m-3 selected-files">
            <h3>Selected Files/Folders</h3>
            Total files: {{ fileArray.length }}
            Total size: {{ fileArray.reduce((total, item) => { return item.size + total },0) }}
            <b-table
                scrollY
                selectable
                striped
                hover
                :items="fileArray"
                :borderless="true"
                :striped="false"
                :fields="table.fields"
                style="overflow-y: scroll;"
            >
          </b-table>
          </b-col>
        </b-row>
      </b-container>
    </div>
</template>

<script>
import PageNavigation from '@/components/PageNavigation.vue';
import BrowseFiles from '@/components/collections/BrowseFiles.vue'
import CollectionApi from '@/services/apiV1/CollectionManager'

export default {
    name: 'AddFiles',
    components: {
      PageNavigation,
      BrowseFiles
    },
    props:{
      pk:{
        //Pk of collection to add files to
        required: true,
        type: Number
      }
    },
    data(){
      return{
        collection: {},
        selectedFiles: {},
        table: {
          fields: [
              {
                  key: 'text',
                  label: "Name",
                  sortable: true
              },
              {
                  key: 'size'
              },
              {
                key: 'path'
              }
          ]
        }
      }
    },
    mounted: function(){
      CollectionApi.getCollection(this.pk)
      .then((data) => {
        this.collection = data
        console.log(this.collection)
      })
    },
    computed:{
      fileArray(){
        return Object.values(this.selectedFiles)
      }
    },
    methods:{
      addSelected(){
        CollectionApi.addSamples(this.fileArray.map((item) => {
           return {name: item.text, path: item.path}
         }),this.pk)
         .then((result)=>{
           this.$router.push({name: 'collection', query: { pk: this.pk }})
         })
      }
    }
};
</script>

<style scoped lang="sass">
</style>
