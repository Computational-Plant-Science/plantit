<template>
    <div>
        <div id="grid-container">
            <div
                id="thumbnails"
                class="p-2 thumbnail"
                v-for="(sample,idx) in displayedSamples"
            >
              <div
                style="position: relative; min-width: 100px"
                @mouseover="selectedRow(idx)"
                @mouseout="selectedRow(null)"
              >
                <b-img
                  :id="`image-${idx}`"
                  v-if="sample.thumbnail"
                  :src="sample.thumbnail"
                  width="100px"
                  :title="sample.name">
                </b-img>
                <b-spinner
                  v-else
                  :id="`image-${idx}`"
                  v-b-tooltip.hover
                  :title="sample.name">
                </b-spinner>

                <b-button
                  v-show="selectedSample.hover == true && selectedSample.index === idx"
                  style="position: absolute; right:0; top:0"
                  class="plantit-btn thumbnail-btn"
                  v-b-tooltip.hover
                  title="Edit sample name and metadata."
                  @click="$bvModal.show('editSampleMeta')"
                >
                  <i class="far fa-edit"></i>
                </b-button>

                <b-button
                  v-show="selectedSample.hover == true && selectedSample.index === idx"
                  style="position: absolute; left:0; top:0"
                  class="plantit-btn thumbnail-btn"
                  v-b-tooltip.hover
                  title="Delete sample."
                  @click="deleteSample(idx)"
                >
                  <i class="fas fa-trash-alt"></i>
                </b-button>

                <b-popover
                  :target="`image-${idx}`"
                  :title="sample.name"
                  triggers="hover focus"
                >
                  <table width="100%">
                    <tr v-for="field in sample.metadata">
                      <td><b>{{ field.name }}:</b></td>
                      <td>{{ field.value }}</td>
                    </tr>
                  </table>

                </b-popover>
                <br />
              </div>
            </div>
        </div>
        <EditMetadataModal
          modal-id="editSampleMeta"
          :metadata="selectedSample.sample.metadata"
          :name="selectedSample.sample.name"
          @save="saveSample"
          @cancel="cancelEdit"
        >
       </EditMetadataModal>
        <b-pagination
            v-if="samples.length > this.perPage"
            v-model="currentPage"
            :total-rows="rows"
            :per-page="perPage"
            aria-controls="thumbnails"
            align="center"
            style="margin: 20px"
        ></b-pagination>
    </div>
</template>

<script>
import router from '@/router';
import EditMetadataModal from '@/components/collections/EditMetadataModal'
import CollectionApi from '@/services/apiV1/CollectionManager'

export default {
    name: 'CollectionThumbnails',
    components: {
      EditMetadataModal
    },
    props: ['pk','samples'],
    methods: {},
    data() {
        return {
            perPage: 20,
            currentPage: 1,
            selectedSample: {
              hover: false,
              index: null,
              sample: {
                metadata: [],
                name: ""
              }
            }
        };
    },
    computed: {
        rows() {
            return this.samples.length;
        },
        displayedSamples() {
            return this.samples.slice(
                this.perPage * (this.currentPage - 1),
                this.perPage * this.currentPage
            );
        }
    },
    methods: {
      selectedRow(idx){
        if(idx != null){
          this.selectedSample.index = idx
          this.selectedSample.sample = this.samples[idx]
          this.selectedSample.hover = true
        }else{
          this.selectedSample.hover = false
        }
      },
      saveSample(name,description,metadata){
        this.selectedSample.sample.name = name
        CollectionApi.updateSample(this.selectedSample.sample).then((response) =>{
        }).catch((err) => {
          console.log(err)
        })
      },
      cancelEdit(){
        CollectionApi.getSample(this.selectedSample.sample.pk)
        .then((sample) =>{
          this.$set(this.samples,this.selectedSample.index,sample)
        }).catch((err) => {
          console.log(err)
        })
      },
      deleteSample(){
        this.$bvModal.msgBoxConfirm(`Delete sample ${this.selectedSample.sample.name}?`,{
          title: 'Delete Confirmation',
          centered: true
        })
        .then(value => {
            if(value == true){
              CollectionApi.deleteSample(this.selectedSample.sample.pk).then((sucess) => {
                if(sucess){
                  this.samples.splice(this.selectedSample.index,1)
                }
              }).catch((err) => {
                console.log(err)
              })
            }
          })
      },
    }
};
</script>

<style scoped lang="sass">
.thumbnail
    text-align: center

#grid-container
  display: grid
  grid-template-columns: repeat( auto-fit, minmax(125px, 1fr) )
  justify-items: center

.thumbnail-btn
  margin: 5px
  opacity: 0.65

.thumbnail-btn:hover
  opacity: 1

</style>
