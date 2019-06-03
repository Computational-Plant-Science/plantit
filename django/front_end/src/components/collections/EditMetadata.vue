<template>
    <table>
      <th>Key</th><th>Value</th>
      <tr v-for="(field, index) in metadata" v-bind:key="field.name + field.value">
        <td>
          <ClickToEdit
            v-model="field.name"
            v-b-tooltip.hover
            title="Click on text to edit.">
          </ClickToEdit>
        </td>
        <td>
          <ClickToEdit
            v-model="field.value"
            v-b-tooltip.hover
            title="Click on text to edit.">
          </ClickToEdit>
        </td>
        <td>
          <b-button @click="deleteField(index)"><i class="fas fa-trash-alt"></i></b-button>
        </td>
      </tr>
      <tr>
        <td>
          <input
            id="newField"
            ref="newField"
            v-model="newField.name"
            v-on:keyup="edited"
            placeholder="E.g. Date Collected"
            v-on:keyup.enter="addField">
        </td>
        <td>
          <input
            id="newValue"
            ref="newValue"
            placeholder="E.g. 12/20/1998"
            v-model="newField.value"
            v-on:keyup="edited"
            v-on:keyup.enter="addField"
          >
        </td>
        <td>
          <b-button @click="addField"><i class="fas fa-plus"></i></b-button>
        </td>
      </tr>
    </table>
</template>

<script>
  import ClickToEdit from '@/components/collections/ClickToEdit'

  export default {
    /*
      This allows editing of an objects metadata, for example for a Sample
      or Collection. Metdata is an array of objects with a "name" and "value"
      property. Both are saved as strings.

      Events:
        unsaved(): emits true when there is unsaved metadata (i.e.) text
        in the input boxes, false when the input boxes are empty

     */
    components:{
      ClickToEdit
    },
    props: {
      //The objects metadata. Provided as an arry of objects of key (name) and
      // value (value) pairs.
      // metadata: [
      //  {
      //    name: "Name of metadata value",
      //      value: "value of metadata"
      //  },
      //  ...
      // ]
      metadata: {
        type: Array,
        required: true
      },
    },
    model: {
      prop: 'metadata',
      event: 'input'
    },
    data: function(){
      return {
          // Keeps the values for a new metadata value to be added to the
          // metadata array.
          newField: {
            type: Object,
            required: false,
            default: function(){
              return {
                name: '',
                value: '',
              }
            }
          },
      }
    },
    methods:{
      addField(){
        this.metadata.push({...this.newField})
        this.newField = {
          name: '',
          value: '',
        }
        this.$refs.newField.focus()
        this.$emit('input', this.metadata)
        this.edited()
      },
      deleteField(idx){
        this.$delete(this.metadata,idx)
        this.$emit('input', this.metadata)
      },
      edited(){
        this.$emit('unsaved',!(this.newField.name == '' && this.newField.value == ''))
      }
    },
  }
</script>

<style scoped></style>
