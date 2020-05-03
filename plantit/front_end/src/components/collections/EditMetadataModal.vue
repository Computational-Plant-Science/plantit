<template>
    <b-modal
        :id="modalId"
        title="Edit Metadata"
        ok-title="Save"
        @cancel="cancel"
        @close="cancel"
        @ok="save"
        hide-header-close
        cancel-variant="outline-danger"
        ok-variant="outline-dark"
        no-close-on-backdrop
        centered
        header-bg-variant="dark"
        header-border-variant="dark"
        footer-bg-variant="white"
        footer-border-variant="white"
        header-text-variant="white"
    >
        <EditMetadata
            v-model="metadata"
            @unsaved="
                e => {
                    unsavedMetadata = e;
                }
            "
        >
        </EditMetadata>
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
        metadata: {
            type: Array,
            required: true
        },
        modalId: {
            type: String,
            required: true
        }
    },
    data() {
        return {
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
                        if (value === true) {
                            this.$emit(
                                'save',
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
                    this.metadata
                );
            }
        },
        cancel() {
            this.$emit('cancel');
        }
    }
};
</script>

<style scoped></style>
