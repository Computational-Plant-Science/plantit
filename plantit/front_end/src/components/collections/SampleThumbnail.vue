<template>
    <p>
        <span v-if="!thumbnail.supported">
            <b-img
                :src="require('@/assets/icons/no-thumbnail.png')"
                width="100px"
                :alt="sample.name"
            ></b-img>
        </span>
        <span v-else>
            <b-img
                v-if="thumbnail.url"
                :src="thumbnail.url"
                width="100px"
                :alt="sample.name"
            >
            </b-img>
            <b-spinner v-else v-b-tooltip.hover :title="sample.name">
            </b-spinner>
        </span>
    </p>
</template>

<script>
import CollectionApi from '@/services/apiV1/DatasetManager';

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
    data() {
        return {
            thumbnail: {
                url: this.sample.thumbnail,
                supported: this.sample.thumbnail_supported
            },
            timer: ''
        };
    },
    created: function() {
        if (this.thumbnail.supported && !this.thumbnail.url) {
            this.timer = setInterval(this.fetch_url, 10000);
        }
    },
    methods: {
        fetch_url: function() {
            CollectionApi.getSample(this.sample.pk).then(sample => {
                this.thumbnail.supported = sample.thumbnail_supported;
                this.thumbnail.url = sample.thumbnail;
                if (!this.thumbnail.supported || this.thumbnail.url != null) {
                    clearInterval(this.timer);
                }
            });
        }
    },
    beforeDestroy() {
        clearInterval(this.timer);
    }
};
</script>

<style scoped></style>
