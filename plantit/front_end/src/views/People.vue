<template>
    <div>
        <b-container>
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    PlantIT is developed and maintained by the University of Georgia's
                    <b-link
                        href="https://www.computational-plant-science.org/joomla30/"
                        >Computational Plant Science lab</b-link
                    >.
                </b-col>
            </b-row>
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <h3>Workflow Contributors</h3>
                    <hr />
                    <b-card-group> </b-card-group>
                </b-col>
            </b-row>
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <h3>PlantIT Team</h3>
                    <hr />
                    <!-- TODO tab group for current vs previous -->
                    <b-card-group deck>
                        <b-card
                            title="Alexander Bucksch"
                            sub-title="Principal Investigator"
                            border-variant="dark"
                            footer-bg-variant="dark"
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
                                        class="fab fa-github fa-2x color-box-background"
                                    ></i>
                                </a>
                                <a
                                    href="https://www.researchgate.net/profile/Alexander_Bucksch"
                                    class="card-link"
                                >
                                    <i
                                        class="fab fa-researchgate fa-2x color-box-background"
                                    ></i>
                                </a>
                            </template>
                        </b-card>
                        <b-card
                            title="Chris Cotter"
                            sub-title="Lead Developer (Previous)"
                            border-variant="dark"
                            footer-bg-variant="dark"
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
                                        class="fab fa-github fa-2x color-box-background"
                                    ></i>
                                </a>
                            </template>
                        </b-card>
                        <b-card
                            title="Wes Bonelli"
                            sub-title="Lead Developer"
                            border-variant="dark"
                            footer-bg-variant="dark"
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
                                        class="fab fa-github fa-2x color-box-background"
                                    ></i>
                                </a>
                                <a
                                    href="https://www.researchgate.net/profile/Wes_Bonelli"
                                    class="card-link"
                                >
                                    <i
                                        class="fab fa-researchgate fa-2x color-box-background"
                                    ></i>
                                </a>
                            </template>
                        </b-card>
                        <b-card
                            title="Megan Flory"
                            sub-title="Graphic Designer"
                            footer-bg-variant="dark"
                            border-variant="dark"
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
                                        class="fab fa-github fa-2x color-box-background"
                                    ></i>
                                </a>
                            </template>
                        </b-card>
                    </b-card-group>
                </b-col>
            </b-row>
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <h3>Usage Statistics</h3>
                    <hr />
                    <b-card-group> </b-card-group>
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
.color-box-background
  color: $color-button
</style>
