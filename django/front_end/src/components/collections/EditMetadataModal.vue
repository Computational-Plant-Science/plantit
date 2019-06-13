<template>
    <b-modal
        :id="modalId"
        title="Edit Metadata"
        ok-title="Save"
        @cancel="cancel"
        @close="cancel"
        @ok="save"
        no-close-on-backdrop
    >
        <b-form-group
            v-if="name !== null"
            label="Name:"
            label-for="metadata-name"
        >
            <b-form-input
                id="metadata-name"
                v-model="name_internal"
            ></b-form-input>
        </b-form-group>

        <b-form-group
            v-if="description !== null"
            label="Description:"
            label-for="metadata-description"
        >
            <b-form-textarea
                id="metadata-description"
                v-model="desc_internal"
                rows="3"
                max-rows="6"
            ></b-form-textarea>
        </b-form-group>

        Metadata:
        <EditMetadata
            v-model="metadata"
            @unsaved="
                e => {
                    unsavedMetadata = e;
                }
            "
        ></EditMetadata>
    </b-modal>
</template>

<script>
import EditMetadata from '@/components/collections/EditMetadata';

export default {
    /*
      This allows editing of an objects metadta, for example for a Sample
      or Collection. Metdata is an array of objects with a "name" and "value"
      property. Both are saved as strings.

      The modal can be shown using the typical bootstrap-vue method:
      this.$bvModal.show('modal-id') where modal-id is the value of the
      modalId property.

      A name and description input box can be added to the metadata modal by
      setting the "name" and "description" properites. If they are unset
      the respecitve input boxes are not shown.

      Events:
            save(name,description,metadata): emitted when the "save" button
            is clicked. It returns the updated metadata as well as the
            name and description. Name and description are null if not assigned.

            cancel(): emitted when the cancel button is clicked.
     */
    components: {
        EditMetadata
    },
    props: {
        //The name of the object. If the name is set, an extra
        //  input field is provided to edit it.
        name: {
            type: String,
            default: function() {
                return null;
            }
        },
        //The description of the object. If the name is set, an extra
        //  input field is provided to edit it.
        description: {
            type: String,
            default: function() {
                return null;
            }
        },
        //The objects metadata. Provided as an arry of objects of key (name) and
        // value (value) pairs.
        // metadata: [
        //  {
        //    name: "Name of metadata value",
        //      value: "value of metadata"
        //  },
        //  ...
        // ]
        metadata: {
            type: Array,
            required: true
        },
        // The id given to the modal.
        modalId: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            name_internal: this.name,
            desc_internal: this.description,
            unsavedMetadata: false
        };
    },
    methods: {
        addField() {
            this.metadata.push({ ...this.newField });
            this.newField = {
                name: '',
                value: ''
            };
            this.$refs.newField.focus();
        },
        deleteField(idx) {
            this.$delete(this.metadata, idx);
        },
        save(bvModalEvent) {
            if (this.unsavedMetadata) {
                bvModalEvent.preventDefault();
                this.$bvModal
                    .msgBoxConfirm(
                        `The metadata key/value left in the input box will not be saved,
             continue anyways? (Click the "plus" next to the value to save it)`,
                        {
                            title: 'Unsaved Metadata',
                            centered: true
                        }
                    )
                    .then(value => {
                        if (value == true) {
                            this.$emit(
                                'save',
                                this.name_internal,
                                this.desc_internal,
                                this.metadata
                            );
                            this.$bvModal.hide(bvModalEvent.componentId);
                        } else {
                            this.$bvModal.show(bvModalEvent.componentId);
                        }
                    });
            } else {
                this.$emit(
                    'save',
                    this.name_internal,
                    this.desc_internal,
                    this.metadata
                );
            }
        },
        cancel() {
            this.$emit('cancel');
        }
    },
    watch: {
        name: function(val) {
            this.name_internal = val;
        },
        description: function(val) {
            this.desc_internal = val;
        }
    }
};
</script>

<style scoped></style>
