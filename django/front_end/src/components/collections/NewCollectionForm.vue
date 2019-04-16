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

            <b-form-group label="Location:" label-for="input-storageType">
                <b-form-select
                    :v-model="form.storageType"
                    :options="options"
                ></b-form-select>
            </b-form-group>

            <b-form-group label="Base File Path:" label-for="input-base-path">
                <b-form-input
                    id="input-base-path"
                    v-model="form.basePath"
                    required
                    placeholder="Enter base file path."
                ></b-form-input>
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
import FileManagerApi from '@/services/apiV1/FileManager'
import CollectionApi from '@/services/apiV1/CollectionManager'

export default {
    name: 'NewCollection',
    components: {},
    data() {
        return {
            form: {
                name: '',
                description: '',
                storageType: 'irods',
                basePath: 'files/'
            },
            options: []
        };
    },
    mounted: function() {
      FileManagerApi.getStorageTypes()
      .then((data) =>{ this.options = data.map( (item) => {
        return { value: item, text: item}
        })
      })
    },
    methods: {
        onSubmit(evt) {
            evt.preventDefault();
            CollectionApi.newCollection(
              this.form.name,
              this.form.description,
              this.form.storageType,
              this.form.basePath
            ).then((response) => {
              router.push({ name: 'collection', query: { pk: response.data.pk }})
            });
        },
        cancel() {
            router.push({ name: 'collections' });
        }
    }
};
</script>
