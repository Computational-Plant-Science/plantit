<template>
    <div class="w-100 p-4">
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template slot="header">
                <b-row>
                    <b-col md="auto">
                        <h2>{{ pipeline.config.name }}</h2>
                    </b-col>
                    <b-col style="color:white">
                        <h3>
                            <b-badge variant="success" class="p-0 m-0 mr-2">{{
                                run.id
                            }}</b-badge>
                            <b-badge
                                variant="success"
                                class="p-0 m-0 ml-2 mr-2"
                            >
                                {{ run.cluster }}
                            </b-badge>
                            <b-badge
                                pill
                                class="ml-2 mr-2"
                                style="color: white"
                                :variant="
                                    error_count !== 0
                                        ? 'danger'
                                        : warning_error_count !== 0
                                        ? 'warning'
                                        : 'success'
                                "
                                >{{ statusToString(job_status)
                                }}<span v-if="warning_error_count > 0">
                                    with {{ warning_count }} warning(s) and
                                    {{ error_count }} error(s)
                                </span>
                            </b-badge>
                        </h3>
                    </b-col>
                </b-row>
            </template>
            <b-row no-gutters>
                <b-col
                    md="auto"
                    style="min-width: 8em; max-width: 8rem; min-height: 8rem; max-height: 8rem"
                >
                    <b-img
                        v-if="pipeline.icon_url"
                        style="max-width: 8rem"
                        :src="pipeline.icon_url"
                        right
                    >
                    </b-img>
                    <b-img
                        v-else
                        style="max-width: 8rem"
                        :src="require('../assets/logo.png')"
                        right
                    ></b-img>
                </b-col>
                <b-card-body>
                    <b-col>
                        <b-row>
                            <b-col>
                                {{ pipeline.repo.description }}
                            </b-col>
                        </b-row>
                        <br />
                        <b-row>
                            <b-col>
                                <b-row>
                                    <b-col>
                                        Author:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{ pipeline.config.author }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Image:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{ pipeline.config.image }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Clone:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{
                                            pipeline.config.clone ? 'Yes' : 'No'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Parameters:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{
                                            params.length === 0
                                                ? 'None'
                                                : params.length
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Input:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{
                                            pipeline.config.input
                                                ? pipeline.config.input.capitalize()
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Output:
                                    </b-col>
                                    <b-col cols="11">
                                        <b>{{
                                            pipeline.config.output
                                                ? pipeline.config.output.capitalize()
                                                : 'None'
                                        }}</b>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        Command:
                                    </b-col>
                                    <b-col cols="11">
                                        <b
                                            ><code>{{
                                                ' ' + pipeline.config.commands
                                            }}</code></b
                                        >
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-col>
                </b-card-body>
            </b-row>
        </b-card>
        <b-card
            bg-variant="white"
            header-bg-variant="white"
            footer-bg-variant="white"
            border-variant="white"
            footer-border-variant="white"
            header-border-variant="dark"
            class="mb-4"
        >
            <template slot="header">
                <b-row align-v="center">
                    <b-col>
                        <h4>Logs</h4>
                    </b-col>
                    <b-col md="auto" class="ml-0 pl-1">
                        <b-button
                            variant="outline-dark"
                            v-b-tooltip.hover
                            title="Refresh"
                            @click="reloadJob"
                        >
                            <i class="fas fa-redo"></i>
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <b-row>
                <b-col>
                    <b-alert
                        :show="reloadAlertDismissCountdown"
                        dismissible
                        variant="success"
                        @dismissed="reloadAlertDismissCountdown = 0"
                        @dismiss-count-down="countDownChanged"
                    >
                        <p>
                            Logs refreshed.
                        </p>
                    </b-alert>
                </b-col>
            </b-row>
            <b-row align-h="center" v-if="loadingRun">
                <b-spinner
                    type="grow"
                    label="Loading..."
                    variant="dark"
                ></b-spinner>
            </b-row>
            <b-row v-if="!loadingRun">
                <b-col>
                    <b-table
                        id="error-log"
                        striped
                        borderless
                        responsive="lg"
                        :items="run.status_set"
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
import Pipelines from '@/services/apiV1/PipelineManager';
import Users from '@/services/apiV1/UserManager';
import Runs from '@/services/apiV1/RunManager.js';
import moment from 'moment';

export default {
    name: 'Job',
    components: {},
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
            user: null,
            pipeline: null,
            loadingRun: false,
            run: {
                pipeline_owner: null,
                pipeline_name: null
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
            this.loadingRun = true;
            Runs.getRun(this.$router.currentRoute.params.id).then(run => {
                this.run = run;
                if (toast) this.showAlert();
                this.loadingRun = false;
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
        Runs.getRun(this.$router.currentRoute.params.id).then(r => {
            this.run = r;
            Users.getCurrentUser().then(user => {
                this.user = user;
                Pipelines.get(
                    this.run.pipeline_owner,
                    this.run.pipeline_name
                ).then(pipeline => {
                    this.pipeline = pipeline;
                    if (pipeline.config.params != null) {
                        this.params = pipeline.config.params.map(function(
                            param
                        ) {
                            return {
                                key: param,
                                value: ''
                            };
                        });
                    }
                });
            });
        });
    },
    computed: {
        job_status() {
            if (this.run.status_set.length > 0) {
                return this.run.status_set[0].state;
            } else {
                return 0;
            }
        },
        warning_count() {
            return this.run.status_set.filter(status => {
                return status.state === 4;
            }).length;
        },
        error_count() {
            return this.run.status_set.filter(status => {
                return status.state === 2;
            }).length;
        },
        warning_error_count() {
            return this.run.status_set.filter(status => {
                return status.state === 2 || status.state === 4;
            }).length;
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY HH:mm');
        },
        resultsLink() {
            return Runs.resultsLink(this.pk);
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
