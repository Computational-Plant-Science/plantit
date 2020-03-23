<template>
    <div>
        <b-container>
            <b-row class="justify-content-md-center">
                <b-col>
                    <h3>Collection
                        <b-badge class="collection-id">{{pk}}</b-badge>
                        <b-badge class="collection-name">{{ this.collection.name }}</b-badge>
                    </h3>
                </b-col>
            </b-row>
            <b-row class="justify-content-md-center">
                <b-col>
                    <b-card class="mt-2 mb-2">
                        <b-row>
                            <b-col>
                                <h4>Details</h4>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                        id="edit-btn"
                                        @click="$bvModal.show('editCollectionMeta')"
                                        class="plantit-btn"
                                        v-b-tooltip.hover
                                        title="Edit collection name, description, and metadata.">
                                    <i class="far fa-edit"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                        <hr>
                        <b-row>
                            <b-col>
                                <b-form class="form-horizontal">
                                    <b-form-group label="Description:" class="lb">
                                        <b-form-textarea
                                                disabled
                                                :placeholder="collection.description"
                                        plaintext>
                                        </b-form-textarea>
                                    </b-form-group>
                                    <b-form-group label="Metadata:">
                                        <b-table
                                                show-empty
                                                selectable
                                                hover
                                                striped responsive="md"
                                                :items="collection.metadata"
                                                :fields="fields"
                                                :borderless="true"
                                                select-mode="single"
                                                class="table-responsive"></b-table>
                                    </b-form-group>
                                </b-form>
                            </b-col>
                        </b-row>
                    </b-card>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <b-card class="mt-2 mb-2">
                        <h4>Samples</h4>
                        <hr>
                        <b-spinner
                                v-if="this.collection.sample_set === undefined"
                                label="Loading...">
                        </b-spinner>
                        <span v-else>
                        <span v-if="this.collection.sample_set === 0">
                            Add files to the collection by clicking
                            <b-link
                                    :to="{
                                    name: 'addFiles',
                                    query: { pk: this.pk }
                                }">
                                "Add Files"
                            </b-link>
                        </span>
                        <CollectionThumbnails
                                v-if="this.collection.sample_set.length > 0"
                                :pk="pk"
                                :samples="collection.sample_set">
                        </CollectionThumbnails>
                    </span>
                    </b-card>
                </b-col>
            </b-row>
        </b-container>
        <EditMetadataModal
                modal-id="editCollectionMeta"
                :metadata="collection.metadata"
                :name="collection.name"
                :description="collection.description"
                @save="saveDetails"
                @cancel="cancelEdit">
        </EditMetadataModal>

    </div>
</template>

<script>
    import router from '../router';
    import CollectionThumbnails from '@/components/collections/CollectionThumbnails.vue';
    import CollectionApi from '@/services/apiV1/CollectionManager';
    import EditMetadataModal from '@/components/collections/EditMetadataModal';

    export default {
        name: 'Collection',
        components: {
            CollectionThumbnails,
            EditMetadataModal
        },
        props: {
            pk: {
                //Pk of the collection to show
                required: true
            }
        },
        data() {
            return {
                collection: {
                    metadata: [] //Must be defined for EditMetadata component.
                },
                fields: [
                    {
                        key: 'name',
                        sortable: true
                    },
                    {
                        key: 'value',
                    }
                ]
            };
        },
        mounted: function () {
            CollectionApi.getCollection(this.pk).then(data => {
                this.collection = data;
            });
        },
        computed: {
            hasSamples() {
                return !(
                    this.collection.sample_set === undefined ||
                    this.collection.sample_set == 0
                );
            }
        },
        methods: {
            addFiles() {
                router.push({name: 'addFiles', query: {pk: this.pk}});
            },
            analyze() {
                router.push({name: 'analyze', query: {pk: this.pk}});
            },
            deleteCollection() {
                this.$bvModal
                    .msgBoxConfirm(`Delete collection ${this.collection.name}?`, {
                        title: 'Delete Confirmation',
                        centered: true
                    })
                    .then(value => {
                        if (value == true) {
                            CollectionApi.deleteCollection(this.collection.pk).then(
                                value => {
                                    if (value == true) {
                                        router.push({name: 'collections'});
                                    }
                                }
                            );
                        }
                    });
            },
            // eslint-disable-next-line no-unused-vars
            saveDetails(name, description, metadata) {
                CollectionApi.updateMetadata(
                    name,
                    description,
                    this.collection.metadata,
                    this.collection.pk
                ).then(() => {
                    this.collection.description = description;
                    this.collection.name = name;
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
