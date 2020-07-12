<template>
    <div>
        <b-row>
            <b-col>
                <b>Configure iRODS connection.</b>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col> Username </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="username"
                    placeholder="Enter a value for 'username'"
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Password </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    type="password"
                    v-model="password"
                    placeholder="Enter a value for 'password'"
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Host </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="host"
                    placeholder="Enter a value for 'host'"
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Port </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="port"
                    placeholder="Enter a value for 'port'"
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Zone </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="zone"
                    placeholder="Enter a value for 'zone'"
                ></b-form-input>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b>Configure iRODS path.</b>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col> iRODS Path </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="irods_path"
                    placeholder="Enter a path."
                ></b-form-input>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-button @click="listFiles()" variant="success" block>
                    Verify
                </b-button>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-alert v-model="irodsConfigIncomplete" variant="warning"
                    >iRODS configuration incomplete.</b-alert
                >
            </b-col>
        </b-row>
        <b-row align-h="center" v-if="filesLoading">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="dark"
            ></b-spinner>
        </b-row>
        <b-row align-h="center" v-for="file in files" :key="file">
            <b-col class="text-center">
                {{ file }}
            </b-col>
        </b-row>
    </div>
</template>

<script>
import Files from '@/services/apiV1/FileManager';

export default {
    name: 'EditInput',
    data() {
        return {
            username: '',
            password: '',
            host: '',
            port: '',
            zone: '',
            irods_path: '',
            files: [],
            filesLoading: false,
            irodsConfigIncomplete: false
        };
    },
    mounted() {
        Files.connectionInfo().then(info => {
            this.username = info.username;
            this.host = info.host;
            this.port = info.port;
            this.zone = info.zone;
            this.irods_path = info.path;
        });
    },
    methods: {
        listFiles() {
            if (
                !(
                    this.username &&
                    this.password &&
                    this.host &&
                    this.port &&
                    this.zone &&
                    this.irods_path
                )
            ) {
                this.irodsConfigIncomplete = true;
            } else {
                this.irodsConfigIncomplete = false;
                this.filesLoading = true;
                Files.list(
                    this.username,
                    this.password,
                    this.host,
                    this.port,
                    this.zone,
                    this.irods_path
                ).then(files => {
                    this.files = files.files;
                    this.filesLoading = false;
                    if (this.files.length > 0) {
                        this.$emit('inputSelected', {
                            username: this.username,
                            password: this.password,
                            host: this.host,
                            port: this.port,
                            zone: this.zone,
                            irods_path: this.irods_path,
                            files: this.files
                        });
                    }
                });
            }
        }
    }
};
</script>

<style scoped></style>
