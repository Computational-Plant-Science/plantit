<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            profile.darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <b-row>
                <b-col>
                    <b-row align-h="center" v-if="openedCollectionLoading">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner> </b-row
                    ><b-row v-else-if="data !== null && data !== undefined"
                        ><b-col>
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                {{ openedCollection.path }}
                            </h4>
                            <small
                                >Open on
                                <b>{{ openedCollection.cluster }}</b></small
                            ><br />
                            <small
                                >Showing
                                <b class="mr-1"
                                    >{{ filesShown }} of
                                    {{ data.files.length }}</b
                                >file(s),
                                <b class="mr-1">{{
                                    openedCollection.modified.length
                                }}</b
                                >modified</small
                            >
                        </b-col></b-row
                    ></b-col
                >
                <b-col md="auto" align-self="end">
                    <b-row>
                        <b-dropdown
                            :disabled="
                                !dataLoading &&
                                    data !== null &&
                                    data.files.length === 0
                            "
                            dropleft
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            class="mb-2 text-right"
                        >
                            <template #button-content>
                                {{ viewMode }} View
                            </template>
                            <b-dropdown-item @click="setViewMode('Grid')"
                                >Grid</b-dropdown-item
                            >
                            <b-dropdown-item @click="setViewMode('Carousel')"
                                >Carousel</b-dropdown-item
                            >
                        </b-dropdown>
                        <b-button
                            title="Close collection"
                            variant="outline-danger"
                            class="ml-1 mb-2 text-right"
                            @click="closeCollection"
                        >
                            Close Collection
                            <i class="far fa-folder fa-1x fa-fw"></i>
                        </b-button>
                    </b-row>
                    <b-row align-h="end">
                        <b-pagination
                            size="sm"
                            class="mr-2"
                            v-model="currentPage"
                            :per-page="filesPerPage"
                            :total-rows="totalFileCount"
                        ></b-pagination></b-row></b-col
            ></b-row>
            <br />
            <b-row
                v-if="!dataLoading && data !== null && data !== undefined"
                align-h="center"
                class="m-1"
            >
                <b-col>
                    <b-overlay
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        :show="openedCollection.opening"
                        rounded="sm"
                    >
                        <span
                            v-if="
                                !dataLoading &&
                                    data !== null &&
                                    data.files.length === 0
                            "
                            >No files in this collection.</span
                        >
                        <b-card-group v-else-if="viewMode === 'Grid'" columns>
                            <b-card
                                :img-src="
                                    openedCollection.opening ||
                                    fileIs3dModel(file.label)
                                        ? null
                                        : `/apis/v1/collections/thumbnail/?path=${file.path}`
                                "
                                v-for="file in currentPageFiles"
                                v-bind:key="file.id"
                                style="min-width: 20rem;"
                                class="overflow-hidden mb-4 mr-4 text-left"
                                :bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                :header-bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                border-variant="default"
                                :header-border-variant="
                                    profile.darkMode ? 'secondary' : 'default'
                                "
                                :text-variant="
                                    profile.darkMode ? 'white' : 'dark'
                                "
                            >
                                <p
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    <b>{{ file.label }}</b>
                                    <br />
                                    <small
                                        >{{
                                            `Last modified: ${prettifyShort(
                                                file['date-modified']
                                            )}`
                                        }}
                                    </small>
                                </p>
                                <hr />
                                <b-button
                                    :title="`Download ${file.label}`"
                                    v-b-tooltip.hover
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    class="text-left m-0"
                                    @click="downloadFile(file)"
                                >
                                    <i class="fas fa-download fa-fw"></i>
                                </b-button>
                                <b-button
                                    :title="`Annotate ${file.label}`"
                                    v-b-tooltip.hover
                                    v-if="fileIsImage(file.label)"
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    class="text-left m-0"
                                    @click="annotateFile(file)"
                                >
                                    <i class="fas fa-pen-fancy fa-fw"></i>
                                </b-button>
                            </b-card>
                        </b-card-group>
                        <b-carousel
                            v-show="viewMode === 'Carousel'"
                            controls
                            :interval="0"
                            @sliding-end="
                                slide => renderPreview(currentPageFiles[slide])
                            "
                        >
                            <b-carousel-slide
                                v-for="file in currentPageFiles"
                                v-bind:key="file.id"
                                :img-src="
                                    fileIsImage(file.label)
                                        ? `/apis/v1/collections/thumbnail/?path=${file.path}`
                                        : ''
                                "
                                ><template
                                    v-if="
                                        fileIsText(file.label) ||
                                            fileIs3dModel(file.label)
                                    "
                                    #img
                                    ><div
                                        :id="file.id"
                                        :class="
                                            profile.darkMode
                                                ? 'theme-container-dark'
                                                : 'theme-container-light'
                                        "
                                        style="min-height: 50rem;white-space: pre-line;"
                                    >
                                        {{ file.textContent }}
                                    </div></template
                                >
                                <template
                                    v-else-if="fileIs3dModel(file.label)"
                                    #img
                                    ><div
                                        :class="
                                            profile.darkMode
                                                ? 'theme-container-dark'
                                                : 'theme-container-light'
                                        "
                                        style="min-height: 50rem;white-space: pre-line;"
                                        :id="file.id"
                                    ></div
                                ></template>
                                <template #default
                                    ><b-row
                                        :class="
                                            profile.darkMode
                                                ? 'theme-container-dark p-3'
                                                : 'theme-container-light p-3'
                                        "
                                        style="opacity: 0.9;"
                                    >
                                        <b-col class="text-left">
                                            <h5
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                            >
                                                {{ file.label }}
                                            </h5>
                                            <small>{{
                                                `Last modified: ${prettifyShort(
                                                    file['date-modified']
                                                )}`
                                            }}</small>
                                        </b-col>
                                        <b-col md="auto" align-self="end">
                                            <b-button
                                                :title="
                                                    `Download ${file.label}`
                                                "
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                class="text-right m-0"
                                                @click="downloadFile(file)"
                                            >
                                                <i
                                                    class="fas fa-download fa-fw"
                                                ></i>
                                            </b-button>
                                            <b-button
                                                v-if="fileIsImage(file.label)"
                                                :title="
                                                    `Annotate ${file.label}`
                                                "
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                class="text-right m-0"
                                                @click="annotateFile(file)"
                                            >
                                                <i
                                                    class="fas fa-pen-fancy fa-fw"
                                                ></i> </b-button
                                        ></b-col> </b-row></template
                            ></b-carousel-slide>
                        </b-carousel>
                    </b-overlay>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';
import router from '@/router';
import * as yaml from 'js-yaml';
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';

export default {
    name: 'collection',
    data: function() {
        return {
            data: null,
            dataLoading: false,
            viewMode: 'Grid',
            collectionNotFound: false,
            currentFile: '',
            currentPage: 1,
            filesPerPage: 10,
            currentModel: {
                scene: null,
                mesh: null,
                material: null,
                geometry: null,
                renderer: null,
                loader: null,
                id: null
            }
        };
    },
    beforeDestroy() {
      this.unrenderPreview();
    },
  async mounted() {
        await this.loadCollection();
        this.renderPreviews(false);
        this.renderPreview(this.currentPageFiles[0]);
        this.currentFile =
            this.data !== null && this.data.files.length > 0
                ? this.data.files[0]
                : '';
    },
    watch: {
        viewMode() {
            this.unrenderPreview();
        },
        openedCollection() {
            if (!this.openedCollection.opening) this.renderPreviews();
        }
    },
    methods: {
        renderPreview(f) {
            var camera = new THREE.PerspectiveCamera(
                35,
                window.innerWidth / window.innerHeight,
                1,
                15
            );
            // camera.position.set(3, 0.15, 3);
            camera.position.z = 2;
            camera.zoom = 0.5;

            var cameraTarget = new THREE.Vector3(0, -0.1, 0);

            var scene = new THREE.Scene();
            // scene.background = new THREE.Color(0x72645b);
            scene.fog = new THREE.Fog(0x72645b, 2, 15);

            const loader = new PLYLoader();
            var comp = this;
            loader.load(
                `/apis/v1/collections/thumbnail/?path=${f.path}`,
                function(geometry) {
                    geometry.computeVertexNormals();

                    // const material = new THREE.MeshStandardMaterial({
                    //     color: 0x0055ff,
                    //     flatShading: true
                    // });
                    const material = new THREE.PointsMaterial({
                        // color: 0x0055ff,
                        size: 0.005,
                      vertexColors: THREE.VertexColors
                    });
                    const mesh = new THREE.Points(geometry, material);
                    //const mesh = new THREE.Mesh(geometry, material);
                    // const mesh = new THREE.Mesh(geometry);

                    mesh.position.y = -0.3;
                    // mesh.position.z = 0.3;
                    mesh.rotation.x = -Math.PI / 2;
                    mesh.scale.multiplyScalar(0.5);

                    mesh.castShadow = true;
                    mesh.receiveShadow = true;

                    comp.currentModel.geometry = geometry;
                    comp.currentModel.material = material;
                    comp.currentModel.mesh = mesh;

                    scene.add(mesh);
                }
            );

            // Lights

            scene.add(new THREE.HemisphereLight(0x443333, 0x111122));

            var addShadowedLight = function(x, y, z, color, intensity) {
                const directionalLight = new THREE.DirectionalLight(
                    color,
                    intensity
                );
                directionalLight.position.set(x, y, z);
                scene.add(directionalLight);

                directionalLight.castShadow = true;

                const d = 1;
                directionalLight.shadow.camera.left = -d;
                directionalLight.shadow.camera.right = d;
                directionalLight.shadow.camera.top = d;
                directionalLight.shadow.camera.bottom = -d;

                directionalLight.shadow.camera.near = 1;
                directionalLight.shadow.camera.far = 4;

                directionalLight.shadow.mapSize.width = 1024;
                directionalLight.shadow.mapSize.height = 1024;

                directionalLight.shadow.bias = -0.001;
            };

            var onWindowResize = function() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();

                renderer.setSize(window.innerWidth, window.innerHeight);
            };

            var animate = function() {
                requestAnimationFrame(animate);
                render();
            };

            var render = function() {
                const timer = Date.now() * 0.00005;

                camera.position.x = Math.sin(timer) * 2.5;
                camera.position.z = Math.cos(timer) * 2.5;

                camera.lookAt(cameraTarget);

                renderer.render(scene, camera);
            };

            addShadowedLight(1, 1, 1, 0xffffff, 1.35);
            // addShadowedLight(0.5, 1, -1, 0xffaa00, 1);

            // renderer

            var renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.outputEncoding = THREE.sRGBEncoding;

            renderer.shadowMap.enabled = true;

            // resize

            window.addEventListener('resize', onWindowResize);
            document.getElementById(f.id).innerHTML = '';
            document.getElementById(f.id).prepend(renderer.domElement);
            //.appendChild(renderer.domElement);

            this.currentModel.scene = scene;
            this.currentModel.loader = loader;
            this.currentModel.renderer = renderer;
            this.currentModel.id = f.id;

            animate();
        },
        unrenderPreview() {
            this.currentModel.scene.remove(this.currentModel.mesh);
            this.currentModel.renderer.dispose();
            this.currentModel.renderer.renderLists.dispose();
            // this.currentModel.loader.dispose();
            this.currentModel.geometry.dispose();
            this.currentModel.material.dispose();
        },
        renderPreviews(plys = false) {
            this.data.files
                .filter(f => this.fileIsText(f.label))
                .map(async f => await this.loadTextContent(f));
            if (plys)
                this.data.files
                    .filter(f => this.fileIs3dModel(f.label))
                    .map(f => this.renderPreview(f));
        },
        async downloadFile(file) {
            this.downloading = true;
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/fileio/download?path=${file.path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        },
                        responseType: 'blob'
                    }
                )
                .then(response => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', file.path);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    alert(`Failed to download '${file.path}''`);
                    throw error;
                });
        },
        fileIsImage(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'czi'
            );
        },
        fileIsText(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'csv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'tsv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yaml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'log' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'out' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'err'
            );
        },
        fileIs3dModel(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'ply'
            );
        },
        async closeCollection() {
            await this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to close ${this.openedCollection.path} on ${this.openedCollection.cluster}?`,
                    {
                        title: 'Close Collection?',
                        size: 'sm',
                        okVariant: 'outline-danger',
                        cancelVariant: 'white',
                        okTitle: 'Yes',
                        cancelTitle: 'No',
                        centered: true
                    }
                )
                .then(async value => {
                    if (value) {
                        await this.$store.dispatch('collections/closeOpened');
                        await router.push({
                            name: 'user',
                            params: {
                                username: this.profile.djangoProfile.username
                            }
                        });
                    }
                })
                .catch(err => {
                    throw err;
                });
        },
        annotateFile() {},
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        setViewMode(mode) {
            this.viewMode = mode;
        },
        async loadCollection() {
            this.dataLoading = true;
            return await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${this.$router.currentRoute.params.path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(async response => {
                    this.data = response.data;
                    this.dataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.dataLoading = false;
                    throw error;
                });
        },
        async loadTextContent(file) {
            await axios
                .get(`/apis/v1/collections/content/?path=${file.path}`)
                .then(response => {
                    this.data.files = this.data.files.map(f => {
                        if (f.label === file.label) {
                            if (
                                f.label.endsWith('yml') ||
                                f.label.endsWith('yaml')
                            ) {
                                f['textContent'] = yaml.dump(
                                    yaml.load(response.data)
                                );
                            } else f['textContent'] = response.data;
                        }
                        return f;
                    });
                });
        }
    },
    asyncComputed: {},
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow', 'workflowsRecentlyRun']),
        ...mapGetters('collections', [
            'openedCollection',
            'openedCollectionLoading'
        ]),
        filesShown() {
            return this.totalFileCount < this.filesPerPage
                ? this.totalFileCount
                : `${Math.max(
                      this.filesPerPage * this.currentPage -
                          this.filesPerPage +
                          1,
                      1
                  )} - ${
                      this.currentPage * this.filesPerPage <=
                      this.totalFileCount
                          ? (this.totalFileCount < this.filesPerPage
                                ? this.totalFileCount
                                : this.filesPerPage) *
                                (this.currentPage + 1) -
                            this.filesPerPage
                          : this.totalFileCount
                  }`;
        },
        totalFileCount() {
            return this.dataLoading || this.data === null
                ? 0
                : this.data.files.length;
        },
        currentPageFiles() {
            return this.dataLoading || this.data === null
                ? []
                : this.data.files.slice(
                      this.currentPage - 1,
                      this.filesPerPage
                  );
        }
    }
};
</script>

<style scoped></style>
