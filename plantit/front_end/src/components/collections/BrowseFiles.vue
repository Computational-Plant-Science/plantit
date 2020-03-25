<template>
    <div>
        <v-jstree
            :data="treeData"
            @item-click="changed"
            ref="tree"
            show-checkbox
            multiple
            :allow-batch="selectFiles"
            whole-row
            class="file-browser"
            :async="loadTreeDataAsync"
        ></v-jstree>
    </div>
</template>

<script>
import VJstree from 'vue-jstree';
import FileManagerApi from '@/services/apiV1/FileManager';

export default {
    name: 'BrowseFiles',
    components: {
        VJstree,
    },
    props: {
        selectedFiles: {
            //Object to place the selected items in.
            // selected[item.text] = item
            required: true,
            type: Object
        },
        basePath: {
            //The base path of the file browse
            required: true,
            type: String
        },
        storageType: {
            //The storage type to access
            required: true,
            type: String
        }
    },
    data() {
        return {
            //The file tree data structure
            treeData: [],
            // Select files (true) or folders (false) as samples
            selectFiles: true
        };
    },
    methods: {
        loadTreeDataAsync(oriNode, resolve) {
            /* Load file tree branches as needed Async. */
            let path = oriNode.data.path ? oriNode.data.path : '';
            FileManagerApi.listDirBase(
                this.basePath,
                path,
                this.storageType
            ).then(data => {
                data = data.map(d => {
                    if (d.isLeaf) {
                        d.disabled = !this.selectFiles;
                    }

                    return d;
                });
                resolve(data);
            });
        },
        fileUploaded(files) {
            /* Add uplaoded files to the file tree

           Args:
              files (array): name of files to add
        */
            files.forEach(file => {
                this.treeData.push(
                    this.$refs.tree.initializeDataItem({
                        text: file,
                        size: 0,
                        path: file,
                        isLeaf: true,
                        icon: 'far fa-file'
                    })
                );
            });
        },
        //eslint-disable-next-line no-unused-vars
        changed(node, item, e) {
            /*
          Called when a file tree node is changed
        */
            let set = item => {
                /** Add item to the selectedFiles list **/
                if (this.selectFiles) {
                    if (item.isLeaf) {
                        this.$set(this.selectedFiles, item.text, item);
                    }
                    item.children.forEach(i => {
                        set(i);
                    });
                } else {
                    this.$set(this.selectedFiles, item.text, item);
                }
            };
            let del = item => {
                /* remove item from the selected files list */
                if (this.selectedFiles) {
                    if (item.isLeaf) {
                        this.$delete(this.selectedFiles, item.text);
                    }
                    item.children.forEach(i => {
                        del(i);
                    });
                } else {
                    this.$delete(this.selectedFiles, item.text);
                }
            };

            if (item.selected) {
                set(item);
            } else {
                del(item);
            }
        }
    },
    watch: {
        selectFiles() {
            /** Disable / Enable file selection in file tree **/
            this.treeData = this.treeData.map(node => {
                if (node.isLeaf) {
                    node.disabled = !this.selectFiles;
                }
                return node;
            });
        }
    }
};
</script>
