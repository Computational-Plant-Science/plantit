<template>
    <b-modal
        :id="modalId"
        title="User Profile"
        ok-title="Save"
        ok-variant="success"
        cancel-variant="outline-danger"
        no-close-on-esc
        @ok="save"
        :ok-disabled="invalid"
        no-close-on-backdrop
        hide-header-close
        centered
    >
        <p>
            PlantIT collects user information to report to funding
            organizations. Please enter your information below.
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
            <b-form-select
                :disabled="loadingCountries"
                v-model="country_internal"
                :options="countries"
                @change="getInstitutions(country_internal)"
            >
            </b-form-select>
        </b-form-group>
        <b-form-group
            :disabled="loadingInstitutions"
            label="Institution"
            label-for="institution"
            invalid-feedback="Please enter your institution or organization."
            :state="valid(institution_internal)"
        >
            <b-form-select
                v-model="institution_internal"
                :options="institutions"
            >
            </b-form-select>
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
import Users from '../services/apiV1/Users';

export default {
    name: 'EditUserInfoModal',
    props: {
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
        institution: {
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
            loadingCountries: true,
            loadingInstitutions: true,
            countries: [],
            institutions: [],
            username_internal: this.username,
            first_name_internal: this.first_name,
            last_name_internal: this.last_name,
            country_internal: this.country,
            institution_internal: this.institution,
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
                this.institution_internal,
                this.field_of_study_internal
            );
            this.$bvModal.hide(bvModalEvent.componentId);
        },
        valid(str) {
            return str !== null && str !== undefined && str.length > 0;
        },
        getCountries() {
            this.loadingCountries = true;
            Users.getCountries().then(countries => {
                this.countries = countries.countries;
                this.loadingCountries = false;
                if (this.country_internal !== 'Loading...') {
                    this.getInstitutions(this.country_internal);
                }
            });
        },
        getInstitutions(country) {
            this.loadingInstitutions = true;
            Users.getUniversities(country).then(institutions => {
                this.institutions = institutions.universities;
                this.loadingInstitutions = false;
            });
        }
    },
    mounted() {
        this.getCountries();
    },
    computed: {
        invalid: function() {
            return !(
                this.valid(this.first_name_internal) &&
                this.valid(this.last_name_internal) &&
                this.valid(this.country_internal) &&
                this.valid(this.institution_internal) &&
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
        institution: function(val) {
            this.institution_internal = val;
        },
        field_of_study: function(val) {
            this.field_of_study_internal = val;
        }
    }
};
</script>

<style scoped></style>
