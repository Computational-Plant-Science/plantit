<template>
    <b-modal
        :id="modalId"
        title="Edit User Info"
        ok-title="Save"
        ok-variant="dark"
        :ok-disabled="invalid"
        @cancel="cancel"
        @close="cancel"
        @ok="save"
        no-close-on-backdrop
        centered
    >
        <p v-if="prompt">
            Please enter your personal information. PlantIT relies on accurate
            demographic reporting to insure funding continuity.
        </p>
        <b-form-group
            label="First Name"
            label-for="first-name"
            invalid-feedback="Please enter your first name."
            :state="valid(first_name_internal)"
        >
            <b-form-input id="first-name" v-model="first_name_internal" trim>
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Last Name"
            label-for="last-name"
            invalid-feedback="Please enter your last name."
            :state="valid(last_name_internal)"
        >
            <b-form-input id="last-name" v-model="last_name_internal" trim>
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Country"
            label-for="country"
            invalid-feedback="Please enter your institution's country of origin."
            :state="valid(country_internal)"
        >
            <b-form-input id="country" v-model="country_internal" trim>
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Continent"
            label-for="continent"
            invalid-feedback="Please enter your institution's continent of origin."
            :state="valid(continent_internal)"
        >
            <b-form-input id="continent" v-model="continent_internal" trim>
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Institution"
            label-for="institution"
            invalid-feedback="Please enter your institution or organization."
            :state="valid(institution_internal)"
        >
            <b-form-input id="institution" v-model="institution_internal" trim>
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Institution Type"
            label-for="institution-type"
            invalid-feedback="Please enter your institution type (e.g., private company, research university, public organization)."
            :state="valid(institution_type_internal)"
        >
            <b-form-input
                id="institution-type"
                v-model="institution_type_internal"
                trim
            >
            </b-form-input>
        </b-form-group>
        <b-form-group
            label="Field of Study"
            label-for="field-of-study"
            invalid-feedback="Please enter your field of study."
            :state="valid(field_of_study_internal)"
        >
            <b-form-input
                id="field-of-study"
                v-model="field_of_study_internal"
                trim
            >
            </b-form-input>
        </b-form-group>
    </b-modal>
</template>

<script>
export default {
    name: 'EditUserInfoModal',
    props: {
        prompt: {
            type: Boolean,
            default: false
        },
        username: {
            type: String,
            default: function() {
                return null;
            }
        },
        first_name: {
            type: String,
            default: function() {
                return null;
            }
        },
        last_name: {
            type: String,
            default: function() {
                return null;
            }
        },
        country: {
            type: String,
            default: function() {
                return null;
            }
        },
        continent: {
            type: String,
            default: function() {
                return null;
            }
        },
        institution: {
            type: String,
            default: function() {
                return null;
            }
        },
        institution_type: {
            type: String,
            default: function() {
                return null;
            }
        },
        field_of_study: {
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
            username_internal: this.username,
            first_name_internal: this.first_name,
            last_name_internal: this.last_name,
            country_internal: this.country,
            continent_internal: this.continent,
            institution_internal: this.institution,
            institution_type_internal: this.institution_type,
            field_of_study_internal: this.field_of_study
        };
    },
    methods: {
        save(bvModalEvent) {
            this.$emit(
                'saveUserInfo',
                this.username_internal,
                this.first_name_internal,
                this.last_name_internal,
                this.country_internal,
                this.continent_internal,
                this.institution_internal,
                this.institution_type_internal,
                this.field_of_study_internal
            );
            this.$bvModal.hide(bvModalEvent.componentId);
        },
        cancel() {
            this.$emit('cancel');
        },
        valid(str) {
            return str !== null && str !== undefined && str.length > 0;
        }
    },
    computed: {
        invalid: function() {
            return !(
                this.valid(this.first_name_internal) &&
                this.valid(this.last_name_internal) &&
                this.valid(this.country_internal) &&
                this.valid(this.continent_internal) &&
                this.valid(this.institution_internal) &&
                this.valid(this.institution_type_internal) &&
                this.valid(this.field_of_study_internal)
            );
        }
    },
    watch: {
        username: function(val) {
            this.username_internal = val;
        },
        first_name: function(val) {
            this.first_name_internal = val;
        },
        last_name: function(val) {
            this.last_name_internal = val;
        },
        country: function(val) {
            this.country_internal = val;
        },
        continent: function(val) {
            this.continent_internal = val;
        },
        institution: function(val) {
            this.institution_internal = val;
        },
        institution_type: function(val) {
            this.institution_type_internal = val;
        },
        field_of_study: function(val) {
            this.field_of_study_internal = val;
        }
    }
};
</script>

<style scoped></style>
