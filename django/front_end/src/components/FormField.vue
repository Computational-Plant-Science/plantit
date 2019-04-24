<template>
  <div v-b-tooltip.hover :title="field.description">

    <label class="mr-sm-2" v-if="field.type != 'bool'">{{field.name}}</label>
    <b-form-input
      class="mb-2 mr-sm-2 mb-sm-0"
      v-if="field.type == 'int' || field.type == 'float'"
      type="number"
      :step="numberStep"
      v-model="value"
    >
    </b-form-input>

    <b-form-checkbox
      v-if="field.type == 'bool'"
      v-model="value"
    >{{field.name}}</b-form-checkbox>

    <b-form-select
      v-if="field.type == 'select'"
      v-model="value"
      :options="field.options">
    </b-form-select>

  </div>
</template>

<script>
export default {
    name: 'FormField',
    props: ['field'],
    data: function(){
      return{
        value: this.field.initial
      }
    },
    watch:{
      value: function(newValue, oldValue){
        this.$emit('onChange',this.field.id,newValue)
      }
    },
    mounted:function(){
        this.$emit('onChange',this.field.id,this.value)
    },
    computed:{
      numberStep(){
        if(this.type == 'int'){
          return '1'
        }else{
          return 'any'
        }
      }
    }
  }
</script>
