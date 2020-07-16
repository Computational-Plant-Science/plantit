<template>
    <div>
        <br />
        <br />
        <br />
        <div class="p-0 m-0 background-white text-white">
            <b-img
                style="max-width: 8rem;transform: translate(0px, 20px);"
                :src="require('../assets/logo.png')"
                center
                class="m-0 p-0"
            ></b-img>
        </div>
        <div

            class="p-5 m-0 background-dark text-white"
            style="min-height: 100%"
        >
            <b-container class="text-center">
                <h1 class="text-success text-center">
                    <b>PlantIT</b>
                </h1>
                <br/>
                <br/>
                <p>
                    PlantitIT is maintained by the University of Georgia's
                    <b-link
                        href="https://www.computational-plant-science.org/joomla30/"
                        >Computational Plant Science lab</b-link>
                    and funded by the
                    <b-link
                        href="https://arpa-e.energy.gov/?q=arpa-e-programs/roots"
                        >ARPA-E ROOTS project</b-link
                    >.
                </p>
                <br />
                <br/>
                <b-row class="justify-content-md-center mb-4">
                    <b-col>
                        <b-tabs
                            justified
                            active-nav-item-class="bg-dark text-dark"
                            nav-class="bg-dark outline-dark"
                        >
                            <br />
                            <br />
                            <b-tab title="Development Team" active>
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-success">Development Team</b>
                                </template>
                                <b-tabs
                                    justified
                                    active-nav-item-class="bg-dark text-dark"
                                    nav-class="bg-dark"
                                >
                                    <br />
                                    <br />
                                    <b-tab title="Active" active>
                                        <template v-slot:title class="m-0 p-0">
                                            <b class="text-success">Active</b>
                                        </template>
                                        <b-card-group deck columns>
                                            <b-card
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                sub-title-text-variant="white"
                                                text-variant="white"
                                                title="Alexander Bucksch"
                                                sub-title="Principal Investigator"
                                                style="min-width: 20rem"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://github.com/koalaspirit"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-github fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.researchgate.net/profile/Alexander_Bucksch"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-researchgate fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/abucksch/"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                            <b-card
                                                text-variant="white"
                                                sub-title-text-variant="white"
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                title="Wes Bonelli"
                                                sub-title="Developer"
                                                style="min-width: 20rem"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        class="mr-2 p-2"
                                                        variant="outline-dark"
                                                        href="https://github.com/w-bonelli"
                                                    >
                                                        <i
                                                            class="fab fa-github fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        variant="outline-dark"
                                                        class="mr-2 p-2"
                                                        href="https://www.researchgate.net/profile/Wes_Bonelli"
                                                    >
                                                        <i
                                                            class="fab fa-researchgate fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        class="mr-2 p-2"
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/wesley-bonelli/"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                        </b-card-group>
                                    </b-tab>
                                    <b-tab title="Former">
                                        <template v-slot:title class="m-0 p-0">
                                            <b class="text-success">Former</b>
                                        </template>
                                        <b-card-group columns>
                                            <b-card
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                text-variant="white"
                                                sub-title-text-variant="white"
                                                title="Chris Cotter"
                                                sub-title="Developer"
                                                style="min-width: 20rem;"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        class="mr-2 p-2"
                                                        variant="outline-dark"
                                                        href="https://github.com/cottersci"
                                                    >
                                                        <i
                                                            class="fab fa-github fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/crcotter/"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                            <b-card
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                text-variant="white"
                                                sub-title-text-variant="white"
                                                title="Abhiram Das"
                                                sub-title="Developer (DIRT)"
                                                style="min-width: 20rem"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/abhiram-das-7a8b382/"
                                                        class="card-link"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                            <b-card
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                text-variant="white"
                                                sub-title-text-variant="white"
                                                title="Megan Flory"
                                                sub-title="Designer"
                                                style="min-width: 20rem"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://github.com/meganflory"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-github fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/meganflory13/"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                            <b-card
                                                bg-variant="dark"
                                                footer-bg-variant="dark"
                                                footer-border-variant="white"
                                                border-variant="white"
                                                text-variant="white"
                                                sub-title-text-variant="white"
                                                title="Maria Luck"
                                                sub-title="Developer"
                                                style="min-width: 20rem"
                                            >
                                                <template
                                                    v-slot:footer
                                                    style="background-color: white"
                                                >
                                                    <b-button
                                                        variant="outline-dark"
                                                        href="https://www.linkedin.com/in/mariacpedrosa/"
                                                        class="mr-2 p-2"
                                                    >
                                                        <i
                                                            class="fab fa-linkedin fa-2x success"
                                                        ></i>
                                                    </b-button>
                                                </template>
                                            </b-card>
                                        </b-card-group>
                                    </b-tab>
                                </b-tabs>
                            </b-tab>
                            <b-tab title="Pipeline Contributors">
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-success"
                                        >Pipeline Developers</b
                                    >
                                </template>
                                <b-card-group columns>
                                    <b-card
                                        bg-variant="dark"
                                        footer-bg-variant="dark"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="white"
                                        sub-title-text-variant="white"
                                        v-for="developer in pipeline_developers"
                                        :title="developer"
                                        :key="developer"
                                    >
                                        <template
                                            v-slot:footer
                                            style="background-color: white"
                                        >
                                            <b-button
                                                class="mr-2 p-2"
                                                variant="outline-dark"
                                                :href="
                                                    'https://github.com/' +
                                                        developer
                                                "
                                            >
                                                <i
                                                    class="fab fa-github fa-2x success"
                                                ></i>
                                            </b-button>
                                        </template>
                                    </b-card>
                                </b-card-group>
                            </b-tab>
                            <b-tab title="Users">
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-success">Users</b>
                                </template>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </b-container>
        </div>
    </div>
</template>

<script>
import Users from '@/services/apiV1/UserManager';

export default {
    name: 'Contact',
    data: function() {
        return {
            pipeline_developers: []
        };
    },
    mounted: function() {
        Users.list().then(data => {
            this.pipeline_developers = data
                .filter(user => {
                    return user.profile.github_username != null;
                })
                .map(user => {
                    return user.profile.github_username;
                });
        });
    }
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'
.dark
    color: $dark
    padding: 0px
    margin: 0px

.background-dark
    background-color: $dark

.success
    color: $success

.selected
    background-color: $color-button
    color: $dark

p a
  font-weight: 400
  color: $success !important
  text-decoration: underline
  text-decoration-color: $color-button

h4
  font-weight: 200
  color: $white !important
</style>
