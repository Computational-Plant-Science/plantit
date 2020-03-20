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
            <b-row class="justify-content-md-center">
                <b-col md="auto">
                    <b-row>
                        <UserInfo></UserInfo>
                    </b-row>
                </b-col>
                <b-col>
                    <b-row>
                        <ListJobs per-page="4"></ListJobs>
                    </b-row>
                    <b-row>
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
import UserInfo from "../components/UserInfo";

export default {
    name: 'Jobs',
    components: {
        UserInfo,
        ListJobs,
        ListCollections,
        PageNavigation
    },
    data() {
        return {};
    }
};
</script>
