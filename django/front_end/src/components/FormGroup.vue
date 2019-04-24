<template>
  <div>
      <h4> {{group.name}} </h4>
      <div
        v-if="group.params"
        class="form-group-fields"
      >
        <FormField
          class="p-2"
          v-for="field in group.params"
          :field="field"
          @onChange="changed"
          >
        </FormField>
      </div>

      <FormGroup @onChange="changed" v-for="subgroup in group.groups" :group="subgroup"></FormGroup>
  </div>
</template>

<script>
import FormField from '@/components/FormField'
export default {
    name: 'FormGroup',
    components: {
      FormField
    },
    props: ['group'],
    data: function(){
      return {
        values: {}
      }
    },
    methods:{
      changed(field,value){
        this.values[field] = value
        this.$emit('onChange',this.group.id,this.values)
      }
    }
  }
</script>

<style lang="sass">
  .form-group-fields
    display: flex
    flex-wrap: wrap
    align-items: center
    justify-content: flex-start
</style>
