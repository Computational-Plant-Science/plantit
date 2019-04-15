<template>
    <div>
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
            </template>
        </PageNavigation>
        <b-container class="content-box p-4 center-container">
            <h2>Your Jobs</h2>
            <ListJobs filterable="true" class="text-center"></ListJobs>
        </b-container>
    </div>
</template>

<script>
import ListJobs from '@/components/ListJobs.vue';
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'Jobs',
    components: {
        ListJobs,
        PageNavigation
    }
};
</script>
