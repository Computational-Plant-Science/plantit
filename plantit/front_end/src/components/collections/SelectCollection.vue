<template>
    <div class="w-100">
        <b-card
            header-bg-variant="dark"
            footer-bg-variant="white"
            border-variant="white"
        >
            <template
                    v-slot:header
                  style="background-color: white">
                <b-row>
                    <b-col class="mt-2" style="color: white">
                        <h5>
                            <i class="fas fa-layer-group green"></i> Collections
                        </h5>
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
                                    variant="dark"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                    <b-col md="auto">
                        <b-button
                            variant="dark"
                            to="/user/collection/new"
                            v-b-tooltip.hover
                            title="Create a new collection"
                        >
                            <i class="fas fa-plus"></i>
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <p v-if="selectable">
                Select a collection.
            </p>
            <p v-else>
                To create a new collection , click
                <i class="fas fa-plus"></i>. Select an existing collection to
                edit metadata and upload samples.
            </p>
            <b-table
                show-empty
                small
                sticky-header="true"
                selectable
                hover
                responsive="sm"
                :items="items"
                :fields="fields"
                :per-page="perPage"
                select-mode="single"
                :filter="filter"
                :borderless="true"
                class="table-responsive"
                @row-selected="rowSelected"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
            >
                <template v-slot:cell(samples)="row">
                    <b>{{ row.item.sample_set.length }}</b>
                </template>
                <template v-slot:cell(actions)="row">
                    <!--<b-button
                                size="sm"
                                @click="togglePin(row.item)"
                                variant="dark"
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
                            </b-button>-->
                    <b-button
                        size="sm"
                        variant="outline-danger"
                        @click="remove(row.item)"
                        class="ml-2 mr-2"
                    >
                        Delete
                    </b-button>
                </template>
            </b-table>
            <template
                v-slot:footer
                style="background-color: white"
                v-if="selectable"
            >
                <b-row align-v="center">
                    <b-col>
                        Selected:
                        {{ any_selected > 0 ? selected.name : '(none)' }}
                    </b-col>
                </b-row>
            </template>
        </b-card>
    </div>
</template>

<script>
import CollectionApi from '@/services/apiV1/CollectionManager';

export default {
    name: 'ListCollections',
    components: {},
    props: {
        selectable: {
            default: false
        },
        perPage: {
            default: 0
        },
        filterable: {
            default: false
        }
    },
    computed: {
        any_selected: function() {
            return Object.keys(this.selected).length > 0;
        }
    },
    methods: {
        rowSelected: function(items) {
            this.selected = items[0];
            this.$emit('selected', this.selected);
        },
        remove(item) {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete collection '${item.name}?'`,
                    {
                        title: 'Delete Collection',
                        centered: true,
                        cancelVariant: 'outline-dark',
                        okVariant: 'outline-danger',
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
        }
        // togglePin(item) {
        //     CollectionApi.pin(item.pk, !item.pinned).then(success => {
        //         if (success) {
        //             item.pinned = !item.pinned;
        //         }
        //     });
        // }
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
                    key: 'samples',
                    sortable: true
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            items: [],
            selected: {}
        };
    },
    mounted: function() {
        CollectionApi.getCollectionList().then(list => {
            this.items = list;
        });
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.green
    color: $color-button

.color
    color: $color-button
    //border-left: 5px solid $color-button
    vertical-align: middle
</style>
