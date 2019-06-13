<template>
    <div>
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
            </template>
        </PageNavigation>
        <b-container>
            <b-row>
                <b-col>
                    <h1>Job ID: {{ this.$route.query.pk }}</h1>
                    <h3>Collection: {{ this.job.collection }}</h3>
                </b-col>
                <b-col cols="5">
                    <b>Current Status:</b> {{ job.current_status }}<br />
                    <b>Submission ID:</b> {{ job.submission_id }}<br />
                    <b>Work DIR:</b> {{ job.work_dir }}<br />
                    <b>Created:</b> {{ job.date_created | format_date }}<br />
                </b-col>
            </b-row>
            <b-row>
                <b-col class="content-box text-center p-5">
                    <b-img
                        v-if="job.remote_results_path == null"
                        :src="require('../assets/PlantITLoading.gif')"
                        width="250%"
                        alt="Plant IT"
                    ></b-img>
                    <b-link v-else :href="job | resultsLink">
                        <b-img
                            :src="require('../assets/icons/download.png')"
                            width="250%"
                            alt="Download"
                        ></b-img>
                    </b-link>
                    <DiscreteProgress
                        style="padding: 20px 15% 10px 15%;"
                        :tasks="job.task_set"
                    ></DiscreteProgress>
                    Current Status: {{ current_status }}
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import PageNavigation from '@/components/PageNavigation.vue';
import DiscreteProgress from '@/components/DiscreteProgress.vue';
import JobApi from '@/services/apiV1/JobManager.js';
import moment from 'moment';

export default {
    name: 'Job',
    components: {
        PageNavigation,
        DiscreteProgress
    },
    data() {
        return {
            job: {
                pk: this.$route.query.pk,
                collection: 'NULL',
                current_status: 'NULL',
                submission_id: 'NULL',
                work_dir: 'NULL',
                auth_token: 'NULL',
                remote_results_path: null,
                task_set: [],
                status_set: []
            }
        };
    },
    mounted: function() {
        JobApi.getJob(this.job.pk).then(data => {
            this.job = data;
        });
    },
    computed: {
        current_status() {
            if (this.job.status_set.length > 0) {
                return this.job.status_set[0].description;
            } else {
                return '';
            }
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        },
        resultsLink(job) {
            return JobApi.resultsLink(job.pk);
        }
    }
};
</script>
