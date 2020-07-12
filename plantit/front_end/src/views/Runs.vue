<template>
    <div class="w-100 p-4">
        <b-card
            header-bg-variant="white"
            border-variant="dark"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h2>
                            <b>
                                Your Runs
                            </b>
                        </h2>
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
                                    :disabled="!runs_query"
                                    @click="runs_query = ''"
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
                        style="min-height: 100%"
                        :borderless="true"
                        select-mode="single"
                        :filter="filter"
                        class="table-responsive"
                        @row-selected="onRunSelected"
                    >
                    </b-table>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import Runs from '@/services/apiV1/RunManager.js';
import moment from 'moment';
import router from '../router';

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
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id
                }
            });
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
                    key: 'id',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return `${moment(value).fromNow()} (${moment(
                            value
                        ).format('MMMM Do YYYY, h:mm a')})`;
                    }
                },
                {
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
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
                                return 'Running';
                            case 4:
                                return 'Created';
                        }
                    }
                }
            ],
            runs: []
        };
    },
    mounted: function() {
        Runs.list().then(runs => {
            this.runs = runs;
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
