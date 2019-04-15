<template>
    <div>
      <PageNavigation>
        <template v-slot:buttons>
            <b-button
              @click="$router.push({name: 'collection', query: { pk: pk }})"
            >
                Add Selected
            </b-button>
        </template>
      </PageNavigation>

      <b-container>
        <b-row>
          <b-col class="content-box center-container p-5 m-3">
            <h3>Add Files To Collection From Server</h3>
            <BrowseFiles :selectedFiles="selectedFiles"></BrowseFiles>
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
                style="overflow-y: scroll"
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
              }

          ]
        }
      }
    },
    computed:{
      fileArray(){
        return Object.values(this.selectedFiles)
      }
    }
};
</script>

<style scoped lang="sass">
</style>
