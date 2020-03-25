<template>
    <div class="w-100 p-2 pb-4">
        <b-card>
            <b-row>
                <b-col>
                    <h4>Collections</h4>
                </b-col>
                <b-col md="auto" v-if="filterable">
                    <b-input-group>
                        <b-form-input
                            v-model="filter"
                            placeholder="Filter..."
                        ></b-form-input>
                        <b-input-group-append>
                            <b-button :disabled="!filter" @click="filter = ''"
                                >Clear
                            </b-button>
                        </b-input-group-append>
                    </b-input-group>
                </b-col>
                <b-col md="auto">
                    <b-button class="plantit-btn" to="collection/new">New</b-button>
                </b-col>
            </b-row>
            <br>
            <b-row>
                <b-col>
                    <b-table
                        show-empty
                        small
                        sticky-header="true"
                        head-variant="light"
                        selectable
                        hover
                        :items="items"
                        :fields="fields"
                        responsive="sm"
                        :per-page="perPage"
                        select-mode="single"
                        :filter="filter"
                        class="table-responsive"
                        @row-selected="rowSelected"
                        :sort-by.sync="sortBy"
                        :sort-desc.sync="sortDesc"
                    >
                        <template v-slot:cell(actions)="row">
                            <b-button
                                size="sm"
                                @click="view(row.item.pk)"
                                class="mr-2 plantit-btn"
                            >
                                View
                            </b-button>
                            <b-button
                                size="sm"
                                @click="analyze(row.item.pk)"
                                class="mr-2 plantit-btn"
                            >
                                Analyze
                            </b-button>
                            <b-button
                                size="sm"
                                variant="danger"
                                @click="remove(row.item)"
                                class="mr-2"
                            >
                                Delete
                            </b-button>
                            <b-button
                                size="sm"
                                @click="togglePin(row.item)"
                                class="mr-2 plantit-btn"
                            >
                                <b-img
                                    v-if="row.item.pinned"
                                    :src="
                                        require('@/assets/icons/pin icons/pin2.svg')
                                    "
                                    width="18px"
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    :src="
                                        require('@/assets/icons/pin icons/pin.svg')
                                    "
                                    width="18px"
                                >
                                </b-img>
                            </b-button>
                        </template>
                    </b-table>
                </b-col>
            </b-row>
        </b-card>
    </div>
</template>

<script>
import router from '@/router';
import CollectionApi from '@/services/apiV1/CollectionManager';

export default {
    name: 'ListCollections',
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
        rowSelected: function(items) {
            router.push({ path: 'collection', query: { pk: items[0].pk } });
        },
        view(pk) {
            router.push({ name: 'collection', query: { pk: pk } });
        },
        analyze(pk) {
            router.push({ name: 'analyze', query: { pk: pk } });
        },
        remove(item) {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete collection '${item.name}?'`,
                    {
                        title: 'Delete Collection',
                        centered: true,
                        okVariant: 'danger',
                        okTitle: 'Delete'
                    }
                )
                .then(value => {
                    if (value === true) {
                        CollectionApi.deleteCollection(item.pk).then(value => {
                            if (value === true) {
                                this.items = this.items.filter(obj => {
                                    return obj.pk !== item.pk;
                                });
                            }
                        });
                    }
                });
        },
        togglePin(item) {
            CollectionApi.pin(item.pk, !item.pinned).then(success => {
                if (success) {
                    item.pinned = !item.pinned;
                }
            });
        }
    },
    data() {
        return {
            filter: '',
            sortBy: 'date',
            sortDesc: true,
            fields: [
                {
                    key: 'pk',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'name',
                    sortable: true
                },
                {
                    key: 'pinned',
                    sortable: true
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            items: []
        };
    },
    mounted: function() {
        CollectionApi.getCollectionList().then(list => {
            this.items = list;
        });
    }
};
</script>
