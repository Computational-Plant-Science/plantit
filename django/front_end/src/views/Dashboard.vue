<template>
    <div>
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
            </template>
            <template v-slot:buttons> </template>
        </PageNavigation>

        <b-container>
            <b-row>
                <b-col class="content-box">
                    User Stuff
                </b-col>
                <b-col md="8">
                    <b-row class="table-responsive content-box">
                        <h2 class="text-center">Recent Jobs</h2>
                        <ListJobs per-page="4"></ListJobs>
                    </b-row>
                    <b-row class="table-responsive content-box">
                        <h2 class="text-center">Recent Collections</h2>
                        <ListCollections per-page="4"></ListCollections>
                    </b-row>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import ListJobs from '@/components/ListJobs.vue';
import ListCollections from '@/components/collections/ListCollections.vue';
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'Jobs',
    components: {
        ListJobs,
        ListCollections,
        PageNavigation
    },
    data() {
        return {};
    }
};
</script>
