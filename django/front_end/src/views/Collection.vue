<template>
    <div style="text-align:center">
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
            </template>
            <template v-slot:buttons>
                <b-button @click="addFiles">
                    Add Files
                </b-button>

                <b-button
                  @click="analyze"
                >
                    Analyze
                </b-button>

                <b-button
                  @click="deleteCollection"
                >
                    Delete
                </b-button>
            </template>
        </PageNavigation>

        <b-container>
            <b-row>
                <b-col class="content-box">
                    <b-spinner
                     v-if="this.collection.sample_set === undefined"
                     label="Loading...">
                   </b-spinner>
                   <span v-else>
                     <span
                       v-if="this.collection.sample_set == 0"
                     >
                       Add files to the collection by clicking
                       <b-link :to="{name: 'addFiles', query: { pk: this.pk }}">
                         "Add Files"
                       </b-link>
                     </span>
                      <CollectionThumbnails
                          v-if="this.collection.sample_set.length > 0"
                          :pk="this.$route.query.pk"
                          :samples="collection.sample_set"
                      ></CollectionThumbnails>
                    </span>
                </b-col>
                <b-col class="content-box" md="5">
                    <CollectionDetails></CollectionDetails>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import PageNavigation from '@/components/PageNavigation.vue';
import CollectionThumbnails from '@/components/collections/CollectionThumbnails.vue';
import CollectionDetails from '@/components/collections/CollectionDetails.vue';
import CollectionApi from '@/services/apiV1/CollectionManager'

export default {
    name: 'Collection',
    components: {
        PageNavigation,
        CollectionThumbnails,
        CollectionDetails
    },
    props:{
      pk: {
        //Pk of the collection to show
        required: true
      }
    },
    data(){
      return {
        collection: {}
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
      hasSamples(){
        return !(this.collection.sample_set === undefined
                || this.collection.sample_set == 0)
      }
    },
    methods: {
        addFiles() {
            router.push({name: 'addFiles', query: { pk: this.pk }})
        },
        analyze() {
            router.push({name: 'analyze', query: { pk: this.pk }})
        },
        deleteCollection() {
          this.$bvModal.msgBoxConfirm(`Delete collection ${this.collection.name}?`,{
            title: 'Delete Confirmation',
            centered: true
          })
            .then(value => {
              if(value == true){
                CollectionApi.deleteCollection(this.collection.pk).then(value => {
                  if(value == true){
                    router.push({name: 'collections'})
                  }
                })
              }
            })
            .catch(err => {
              console.log("Error :" + err)
            })
        }
    }
};
</script>
