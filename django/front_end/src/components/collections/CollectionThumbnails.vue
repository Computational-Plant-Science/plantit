<template>
    <div>
        <div class="d-flex flex-wrap">
            <div
                id="thumbnails"
                class="p-2 thumbnail"
                v-for="sample in displayedSamples"
            >
                <b-img :src="sample.thumbnail" width="100px"></b-img>
                <br />
                {{ sample.name }}
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
            perPage: 10,
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

<style scoped>
.thumbnail {
    text-align: center;
}
</style>
