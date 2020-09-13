<template>
    <li>
        <div :class="{ bold: isDir }" @click="toggle">
            {{ item.name }}
            <span v-if="isDir">[{{ isOpen ? '-' : '+' }}]</span>
        </div>
        <ul v-show="isOpen" v-if="isDir">
            <DataTreeNode
                v-for="(child, index) in node.children"
                :key="index"
                :node="child"
            ></DataTreeNode>
            <li>+</li>
        </ul>
    </li>
</template>
<script>
export default {
    name: 'DataTreeNode',
    props: {
        node: Object,
        isDirectory: Boolean
    },
    data: function() {
        return {
            isOpen: false
        };
    },
    computed: {
        isDir: function() {
            return this.node.children && this.node.children.length;
        }
    },
    methods: {
        toggle: function() {
            if (this.isDirectory) this.isOpen = !this.isOpen;
        }
        // createDir: function() {
        //     if (!this.isDir) {
        //         this.$emit('addDirectory', this.node.path);
        //         this.isOpen = true;
        //     }
        // }
    }
};
</script>

<style scoped></style>
