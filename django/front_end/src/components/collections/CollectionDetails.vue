<template>
    <div style="position: relative">
        <b-button
          id="edit-btn"
          @click="$bvModal.show('editCollectionMeta')"
          class="plantit-btn"
          v-b-tooltip.hover
          title="Edit collection name, description, and metadata.">
          <i class="far fa-edit"></i>
        </b-button>
        {{ collection.name }}
        <br />
        {{ collection.description }}
        <br />
        <table width="100%">
          <tr v-for="field in collection.metadata">
            <td>{{ field.name }}</td>
            <td>{{ field.value }}</td>
          </tr>
        </table>
        <EditMetadataModal
          modal-id="editCollectionMeta"
          :metadata="collection.metadata"
          :name="collection.name"
          :description="collection.description"
          @save="saveDetails"
          @cancel="cancelEdit"
        >
      </EditMetadataModal>
    </div>
</template>

<script>
import EditMetadataModal from '@/components/collections/EditMetadataModal'
import CollectionApi from '@/services/apiV1/CollectionManager'

export default {
    name: 'CollectionDetails',
    components: {
      EditMetadataModal
    },
    props: ['collection'],
    data() {
        return {};
    },
    methods: {
      saveDetails(name,description,metadata){
        CollectionApi.updateMetadata(name,
                                     description,
                                     this.collection.metadata,
                                     this.collection.pk).then(() =>{
                                       this.collection.description = description
                                       this.collection.name = name
                                     })
      },
      cancelEdit(){
        CollectionApi.getCollection(this.collection.pk).then((collection) => {
          this.collection.metadata = collection.metadata
          this.collection.name = collection.name
          this.collection.description = collection.description
        })
      }
    },
};
</script>

<style scoped lang="sass">
  #edit-btn
    position: absolute
    top: 0
    right: 0
    margin: 5px
</style>
