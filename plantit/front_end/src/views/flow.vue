<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <b-row>
                <b-col>
                    <b-row>
                        <b-col>
                            <b-card
                                :bg-variant="darkMode ? 'dark' : 'white'"
                                :header-bg-variant="darkMode ? 'dark' : 'white'"
                                border-variant="default"
                                :header-border-variant="
                                    darkMode ? 'dark' : 'white'
                                "
                                :text-variant="darkMode ? 'white' : 'dark'"
                                class="overflow-hidden"
                            >
                                <b-alert
                                    id="flowInvalid"
                                    :show="
                                        !this.flowLoading && !this.flowValidated
                                    "
                                    variant="danger"
                                    >This flow's configuration is invalid. It
                                    cannot be run in this state.
                                    <b-link
                                        :href="
                                            'https://github.com/' +
                                                this.username +
                                                '/' +
                                                this.name +
                                                '/issues/new'
                                        "
                                        ><i
                                            class="fab fa-github fa-1x mr-1 fa-fw"
                                        ></i
                                        >File an issue?</b-link
                                    ><br />
                                    Errors:
                                    {{ this.flowValidationErrors.join(', ') }}
                                </b-alert>
                                <flowdetail
                                    :show-public="true"
                                    :flow="flow"
                                    :selectable="false"
                                ></flowdetail>
                            </b-card>
                        </b-col>
                    </b-row>
                    <br />
                    <b-row
                        ><b-col md="auto" class="mr-0" align-self="end">
                            <b-input-group>
                                <template #prepend>
                                    <b-input-group-text
                                        >Run
                                        {{
                                            flow.config.name
                                        }}</b-input-group-text
                                    >
                                </template>
                                <template #append>
                                    <b-dropdown
                                        :variant="darkMode ? 'dark' : 'light'"
                                        :text="submitType"
                                        v-model="submitType"
                                        block
                                    >
                                        <b-dropdown-item
                                            @click="submitType = 'Once'"
                                            >Once</b-dropdown-item
                                        >
                                        <!--<b-dropdown-item
                                            @click="submitType = 'Periodically'"
                                            >Periodically</b-dropdown-item
                                        >-->
                                    </b-dropdown>
                                </template>
                            </b-input-group> </b-col
                        ><b-col
                            ><b-button
                                :disabled="!flowReady"
                                @click="onStart"
                                variant="success"
                                block
                            >
                                {{
                                    submitType === 'Once' ? 'Start' : 'Schedule'
                                }}
                            </b-button></b-col
                        ></b-row
                    >
                    <br />
                    <b-row v-if="submitType === 'Periodically'"
                        ><b-col
                            ><b-card
                                ><b-form-group
                                    id="input-group-4"
                                    label-for="input-4"
                                    description="Configure when this flow should run."
                                >
                                    <VueCronEditorBuefy
                                        v-model="submissionTime"
                                    ></VueCronEditorBuefy> </b-form-group></b-card></b-col
                    ></b-row>
                    <b-row>
                        <b-col>
                            <b-card-group deck columns>
                                <b-card
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="darkMode ? 'white' : 'dark'"
                                    style="min-width: 20rem"
                                    class="mb-4"
                                >
                                    <b-row>
                                        <b-col>
                                            <h4
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="tags.length > 0"
                                                    class="fas fa-tags fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="fas fa-tags fa-fw"
                                                ></i>
                                                Tags
                                            </h4>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col
                                            ><b
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Attach tags to this run.
                                            </b>
                                        </b-col>
                                    </b-row>
                                    <b-row>
                                        <b-col>
                                            <multiselect
                                                style="z-index: 100"
                                                v-model="tags"
                                                mode="tags"
                                                :multiple="true"
                                                :close-on-select="false"
                                                :clear-on-select="false"
                                                :preserve-search="true"
                                                :options="tagOptions"
                                                :taggable="true"
                                                placeholder="Add tags..."
                                                :createTag="true"
                                                :appendNewTag="true"
                                                :searchable="true"
                                                @tag="addTag"
                                            >
                                            </multiselect>
                                        </b-col>
                                    </b-row>
                                </b-card>
                                <b-card
                                    v-if="
                                        flow !== null &&
                                        flow.config.params !== undefined
                                            ? flow.config.params.length !== 0
                                            : false
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="darkMode ? 'white' : 'dark'"
                                    style="min-width: 20rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="
                                                        params &&
                                                            params.every(
                                                                p =>
                                                                    p.value !==
                                                                    ''
                                                            )
                                                    "
                                                    class="fas fa-keyboard fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="fas fa-keyboard fa-fw"
                                                ></i>
                                                Parameters
                                            </h4>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col
                                            ><b>
                                                Configure parameters for this
                                                run.
                                            </b>
                                            <br /><b-table
                                                :items="params"
                                                :fields="fields"
                                                responsive="sm"
                                                borderless
                                                small
                                                sticky-header="true"
                                                caption-top
                                                :table-variant="
                                                    darkMode ? 'dark' : 'white'
                                                "
                                            >
                                                <template
                                                    v-slot:cell(name)="param"
                                                >
                                                    {{
                                                        param.item.key
                                                            .split('=')[0]
                                                            .toLowerCase()
                                                    }}
                                                </template>
                                                <template
                                                    v-slot:cell(value)="param"
                                                >
                                                    <!--<multiselect
                                            v-if="
                                                param.key === 'filetype' &&
                                                    this.input.patterns.length >
                                                        0
                                            "
                                            :multiple="true"
                                            :close-on-select="false"
                                            :clear-on-select="false"
                                            :preserve-search="true"
                                            :preselect-first="true"
                                            v-model="inputSelectedPatterns"
                                            :options="input.patterns"
                                        ></multiselect>-->
                                                    <b-form-input
                                                        size="sm"
                                                        v-model="
                                                            param.item.value
                                                        "
                                                        :placeholder="
                                                            param.item.key.split(
                                                                '='
                                                            ).length === 1
                                                                ? 'Enter a value for \'' +
                                                                  param.item.key
                                                                      .split(
                                                                          '='
                                                                      )[0]
                                                                      .toLowerCase() +
                                                                  '\''
                                                                : param.item.key
                                                                      .split(
                                                                          '='
                                                                      )[1]
                                                                      .toLowerCase()
                                                        "
                                                    ></b-form-input>
                                                </template> </b-table></b-col
                                    ></b-row>
                                </b-card>
                                <b-card
                                    v-if="
                                        flow !== null &&
                                            flow.config.input !== undefined &&
                                            flow.config.input.path !== undefined
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="darkMode ? 'white' : 'dark'"
                                    style="min-width: 50rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="inputReady"
                                                    class="fas fa-download fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="fas fa-download fa-fw"
                                                ></i>
                                                Input
                                                {{
                                                    this.input.kind[0].toUpperCase() +
                                                        this.input.kind.substr(
                                                            1
                                                        )
                                                }}
                                            </h4>
                                        </b-col>
                                    </b-row>
                                    <runinput
                                        :default-path="flow.config.input.path"
                                        :user="user"
                                        :kind="input.kind"
                                        v-on:inputSelected="inputSelected"
                                    ></runinput>
                                    <b-row v-if="input.filetypes.length > 0">
                                        <b-col>
                                            <b
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Select one or more input
                                                filetypes.
                                            </b>
                                            <multiselect
                                                :multiple="true"
                                                :close-on-select="false"
                                                :clear-on-select="false"
                                                :preserve-search="true"
                                                :preselect-first="true"
                                                v-model="inputSelectedPatterns"
                                                :options="input.filetypes"
                                            ></multiselect>
                                        </b-col>
                                    </b-row>
                                    <b-alert
                                        class="mt-1"
                                        :variant="
                                            inputFiletypeSelected
                                                ? 'success'
                                                : 'danger'
                                        "
                                        :show="true"
                                        >Selected:
                                        {{
                                            inputFiletypeSelected
                                                ? '*.' +
                                                  inputSelectedPatterns.join(
                                                      ', *.'
                                                  )
                                                : 'None'
                                        }}
                                        <i
                                            v-if="inputFiletypeSelected"
                                            class="fas fa-check text-success"
                                        ></i>
                                        <i
                                            v-else
                                            class="fas fa-exclamation text-danger"
                                        ></i>
                                    </b-alert>
                                </b-card>
                                <b-card
                                    v-if="
                                        flow &&
                                            flow.config &&
                                            flow.config.input !== undefined &&
                                            flow.config.output.path !==
                                                undefined
                                    "
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="darkMode ? 'white' : 'dark'"
                                    style="min-width: 50rem"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="outputDirectory"
                                                    class="fas fa-upload fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else-if="
                                                        !outputDirectory &&
                                                            darkMode
                                                    "
                                                    class="fas fa-upload fa-fw text-white"
                                                ></i>
                                                <i
                                                    v-else-if="
                                                        !outputDirectory &&
                                                            !darkMode
                                                    "
                                                    class="fas fa-upload fa-fw text-dark"
                                                ></i>
                                                Output Sync
                                                {{
                                                    outputDirectory
                                                        ? ''
                                                        : ' (off)'
                                                }}
                                            </h4>
                                        </b-col>
                                        <b-col md="auto">
                                            <b-form-checkbox
                                                v-model="outputDirectory"
                                                switch
                                                size="md"
                                            >
                                            </b-form-checkbox>
                                        </b-col>
                                    </b-row>
                                    <runoutput
                                        v-if="outputDirectory"
                                        :user="user"
                                        v-on:outputSelected="outputSelected"
                                    ></runoutput>
                                </b-card>
                                <b-card
                                    :bg-variant="darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        darkMode ? 'dark' : 'white'
                                    "
                                    style="min-width: 40rem"
                                    :text-variant="darkMode ? 'white' : 'dark'"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="target.name !== ''"
                                                    class="fas fa-server fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="fas fa-server fa-fw"
                                                ></i>
                                                Deployment Target
                                            </h4>
                                        </b-col>
                                    </b-row>
                                    <div>
                                        <b
                                            :class="
                                                darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            Select a cluster or server to submit
                                            this run to.
                                        </b>
                                        <b-row
                                            class="text-right"
                                            v-for="target in targets"
                                            v-bind:key="target.name"
                                        >
                                            <b-col md="auto"
                                                ><b-button
                                                    size="md"
                                                    class="text-left pt-2"
                                                    @click="
                                                        targetSelected(target)
                                                    "
                                                    :variant="
                                                        darkMode
                                                            ? 'dark'
                                                            : 'white'
                                                    "
                                                    :disabled="
                                                        targetUnsupported(
                                                            target
                                                        ) || target.disabled
                                                    "
                                                    >{{ target.name }}</b-button
                                                ></b-col
                                            >
                                            <b-col>
                                                <small
                                                    >{{ target.max_cores }}
                                                    cores,
                                                    {{ target.max_processes }}
                                                    processes, </small
                                                ><span
                                                    v-if="
                                                        parseInt(
                                                            target.max_mem
                                                        ) >=
                                                            parseInt(
                                                                flow.config
                                                                    .resources
                                                                    .mem
                                                            ) &&
                                                            parseInt(
                                                                target.max_mem
                                                            ) > 0
                                                    "
                                                    >{{ target.max_mem }} GB
                                                    memory</span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            target.max_mem
                                                        ) > 0
                                                    "
                                                    class="text-danger"
                                                    >{{ target.max_mem }} GB
                                                    memory</span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            target.max_mem
                                                        ) === -1
                                                    "
                                                    >virtual memory</span
                                                ><span v-if="target.gpu">
                                                    , GPU
                                                </span>
                                                <span v-else
                                                    >, No GPU
                                                </span></b-col
                                            >
                                        </b-row>
                                        <b-row
                                            align-h="center"
                                            v-if="targetsLoading"
                                        >
                                            <b-spinner
                                                type="grow"
                                                label="Loading..."
                                                variant="success"
                                            ></b-spinner>
                                        </b-row>
                                        <b-row
                                            align-h="center"
                                            class="text-center"
                                            v-else-if="
                                                !targetsLoading &&
                                                    targets.length === 0
                                            "
                                        >
                                            <b-col>
                                                None to show.
                                            </b-col>
                                        </b-row>
                                        <b-alert
                                            v-else
                                            class="mt-1"
                                            :variant="
                                                target.name !== ''
                                                    ? 'success'
                                                    : 'danger'
                                            "
                                            :show="true"
                                            >Selected:
                                            {{
                                                target.name !== ''
                                                    ? target.name
                                                    : 'None'
                                            }}
                                            <i
                                                v-if="target.name !== ''"
                                                class="fas fa-check text-success"
                                            ></i>
                                            <i
                                                v-else
                                                class="fas fa-exclamation text-danger"
                                            ></i>
                                        </b-alert>
                                    </div>
                                </b-card>
                            </b-card-group>
                        </b-col>
                    </b-row>
                </b-col>
                <b-col md="auto">
                    <b-row
                        ><b-col align-self="end"
                            ><h5 :class="darkMode ? 'text-white' : 'text-dark'">
                                Scheduled Runs
                            </h5></b-col
                        ></b-row
                    >
                    <b-list-group class="text-left m-0 p-0">
                        <b-row v-if="scheduledRuns.length === 0"
                            ><b-col
                                ><small
                                    >You haven't scheduled any
                                    {{ flow.config.name }} runs.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="task in scheduledRuns"
                            v-bind:key="task.id"
                            :class="
                                darkMode
                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                            "
                        >
                        </b-list-group-item>
                    </b-list-group>
                    <hr />
                    <b-row
                        ><b-col align-self="end"
                            ><h5 :class="darkMode ? 'text-white' : 'text-dark'">
                                Recent Runs
                            </h5></b-col
                        ><!--<b-col class="mb-1" align-self="start" md="auto"
                            ><b-button
                                :variant="darkMode ? 'outline-light' : 'white'"
                                size="sm"
                                v-b-tooltip.hover
                                title="Create Periodic Task"
                                :disabled="target.role !== 'own'"
                                v-b-modal.createTask
                            >
                                <i class="fas fa-plus fa-fw"></i>
                                Create
                            </b-button></b-col
                        >--></b-row
                    >
                    <b-list-group class="text-left m-0 p-0">
                        <b-row v-if="runs.length === 0"
                            ><b-col
                                ><small
                                    >You haven't run
                                    {{ flow.config.name }} yet.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="run in runs"
                            v-bind:key="run.id"
                            :class="
                                darkMode
                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                            "
                            @click="onRunSelected(run)"
                        >
                            <!--<b-img
                                        v-if="
                                            run.flow_image_url !== undefined &&
                                                run.flow_image_url !== null
                                        "
                                        rounded
                                        class="card-img-right"
                                        style="max-width: 4rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                        right
                                        :src="run.flow_image_url"
                                    ></b-img>-->
                            <a
                                :class="darkMode ? 'text-light' : 'text-dark'"
                                :href="`/run/${run.id}`"
                                >{{ run.id }}</a
                            >
                            <br />
                            <b-badge
                                v-for="tag in run.tags"
                                v-bind:key="tag"
                                class="mr-1"
                                variant="secondary"
                                >{{ tag }}
                            </b-badge>
                            <br v-if="run.tags.length > 0" />
                            <small v-if="!run.is_complete">Running</small>
                            <b-badge
                                :variant="
                                    run.is_failure || run.is_timeout
                                        ? 'danger'
                                        : run.is_cancelled
                                        ? 'secondary'
                                        : 'success'
                                "
                                v-else
                                >{{ run.job_status }}</b-badge
                            >
                            <small> on </small>
                            <b-badge class="ml-0 mr-0" variant="secondary">{{
                                run.target
                            }}</b-badge
                            ><small> {{ prettify(run.updated) }}</small>
                            <!--<br />
                                    <small class="mr-1"
                                        ><a
                                            :class="
                                                darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                            :href="
                                                `https://github.com/${run.flow_owner}/${run.flow_name}`
                                            "
                                            ><i class="fab fa-github fa-fw"></i>
                                            {{ run.flow_owner }}/{{
                                                run.flow_name
                                            }}</a
                                        >
                                    </small>-->
                        </b-list-group-item>
                    </b-list-group>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import VueCronEditorBuefy from 'vue-cron-editor-buefy';
import flowdetail from '../components/flow-detail';
import runinput from '../components/run-input';
import runoutput from '../components/run-output';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '../router';
import Multiselect from 'vue-multiselect';
import moment from 'moment';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'flow',
    components: {
        VueCronEditorBuefy,
        Multiselect,
        flowdetail,
        runinput,
        runoutput
    },
    props: {
        username: {
            required: true
        },
        name: {
            required: true
        }
    },
    data: function() {
        return {
            submitType: 'Once',
            submissionTime: '',
            runs: [],
            scheduledRuns: [],
            flow: null,
            flowLoading: true,
            flowValidated: false,
            flowValidationErrors: [],
            tags: [],
            tagOptions: [],
            params: [],
            input: {
                kind: '',
                from: '',
                filetypes: []
            },
            inputSelectedPatterns: [],
            outputDirectory: false,
            outputSpecified: false,
            output: {
                from: '',
                to: '',
                include: {
                    patterns: [],
                    names: []
                },
                exclude: {
                    patterns: [],
                    names: []
                }
            },
            includedFile: '',
            excludedFile: '',
            includedPattern: '',
            excludedPattern: '',
            output_include_fields: [
                {
                    key: 'name',
                    label: 'Included File Names'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_include_pattern_fields: [
                {
                    key: 'name',
                    label: 'Included File Patterns'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_exclude_fields: [
                {
                    key: 'name',
                    label: 'Excluded File Names'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            output_exclude_pattern_fields: [
                {
                    key: 'name',
                    label: 'Excluded File Patterns'
                },
                {
                    key: 'actions',
                    label: 'Actions'
                }
            ],
            target: {
                name: ''
            },
            targets: [],
            targetsLoading: false,
            targetFields: [
                {
                    key: 'name',
                    label: ''
                },
                {
                    key: 'description',
                    label: 'Description'
                },
                {
                    key: 'max_cores',
                    label: 'Max Cores'
                },
                {
                    key: 'max_processes',
                    label: 'Max Processes'
                },
                {
                    key: 'max_mem',
                    label: 'Max Memory'
                },
                {
                    key: 'gpu',
                    label: 'GPU'
                }
            ],
            fields: [
                {
                    key: 'name',
                    label: 'Name'
                },
                {
                    key: 'value',
                    label: 'Value'
                }
            ]
        };
    },
    mounted: function() {
        this.loadFlow();
        this.loadTargets();
        this.loadRuns();
    },
    methods: {
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id
                }
            });
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        addTag(tag) {
            this.tags.push(tag);
            this.tagOptions.push(tag);
        },
        validate() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/validate/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flowValidated = response.data.result;
                    if (!this.flowValidated)
                        this.flowValidationErrors = response.data.errors;
                    this.flowLoading = false;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        loadRuns() {
            axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/get_by_user_and_flow/${this.name}/0/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    this.runs = response.data;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        loadFlow() {
            axios
                .get(`/apis/v1/flows/${this.username}/${this.name}/`, {
                    headers: {
                        Authorization: 'Bearer ' + this.githubToken
                    }
                })
                .then(response => {
                    this.flow = response.data;
                    this.validate();

                    // if a local input path is specified, set it
                    if (
                        'input' in response.data.config &&
                        response.data.config.input !== undefined &&
                        response.data.config.input.path !== undefined &&
                        response.data.config.input.kind !== undefined
                    ) {
                        this.input.from =
                            response.data.config.input.path !== null
                                ? response.data.config.input.path
                                : '';
                        this.input.kind = response.data.config.input.kind;
                        this.input.filetypes =
                            response.data.config.input.filetypes !==
                                undefined &&
                            response.data.config.input.filetypes !== null
                                ? response.data.config.input.filetypes
                                : [];
                        if (this.input.filetypes.length > 0)
                            this.inputSelectedPatterns = this.input.filetypes;
                    }

                    // if a local output path is specified, add it to included files
                    if (
                        response.data.config.output !== undefined &&
                        response.data.config.output.path !== undefined
                    ) {
                        this.output.from =
                            response.data.config.output.path !== null
                                ? response.data.config.output.path
                                : '';
                        if (
                            response.data.config.output.include !== undefined &&
                            response.data.config.output.include.names !==
                                undefined
                        )
                            this.output.include.names =
                                response.data.config.output.include.names;
                        if (
                            response.data.config.output.include !== undefined &&
                            response.data.config.output.include.patterns !==
                                undefined
                        )
                            this.output.include.patterns =
                                response.data.config.output.include.patterns;
                        if (
                            response.data.config.output.exclude !== undefined &&
                            response.data.config.output.exclude.names !==
                                undefined
                        )
                            this.output.exclude.names =
                                response.data.config.output.exclude.names;
                        if (
                            response.data.config.output.exclude !== undefined &&
                            response.data.config.output.exclude.patterns !==
                                undefined
                        )
                            this.output.exclude.patterns =
                                response.data.config.output.exclude.patterns;
                    }

                    // if params are specified, set them
                    if ('params' in response.data['config'])
                        this.params = response.data['config']['params'].map(
                            param => {
                                let split = param.split('=');
                                return {
                                    key: split[0],
                                    value: split.length === 2 ? split[1] : ''
                                };
                            }
                        );

                    // if we have pre-configured values for this flow, populate them
                    if (
                        `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}` in
                        this.flowConfigs
                    ) {
                        let flowConfig = this.flowConfigs[
                            `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`
                        ];
                        this.params =
                            flowConfig.params !== undefined
                                ? flowConfig.params
                                : this.params;
                        this.input = flowConfig.input;
                        this.output = flowConfig.output;
                        this.target = flowConfig.target;
                    }
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        inputSelected(node) {
            this.input.from = node.path;
        },
        outputSelected(node) {
            this.output.to = node.path;
        },
        targetSelected(target) {
            this.target = target;
        },
        targetUnsupported(target) {
            return (
                (parseInt(target.max_mem) !== -1 &&
                    parseInt(target.max_mem) <
                        parseInt(this.flow.config.resources.mem)) ||
                parseInt(target.max_cores) <
                    parseInt(this.flow.config.resources.cores) ||
                parseInt(target.max_processes) <
                    parseInt(this.flow.config.resources.processes)
            );
            // TODO walltime
        },
        loadTargets: function() {
            this.targetsLoading = true;
            return axios
                .get('/apis/v1/targets/')
                .then(response => {
                    this.targets = response.data;
                    this.targetsLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        onStart() {
            if (!this.flow.config.resources && this.target.name !== 'Sandbox') {
                alert('This flow can only run in the Sandbox.');
                return;
            }

            // prepare run definition
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
            let target = this.target;
            if (this.flow.config.resources)
                target['resources'] = this.flow.config.resources;
            let config = {
                name: this.flow.config.name,
                image: this.flow.config.image,
                parameters: this.params,
                target: target,
                commands: this.flow.config.commands,
                tags: this.tags
            };
            if ('gpu' in this.flow.config) config['gpu'] = this.flow.config.gpu;
            if ('branch' in this.flow.config)
                config['branch'] = this.flow.config.branch;
            if (this.flow.config.mount !== null)
                config['mount'] = this.flow.config.mount;
            if (this.input !== undefined && this.input.from) {
                config.input = this.input;
                config.input.patterns =
                    this.inputSelectedPatterns.length > 0
                        ? this.inputSelectedPatterns
                        : this.input.filetypes;
            }
            if (this.output !== undefined) {
                config.output = this.output;
                if (!this.outputDirectory) delete config.output['to'];
            }

            // save config
            this.$store.dispatch('setFlowConfig', {
                name: this.flowKey,
                config: config
            });

            // submit run
            axios({
                method: 'post',
                url: `/apis/v1/runs/`,
                data: {
                    repo: this.flow.repo,
                    config: config
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    router.push({
                        name: 'run',
                        params: {
                            username: this.profile.djangoProfile.username,
                            id: response.data.id
                        }
                    });
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
    },
    computed: {
        ...mapGetters(['profile', 'flowConfigs', 'loggedIn', 'darkMode']),
        flowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        },
        inputFiletypeSelected: function() {
            return this.inputSelectedPatterns.some(pattern => pattern !== '');
        },
        inputReady: function() {
            if (this.flow !== null && this.flow.config.input !== undefined)
                return (
                    this.flow.config.input.path !== undefined &&
                    this.input.from !== '' &&
                    this.input.kind !== '' &&
                    this.inputFiletypeSelected
                );
            return true;
        },
        outputReady: function() {
            if (
                this.outputDirectory &&
                this.flow &&
                this.flow.config &&
                this.flow.config.input !== undefined &&
                this.flow.config.output.path !== undefined
            )
                return this.output.to !== '';
            return true;
        },
        flowReady: function() {
            return (
                !this.flowLoading &&
                this.flowValidated &&
                this.inputReady &&
                this.outputReady &&
                this.target.name !== ''
            );
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.workflow-icon
    width: 200px
    height: 200px
    margin: 0 auto
    margin-bottom: -10px
    background-color: white
    padding: 24px

    img
        margin-top: 20px
        max-width: 140px
        max-height: 190px
</style>
