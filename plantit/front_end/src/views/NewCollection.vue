<template>
    <div></div>
</template>

<template>
    <div>
        <b-container class="justify-content-md-center">
            <b-card>
                <template v-slot:header style="background-color: white">
                    <b-row align-v="center">
                        <b-col class="mt-2" style="color: white">
                            <h5>
                                <i class="fas fa-layer-group dark"></i> Sources
                            </h5>
                        </b-col>
                    </b-row>
                </template>
                <div>
                    <h5>Existing</h5>
                    <SelectCollection
                        selectable="true"
                        perPage="10"
                        filterable="true"
                    ></SelectCollection>
                    <h5>New</h5>
                    <b-form @submit="onSubmit">
                        <b-form-group label="Name:" label-for="input-name">
                            <b-form-input
                                id="input-name"
                                v-model="form.name"
                                required
                                placeholder="Enter name..."
                            ></b-form-input>
                        </b-form-group>
                        <b-form-group
                            label="Location:"
                            label-for="input-storageType"
                        >
                            <b-form-select
                                v-model="form.storageType"
                                :options="options"
                            ></b-form-select>
                        </b-form-group>
                    </b-form>
                </div>
                <template v-slot:footer style="background-color: white">
                    <b-row align-v="center">
                        <b-col class="mr-1 pr-1">
                            <b-button @click="cancel" variant="outline-danger"
                                >Cancel</b-button
                            >
                        </b-col>
                        <b-col class="ml-1 pl-1 pr-2" md="auto">
                            <b-button
                                type="submit"
                                variant="outline-dark"
                                @click="onSubmit"
                                >Submit</b-button
                            >
                        </b-col>
                    </b-row>
                </template>
            </b-card>
        </b-container>
    </div>
</template>

<script>
import SelectCollection from '@/components/collections/SelectCollection';
import FileManagerApi from '@/services/apiV1/FileManager';
import CollectionApi from '@/services/apiV1/CollectionManager';

export default {
    name: 'NewCollection',
    components: {
        SelectCollection
    },
    data() {
        return {
            form: {
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
                        if (value === true) {
                            this.saveCollection();
                        }
                    });
            } else {
                this.saveCollection();
            }
        },
        cancel() {
            this.$emit('back');
        },
        saveCollection() {
            CollectionApi.newCollection(
                this.form.name,
                this.form.description,
                this.form.storageType,
                this.form.metadata
            ).then(response => {
                this.$emit('view', response.data);
                // router.push({
                //     name: 'collection',
                //     query: { pk: response.data.pk }
                // });
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.color
    color: $color-button
    //border-left: 5px solid $color-button
    vertical-align: middle

.green
    color: $color-button
</style>
