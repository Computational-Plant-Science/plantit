<template>
    <div>
        <b-tabs content-class="mt-3">
            <b-tab title="Dataset" active>
                <b-card
                    header-bg-variant="white"
                    border-variant="white"
                    header-border-variant="white"
                >
                    <template v-slot:header style="background-color: white">
                        <b-row align-v="center">
                            <b-col style="color: white">
                                <h5>Community Datasets</h5>
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
                                <h5>Your Datasets</h5>
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
                    </b-table>
                </b-card>
            </b-tab>
            <b-tab title="Custom iRODS connection">
                <b-row>
                    <b-col>
                        <b>Configure iRODS connection.</b>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col> Username </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            v-model="username"
                            placeholder="Enter a value for 'username'"
                        ></b-form-input>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col> Password </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            type="password"
                            v-model="password"
                            placeholder="Enter a value for 'password'"
                        ></b-form-input>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col> Host </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            v-model="host"
                            placeholder="Enter a value for 'host'"
                        ></b-form-input>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col> Port </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            v-model="port"
                            placeholder="Enter a value for 'port'"
                        ></b-form-input>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col> Zone </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            v-model="zone"
                            placeholder="Enter a value for 'zone'"
                        ></b-form-input>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col>
                        <b>Configure iRODS path.</b>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col> iRODS Path </b-col>
                    <b-col cols="10">
                        <b-form-input
                            size="sm"
                            v-model="irods_path"
                            placeholder="Enter a path."
                        ></b-form-input>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col>
                        <b-button @click="listFiles()" variant="success" block>
                            Verify
                        </b-button>
                    </b-col>
                </b-row>
                <br />
                <b-row>
                    <b-col>
                        <b-alert
                            v-model="irodsConfigIncomplete"
                            variant="warning"
                            >iRODS configuration incomplete.</b-alert
                        >
                    </b-col>
                </b-row>
                <b-row align-h="center" v-if="filesLoading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="dark"
                    ></b-spinner>
                </b-row>
                <b-row align-h="center" v-for="file in files" :key="file">
                    <b-col class="text-center">
                        {{ file }}
                    </b-col>
                </b-row>
            </b-tab>
        </b-tabs>
    </div>
</template>

<script>
import Datasets from '@/services/apiV1/Datasets';

export default {
    name: 'EditInput',
    props: {
        kind: {
            required: true,
            type: String
        }
    },
    data() {
        return {
            username: '',
            password: '',
            host: '',
            port: '',
            zone: '',
            irods_path: '',
            files: [],
            filesLoading: false,
            irodsConfigIncomplete: false,
            communityDatasets: [],
            userDatasets: [],
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
            communityFilter: '',
            userFilter: ''
        };
    },
    mounted() {
        this.reloadDatasets();
    },
    methods: {
        reloadDatasets() {
            Datasets.listAll().then(list => {
                this.communityDatasets = list.community;
                this.userDatasets = list.user;
            });
        },
        onSelected(items) {
            alert(`Selected ${items[0].name}`);
            // router.push({
            //     name: 'dataset',
            //     params: { owner: items[0].owner, name: items[0].name }
            // });
        },
        listFiles() {
            if (
                !(
                    this.username &&
                    this.password &&
                    this.host &&
                    this.port &&
                    this.zone &&
                    this.irods_path
                )
            ) {
                this.irodsConfigIncomplete = true;
            } else {
                this.irodsConfigIncomplete = false;
                this.filesLoading = true;
                Datasets.listFilesForCustomIrodsConnection(
                    this.username,
                    this.password,
                    this.host,
                    this.port,
                    this.zone,
                    this.irods_path
                ).then(files => {
                    this.files = files.files;
                    this.filesLoading = false;
                    if (this.files.length > 0) {
                        this.$emit('inputSelected', {
                            kind: this.kind,
                            username: this.username,
                            password: this.password,
                            host: this.host,
                            port: this.port,
                            zone: this.zone,
                            irods_path: this.irods_path,
                            files: this.files
                        });
                    }
                });
            }
        }
    }
};
</script>

<style scoped></style>
