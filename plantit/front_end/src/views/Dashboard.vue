<template>
    <div>
        <PageNavigation></PageNavigation>
        <b-container>
            <b-row class="justify-content-md-center">
                <b-col md="auto">
                    <b-row>
                        <UserInfo></UserInfo>
                    </b-row>
                </b-col>
                <b-col>
                    <b-row>
                        <ListCollections per-page="4"></ListCollections>
                    </b-row>
                    <b-row>
                        <ListJobs per-page="4"></ListJobs>
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
