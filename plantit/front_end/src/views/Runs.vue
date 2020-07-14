<template>
    <div class="w-100 p-4">
        <b-row>
            <b-col>
                <b-card
                    header-bg-variant="white"
                    border-variant="dark"
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h1>
                                    Your Runs
                                </h1>
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
                    <b-table
                        show-empty
                        sticky-header="true"
                        selectable
                        hover
                        small
                        responsive="sm"
                        :sort-by.sync="sortBy"
                        :sort-desc.sync="sortDesc"
                        :items="runs"
                        :fields="fields"
                        borderless
                        select-mode="single"
                        :filter="filter"
                        @row-selected="onRunSelected"
                    >
                        <template v-slot:cell(state)="run">
                            <h4>
                                <b-badge
                                    :variant="
                                        run.item.state === 2
                                            ? 'danger'
                                            : 'success'
                                    "
                                    >{{ statusToString(run.item.state) }}
                                </b-badge>
                            </h4>
                        </template>
                    </b-table>
                </b-card>
            </b-col>
        </b-row>
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
            default: 50
        },
        filterable: {
            default: false
        }
    },
    methods: {
        statusToString(status) {
            switch (status) {
                case 1:
                    return 'Completed';
                case 2:
                    return 'Failed';
                case 3:
                    return 'Running';
                case 4:
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
                    key: 'state',
                    label: 'State'
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
