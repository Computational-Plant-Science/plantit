<template>
  <p>
    <b-img
      v-if="url"
      :src="url"
      width="100px"
      :alt="sample.name">
    </b-img>
    <b-spinner
      v-else
      v-b-tooltip.hover
      :title="sample.name">
    </b-spinner>
  </p>
</template>

<script>
  import CollectionApi from '@/services/apiV1/CollectionManager'

  export default {
    /**
      Displays the sample thumbnail, if available (sample.thumbnail != null).
      Otherwise as spinner is displayed. The server is pinged every 15 seconds
      to check a thumbnail is now available.
    **/
    props: {
      //The object of the sample
      sample: {
        type: Object,
        required: true
      }
    },
    data(){
      return {
        url: this.sample.thumbnail,
        timer: ''
      }
    },
    created: function(){
      if(! this.url){
        this.timer = setInterval(this.fetch_url, 10000)
      }
    },
    methods:{
      fetch_url: function() {
        CollectionApi.getSample(this.sample.pk).then((sample) =>{
          this.url = sample.thumbnail
          if(this.url){
            clearInterval(this.timer)
          }
        })
      }
    },
    beforeDestroy() {
      clearInterval(this.timer)
    }
  }
</script>

<style scoped></style>
