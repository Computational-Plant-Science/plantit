<template>
    <b-modal
        :id="modalId"
        :title="
            prompt ? 'Update User Information' : 'Edit User Information'
        "
        ok-title="Save"
        ok-variant="dark"
        cancel-variant="outline-danger"
        header-bg-variant="dark"
        header-border-variant="dark"
        header-text-variant="white"
        footer-bg-variant="dark"
        footer-border-variant="dark"
        :ok-only="prompt"
        no-close-on-esc
        @ok="save"
        :ok-disabled="invalid"
        no-close-on-backdrop
        hide-header-close
        centered
    >
        <p v-if="prompt">
            PlantIT collects user information to report to funding organizations.
            Please enter your information below.
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
            <b-form-input id="institution" v-model="institution_internal" trim @input="searchInstitution(institution_internal)">
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
import PlaceManager from "../../services/apiV1/PlaceManager";

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
            institutions: [],
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
        valid(str) {
            return str !== null && str !== undefined && str.length > 0;
        },
        searchInstitution(name) {
            this.institutions = PlaceManager.searchInstitution(name);
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
    mounted() {
        const plugin = document.createElement('script');
        plugin.setAttribute(
            'src',
            'https://maps.googleapis.com/maps/api/js?key=AIzaSyChHaZfwFcVigXg_T8DfDI5tqUP8QQJE88&libraries=places'
        );
        plugin.async = true;
        document.head.appendChild(plugin);
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
