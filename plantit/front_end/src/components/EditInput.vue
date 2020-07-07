<template>
    <div>
        <b-row>
            <b-col>
                Configure iRODS connection.
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
        <b-row>
            <b-col> Path </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="path"
                    placeholder="Enter a value for 'path'"
                ></b-form-input>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-button @click="listFiles()" variant="success">
                    List Files
                </b-button>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-alert v-model="showAlert" variant="danger"
                    >Connection configuration incomplete.</b-alert
                >
            </b-col>
        </b-row>
        <b-row v-for="file in files" :key="file">
            <b-col>
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
            path: '',
            files: [],
            showAlert: false
        };
    },
    mounted() {
        Files.connectionInfo().then(info => {
            this.username = info.username;
            this.host = info.host;
            this.port = info.port;
            this.zone = info.zone;
            this.path = info.path;
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
                    this.path
                )
            ) {
                this.showAlert = true;
            } else {
                this.showAlert = false;
            }
            Files.list(
                this.username,
                this.password,
                this.host,
                this.port,
                this.zone,
                this.path
            ).then(files => {
                this.files = files.files;
                if (this.files.length > 0) {
                    this.$emit('inputSelected', {
                        username: this.username,
                        password: this.password,
                        host: this.host,
                        port: this.port,
                        zone: this.zone,
                        path: this.path,
                        files: this.files
                    });
                }
            });
        }
    }
};
</script>

<style scoped></style>
