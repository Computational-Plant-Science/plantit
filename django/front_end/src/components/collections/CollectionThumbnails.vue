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
    props: ['pk'],
    methods: {},
    data() {
        return {
            perPage: 10,
            currentPage: 1,
            samples: [
                { name: 'Sample 1', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 2', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 3', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 4', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 5', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 6', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 7', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 8', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 9', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 10', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 11', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 12', thumbnail: require('../../assets/logo.png') },
                { name: 'Sample 13', thumbnail: require('../../assets/logo.png') }
            ]
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
