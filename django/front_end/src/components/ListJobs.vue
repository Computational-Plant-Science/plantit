<template>
    <div>
        <b-container>
            <b-row v-if="filterable">
                <b-col md="8" class="my-1">
                    <b-form-group label-cols-sm="2" label="Filter">
                        <b-input-group>
                            <b-form-input
                                v-model="filter"
                                placeholder="Type to Filter"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!filter"
                                    @click="filter = ''"
                                    >Clear</b-button
                                >
                            </b-input-group-append>
                        </b-input-group>
                    </b-form-group>
                </b-col>
            </b-row>

            <b-table
                selectable
                hover
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
                :items="items"
                :fields="fields"
                :per-page="perPage"
                :borderless="true"
                select-mode="single"
                :filter="filter"
                @row-selected="rowSelected"
            >
                <template slot="tasks" slot-scope="data">
                    <DiscreteProgress
                        :tasks="data.item.task_set"
                        :show-name="false"
                    ></DiscreteProgress>
                </template>
                <template slot="date_created" slot-scope="data">
                    {{ data.item.date_created | format_date }}
                </template>
                <template slot="pinned" slot-scope="data">
                    <b-button
                        class="plantit-btn"
                        size="sm"
                        @click="togglePin(data.item.pk, data.item)"
                    >
                        <b-img
                            v-if="data.item.pinned"
                            :src="require('@/assets/icons/pin icons/pin2.svg')"
                            width="30px"
                        >
                        </b-img>
                        <b-img
                            v-else
                            :src="require('@/assets/icons/pin icons/pin.svg')"
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
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import DiscreteProgress from './DiscreteProgress.vue';
import JobApi from '@/services/apiV1/JobManager.js';
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
                    if (value == true) {
                        JobApi.deleteJob(pk).then(value => {
                            if (value == true) {
                                this.items = this.items.filter(obj => {
                                    return obj.pk != pk;
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
                    key: 'collection',
                    sortable: true
                },
                {
                    key: 'tasks',
                    label: 'Progress',
                    sortable: false
                },
                {
                    key: 'date_created',
                    sortable: true
                },
                {
                    key: 'tools',
                    label: ''
                },
                {
                    key: 'pinned',
                    sortable: true
                }
            ],
            items: []
        };
    },
    mounted: function() {
        JobApi.getJobList().then(list => {
            this.items = list;
        });
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>
