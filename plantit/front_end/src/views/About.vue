<template>
    <div>
        <b-container>
            <h3>
                What is PlantIT?
            </h3>
            <hr />
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    PlantIT is a workflow automation platform for the phenomics
                    community, developed and maintained by the University of
                    Georgia's
                    <b-link
                        href="https://www.computational-plant-science.org/joomla30/"
                        >Computational Plant Science lab
                    </b-link>
                    and funded by the
                    <b-link
                        href="https://arpa-e.energy.gov/?q=arpa-e-programs/roots"
                        >ARPA-E ROOTS project</b-link
                    >. It allows users to upload or access data in-place, run
                    bespoke analyses on high-performance and high-throughput
                    computing systems, and retrieve results &mdash; all from the
                    browser, no programming required.
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
                                <b-tab title="Active" active>
                                    <template v-slot:title class="m-0 p-0">
                                        <b class="dark">Active</b>
                                    </template>
                                    <b-card-group deck columns>
                                        <b-card
                                            title="Alexander Bucksch"
                                            sub-title="Principal Investigator"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://github.com/koalaspirit"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-github fa-2x success"
                                                    ></i>
                                                </a>
                                                <a
                                                    href="https://www.researchgate.net/profile/Alexander_Bucksch"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-researchgate fa-2x success"
                                                    ></i>
                                                </a>
                                                <a
                                                    href="https://www.linkedin.com/in/abucksch/"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x success"
                                                    ></i>
                                                </a>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Wes Bonelli"
                                            sub-title="Lead Developer (PlantIT)"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://github.com/w-bonelli"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-github fa-2x success"
                                                    ></i>
                                                </a>
                                                <a
                                                    href="https://www.researchgate.net/profile/Wes_Bonelli"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-researchgate fa-2x success"
                                                    ></i>
                                                </a>
                                                <a
                                                    href="https://www.linkedin.com/in/wesley-bonelli/"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x success"
                                                    ></i>
                                                </a>
                                            </template>
                                        </b-card>
                                    </b-card-group>
                                </b-tab>
                                <b-tab title="Former">
                                    <template v-slot:title class="m-0 p-0">
                                        <b class="dark">Former</b>
                                    </template>
                                    <b-card-group columns>
                                        <b-card
                                            title="Chris Cotter"
                                            sub-title="Lead Developer (PlantIT)"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem;"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://github.com/cottersci"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-github fa-2x success"
                                                    ></i>
                                                </a>
                                                <a
                                                    href="https://www.linkedin.com/in/crcotter/"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x success"
                                                    ></i>
                                                </a>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Abhiram Das"
                                            sub-title="Lead Developer (DIRT)"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://www.linkedin.com/in/abhiram-das-7a8b382/"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x success"
                                                    ></i>
                                                </a>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Megan Flory"
                                            sub-title="Graphic Designer"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://github.com/meganflory"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-github fa-2x success"
                                                    ></i>
                                                </a>
                                            </template>
                                        </b-card>
                                        <b-card
                                            title="Maria Pedrosa"
                                            sub-title="Developer"
                                            border-variant="dark"
                                            footer-bg-variant="dark"
                                            footer-border-variant="dark"
                                            style="min-width: 20rem"
                                        >
                                            <template
                                                v-slot:footer
                                                style="background-color: white"
                                            >
                                                <a
                                                    href="https://www.linkedin.com/in/mariacpedrosa/"
                                                    class="card-link"
                                                >
                                                    <i
                                                        class="fab fa-linkedin fa-2x success"
                                                    ></i>
                                                </a>
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

.success
    color: $success

.selected
    background-color: $color-button
    color: $dark
</style>
