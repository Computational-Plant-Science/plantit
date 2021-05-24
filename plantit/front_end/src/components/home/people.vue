<template>
    <div>
        <b-card
            class="rounded-0 text-center m-0 overflow-hidden"
            bg-variant="info"
            border-variant="info"
            text-variant="dark"
            header-bg-variant="dark"
            header-border-variant="dark"
        >
            <b-img
                rounded
                style="min-height: 30rem;position: absolute;left:-180px;bottom:-150px"
                center
                :src="require('../../assets/PlantITLoading.gif')"
            ></b-img>
            <br />
            <br />
            <br />
            <b-container class="text-center">
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col
                        ><b-img
                            center
                            style="max-width: 15rem;transform: translate(0px, 20px);"
                            :src="require('../../assets//cps2.png')"
                            class="m-0 p-0"
                        ></b-img
                    ></b-col>
                </b-row>
                <br />
                <br />
                <br />
                <b-row class="justify-content-md-center mb-4">
                    <b-col>
                        <b-tabs
                            justified
                            pills
                            active-nav-item-class="text-dark bg-white"
                            nav-class=""
                        >
                            <br />
                            <b-tab title="Active" active>
                                <template v-slot:title class="m-0 p-0">
                                    <b class="text-dark">Active Contributors</b>
                                </template>
                                <br />
                                <b-card-group deck columns>
                                    <b-card
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        sub-title-text-variant="secondary"
                                        text-variant="dark"
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
                                        sub-title-text-variant="secondary"
                                        text-variant="dark"
                                        bg-variant="white"
                                        footer-bg-variant="white"
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
                                    <b class="text-dark">Former Contributors</b>
                                </template>
                                <br />
                                <b-card-group columns>
                                    <b-card
                                        bg-variant="white"
                                        sub-title-text-variant="secondary"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        text-variant="dark"
                                        border-variant="white"
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
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
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
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
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
                                        bg-variant="white"
                                        footer-bg-variant="white"
                                        footer-border-variant="white"
                                        border-variant="white"
                                        text-variant="dark"
                                        sub-title-text-variant="secondary"
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
                    </b-col>
                </b-row>
                <br />
            </b-container>
        </b-card>
    </div>
</template>

<script>
export default {
    name: 'people'
};
</script>

<style scoped></style>
