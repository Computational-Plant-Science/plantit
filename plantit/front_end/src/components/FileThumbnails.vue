<template>
    <div>
        <div id="grid-container">
            <div
                id="thumbnails"
                class="p-2 thumbnail"
                v-for="(sample, idx) in displayedSamples"
                :key="sample.pk"
            >
                <div
                    style="position: relative; min-width: 100px"
                    @mouseover="selectedRow(idx)"
                    @mouseout="selectedRow(null)"
                    :id="`image-${idx}`"
                >
                    <SampleThumbnail :sample="sample" key="sample">
                    </SampleThumbnail>

                    <b-button
                        v-show="
                            selectedSample.hover === true &&
                                selectedSample.index === idx
                        "
                        style="position: absolute; right:0; top:0"
                        class="plantit-btn thumbnail-btn"
                        v-b-tooltip.hover
                        title="Edit sample metadata."
                        @click="$bvModal.show('editSampleMeta')"
                    >
                        <i class="far fa-edit"></i>
                    </b-button>

                    <b-button
                        v-show="
                            selectedSample.hover === true &&
                                selectedSample.index === idx
                        "
                        style="position: absolute; left:0; top:0"
                        class="thumbnail-btn"
                        variant="danger"
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
                            <tr
                                v-for="field in sample.metadata"
                                :key="field.name + field.value"
                            >
                                <td>
                                    <b>{{ field.name }}:</b>
                                </td>
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
import EditMetadataModal from '@/components/collections/EditMetadataModal';
import SampleThumbnail from '@/components/collections/SampleThumbnail';
import CollectionApi from '@/services/apiV1/Datasets';

export default {
    name: 'CollectionThumbnails',
    components: {
        EditMetadataModal,
        SampleThumbnail
    },
    props: {
        pk: {
            //The collection pk
            required: true,
            type: Number
        },
        samples: {
            //The Array of samples to display, as formatted in the colletion object.
            required: true,
            type: Array
        }
    },
    data() {
        return {
            //Number of samples per page
            perPage: 20,
            //Current page being displayed
            currentPage: 1,
            //Current sample being interacted with by user
            selectedSample: {
                hover: false,
                index: null,
                sample: {
                    metadata: [],
                    name: ''
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
        selectedRow(idx) {
            if (idx != null) {
                this.selectedSample.index = idx;
                this.selectedSample.sample = this.samples[idx];
                this.selectedSample.hover = true;
            } else {
                this.selectedSample.hover = false;
            }
        },
        // eslint-disable-next-line no-unused-vars
        saveSample(name, description, metadata) {
            this.selectedSample.sample.name = name;
            CollectionApi.updateSample(this.selectedSample.sample);
        },
        cancelEdit() {
            CollectionApi.getSample(this.selectedSample.sample.pk).then(
                sample => {
                    this.$set(this.samples, this.selectedSample.index, sample);
                }
            );
        },
        deleteSample() {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete sample '${this.selectedSample.sample.name}'?`,
                    {
                        title: 'Delete Sample',
                        centered: true
                    }
                )
                .then(value => {
                    if (value == true) {
                        CollectionApi.deleteSample(
                            this.selectedSample.sample.pk
                        ).then(sucess => {
                            if (sucess) {
                                this.samples.splice(
                                    this.selectedSample.index,
                                    1
                                );
                            }
                        });
                    }
                });
        }
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
