<template>
    <div>
        <b-card header-bg-variant="dark" border-variant="white">
            <template
                v-slot:header
                v-bind:collection="this.collection"
                style="background-color: white"
            >
                <b-row>
                    <b-col class="mt-2" style="color:white">
                        <h5>
                            <i class="fas fa-layer-group green"></i>
                            Collection
                            <b-badge
                                pill
                                variant="dark"
                                class="green p-0 m-0 ml-1 mr-1"
                                >{{ collection.pk }}</b-badge
                            >
                            <b-badge
                                pill
                                variant="dark"
                                class="green p-0 m-0 ml-1 mr-1"
                                >{{ collection.name }}</b-badge
                            >
                        </h5>
                    </b-col>
                    <b-col md="auto">
                        <b-button
                            @click="$bvModal.show('editNameModal')"
                            variant="dark"
                            v-b-tooltip.hover
                            title="Edit collection name"
                        >
                            <i class="far fa-edit"></i>
                        </b-button>
                        <b-button
                            size="md"
                            variant="outline-danger"
                            @click="remove()"
                            v-b-tooltip.hover
                            title="Delete collection"
                        >
                            Delete
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <b-row class="justify-content-md-center">
                <b-col>
                    <b-card class="mb-2" border-variant="white">
                        <b-row>
                            <b-col>
                                <h4>Description</h4>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    id="edit-description-btn"
                                    @click="
                                        $bvModal.show('editDescriptionModal')
                                    "
                                    variant="outline-dark"
                                    v-b-tooltip.hover
                                    title="Edit description."
                                >
                                    <i class="far fa-edit"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                        <br />
                        <b-row>
                            <b-col>
                                <b-form class="form-horizontal">
                                    <b-form-group class="lb">
                                        <b-form-textarea
                                            disabled
                                            :placeholder="
                                                collection.description
                                            "
                                            plaintext
                                        >
                                        </b-form-textarea>
                                    </b-form-group>
                                </b-form>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
                <b-col>
                    <b-card class="mb-2" border-variant="white">
                        <b-row>
                            <b-col>
                                <h4>Metadata</h4>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    id="edit-metadata-btn"
                                    @click="$bvModal.show('editMetadataModal')"
                                    variant="outline-dark"
                                    v-b-tooltip.hover
                                    title="Edit metadata."
                                >
                                    <i class="far fa-edit"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                        <br />
                        <b-row>
                            <b-col>
                                <b-table
                                    show-empty
                                    selectable
                                    hover
                                    small
                                    sticky-header="true"
                                    responsive="sm"
                                    :borderless="true"
                                    :items="collection.metadata"
                                    :fields="fields"
                                    class="table-responsive"
                                ></b-table>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <b-overlay
                        :show="show"
                        rounded="sm"
                        @shown="onShown"
                        @hidden="onHidden"
                    >
                        <template v-slot:overlay>
                            <div class="text-center">
                                <!--<ul v-if="files.length">
                                    <li v-for="file in files" :key="file.id">
                                        <span>{{ file.name }}</span> - -
                                        <span v-if="file.error">{{
                                            file.error
                                        }}</span>
                                        <span v-else-if="file.success"
                                            >success</span
                                        >
                                        <span v-else-if="file.active"
                                            >active</span
                                        >
                                        <span v-else></span>
                                    </li>
                                </ul>-->
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
                            class="mt-4 mb-2"
                            :aria-hidden="show ? 'true' : null"
                        >
                            <div
                                v-show="$refs.upload && $refs.upload.dropActive"
                                class="drop-active"
                            >
                                <h3>Drop files to upload</h3>
                            </div>
                            <b-row>
                                <b-col>
                                    <h4>Samples</h4>
                                </b-col>
                                <b-col md="auto">
                                    <vue-upload
                                        class="btn btn-outline-dark"
                                        v-model="files"
                                        :multiple="true"
                                        :drop="true"
                                        :drop-directory="true"
                                        :headers="headers"
                                        postAction="/apis/v1/files/upload/"
                                        :data="{
                                            storage_type: this.collection
                                                .storage_type,
                                            path: this.collection.base_file_path
                                        }"
                                        ref="upload"
                                        @input-file="inputFile"
                                        v-b-tooltip.hover
                                        title="Upload samples."
                                    >
                                        <i class="fas fa-plus"></i>
                                    </vue-upload>
                                </b-col>
                            </b-row>
                            <br />
                            <b-row>
                                <b-col>
                                    <b-spinner
                                        v-if="
                                            this.collection.sample_set ===
                                                undefined
                                        "
                                        label="Loading..."
                                    >
                                    </b-spinner>
                                    <span v-else>
                                        <span
                                            v-if="
                                                this.collection.sample_set
                                                    .length === 0
                                            "
                                        >
                                            Drop files anywhere or click the '+'
                                            button to upload samples.
                                        </span>
                                        <CollectionThumbnails
                                            v-if="
                                                this.collection.sample_set
                                                    .length > 0
                                            "
                                            :pk="pk"
                                            :samples="collection.sample_set"
                                        >
                                        </CollectionThumbnails>
                                    </span>
                                </b-col>
                            </b-row>
                        </b-card>
                    </b-overlay>
                </b-col>
            </b-row>
        </b-card>
        <EditNameModal
            modal-id="editNameModal"
            :name="collection.name"
            @saveName="saveName"
            @cancel="cancelEdit"
        >
        </EditNameModal>
        <EditDescriptionModal
            modal-id="editDescriptionModal"
            :description="collection.description"
            @saveDescription="saveDescription"
            @cancel="cancelEdit"
        >
        </EditDescriptionModal>
        <EditMetadataModal
            modal-id="editMetadataModal"
            :metadata="collection.metadata"
            @saveMetadata="saveMetadata"
            @cancel="cancelEdit"
        >
        </EditMetadataModal>
    </div>
</template>

<script>
import router from '../router';
import VueUpload from 'vue-upload-component';
import Auth from '@/services/apiV1/Auth';
import CollectionThumbnails from '@/components/collections/CollectionThumbnails.vue';
import CollectionApi from '@/services/apiV1/CollectionManager';
import EditNameModal from '@/components/collections/EditNameModal';
import EditDescriptionModal from '@/components/collections/EditDescriptionModal';
import EditMetadataModal from '@/components/collections/EditMetadataModal';

export default {
    name: 'Collection',
    components: {
        VueUpload,
        CollectionThumbnails,
        EditNameModal,
        EditDescriptionModal,
        EditMetadataModal
    },
    props: {
        pk: {
            required: true
        }
    },
    data() {
        return {
            show: false,
            collection: {
                metadata: []
            },
            fields: [
                {
                    key: 'name',
                    sortable: true
                },
                {
                    key: 'value'
                }
            ],
            files: [],
            headers: {
                'X-CSRFTOKEN': Auth.getCSRFToken()
            }
        };
    },
    mounted: function() {
        CollectionApi.getCollection(this.pk).then(data => {
            this.collection = data;
        });
    },
    computed: {
        hasSamples() {
            return !(
                this.collection.sample_set === undefined ||
                this.collection.sample_set === 0
            );
        }
    },
    methods: {
        inputFile(newFile, oldFile) {
            if (newFile && oldFile) {
                // update
                if (newFile.active && !oldFile.active) {
                    // beforeSend
                    // min size
                    if (
                        newFile.size >= 0 &&
                        this.minSize > 0 &&
                        newFile.size < this.minSize
                    ) {
                        this.$refs.upload.update(newFile, { error: 'size' });
                    }
                }
                if (newFile.progress !== oldFile.progress) {
                    // progress
                }
                if (newFile.error && !oldFile.error) {
                    // error
                }
                if (newFile.success && !oldFile.success) {
                    // success
                }
            }
            if (!newFile && oldFile) {
                // remove
                if (oldFile.success && oldFile.response.id) {
                    // $.ajax({
                    //   type: 'DELETE',
                    //   url: '/upload/delete?id=' + oldFile.response.id,
                    // })
                }
            }
            // Automatically activate upload
            if (
                Boolean(newFile) !== Boolean(oldFile) ||
                oldFile.error !== newFile.error
            ) {
                this.show = true;
                this.$refs.upload.active = true;
                CollectionApi.addSamples(
                    Object.values(
                        [newFile].reduce((result, item) => {
                            result[item.name] = item;
                            return result;
                        }, {})
                    ).map(item => {
                        return {
                            name: item.name,
                            path: this.collection.base_file_path
                        };
                    }),
                    this.pk
                ).then(() => {
                    CollectionApi.getCollection(this.pk).then(data => {
                        this.collection = data;
                    });
                });
            }
        },
        onFileInput() {
            if (!this.$refs.upload.active) {
                this.show = true;
                this.$refs.upload.active = true;
                let samples = Object.values(
                    this.files.reduce((result, item) => {
                        result[item.name] = item;
                        return result;
                    }, {})
                ).map(item => {
                    return {
                        name: item.name,
                        path: this.collection.base_file_path
                    };
                });
                CollectionApi.addSamples(samples, this.pk).then(() => {
                    CollectionApi.getCollection(this.pk).then(data => {
                        this.collection = data;
                        this.$refs.upload.active = false;
                    });
                });
            }
        },
        onShown() {
            this.$refs.cancel.focus();
        },
        onHidden() {},
        remove() {
            this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to delete collection '${this.collection.name}?'`,
                    {
                        title: 'Delete Collection',
                        centered: true,
                        okVariant: 'danger',
                        okTitle: 'Delete'
                    }
                )
                .then(value => {
                    if (value === true) {
                        CollectionApi.deleteCollection(this.pk).then(value => {
                            if (value === true) {
                                this.items = this.items.filter(obj => {
                                    return obj.pk !== this.pk;
                                });
                            }
                        });
                        router.push({ name: 'collections' });
                    }
                });
        },
        saveName(name) {
            CollectionApi.updateMetadata(
                name,
                this.collection.description,
                this.collection.metadata,
                this.collection.pk
            ).then(() => {
                this.collection.name = name;
            });
        },
        saveDescription(description) {
            CollectionApi.updateMetadata(
                this.collection.name,
                description,
                this.collection.metadata,
                this.collection.pk
            ).then(() => {
                this.collection.description = description;
            });
        },
        saveMetadata(metadata) {
            CollectionApi.updateMetadata(
                this.collection.name,
                this.collection.description,
                metadata,
                this.collection.pk
            ).then(() => {
                this.collection.metadata = metadata;
            });
        },
        cancelEdit() {
            CollectionApi.getCollection(this.collection.pk).then(collection => {
                this.collection.metadata = collection.metadata;
                this.collection.name = collection.name;
                this.collection.description = collection.description;
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
