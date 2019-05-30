<template>
  <b-modal id="editMetadata" title="Edit Metadata" hide-footer>
    Name:
    <b-form-input
      v-model="collection.name">
    </b-form-input>
    Description:
    <b-form-textarea
      id="textarea"
      v-model="collection.description"
      rows="3"
      max-rows="6"
    ></b-form-textarea>
    Metadata:
    <table width="100%">
      <tr v-for="(field,idx) in collection.metadata">
        <td>{{ field.name }}</td>
        <td>
          <ClickToEdit v-model="field.value"></ClickToEdit>
        </td>
        <td>
          <b-button @click="deleteField(idx)"><i class="fas fa-trash-alt"></i></b-button>
        </td>
      </tr>
      <tr>
        <td>
          <input
            id="newField"
            ref="newField"
            v-model="newField.name"
            v-on:keyup.enter="addField"
            v-on:keyup.tab="this.$refs.newValue.focus()">
        </td>
        <td>
          <input
            id="newValue"
            ref="newValue"
            v-model="newField.value"
            v-on:keyup.enter="addField"
          >
        </td>
        <td>
          <b-button @click="addField"><i class="fas fa-plus"></i></b-button>
        </td>
      </tr>
    </table>
    <b-button class="mt-3" block @click="save">Save</b-button>
    <b-button class="mt-3" block @click="cancel">Cancel</b-button>
  </b-modal>
</template>

<script>
  import ClickToEdit from '@/components/collections/ClickToEdit'
  import CollectionApi from '@/services/apiV1/CollectionManager'

  export default {
    props: ['collection'],
    data(){
      return{
        newField: {
          name: '',
          value: '',
        }
      }
    },
    components:{
      ClickToEdit
    },
    methods:{
      show(){
        this.$bvModal.show("editMetadata")
      },
      hide(){
        this.$bvModal.hide("editMetadata")
      },
      toggle(){
        this.$bvModal.toggle("editMetadata")
      },
      addField(){
        this.collection.metadata.push({...this.newField})
        this.newField = {
          name: '',
          value: '',
        }
        this.$refs.newField.focus()
      },
      deleteField(idx){
        this.collection.metadata.splice(idx,1)
      },
      save(){
        this.$bvModal.hide('editMetadata')
        CollectionApi.updateMetadata(this.collection.name,
                                     this.collection.description,
                                     this.collection.metadata,
                                     this.collection.pk)
      },
      cancel(){
        CollectionApi.getCollection(this.collection.pk).then((collection) => {
          this.collection.metadata = collection.metadata
          this.collection.name = collection.name
          this.collection.description = collection.description
          this.$bvModal.hide('editMetadata')
        })
      }
    }
  }
</script>

<style scoped></style>
