<template>
    <div>
        {{ collection.name }}
        <br />
        {{ collection.description }}
        <br />
        <table width="100%">
          <tr v-for="field in collection.metadata">
            <td>{{ field.name }}</td>
            <td>{{ field.value }}</td>
          </tr>
        </table>
        <EditMetadata
          ref="editMeta"
          :collection="collection"
        >
        </EditMetadata>
        <b-button @click="$refs['editMeta'].show()">Edit</b-button>
    </div>
</template>

<script>
import EditMetadata from '@/components/collections/EditMetadata'

export default {
    name: 'CollectionDetails',
    components: {
      EditMetadata
    },
    props: ['collection'],
    methods: {},
    data() {
        return {};
    }
};
</script>

<style scoped></style>
