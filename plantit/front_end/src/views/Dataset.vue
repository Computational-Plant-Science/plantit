<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <div v-if="datasetNotFound">
            <b-row align-content="center">
                <b-col>
                    <h5 class="text-center">
                        This page does not exist.
                    </h5>
                </b-col>
            </b-row>
        </div>
        <div v-if="!datasetNotFound">
            <b-row>
                <b-col>
                    <b-card
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="white"
                        class="overflow-hidden"
                    >
                        <b-row align-h="center" v-if="loadingDataset">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="dark"
                            ></b-spinner>
                        </b-row>
                        <template
                            v-slot:header
                            v-bind:collection="this.collection"
                            style="background-color: white"
                        >
                            <b-row no-gutters>
                                <b-col>
                                    <b-row>
                                        <b-col class="mr-0">
                                            <h1>
                                                Dataset
                                                <b>{{ collection.name }}</b>
                                            </h1>
                                        </b-col>
                                        <b-col
                                            align-self="center"
                                            md="auto"
                                            class="mr-0 pr-0"
                                        >
                                            <b-button
                                                id="edit-description-btn"
                                                @click="
                                                    $bvModal.show(
                                                        'editDescriptionModal'
                                                    )
                                                "
                                                variant="outline-dark"
                                            >
                                                <i class="far fa-edit"></i> Edit
                                                Description
                                            </b-button>
                                        </b-col>
                                        <b-col align-self="center" md="auto">
                                            <b-button
                                                variant="outline-danger"
                                                @click="remove()"
                                            >
                                                <i class="fas fa-trash"></i>
                                                Delete Dataset
                                            </b-button>
                                        </b-col>
                                    </b-row>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row>
                            <b-col>
                                {{ collection.description }}
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <b-card
                        bg-variant="white"
                        header-bg-variant="white"
                        footer-bg-variant="white"
                        border-variant="white"
                        footer-border-variant="white"
                        header-border-variant="white"
                    >
                        <template slot="header">
                            <b-row>
                                <b-col align-self="center">
                                    <h2>Metadata</h2>
                                </b-col>
                                <b-col align-self="center" md="auto">
                                    <b-form-input
                                        v-model="newMetadatumKey"
                                        placeholder="Enter a key."
                                    ></b-form-input>
                                </b-col>
                                <b-col align-self="center" md="auto">
                                    <b-form-input
                                        v-model="newMetadatumValue"
                                        placeholder="Enter a value."
                                    ></b-form-input>
                                </b-col>
                                <b-col align-self="center" md="auto">
                                    <b-button
                                        size="md"
                                        @click="addMetadatum"
                                        variant="success"
                                    >
                                        <i class="fas fa-plus"></i> Add
                                    </b-button>
                                </b-col>
                                <b-col align-self="center" md="auto">
                                    <b-button
                                        :disabled="!metadataChanged"
                                        @click="saveMetadata"
                                        variant="warning"
                                    >
                                        Save Metadata
                                    </b-button>
                                </b-col>
                            </b-row>
                        </template>
                        <b-row>
                            <b-col>
                                <b-table
                                    :fields="metadataFields"
                                    :items="metadata"
                                    responsive="sm"
                                    borderless
                                    small
                                    sticky-header="true"
                                >
                                    <template v-slot:cell(key)="datum">
                                        {{ datum.item.key }}
                                    </template>
                                    <template v-slot:cell(value)="datum">
                                        {{ datum.item.value }}
                                    </template>
                                    <template v-slot:cell(actions)="datum">
                                        <b-button
                                            size="md"
                                            @click="removeMetadatum(datum)"
                                            variant="outline-danger"
                                        >
                                            Delete
                                        </b-button>
                                    </template>
                                </b-table>
                                <b-row
                                    align-h="center"
                                    v-if="metadata.length === 0"
                                >
                                    <b-col
                                        align-self="center"
                                        class="text-center"
                                    >
                                        None to show.
                                    </b-col>
                                </b-row>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <div
                        v-show="$refs.upload && $refs.upload.dropActive"
                        class="drop-active"
                    >
                        <h3>Drop files to upload</h3>
                    </div>
                    <b-overlay
                        :show="show"
                        rounded="sm"
                        @shown="onShown"
                        @hidden="onHidden"
                    >
                        <template v-slot:overlay>
                            <div class="text-center">
                                <p
                                    v-if="
                                        $refs.upload && !$refs.upload.uploaded
                                    "
                                >
                                    Upload in progress...
                                </p>
                                <p v-if="$refs.upload && $refs.upload.uploaded">
                                    Upload complete.
                                </p>
                                <b-button
                                    v-if="
                                        $refs.upload && !$refs.upload.uploaded
                                    "
                                    ref="cancel"
                                    size="sm"
                                    variant="outline-danger"
                                    aria-describedby="cancel-label"
                                    @click="show = false"
                                >
                                    Cancel
                                </b-button>
                                <b-button
                                    v-else-if="
                                        $refs.upload && $refs.upload.uploaded
                                    "
                                    class="plantit-btn"
                                    size="sm"
                                    aria-describedby="ok-label"
                                    @click="show = false"
                                >
                                    Ok
                                </b-button>
                            </div>
                        </template>
                        <b-card
                            bg-variant="white"
                            header-bg-variant="white"
                            footer-bg-variant="white"
                            border-variant="white"
                            footer-border-variant="white"
                            header-border-variant="white"
                        >
                            <template slot="header">
                                <b-row>
                                    <b-col align-self="center" class="mr-0">
                                        <h2>Files</h2>
                                    </b-col>
                                    <b-col align-self="center" md="auto">
                                        <vue-upload
                                            class="btn btn-success"
                                            v-model="filesToUpload"
                                            :multiple="true"
                                            :drop="true"
                                            :drop-directory="true"
                                            :headers="headers"
                                            :postAction="postUrl"
                                            ref="upload"
                                            @input-file="inputFile"
                                            @input-filter="inputFilter"
                                        >
                                            <i class="fas fa-plus"></i> Add
                                        </vue-upload>
                                    </b-col>
                                    <!--<b-col
                                        align-self="center"
                                        md="auto"
                                        v-if="
                                            filesToUpload.length > 0 &&
                                                (!$refs.upload ||
                                                    !$refs.upload.active)
                                        "
                                    >
                                        <b-button
                                            type="button"
                                            class="btn btn-success"
                                            @click.prevent="
                                                $refs.upload.active = true
                                            "
                                        >
                                            <i
                                                class="fa fa-arrow-up"
                                                aria-hidden="true"
                                            ></i>
                                            Start Upload
                                        </b-button>
                                    </b-col>
                                    <b-col
                                        align-self="center"
                                        md="auto"
                                        v-if="
                                            filesToUpload.length > 0 &&
                                                !(
                                                    !$refs.upload ||
                                                    !$refs.upload.active
                                                )
                                        "
                                    >
                                        <button
                                            type="button"
                                            class="btn btn-danger"
                                            @click.prevent="
                                                $refs.upload.active = false
                                            "
                                        >
                                            <i
                                                class="fa fa-stop"
                                                aria-hidden="true"
                                            ></i>
                                            Stop Upload
                                        </button>
                                    </b-col>-->
                                </b-row>
                            </template>
                            <b-row>
                                <b-col>
                                    <b-table>
                                        <b-thead>
                                            <b-tr>
                                                <b-th>#</b-th>
                                                <b-th>Name</b-th>
                                                <b-th>Status</b-th>
                                                <b-th>Action</b-th>
                                            </b-tr>
                                        </b-thead>
                                        <b-tbody>
                                            <b-tr v-if="!files.length">
                                                <b-td colspan="7">
                                                    <div
                                                        class="text-center p-5"
                                                    >
                                                        <h4>
                                                            Drop files anywhere
                                                            to upload<br />or
                                                        </h4>
                                                        <b-button
                                                            class="btn btn-lg btn-primary"
                                                            >Select
                                                            Files</b-button
                                                        >
                                                    </div>
                                                </b-td>
                                            </b-tr>
                                            <b-tr
                                                v-for="(file, index) in files"
                                                :key="file.id"
                                            >
                                                <b-td>{{ index }}</b-td>
                                                <b-td>
                                                    <div class="filename">
                                                        {{ file.name }}
                                                    </div>
                                                    <div
                                                        class="progress"
                                                        v-if="
                                                            file.active ||
                                                                file.progress !==
                                                                    '0.00'
                                                        "
                                                    >
                                                        <div
                                                            :class="{
                                                                'progress-bar': true,
                                                                'progress-bar-striped': true,
                                                                'bg-danger':
                                                                    file.error,
                                                                'progress-bar-animated':
                                                                    file.active
                                                            }"
                                                            role="progressbar"
                                                            :style="{
                                                                width:
                                                                    file.progress +
                                                                    '%'
                                                            }"
                                                        >
                                                            {{ file.progress }}%
                                                        </div>
                                                    </div>
                                                </b-td>
                                                <b-td v-if="file.error">
                                                    {{ file.error }}
                                                </b-td>
                                                <b-td v-else-if="file.success">
                                                    success
                                                </b-td>
                                                <b-td v-else-if="file.active">
                                                    active
                                                </b-td>
                                                <b-td v-else></b-td>
                                                <b-td>
                                                    <div class="btn-group">
                                                        <b-button
                                                            class="btn btn-secondary btn-sm dropdown-toggle"
                                                            type="button"
                                                        >
                                                            Action
                                                        </b-button>
                                                        <div
                                                            class="dropdown-menu"
                                                        >
                                                            <a
                                                                :class="{
                                                                    'dropdown-item': true,
                                                                    disabled:
                                                                        file.active ||
                                                                        file.success ||
                                                                        file.error ===
                                                                            'compressing'
                                                                }"
                                                                href="#"
                                                                @click.prevent="
                                                                    file.active ||
                                                                    file.success ||
                                                                    file.error ===
                                                                        'compressing'
                                                                        ? false
                                                                        : onEditFileShow(
                                                                              file
                                                                          )
                                                                "
                                                                >Edit</a
                                                            >
                                                            <a
                                                                :class="{
                                                                    'dropdown-item': true,
                                                                    disabled: !file.active
                                                                }"
                                                                href="#"
                                                                @click.prevent="
                                                                    file.active
                                                                        ? $refs.upload.update(
                                                                              file,
                                                                              {
                                                                                  error:
                                                                                      'cancel'
                                                                              }
                                                                          )
                                                                        : false
                                                                "
                                                                >Cancel</a
                                                            >

                                                            <a
                                                                class="dropdown-item"
                                                                href="#"
                                                                v-if="
                                                                    file.active
                                                                "
                                                                @click.prevent="
                                                                    $refs.upload.update(
                                                                        file,
                                                                        {
                                                                            active: false
                                                                        }
                                                                    )
                                                                "
                                                                >Abort</a
                                                            >
                                                            <a
                                                                class="dropdown-item"
                                                                href="#"
                                                                v-else-if="
                                                                    file.error &&
                                                                        file.error !==
                                                                            'compressing' &&
                                                                        $refs
                                                                            .upload
                                                                            .features
                                                                            .html5
                                                                "
                                                                @click.prevent="
                                                                    $refs.upload.update(
                                                                        file,
                                                                        {
                                                                            active: true,
                                                                            error:
                                                                                '',
                                                                            progress:
                                                                                '0.00'
                                                                        }
                                                                    )
                                                                "
                                                                >Retry upload</a
                                                            >
                                                            <a
                                                                :class="{
                                                                    'dropdown-item': true,
                                                                    disabled:
                                                                        file.success ||
                                                                        file.error ===
                                                                            'compressing'
                                                                }"
                                                                href="#"
                                                                v-else
                                                                @click.prevent="
                                                                    file.success ||
                                                                    file.error ===
                                                                        'compressing'
                                                                        ? false
                                                                        : $refs.upload.update(
                                                                              file,
                                                                              {
                                                                                  active: true
                                                                              }
                                                                          )
                                                                "
                                                                >Upload</a
                                                            >

                                                            <div
                                                                class="dropdown-divider"
                                                            ></div>
                                                            <a
                                                                class="dropdown-item"
                                                                href="#"
                                                                @click.prevent="
                                                                    $refs.upload.remove(
                                                                        file
                                                                    )
                                                                "
                                                                >Remove</a
                                                            >
                                                        </div>
                                                    </div>
                                                </b-td>
                                            </b-tr>
                                        </b-tbody>
                                    </b-table>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <b-table
                                        :fields="filesFields"
                                        :items="files"
                                        responsive="sm"
                                        borderless
                                        small
                                        sticky-header="true"
                                    >
                                        <template v-slot:cell(name)="file">
                                            {{ file.item }}
                                        </template>
                                        <template v-slot:cell(actions)="file">
                                            <b-button
                                                size="md"
                                                @click="removeFile(file.item)"
                                                variant="outline-danger"
                                            >
                                                Delete
                                            </b-button>
                                        </template>
                                    </b-table>
                                </b-col>
                            </b-row>
                        </b-card>
                    </b-overlay>
                </b-col>
            </b-row>
            <EditDescriptionModal
                modal-id="editDescriptionModal"
                :description="collection.description"
                @saveDescription="saveDescription"
            >
            </EditDescriptionModal>
        </div>
    </div>
</template>

<script>
import router from '../router';
import VueUpload from 'vue-upload-component';
import Auth from '@/services/apiV1/Auth';
import Datasets from '@/services/apiV1/DatasetManager';
import EditDescriptionModal from '@/components/collections/EditDescriptionModal';

export default {
    name: 'Dataset',
    components: {
        VueUpload,
        EditDescriptionModal
    },
    beforeRouteLeave(to, from, next) {
        if (!this.metadataChanged) {
            next();
            return;
        }
        if (
            this.metadataChanged &&
            window.confirm(
                'Do you really want to exit this page? You have unsaved metadata!'
            )
        ) {
            next();
        } else {
            next(false);
        }
    },
    data() {
        return {
            show: false,
            datasetNotFound: false,
            loadingDataset: true,
            loadingSamples: true,
            collection: {},
            metadata: [],
            metadataChanged: false,
            metadataFields: [
                {
                    key: 'key',
                    label: 'Key',
                    sortable: true
                },
                {
                    key: 'value',
                    label: 'Value'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            newMetadatumKey: '',
            newMetadatumValue: '',
            files: [],
            filesToUpload: [],
            filesFields: [
                {
                    key: 'name',
                    label: 'Name',
                    sortable: true
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            headers: {
                'X-CSRFTOKEN': Auth.getCSRFToken()
            }
        };
    },
    mounted: function() {
        this.reloadDataset();
        this.$watch(
            () => {
                return this.$refs.upload.active;
            },
            val => {
                if (!val) {
                    this.reloadFiles();
                }
            }
        );
    },
    computed: {
        hasSamples() {
            return !(
                this.collection.sample_set === undefined ||
                this.collection.sample_set === 0
            );
        },
        postUrl() {
            return (
                '/apis/v1/collections/' +
                this.$route.params.owner +
                '/' +
                this.$route.params.name +
                '/upload_files/'
            );
        }
    },
    methods: {
        reloadFiles() {
            this.loadingSamples = true;
            Datasets.listFiles(
                this.$route.params.owner,
                this.$route.params.name
            ).then(files => {
                this.files = files.files;
                this.loadingSamples = false;
            });
        },
        reloadDataset() {
            this.loadingDataset = true;
            Datasets.get(
                this.$route.params.owner,
                this.$route.params.name
            ).then(collection => {
                if (collection.response && collection.response.status === 404) {
                    this.datasetNotFound = true;
                } else {
                    this.datasetNotFound = false;
                    this.collection = collection;
                    Datasets.listMetadata(
                        this.$route.params.owner,
                        this.$route.params.name
                    ).then(metadata => {
                        this.metadata = metadata.metadata;
                        this.reloadFiles();
                    });
                }
                this.loadingDataset = false;
            });
        },
        inputFile(newFile, oldFile) {
            if (
                Boolean(newFile) !== Boolean(oldFile) ||
                oldFile.error !== newFile.error
            ) {
                if (!this.$refs.upload.active) {
                    this.$refs.upload.active = true;
                }
            }
        },
        removeFile(file) {
            this.loadingSamples = true;
            Datasets.deleteFiles(
                this.$route.params.owner,
                this.$route.params.name,
                [file]
            ).then(files => {
                this.files = files.files;
                this.loadingSamples = false;
            });
        },
        inputFilter() {},
        onShown() {
            this.$refs.cancel.focus();
        },
        onHidden() {},
        remove() {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete dataset '${this.collection.name}?'`,
                    {
                        title: 'Delete Dataset',
                        centered: true,
                        cancelVariant: 'outline-dark',
                        okVariant: 'danger',
                        okTitle: 'Delete'
                    }
                )
                .then(value => {
                    if (value === true) {
                        Datasets.delete(this.collection.pk).then(value => {
                            if (value === true) {
                                this.items = this.items.filter(obj => {
                                    return obj.pk !== this.pk;
                                });
                            }
                        });
                        router.push({ name: 'datasets' });
                    }
                });
        },
        saveName(name) {
            Datasets.update(
                this.collection.pk,
                name,
                this.collection.description
            ).then(() => {
                router.push({
                    name: 'dataset',
                    params: {
                        owner: this.collection.owner,
                        name: name
                    }
                });
            });
        },
        saveDescription(description) {
            Datasets.updateDescription(
                this.collection.owner,
                this.collection.name,
                description
            ).then(data => {
                this.collection.description = data.description;
            });
        },
        removeMetadatum(datum) {
            this.metadataChanged = true;
            this.metadata = this.metadata.filter(
                item => item.key !== datum.item.key
            );
        },
        addMetadatum() {
            this.metadataChanged = true;
            this.metadata.push({
                key: this.newMetadatumKey,
                value: this.newMetadatumValue
            });
            this.newMetadatumKey = '';
            this.newMetadatumValue = '';
        },
        saveMetadata() {
            Datasets.updateMetadata(
                this.collection.owner,
                this.collection.name,
                this.metadata
            ).then(data => {
                this.metadata = data.metadata;
                this.metadataChanged = false;
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
  color: $color-button

.secondary
  color: $secondary
</style>
