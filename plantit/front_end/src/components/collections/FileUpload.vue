<template>
    <div class="container">
        <!--UPLOAD-->
        <form
            enctype="multipart/form-data"
            novalidate
            v-if="isInitial || isSaving"
        >
            <h1>Upload images</h1>
            <div class="dropbox">
                <input
                    type="file"
                    multiple
                    :name="uploadFieldName"
                    :disabled="isSaving"
                    @change="
                        filesChange($event.target.name, $event.target.files)
                    "
                    class="input-file"
                />
                <p v-if="isInitial">
                    Drag your file(s) here to begin<br />
                    or click to browse
                </p>
                <p v-if="isSaving">Uploading {{ fileCount }} files...</p>
            </div>
        </form>
        <!--SUCCESS-->
        <div v-if="isSuccess">
            <h2>Uploaded {{ uploadedFiles.length }} file(s) successfully.</h2>
            <p>
                <a href="javascript:void(0)" @click="reset()">Upload again</a>
            </p>
        </div>
        <!--FAILED-->
        <div v-if="isFailed">
            <h2>Uploaded failed.</h2>
            <p>
                <a href="javascript:void(0)" @click="reset()">Try again</a>
            </p>
            <pre>{{ uploadError }}</pre>
        </div>
    </div>
</template>

<script>
import Auth from '@/services/apiV1/Auth';
import FileApi from '@/services/apiV1/FileManager';

const STATUS_INITIAL = 0,
    STATUS_SAVING = 1,
    STATUS_SUCCESS = 2,
    STATUS_FAILED = 3;

export default {
    name: 'FileUpload',
    components: [FileApi],
    props: ['storageType', 'path'],
    data() {
        return {
            uploadedFiles: [],
            uploadError: null,
            currentStatus: null,
            uploadFieldName: 'samples',
            fileCount: 0,
            headers: {
                'X-CSRFTOKEN': Auth.getCSRFToken()
            }
        };
    },
    computed: {
        isInitial() {
            return this.currentStatus === STATUS_INITIAL;
        },
        isSaving() {
            return this.currentStatus === STATUS_SAVING;
        },
        isSuccess() {
            return this.currentStatus === STATUS_SUCCESS;
        },
        isFailed() {
            return this.currentStatus === STATUS_FAILED;
        }
    },
    methods: {
        reset() {
            // reset form to initial state
            this.currentStatus = STATUS_INITIAL;
            this.uploadedFiles = [];
            this.uploadError = null;
        },
        save(formData) {
            this.currentStatus = STATUS_SAVING;
            formData.set('storage_type', this.storageType);
            formData.set('path', this.path);
            FileApi.upload(formData)
                .then(x => {
                    this.uploadedFiles = [].concat(x);
                    this.currentStatus = STATUS_SUCCESS;
                })
                .catch(err => {
                    this.uploadError = err.response;
                    this.currentStatus = STATUS_FAILED;
                });
        },
        filesChange(fieldName, fileList) {
            const formData = new FormData();
            if (!fileList.length) return;
            Array.from(Array(fileList.length).keys()).map(x => {
                formData.append(fieldName, fileList[x], fileList[x].name);
            });
            this.save(formData);
            this.fileCount = fileList.length;
        }
    },
    mounted() {
        this.reset();
    }
};
</script>
