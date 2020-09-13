<template>
    <div class="w-100 p-4">
        <br />
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h1>Community Datasets</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="communityFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!communityFilter"
                                    @click="communityFilter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                </b-row>
            </template>
            <b-table
                show-empty
                small
                sticky-header="true"
                selectable
                hover
                responsive="sm"
                :items="communityDatasets"
                :fields="fields"
                select-mode="single"
                :filter="communityFilter"
                :borderless="true"
                class="table-responsive"
                @row-selected="onSelected"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
            >
                <template v-slot:cell(actions)="row">
                    <!--<b-button
                                size="sm"
                                @click="togglePin(row.item)"
                                variant="dark"
                            >
                                <b-img
                                    v-if="row.item.pinned"
                                    :src="
                                        require('@/assets/icons/pin icons/pin2.svg')
                                    "
                                    width="18px"
                                >
                                </b-img>
                                <b-img
                                    v-else
                                    :src="
                                        require('@/assets/icons/pin icons/pin.svg')
                                    "
                                    width="18px"
                                >
                                </b-img>
                            </b-button>-->
                    <b-button
                        size="sm"
                        variant="outline-danger"
                        @click="onRemove(row.item)"
                        class="ml-2 mr-2"
                    >
                        Delete
                    </b-button>
                </template>
            </b-table>
        </b-card>
        <br />
        <b-card
            header-bg-variant="white"
            border-variant="white"
            header-border-variant="white"
        >
            <template v-slot:header style="background-color: white">
                <b-row align-v="center">
                    <b-col style="color: white">
                        <h1>Your Datasets</h1>
                    </b-col>
                    <b-col md="auto" class="b-form-col">
                        <b-input-group>
                            <b-form-input
                                v-model="userFilter"
                                placeholder="Filter..."
                                class="b-form-input"
                            ></b-form-input>
                            <b-input-group-append>
                                <b-button
                                    :disabled="!userFilter"
                                    @click="userFilter = ''"
                                    variant="white"
                                    >Clear
                                </b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-col>
                    <b-col md="auto">
                        <b-button
                            variant="outline-dark"
                            v-b-tooltip.hover
                            title="Create a new dataset"
                            v-b-modal.modal-prevent-closing
                        >
                            <i class="fas fa-plus"></i>
                        </b-button>
                    </b-col>
                </b-row>
            </template>
            <FileTreeItem
                node="tree"
                > </FileTreeItem>
        </b-card>
    </div>
</template>

<script>
// import router from '../router';
import DataTreeNode from '@/components/DataTreeNode.vue';
import { mapGetters, mapActions } from 'vuex';

export default {
    name: 'Data',
    components: {
        FileTreeItem: DataTreeNode
    },
    data() {
        return {
            filter: '',
            sortBy: 'pk',
            sortDesc: true,
            fields: [
                {
                    key: 'pk',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'name',
                    sortable: true
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ]
        };
    },
    created: function() {
        this.crumbs = this.$route.meta.crumb;
        this.$store.dispatch('loadUsers');
        this.$store.dispatch('loadRootDirectory', {
            path: `/iplant/home/${this.user.username}`,
            token: this.profile.cyverse_token
        });
    },
    computed: mapGetters(['user', 'profile', 'tree']),
    methods: mapActions(['loadDirectory', 'addDirectory', 'addFile', 'remove']),
};
</script>
