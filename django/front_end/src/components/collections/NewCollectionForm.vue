<template>
    <div>
        <b-form @submit="onSubmit">
            <b-form-group label="Collection Name:" label-for="input-name">
                <b-form-input
                    id="input-name"
                    v-model="form.name"
                    required
                    placeholder="Enter Name"
                ></b-form-input>
            </b-form-group>

            <b-form-group label="Description:" label-for="input-desc">
                <b-form-textarea
                    id="input-desc"
                    v-model="form.description"
                    required
                    placeholder="Enter description...."
                ></b-form-textarea>
            </b-form-group>

            <b-form-group label="Metadata:" label-for="input-desc">
                <EditMetadata
                    v-model="form.metadata"
                    @unsaved="
                        e => {
                            unsavedMetadata = e;
                        }
                    "
                ></EditMetadata>
            </b-form-group>

            <b-form-group label="Location:" label-for="input-storageType">
                <b-form-select
                    v-model="form.storageType"
                    :options="options"
                ></b-form-select>
            </b-form-group>

            <b-button type="submit" variant="primary" class="mr-2"
                >Submit</b-button
            >
            <b-button @click="cancel" variant="danger" class="mr-2"
                >Cancel</b-button
            >
        </b-form>
    </div>
</template>

<script>
import router from '@/router';
import FileManagerApi from '@/services/apiV1/FileManager';
import CollectionApi from '@/services/apiV1/CollectionManager';
import EditMetadata from '@/components/collections/EditMetadata';

export default {
    name: 'NewCollection',
    components: {
        EditMetadata
    },
    data() {
        return {
            form: {
                name: '',
                description: '',
                storageType: 'irods',
                metadata: []
            },
            unsavedMetadata: false,
            options: []
        };
    },
    mounted: function() {
        FileManagerApi.getStorageTypes().then(data => {
            this.options = data.map(item => {
                return { value: item, text: item };
            });
        });
    },
    methods: {
        onSubmit(evt) {
            evt.preventDefault();
            if (this.unsavedMetadata) {
                this.$bvModal
                    .msgBoxConfirm(
                        `The metadata key/value left in the input box will not be saved,
                 continue anyways? (Click the "plus" next to the value to save it)`,
                        {
                            title: 'Unsaved Metadata',
                            centered: true
                        }
                    )
                    .then(value => {
                        if (value == true) {
                            this.saveCollection();
                        }
                    });
            } else {
                this.saveCollection();
            }
        },
        cancel() {
            router.push({ name: 'collections' });
        },
        saveCollection() {
            CollectionApi.newCollection(
                this.form.name,
                this.form.description,
                this.form.storageType,
                this.form.metadata
            ).then(response => {
                router.push({
                    name: 'collection',
                    query: { pk: response.data.pk }
                });
            });
        }
    }
};
</script>
