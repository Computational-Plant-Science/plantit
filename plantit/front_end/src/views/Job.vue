<template>
    <div>
        <b-card header-bg-variant="dark" border-variant="white">
            <template
                v-slot:header
                v-bind:job="this.job"
                style="background-color: white"
            >
                <b-row>
                    <b-col class="mt-2" style="color:white">
                        <h5>
                            <i class="fas fa-terminal green"></i>
                            Job
                            <b-badge
                                pill
                                variant="dark"
                                class="green p-0 m-0 ml-1 mr-1"
                                >{{ job.pk }}</b-badge
                            >
                            <b-badge
                                pill
                                class="ml-1 mr-1"
                                :variant="
                                    job_status === 2
                                        ? 'danger'
                                        : job_status === 4
                                        ? 'warning'
                                        : 'success'
                                "
                                >{{ statusToString(job_status) }}<span v-if="warning_error_count > 0">
                            with {{ warning_count }} warning(s) and {{ error_count }} error(s)
                        </span>
                            </b-badge
                            >
                        </h5>
                    </b-col>
                    <b-col md="auto" class="mr-0 pr-1">
                        <b-button
                                variant="dark"
                            @click="
                                status_table.perPage = status_table.perPage
                                    ? null
                                    : 1
                            "
                        >
                            {{ status_table.perPage ? 'Show' : 'Hide' }}
                            Logs
                        </b-button>
                    </b-col>
                    <b-col md="auto" class="ml-0 pl-1">
                        <b-button
                            variant="dark"
                            v-b-tooltip.hover
                            title="Reload job info"
                            @click="reloadJob"
                        >
                            <i class="fas fa-redo"></i>
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <b-row>
                <b-col>
                    <p><b>Workflow:</b> {{ job.workflow_name }}</p>
                    <p><b>Collection:</b> {{ job.collection }}</p>
                    <p><b>Cluster:</b> {{ job.cluster }}</p>
                    <p>
                        <b>Created:</b> {{ job.date_created | format_date
                        }}<br />
                    </p>
                </b-col>
                <b-col>
                    <b-alert
                        :show="reloadAlertDismissCountdown"
                        dismissible
                        variant="success"
                        @dismissed="reloadAlertDismissCountdown = 0"
                        @dismiss-count-down="countDownChanged"
                    >
                        <p>
                            Job info reloaded.
                        </p>
                        <b-progress
                            variant="dark"
                            :max="reloadAlertDismissSeconds"
                            :value="reloadAlertDismissCountdown"
                            height="2px"
                        ></b-progress>
                    </b-alert>
                </b-col>
            </b-row>
            <b-row>
                <b-col class="text-center p-5">
                    <b-img
                        v-if="job_status !== 1 && job_status !== 2"
                        :src="require('../assets/PlantITLoading.gif')"
                        width="250%"
                        alt="Plant IT"
                    ></b-img>
                    <b-link v-else-if="job_status === 1" :href="job | resultsLink">
                        <b-img
                            :src="require('../assets/icons/download.png')"
                            width="250%"
                            alt="Download"
                        ></b-img>
                    </b-link>
                    <i v-else class="fas fa-bug fa-6x red"></i>
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
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import JobApi from '@/services/apiV1/JobManager.js';
import moment from 'moment';

export default {
    name: 'Job',
    components: {
    },
    props: {
        pk: {
            required: true
        }
    },
    data() {
        return {
            reloadAlertDismissSeconds: 5,
            reloadAlertDismissCountdown: 0,
            showReloadAlert: false,
            job: {
                pk: null,
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
    methods: {
        reloadJob(toast) {
            JobApi.getJob(this.pk).then(data => {
                this.job = data;
                if (toast) this.showAlert();
            });
        },
        countDownChanged(dismissCountDown) {
            this.reloadAlertDismissCountdown = dismissCountDown;
        },
        showAlert() {
            this.reloadAlertDismissCountdown = this.reloadAlertDismissSeconds;
        },
        statusToString(status) {
            switch (status) {
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
    mounted: function() {
        this.reloadJob();
    },
    computed: {
        job_status() {
            if (this.job.status_set.length > 0) {
                return this.job.status_set[0].state;
            } else {
                return '';
            }
        },
        warning_count() {
            return this.job.status_set.filter(status => {
                return status.state === 4;
            }).length;
        },
        error_count() {
            return this.job.status_set.filter(status => {
                return status.state === 2;
            }).length;
        },
        warning_error_count() {
            return this.job.status_set.filter(status => {
                return status.state === 2 || status.state === 4;
            }).length;
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY HH:mm');
        },
        resultsLink() {
            return JobApi.resultsLink(this.pk);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button

.red
    color: $red

.table-td
    text-align: left


#error-log > thead
    display: none !important

#error-count
    padding-top: 10px
    float: right
</style>
