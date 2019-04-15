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
                striped
                hover
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
                :items="items"
                :fields="fields"
                :per-page="perPage"
                :borderless="true"
                :striped="false"
                select-mode="single"
                :filter="filter"
                @row-selected="rowSelected"
            >
                <template slot="analyze" slot-scope="data">
                    <b-link
                        :to="{
                            name: 'analyze',
                            query: { pk: data.item.pk }
                        }"
                    >
                      Analyze
                    </b-link>
                </template>
                <template slot="pinned" slot-scope="data">
                  <b-button
                      size="sm"
                      @click="
                          data.item.pinned = data.item.pinned ? false : true
                      "
                  >
                    <b-img
                      v-if="data.item.pinned"
                      @click="data.item.pinned = true"
                      :src="require('@/assets/pin icons/pin2.svg')"
                      width="30px">
                    </b-img>
                    <b-img
                      v-else
                      :src="require('@/assets/pin icons/pin.svg')"
                      @click="data.item.pinned = false"
                      width="30px">
                    </b-img>
                  </b-button>
                </template>
            </b-table>
        </b-container>
    </div>
</template>

<script>
import router from '@/router';

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
        }
    },
    data() {
        return {
            filter: '',
            sortBy: 'date',
            sortDesc: true,
            fields: [
                {
                    key: 'name',
                    sortable: true
                },
                {
                    key: 'analyze',
                    label: ''
                },
                {
                    key: 'date',
                    label: 'Created',
                    sortable: true
                },
                {
                    key: 'pinned',
                    sortable: true
                }
            ],
            items: [
                { name: 'test', pinned: true, date: 2, pk: 1 },
                { name: 'testa', pinned: true, date: 122, pk: 2 },
                { name: 'testga', pinned: false, date: 112, pk: 3 },
                { name: 'testd', pinned: false, date: 132, pk: 4 },
                { name: 'tesat', pinned: false, date: 1, pk: 5 },
                { name: 'te22st', pinned: false, date: 11, pk: 6 }
            ]
        };
    }
};
</script>
