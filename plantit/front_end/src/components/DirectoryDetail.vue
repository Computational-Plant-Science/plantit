<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-row>
            <b-col>
                <b-card
                    bg-variant="white"
                    header-bg-variant="white"
                    footer-bg-variant="white"
                    border-variant="white"
                    footer-border-variant="white"
                    header-border-variant="white"
                    class="overflow-hidden"
                >
                </b-card>
                <template
                    v-slot:header
                    v-bind:collection="this.directory"
                    style="background-color: white"
                >
                    <b-row no-gutters>
                        <b-col>
                            <h1>
                                Dataset
                                <b>{{ directory.path }}</b>
                            </h1>
                        </b-col>
                    </b-row>
                </template>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import VueUpload from 'vue-upload-component';
import Datasets from '@/services/apiV1/Datasets';

export default {
    name: 'DirectoryDetail',
    components: {
        VueUpload
    },
    data() {
        return {
            directory: {},
            investigation: {},
            study: {},
            environmentParameters: [],
            events: [],
            factors: [],
            biologicalMaterials: [],
            observationUnits: {},
            observedVariables: [],
            dataFiles: []
        };
    }
};
</script>

<style scoped></style>
