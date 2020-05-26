<template>
    <div class="w-100 pb-4">
        <b-card>
            <template v-slot:header style="background-color: white">
                <b-row>
                    <b-col class="mt-2" style="color: white">
                        <h5><i class="fas fa-terminal text-dark"></i> Jobs</h5>
                    </b-col>
                    <b-col md="auto" v-if="filterable" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="filter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter"
                                    @click="filter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                    <b-col md="auto">
                        <b-dropdown
                            variant="outline-dark"
                            to="workflow/new"
                            v-b-tooltip.hover
                            title="Start a new job"
                            right
                            data-toggle="dropdown"
                        >
                            <template v-slot:button-content>
                                <i class="fas fa-plus"></i>
                            </template>
                            <b-dropdown-header
                                >Select Workflow...</b-dropdown-header
                            >
                            <b-dropdown-item
                                v-for="workflow in workflows"
                                :key="workflow.name"
                                @click="workflowSelected"
                            >
                                {{ workflow.name }}
                            </b-dropdown-item>
                        </b-dropdown>
                    </b-col>
                </b-row>
            </template>
            <p>
                To start a new job, click
                <i class="fas fa-plus"></i> or go to the
                <i class="fas fa-stream mr-1"></i>
                <b>Workflows</b>
                tab. Select an existing job to view logs and results.
            </p>
            <b-row>
                <b-col>
                    <b-table
                        show-empty
                        small
                        sticky-header="true"
                        selectable
                        hover
                        responsive="sm"
                        :sort-by.sync="sortBy"
                        :sort-desc.sync="sortDesc"
                        :items="items"
                        :fields="fields"
                        :per-page="perPage"
                        :borderless="true"
                        select-mode="single"
                        :filter="filter"
                        class="table-responsive"
                        @row-selected="rowSelected"
                    >
                        <template v-slot:cell(status_set[0].state)="data">
                            <b>{{ data.value }}</b>
                        </template>
                    </b-table>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import JobApi from '@/services/apiV1/JobManager.js';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import moment from 'moment';

export default {
    name: 'ListJobs',
    components: {},
    props: {
        perPage: {
            default: 0
        },
        filterable: {
            default: false
        }
    },
    methods: {
        statusToString(job) {
            let status = job.status_set[0].state;
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
        },
        workflowSelected(workflow) {
            this.$emit('workflowSelected', workflow);
        },
        rowSelected: function(items) {
            //router.push({ path: 'job', query: { pk: items[0].pk } });
            this.$emit('jobSelected', items[0].pk);
        },
        togglePin(pk, item) {
            JobApi.pin(pk, !item.pinned).then(success => {
                if (success) {
                    item.pinned = !item.pinned;
                }
            });
        },
        deleteJob(pk) {
            this.$bvModal
                .msgBoxConfirm(`Delete this job?`, {
                    title: 'Delete Job',
                    centered: true
                })
                .then(value => {
                    if (value === true) {
                        JobApi.deleteJob(pk).then(value => {
                            if (value === true) {
                                this.items = this.items.filter(obj => {
                                    return obj.pk !== pk;
                                });
                            }
                        });
                    }
                });
        }
    },
    data() {
        return {
            sortBy: 'date',
            sortDesc: true,
            filter: '',
            fields: [
                {
                    key: 'pk',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return moment(value).format('MM/DD/YY HH:mm');
                    }
                },
                {
                    key: 'status_set[0].state',
                    label: 'Status',
                    formatter: status => {
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
                {
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
                },
                {
                    key: 'collection',
                    sortable: true
                },
                {
                    key: 'cluster',
                    sortable: true
                },
                {
                    key: 'work_dir',
                    label: 'Directory',
                    sortable: true,
                },
            ],
            items: [],
            workflows: []
        };
    },
    mounted: function() {
        JobApi.getJobList().then(list => {
            this.items = list;
        });
        WorkflowAPI.getWorkflows().then(workflows => {
            this.workflows = workflows;
        });
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
