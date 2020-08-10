<template>
    <div class="w-100">
        <b-card>
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
