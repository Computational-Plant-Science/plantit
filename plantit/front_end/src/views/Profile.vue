<template>
    <div class="w-100 p-0 m-0">
        <b-container>
            <div class="w-100 pb-4">
                <b-card
                    :img-src="require('../assets/icons/default-user-small.png')"
                    img-alt="Image"
                    img-top
                    style="max-width: 30rem;margin: 0 auto;"
                >
                    <template
                        v-slot:header
                        style="background-color: white"
                        v-bind:info="this.info"
                    >
                        <b-row>
                            <b-col class="mt-2" style="color:white">
                                <h5>
                                    <i class="fas fa-user green"></i>
                                    {{ info.username }}
                                </h5>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    @click="
                                        $bvModal.show('editUserInfoModal')
                                    "
                                    variant="outline-dark"
                                    v-b-tooltip.hover
                                    title="Edit user information."
                                >
                                    <i class="far fa-edit"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                    </template>
                    <b-card-text v-if="!loading">
                        <p><b>Email Address:</b> {{ this.info.email }}</p>
                        <p><b>First Name:</b> {{ this.info.first_name }}</p>
                        <p><b>Last Name:</b> {{ this.info.last_name }}</p>
                        <p>
                            <b>Country:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.country
                            }}
                        </p>
                        <p>
                            <b>Continent:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.continent
                            }}
                        </p>
                        <p>
                            <b>Institution:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.institution
                            }}
                        </p>
                        <p>
                            <b>Institution Type:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.institution_type
                            }}
                        </p>
                        <p>
                            <b>Field of Study:</b>
                            {{
                                this.info.profile === undefined
                                    ? ''
                                    : this.info.profile.field_of_study
                            }}
                        </p>
                    </b-card-text>
                </b-card>
            </div>
        </b-container>
        <!--<EditUserInfoModal
            :prompt="false"
            modal-id="editUserInfoModal"
            :username="this.info.username"
            :first_name="this.info.first_name"
            :last_name="this.info.last_name"
            :country="
                this.info.profile === undefined ? '' : this.info.profile.country
            "
            :continent="
                this.info.profile === undefined
                    ? ''
                    : this.info.profile.continent
            "
            :institution="
                this.info.profile === undefined
                    ? ''
                    : this.info.profile.institution
            "
            :institution_type="
                this.info.profile === undefined
                    ? ''
                    : this.info.profile.institution_type
            "
            :field_of_study="
                this.info.profile === undefined
                    ? ''
                    : this.info.profile.field_of_study
            "
            @saveUserInfo="saveUserInfo"
            @cancel="cancel"
        >
        </EditUserInfoModal>-->
    </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';

export default {
    name: 'UserInfo',
    components: {},
    data() {
        return {
            info: {},
            loading: true
        };
    },
    methods: {
        reload() {
            UserApi.getCurrentUser().then(info => {
                this.info = info;
            });
        },
        saveUserInfo(
            userName,
            firstName,
            lastName,
            country,
            continent,
            institution,
            institutionType,
            fieldOfStudy
        ) {
            UserApi.updateUserInfo(
                userName,
                firstName,
                lastName,
                country,
                continent,
                institution,
                institutionType,
                fieldOfStudy
            ).then(() => {
                this.reload();
            });
        },
        cancel() {
            this.reload();
        }
    },
    created: function() {
        this.reload();
        this.loading = false;
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
