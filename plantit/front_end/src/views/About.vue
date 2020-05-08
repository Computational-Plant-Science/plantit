<template>
    <div>
        <b-container>
            <h2>
                What is PlantIT?
            </h2>
            <hr />
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <p>
                        PlantIT is a workflow automation platform for the
                        phenomics community, developed and maintained by the
                        University of Georgia's
                        <b-link
                            href="https://www.computational-plant-science.org/joomla30/"
                            >Computational Plant Science lab
                        </b-link>
                        and funded by the
                        <b-link
                            href="https://arpa-e.energy.gov/?q=arpa-e-programs/roots"
                            >ARPA-E ROOTS project</b-link
                        >. PlantIT allows computational researchers to make
                        their algorithms available to a broad community, and
                        offers biological researchers an easy-to-use interface
                        to apply algorithms in their own work. Users can
                        schedule reproducible pipelines in high-performance and
                        high-throughput computing environments, then get
                        notified when results are available &mdash; all from the
                        browser, no programming required.
                    </p>
                </b-col>
            </b-row>
            <h3>
                People
            </h3>
            <hr />
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <b-tabs justified active-nav-item-class="bg-success" pills>
                        <br />
                        <b-tab title="Development Team" active>
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark">Core Team</b>
                            </template>
                            <b-tabs
                                justified
                                active-nav-item-class="bg-success"
                                pills
                            >
                                <br />
                                <b-tab title="Active Contributors" active>
                                    <template v-slot:title class="m-0 p-0">
                                        <b class="dark">Active Contributors</b>
                                    </template>
                                    <b-card-group deck columns>
                                        <b-card
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
                                                        class="fab fa-github fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    variant="outline-dark"
                                                    href="https://www.researchgate.net/profile/Alexander_Bucksch"
                                                    class="mr-2 p-2"
                                                >
                                                    <i
                                                        class="fab fa-researchgate fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    variant="outline-dark"
                                                    href="https://www.linkedin.com/in/abucksch/"
                                                    class="mr-2 p-2"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                        <b-card
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
                                                        class="fab fa-github fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    variant="outline-dark"
                                                    class="mr-2 p-2"
                                                    href="https://www.researchgate.net/profile/Wes_Bonelli"
                                                >
                                                    <i
                                                        class="fab fa-researchgate fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    class="mr-2 p-2"
                                                    variant="outline-dark"
                                                    href="https://www.linkedin.com/in/wesley-bonelli/"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                    </b-card-group>
                                </b-tab>
                                <b-tab title="Former Contributors">
                                    <template v-slot:title class="m-0 p-0">
                                        <b class="dark">Former Contributors</b>
                                    </template>
                                    <b-card-group columns>
                                        <b-card
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
                                                        class="fab fa-github fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    variant="outline-dark"
                                                    href="https://www.linkedin.com/in/crcotter/"
                                                    class="mr-2 p-2"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Abhiram Das"
                                            sub-title="Developer"
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
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Megan Flory"
                                            sub-title="Graphic Designer"
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
                                                        class="fab fa-github fa-2x"
                                                    ></i>
                                                </b-button>
                                                <b-button
                                                    variant="outline-dark"
                                                    href="https://www.linkedin.com/in/meganflory13/"
                                                    class="mr-2 p-2"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                        <b-card
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
                                                        class="fab fa-linkedin fa-2x"
                                                    ></i>
                                                </b-button>
                                            </template>
                                        </b-card>
                                    </b-card-group>
                                </b-tab>
                            </b-tabs>
                        </b-tab>
                        <b-tab title="Workflow Contributors">
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark">Workflow Contributors</b>
                            </template>
                        </b-tab>
                        <b-tab title="User Community">
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark">User Community</b>
                            </template>
                        </b-tab>
                    </b-tabs>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
export default {
    name: 'Contact'
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'
.dark
    color: $dark
    padding: 0px
    margin: 0px

.success
    color: $success

.selected
    background-color: $color-button
    color: $dark
</style>
