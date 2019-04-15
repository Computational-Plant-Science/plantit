<template>
    <div style="text-align:center">
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
            </template>
            <template v-slot:buttons>
            </template>
        </PageNavigation>

        <b-container class="content-box center-container">
          <h1> Submit a workflow job </h1>
          Job pk: {{ job_pk }} <br/>
          Workflow pk: {{ workflow_pk }}
        </b-container>

    </div>
</template>

<script>
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'Analyze',
    components: {
      PageNavigation
    },
    props:{
      job_pk:{
        // the pk of the collection to analyze
        required: true
      },
      workflow_pk: {
        required: true
      }
    },
};
</script>
