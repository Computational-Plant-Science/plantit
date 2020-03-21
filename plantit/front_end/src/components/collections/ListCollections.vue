<template>
    <div class="w-100 p-2">
        <b-container>
            <b-row>
                <b-col>
                    <h4>Collections</h4>
                </b-col>
                <b-col v-if="filterable">
                    <b-form-group label-cols-sm="2">
                        <b-input-group>
                            <b-form-input
                                    v-model="filter"
                                    placeholder="Filter..."
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                        :disabled="!filter"
                                        @click="filter = ''"
                                >Clear
                                </b-button
                                >
                            </b-input-group-append>
                        </b-input-group>
                    </b-form-group>
                </b-col>
                <b-col md="auto">
                    <b-button variant="primary" to="collection/new">New</b-button>
                </b-col>
            </b-row>
            <hr>
            <b-table
                    show-empty
                    selectable
                    hover
                    :items="items"
                    :fields="fields"
                    striped responsive="sm"
                    :per-page="perPage"
                    :borderless="true"
                    select-mode="single"
                    :filter="filter"
                    class="table-responsive"
                    @row-selected="rowSelected"
                    :sort-by.sync="sortBy"
                    :sort-desc.sync="sortDesc">
                <template v-slot:cell(actions)="row">
                    <b-button size="sm" @click="view(row.item.pk)" class="mr-2 plantit-btn">
                        View
                    </b-button>
                    <b-button size="sm" @click="analyze(row.item.pk)" class="mr-2 plantit-btn">
                        Analyze
                    </b-button>
                </template>

                <template slot="pinned" slot-scope="data">
                    <b-button
                            size="sm"
                            @click="togglePin(data.item.pk, data.item)"
                            class="plantit-btn">
                        <b-img
                                v-if="data.item.pinned"
                                :src="require('@/assets/icons/pin icons/pin2.svg')"
                                width="30px">
                        </b-img>
                        <b-img
                                v-else
                                :src="require('@/assets/icons/pin icons/pin.svg')"
                                width="30px">
                        </b-img>
                    </b-button>
                </template>
                <template slot="tools" slot-scope="data">
                    <b-button
                            size="sm"
                            class="plantit-btn"
                            @click="deleteCollection(data.item.pk, data.item)"
                    >
                        <i class="fas fa-trash-alt fa-2x"></i>
                    </b-button>
                </template>
            </b-table>
        </b-container>
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
            rowSelected: function (items) {
                router.push({path: 'collection', query: {pk: items[0].pk}});
            },
            togglePin(pk, item) {
                CollectionApi.pin(pk, !item.pinned).then(success => {
                    if (success) {
                        item.pinned = !item.pinned;
                    }
                });
            },
            deleteCollection(pk, item) {
                this.$bvModal
                    .msgBoxConfirm(`Delete collection ${item.name}?`, {
                        title: 'Delete Confirmation',
                        centered: true
                    })
                    .then(value => {
                        if (value == true) {
                            CollectionApi.deleteCollection(pk).then(value => {
                                if (value == true) {
                                    this.items = this.items.filter(obj => {
                                        return obj.pk != pk;
                                    });
                                }
                            });
                        }
                    });
            },
            view(pk) {
                router.push({name: 'collection', query: {pk: pk}});
            },
            analyze(pk) {
                router.push({name: 'analyze', query: {pk: pk}});
            },
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
                        sortable: true,
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
        mounted: function () {
            CollectionApi.getCollectionList().then(list => {
                this.items = list;
            });
        }
    };
</script>
