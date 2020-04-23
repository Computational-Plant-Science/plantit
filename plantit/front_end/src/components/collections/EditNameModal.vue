<template>
    <b-modal
        :id="modalId"
        title="Edit Name"
        ok-title="Save"
        @cancel="cancel"
        @close="cancel"
        @ok="save"
        no-close-on-backdrop
        centered
        ok-variant="dark"
    >
        <b-form-group v-if="name !== null" label="Name:" label-for="name">
            <b-form-input id="name" v-model="name_internal"> </b-form-input>
        </b-form-group>
    </b-modal>
</template>

<script>
export default {
    name: 'EditNameModal',
    props: {
        name: {
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
            name_internal: this.name
        };
    },
    methods: {
        save(bvModalEvent) {
            this.$emit('saveName', this.name_internal);
            this.$bvModal.hide(bvModalEvent.componentId);
        },
        cancel() {
            this.$emit('cancel');
        }
    },
    watch: {
        name: function(val) {
            this.name_internal = val;
        }
    }
};
</script>

<style scoped></style>
