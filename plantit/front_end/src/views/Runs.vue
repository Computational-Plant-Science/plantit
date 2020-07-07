<template>
    <div class="w-100 p-4">
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="dark"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h4>
                            Runs
                        </h4>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="runs_query"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="
                                        !runs_query
                                    "
                                    @click="
                                        runs_query = ''
                                    "
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
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
                        :items="runs"
                        :fields="fields"
                        :per-page="perPage"
                        :borderless="true"
                        select-mode="single"
                        :filter="filter"
                        class="table-responsive"
                        @row-selected="onRunSelected"
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
import Runs from '@/services/apiV1/RunManager.js';
import Pipelines from '@/services/apiV1/PipelineManager';
import moment from 'moment';

export default {
    name: 'Runs',
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
        statusToString(run) {
            let status = run.status_set[0].state;
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
        onPipelineSelected(pipeline) {
            this.$emit('pipelineSelected', pipeline);
        },
        onRunSelected: function(items) {
            this.$emit('runSelected', items[0].pk);
        },
        togglePin(pk, item) {
            Runs.pin(pk, !item.pinned).then(success => {
                if (success) {
                    item.pinned = !item.pinned;
                }
            });
        },
        delete(pk) {
            this.$bvModal
                .msgBoxConfirm(`Delete this run?`, {
                    title: 'Delete Run',
                    centered: true
                })
                .then(value => {
                    if (value === true) {
                        Runs.delete(pk).then(value => {
                            if (value === true) {
                                this.runs = this.runs.filter(obj => {
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
            runs_query: '',
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
                    key: 'pipeline_name',
                    label: 'Pipeline',
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
                    sortable: true
                }
            ],
            runs: [],
            pipelines: []
        };
    },
    mounted: function() {
        Runs.list().then(runs => {
            this.runs = runs;
        });
        Pipelines.list().then(pipelines => {
            this.pipelines = pipelines;
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
