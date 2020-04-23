<template>
    <div class="w-100 m-0 p-0">
        <b-container>
            <div class="w-100 pb-4">
                <b-card header-bg-variant="dark" border-variant="dark">
                    <template
                        v-slot:header
                        v-bind:job="this.job"
                        style="background-color: white"
                    >
                        <b-row align-v="center">
                            <b-col class="mt-2" style="color:white">
                                <h5>
                                    <i class="fas fa-terminal green"></i>
                                    Job
                                    <b-badge class="collection-id">{{
                                        job.pk
                                    }}</b-badge>
                                </h5>
                            </b-col>
                        </b-row>
                    </template>
                    <b-row>
                        <b-col>
                            <p><b>Workflow:</b> {{ job.workflow_name }}</p>
                            <p><b>Collection:</b> {{ job.collection }}</p>
                            <p><b>Cluster:</b> {{ job.cluster }}</p>
                            <p><b>Created:</b> {{ job.date_created | format_date
                            }}<br /></p>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col class="text-center p-5">
                            <b-img
                                v-if="job.remote_results_path == null"
                                :src="require('../assets/PlantITLoading.gif')"
                                width="250%"
                                alt="Plant IT"
                            ></b-img>
                            <b-link v-else :href="job | resultsLink">
                                <b-img
                                    :src="
                                        require('../assets/icons/download.png')
                                    "
                                    width="250%"
                                    alt="Download"
                                ></b-img>
                            </b-link>
                            <DiscreteProgress
                                style="padding: 20px 15% 10px 15%;"
                                :tasks="job.task_set"
                            ></DiscreteProgress>

                            <b-table
                                id="error-log"
                                striped
                                borderless
                                responsive="lg"
                                :items="job.status_set"
                                :fields="status_table.fields"
                                :per-page="status_table.perPage"
                                :sort-by.sync="status_table.sortBy"
                                :sort-desc.sync="status_table.sortDesc"
                            >
                                <span
                                    slot="description"
                                    slot-scope="data"
                                    v-html="data.value"
                                    class="align-left"
                                ></span>
                            </b-table>
                            <div id="error-count">
                                <span v-if="error_count > 0">
                                    There are {{ error_count }} warning(s) /
                                    error(s):
                                </span>
                                <b-button
                                    @click="
                                        status_table.perPage = status_table.perPage
                                            ? null
                                            : 1
                                    "
                                >
                                    {{ status_table.perPage ? 'Show' : 'Hide' }}
                                    Log
                                </b-button>
                            </div>
                        </b-col>
                    </b-row>
                </b-card>
            </div>
        </b-container>
    </div>
</template>

<script>
import DiscreteProgress from '@/components/DiscreteProgress.vue';
import JobApi from '@/services/apiV1/JobManager.js';
import moment from 'moment';

export default {
    name: 'Job',
    components: {
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
            },
            status_table: {
                sortBy: 'date',
                sortDesc: true,
                perPage: 1,
                fields: [
                    {
                        key: 'date',
                        label: 'Time',
                        sortable: true,
                        formatter: value => {
                            return moment(value).format('MM/DD/YY HH:mm');
                        }
                    },
                    {
                        key: 'state',
                        label: 'State',
                        formatter: value => {
                            switch (value) {
                                case 1:
                                    return 'Completed';
                                case 2:
                                    return 'Failed';
                                case 3:
                                    return 'OK';
                                case 4:
                                    return 'Warning';
                                case 5:
                                    return 'Created';
                            }
                        }
                    },
                    {
                        key: 'description',
                        formatter: value => {
                            return value.replace(/(?:\r\n|\r|\n)/g, '<br>');
                        },
                        tdClass: 'table-td'
                    }
                ]
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
        },
        error_count() {
            return this.job.status_set.filter(status => {
                return (status.state === 2) | (status.state === 4);
            }).length;
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY HH:mm');
        },
        resultsLink(job) {
            return JobApi.resultsLink(job.pk);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button

.table-td
    text-align: left


#error-log > thead
    display: none !important

#error-count
    padding-top: 10px
    float: right

</style>
