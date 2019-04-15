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
            </template>
        </PageNavigation>

        <b-container>
            <b-row>
                <b-col class="content-box">
                    <CollectionThumbnails
                        :pk="this.$route.query.pk"
                    ></CollectionThumbnails>
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
    methods: {
        addFiles() {
            router.push({name: 'addFiles', query: { pk: this.pk }})
        },
        analyze() {
            router.push({name: 'analyze', query: { pk: this.pk }})
        }
    }
};
</script>
