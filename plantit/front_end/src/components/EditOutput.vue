<template>
    <div>
        <b-row>
            <b-col>
                <b>Configure local path.</b>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col> File Name </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="local_path"
                    placeholder="Enter a file name."
                ></b-form-input>
            </b-col>
        </b-row>
        <br />
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
                    placeholder="Enter a username."
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
                    placeholder="Enter a password."
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Host </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="host"
                    placeholder="Enter a host FQDN or IP address."
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Port </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="port"
                    placeholder="Enter a port number."
                ></b-form-input>
            </b-col>
        </b-row>
        <b-row>
            <b-col> Zone </b-col>
            <b-col cols="10">
                <b-form-input
                    size="sm"
                    v-model="zone"
                    placeholder="Enter a zone name."
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
                <b-button @click="verify" variant="success" block>
                    Verify
                </b-button>
            </b-col>
        </b-row>
        <br />
        <b-row>
            <b-col>
                <b-alert v-model="localConfigIncomplete" variant="warning"
                    >Local path configuration incomplete.</b-alert
                >
            </b-col>
        </b-row>
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
    </div>
</template>

<script>
import Files from '@/services/apiV1/FileManager';

export default {
    name: 'EditOutput',
    data() {
        return {
            username: '',
            password: '',
            host: '',
            port: '',
            zone: '',
            local_path: '',
            irods_path: '',
            files: [],
            filesLoading: false,
            localConfigIncomplete: false,
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
        verify() {
            this.localConfigIncomplete = this.local_path === '';
            this.listFiles();
        },
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
                    this.$emit('outputSelected', {
                        username: this.username,
                        password: this.password,
                        host: this.host,
                        port: this.port,
                        zone: this.zone,
                        local_path: this.local_path,
                        irods_path: this.irods_path
                    });
                });
            }
        }
    }
};
</script>

<style scoped></style>
