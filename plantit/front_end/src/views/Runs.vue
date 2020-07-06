<template>
    <div class="w-100 p-4">
        <p>
            Select a <b-badge variant="white"><i class="fas fa-terminal text-dark"></i> Run</b-badge> to
            view logs and results. To start a new
            <b-badge variant="white"><i class="fas fa-terminal text-dark"></i> Run</b-badge>, go to the
            <b-badge variant="white"><i class="fas fa-stream text-dark"></i> Pipelines</b-badge>
            page.
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
