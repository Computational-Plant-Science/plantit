<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h1>Community Datasets</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="communityFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!communityFilter"
                                    @click="communityFilter = ''"
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
                small
                sticky-header="true"
                selectable
                hover
                responsive="sm"
                :items="communityDatasets"
                :fields="fields"
                select-mode="single"
                :filter="communityFilter"
                :borderless="true"
                class="table-responsive"
                @row-selected="onSelected"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
            >
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
                        @click="onRemove(row.item)"
                        class="ml-2 mr-2"
                    >
                        Delete
                    </b-button>
                </template>
            </b-table>
        </b-card>
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h1>Your Datasets</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="userFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!userFilter"
                                    @click="userFilter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                    <b-col md="auto">
                        <b-button
                            variant="outline-dark"
                            v-b-tooltip.hover
                            title="Create a new dataset"
                            v-b-modal.modal-prevent-closing
                        >
                            <i class="fas fa-plus"></i>
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <b-table
                show-empty
                small
                sticky-header="true"
                selectable
                hover
                responsive="sm"
                :items="userDatasets"
                :fields="fields"
                select-mode="single"
                :filter="userFilter"
                :borderless="true"
                class="table-responsive"
                @row-selected="onSelected"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
            >
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
                        @click="onRemove(row.item)"
                        class="ml-2 mr-2"
                    >
                        Delete
                    </b-button>
                </template>
            </b-table>
        </b-card>
        <b-modal
            id="modal-prevent-closing"
            ref="modal"
            title="Create New Dataset"
            @show="resetModal"
            @hidden="resetModal"
            @ok="handleOk"
            hide-header-close
            cancel-variant="outline-danger"
            ok-variant="success"
        >
            <b-form-group>
                <b-form-group
                    :state="isValid(newDatasetName)"
                    label="Name"
                    label-for="name-input"
                    invalid-feedback="Name is required"
                >
                    <b-form-input
                        id="name-input"
                        v-model="newDatasetName"
                        :state="isValid(newDatasetName)"
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group
                    label="Description"
                    label-for="description-input"
                    invalid-feedback="Description is required"
                >
                    <b-form-input
                        id="description-input"
                        v-model="newDatasetDescription"
                        required
                    ></b-form-input>
                </b-form-group>
            </b-form-group>
        </b-modal>
    </div>
</template>

<script>
import router from '../router';
import Datasets from '@/services/apiV1/Datasets';

export default {
    name: 'Datasets',
    data() {
        return {
            newDatasetName: '',
            newDatasetDescription: '',
            communityFilter: '',
            userFilter: '',
            sortBy: 'pk',
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
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            communityDatasets: [],
            userDatasets: [],
            selected: {}
        };
    },
    methods: {
        reloadDatasets() {
            Datasets.listAll().then(list => {
                this.communityDatasets = list.community;
                this.userDatasets = list.user;
            });
        },
        isValid(str) {
            return str !== null && str !== undefined && str.length > 0;
        },
        onSelected(items) {
            router.push({
                name: 'dataset',
                params: { owner: items[0].owner, name: items[0].name }
            });
        },
        resetModal() {
            this.newDatasetName = '';
        },
        handleOk() {
            // bvModalEvt.preventDefault();
            Datasets.create(
                this.newDatasetName,
                this.newDatasetDescription
            ).then(dataset => {
                router.push({
                    name: 'dataset',
                    query: {
                        owner: dataset.dataset.owner,
                        name: dataset.dataset.name
                    }
                });
            });
        },
        onRemove(item) {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete dataset '${item.name}?'`,
                    {
                        title: 'Delete Dataset',
                        centered: true,
                        cancelVariant: 'outline-dark',
                        okVariant: 'outline-danger',
                        okTitle: 'Delete'
                    }
                )
                .then(value => {
                    if (value === true) {
                        Datasets.delete(item.pk).then(value => {
                            if (value === true) {
                                this.communityDatasets = this.communityDatasets.filter(
                                    obj => {
                                        return obj.pk !== item.pk;
                                    }
                                );
                                this.userDatasets = this.userDatasets.filter(
                                    obj => {
                                        return obj.pk !== item.pk;
                                    }
                                );
                            }
                        });
                    }
                });
        },
        onPin(item) {
            Datasets.pin(item.pk, !item.pinned).then(success => {
                if (success) {
                    item.pinned = !item.pinned;
                }
            });
        }
    },
    mounted: function() {
        this.reloadDatasets();
    },
};
</script>
