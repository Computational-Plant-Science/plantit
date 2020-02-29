<template>
    <div>
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
            </template>
            <template v-slot:buttons>
                <b-button @click="createNew">
                    New Collection
                </b-button>
            </template>
        </PageNavigation>

        <b-container class="content-box text-left p-4 center-container">
            <h2>Your Collections</h2>
            <ListCollections
                filterable="true"
                class="text-center"
            ></ListCollections>
        </b-container>
    </div>
</template>

<script>
import ListCollections from '@/components/collections/ListCollections.vue';
import PageNavigation from '@/components/PageNavigation.vue';
import router from '../router';

export default {
    name: 'Collections',
    components: {
        ListCollections,
        PageNavigation
    },
    data() {
        return {
            links: [
                {
                    text: 'Dashboard',
                    to: '/user/dashboard'
                },
                {
                    text: 'Jobs',
                    to: '/user/jobs'
                }
            ]
        };
    },
    methods: {
        createNew: function() {
            router.push({ name: 'newCollection' });
        }
    }
};
</script>
