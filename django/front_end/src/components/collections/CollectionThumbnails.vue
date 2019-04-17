<template>
    <div>
        <div id="grid-container">
            <div
                id="thumbnails"
                class="p-2 thumbnail"
                v-for="sample in displayedSamples"
            >
                <b-img
                  v-if="sample.thumbnail"
                  :src="sample.thumbnail"
                  width="100px"
                  v-b-tooltip.hover
                  :title="sample.name">
                </b-img>
                <b-spinner
                  v-else
                  v-b-tooltip.hover
                  :title="sample.name">
                </b-spinner>
                <br />
            </div>
        </div>

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

export default {
    name: 'CollectionThumbnails',
    components: {},
    props: ['pk','samples'],
    methods: {},
    data() {
        return {
            perPage: 20,
            currentPage: 1,
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

</style>
