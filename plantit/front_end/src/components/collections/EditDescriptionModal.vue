<template>
    <b-modal
        :id="modalId"
        title="Edit Description"
        ok-title="Save"
        @cancel="cancel"
        @close="cancel"
        @ok="save"
        no-close-on-backdrop
        centered
        ok-variant="outline-dark"
        cancel-variant="outline-danger"
        hide-header-close
        header-bg-variant="dark"
        header-border-variant="dark"
        footer-bg-variant="white"
        footer-border-variant="white"
        header-text-variant="white"
    >
        <b-form-group
            v-if="description !== null"
            label-for="description"
        >
            <b-form-textarea
                id="description"
                v-model="description_internal"
                rows="3"
                max-rows="6"
            ></b-form-textarea>
        </b-form-group>
    </b-modal>
</template>

<script>
export default {
    name: 'EditDescriptionModal',
    props: {
        description: {
            type: String,
            default: function() {
                return null;
            }
        },
        modalId: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            description_internal: this.description
        };
    },
    methods: {
        save(bvModalEvent) {
            this.$emit(
                'saveDescription',
                this.description_internal,
            );
            this.$bvModal.hide(bvModalEvent.componentId);
        },
        cancel() {
            this.$emit('cancel');
        }
    },
    watch: {
        description: function(val) {
            this.description_internal = val;
        }
    }
};
</script>

<style scoped></style>
