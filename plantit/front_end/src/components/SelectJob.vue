<template>
    <div class="w-100 pb-4">
        <b-card header-bg-variant="dark" border-variant="dark">
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col class="mt-2" style="color: white">
                        <h5>Select Job...</h5>
                    </b-col>
                    <b-col md="auto" v-if="filterable">
                        <b-input-group class="b-form-input">
                            <b-form-input
                                v-model="filter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter"
                                    @click="filter = ''"
                                    variant="dark"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                    <b-col md="auto">
                        <b-dropdown
                            variant="dark"
                            to="workflow/new"
                            v-b-tooltip.hover
                            title="Start a new job"
                            right
                            data-toggle="dropdown"
                        >
                            <template v-slot:button-content>
                                <i class="fas fa-plus"></i>
                            </template>
                            <b-dropdown-header>Select Workflow...</b-dropdown-header>
                            <b-dropdown-item
                                v-for="workflow in workflows"
                                :key="workflow.name"
                                :to="{
                                    name: 'submit_workflow',
                                    query: {
                                        collection_pk: workflow.pk,
                                        workflow_name: workflow.app_name
                                    }
                                }"
                            >
                                {{workflow.name}}
                            </b-dropdown-item>
                        </b-dropdown>
                    </b-col>
                </b-row>
            </template>
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
                        <template slot="tasks" slot-scope="data">
                            <DiscreteProgress
                                :tasks="data.item.task_set"
                                :show-name="false"
                            ></DiscreteProgress>
                        </template>
                        <template slot="pinned" slot-scope="data">
                            <b-button
                                class="plantit-btn"
                                size="sm"
                                @click="togglePin(data.item.pk, data.item)"
                            >
                                <b-img
                                    v-if="data.item.pinned"
                                    :src="
                                        require('@/assets/icons/pin icons/pin2.svg')
                                    "
                                    width="30px"
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    :src="
                                        require('@/assets/icons/pin icons/pin.svg')
                                    "
                                    width="30px"
                                >
                                </b-img>
                            </b-button>
                        </template>
                        <template slot="tools" slot-scope="data">
                            <b-button
                                class="plantit-btn"
                                size="sm"
                                @click="deleteJob(data.item.pk)"
                            >
                                <i class="fas fa-trash-alt fa-2x"></i>
                            </b-button>
                        </template>
                    </b-table>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import router from '../router';
import DiscreteProgress from './DiscreteProgress.vue';
import JobApi from '@/services/apiV1/JobManager.js';
import WorkflowAPI from '@/services/apiV1/WorkflowManager';
import moment from 'moment';

export default {
    name: 'ListJobs',
    components: {
        DiscreteProgress
    },
    props: {
        perPage: {
            default: 0
        },
        filterable: {
            default: false
        }
    },
    methods: {
        rowSelected: function(items) {
            router.push({ path: 'job', query: { pk: items[0].pk } });
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
                    key: 'collection',
                    sortable: true
                },
                {
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
                },
                {
                    key: 'cluster',
                    sortable: true
                },
                {
                    key: 'tasks',
                    label: 'Status',
                    sortable: false
                },
                {
                    key: 'date_created',
                    sortable: true,
                    formatter: value => {
                        return moment(value).format('MM/DD/YY HH:mm');
                    }
                },
                {
                    key: 'tools',
                    label: ''
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
@import '../scss/_colors.sass'

</style>
