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
            <b-row no-gutters class="mt-3">
                <b-col v-if="showStatusAlert">
                    <b-alert
                        :show="showStatusAlert"
                        :variant="
                            statusAlertMessage.startsWith('Failed')
                                ? 'danger'
                                : 'success'
                        "
                        dismissible
                        @dismissed="showStatusAlert = false"
                    >
                        {{ statusAlertMessage }}
                    </b-alert>
                </b-col>
            </b-row>
            <b-row align-h="center" v-if="workflowLoading">
                <b-spinner
                    type="grow"
                    label="Loading..."
                    variant="secondary"
                ></b-spinner>
            </b-row>
            <b-row v-else>
                <b-col>
                    <b-row>
                        <b-col>
                            <b-card
                                :bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                :header-bg-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                border-variant="default"
                                :header-border-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                :text-variant="
                                    profile.darkMode ? 'white' : 'dark'
                                "
                                class="overflow-hidden"
                            >
                                <b-alert
                                    id="flowInvalid"
                                    :show="
                                        !this.workflowLoading &&
                                            !this.workflowValid
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
                                    {{
                                        this.workflowValidationErrors.join(', ')
                                    }}
                                </b-alert>
                                <workflowdetail
                                    :show-public="true"
                                    :workflow="getWorkflow"
                                ></workflowdetail>
                            </b-card>
                        </b-col>
                    </b-row>
                    <br />
                    <b-row
                        ><b-col md="auto"
                            ><b-button
                                :disabled="workflowLoading"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                v-b-tooltip.hover
                                title="Refresh Workflow"
                                @click="refreshWorkflow"
                            >
                                <i class="fas fa-redo"></i>
                                Refresh
                                <b-spinner
                                    small
                                    v-if="workflowLoading"
                                    label="Refreshing..."
                                    :variant="
                                        profile.darkMode ? 'light' : 'dark'
                                    "
                                    class="ml-2 mb-1"
                                ></b-spinner> </b-button></b-col
                        ><b-col md="auto" class="mr-0" align-self="end">
                            <b-input-group>
                                <template #prepend>
                                    <b-input-group-text
                                        >Run
                                        {{
                                            getWorkflow.config.name
                                        }}</b-input-group-text
                                    >
                                </template>
                                <template #append>
                                    <b-dropdown
                                        variant="secondary"
                                        :text="submitType"
                                        v-model="submitType"
                                        block
                                    >
                                        <template #button-content>
                                            {{ submitType }}
                                            <i
                                                class="fas fa-caret-down fa-fw"
                                            ></i>
                                        </template>
                                        <b-dropdown-item
                                            @click="submitType = 'Now'"
                                            >Now</b-dropdown-item
                                        >
                                        <!--<b-dropdown-item
                                            @click="submitType = 'After'"
                                            >After</b-dropdown-item
                                        >-->
                                        <b-dropdown-item
                                            @click="submitType = 'Every'"
                                            >Every</b-dropdown-item
                                        >
                                    </b-dropdown>
                                </template>
                            </b-input-group>
                        </b-col>
                        <b-col
                            md="auto"
                            v-if="
                                submitType === 'After' || submitType === 'Every'
                            "
                            ><b-input-group>
                                <b-form-spinbutton
                                    v-model="delayValue"
                                    min="1"
                                    max="100"
                                ></b-form-spinbutton
                                ><template #append>
                                    <b-dropdown
                                        variant="secondary"
                                        :text="submitType"
                                        v-model="submitType"
                                        block
                                    >
                                        <template #button-content>
                                            {{ delayUnits }}
                                            <i
                                                class="fas fa-caret-down fa-fw"
                                            ></i>
                                        </template>
                                        <b-dropdown-item
                                            @click="delayUnits = 'Seconds'"
                                            >Seconds</b-dropdown-item
                                        >
                                        <b-dropdown-item
                                            @click="delayUnits = 'Minutes'"
                                            >Minutes</b-dropdown-item
                                        >
                                        <b-dropdown-item
                                            @click="delayUnits = 'Hours'"
                                            >Hours</b-dropdown-item
                                        >
                                        <b-dropdown-item
                                            @click="delayUnits = 'Days'"
                                            >Days</b-dropdown-item
                                        >
                                    </b-dropdown>
                                </template></b-input-group
                            ></b-col
                        >
                        <b-col
                            ><b-button
                                :disabled="!flowReady || submitted"
                                @click="onTryStart"
                                variant="success"
                                block
                            >
                                {{
                                    submitType === 'Now'
                                        ? `Start ${getWorkflow.config.name}`
                                        : `Schedule ${getWorkflow.config.name} to run ${scheduledTime}`
                                }}<b-spinner
                                    small
                                    v-if="submitted"
                                    label="Loading..."
                                    variant="dark"
                                    class="ml-2 mb-1"
                                ></b-spinner> </b-button></b-col
                    ></b-row>
                    <br />
                    <!--<b-row v-if="submitType === 'Every'"
                        ><b-col
                            ><b-card
                                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                                border-variant="default"
                                :header-border-variant="
                                    profile.darkMode ? 'dark' : 'white'
                                "
                                :text-variant="profile.darkMode ? 'white' : 'dark'"
                                ><b-form-group
                                    :class="
                                        profile.darkMode ? 'theme-dark' : 'theme-light'
                                    "
                                    id="input-group-4"
                                    label-for="input-4"
                                    description="Configure when this flow should run."
                                >
                                    <VueCronEditorBuefy
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark'
                                                : 'theme-light'
                                        "
                                        v-model="crontime"
                                    ></VueCronEditorBuefy>
                                </b-form-group> </b-card
                            ><br /></b-col
                    ></b-row>-->
                    <b-row>
                        <b-col>
                            <b-card-group deck columns>
                                <b-card
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    style="min-width: 40rem"
                                    class="mb-4"
                                >
                                    <b-row>
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
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
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Attach tags to this run.
                                            </b>
                                        </b-col>
                                    </b-row>
                                    <b-row class="mt-1">
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
                                        workflow !== null &&
                                        getWorkflow.config.params !== undefined
                                            ? getWorkflow.config.params
                                                  .length !== 0
                                            : false
                                    "
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    style="min-width: 40rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="
                                                        params &&
                                                            params.every(
                                                                p =>
                                                                    p.name !==
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
                                            ><b
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                Configure parameters for this
                                                run.
                                            </b>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
                                            <b-row
                                                class="mt-1"
                                                v-for="param in params"
                                                v-bind:key="param.name"
                                            >
                                                <b-col>{{
                                                    param.name.toLowerCase()
                                                }}</b-col
                                                ><b-col>
                                                    <b-form-input
                                                        v-if="
                                                            param.type ===
                                                                'string'
                                                        "
                                                        size="sm"
                                                        v-model="param.value"
                                                        :placeholder="
                                                            param.value === ''
                                                                ? 'Enter a value for \'' +
                                                                  param.name.toLowerCase() +
                                                                  '\''
                                                                : param.value
                                                        "
                                                    ></b-form-input>
                                                    <b-form-select
                                                        v-if="
                                                            param.type ===
                                                                'select'
                                                        "
                                                        size="sm"
                                                        v-model="param.value"
                                                        :options="param.options"
                                                    ></b-form-select>
                                                    <b-form-checkbox-group
                                                        v-if="
                                                            param.type ===
                                                                'multiselect'
                                                        "
                                                        size="sm"
                                                        v-model="param.value"
                                                        :options="param.options"
                                                    ></b-form-checkbox-group>
                                                    <b-form-spinbutton
                                                        v-if="
                                                            param.type ===
                                                                'number'
                                                        "
                                                        size="sm"
                                                        v-model="param.value"
                                                        :min="param.min"
                                                        :max="param.max"
                                                        :step="param.step"
                                                    ></b-form-spinbutton>
                                                    <b-form-checkbox
                                                        v-if="
                                                            param.type ===
                                                                'boolean'
                                                        "
                                                        size="sm"
                                                        v-model="param.value"
                                                        switch
                                                    >
                                                        <b>
                                                            {{ param.value }}</b
                                                        >
                                                    </b-form-checkbox>
                                                </b-col></b-row
                                            >
                                        </b-col></b-row
                                    >
                                </b-card>
                                <b-card
                                    v-if="
                                        workflow !== null &&
                                            getWorkflow.config.input !==
                                                undefined &&
                                            getWorkflow.config.input.path !==
                                                undefined
                                    "
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    style="min-width: 50rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
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
                                        :default-path="
                                            getWorkflow.config.input.path
                                        "
                                        :user="user"
                                        :kind="input.kind"
                                        v-on:inputSelected="inputSelected"
                                    ></runinput>
                                    <b-row v-if="input.filetypes.length > 0">
                                        <b-col>
                                            <b
                                                :class="
                                                    profile.darkMode
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
                                <!--<b-card
                                    v-if="
                                        flow &&
                                            flow.config &&
                                            flow.config.input !== undefined &&
                                            flow.config.output.path !==
                                                undefined
                                    "
                                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                                    style="min-width: 50rem"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
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
                                                            profile.darkMode
                                                    "
                                                    class="fas fa-upload fa-fw text-white"
                                                ></i>
                                                <i
                                                    v-else-if="
                                                        !outputDirectory &&
                                                            !profile.darkMode
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
                                </b-card>-->
                                <b-card
                                    :bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :header-bg-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    border-variant="default"
                                    :header-border-variant="
                                        profile.darkMode ? 'dark' : 'white'
                                    "
                                    :text-variant="
                                        profile.darkMode ? 'white' : 'dark'
                                    "
                                    style="min-width: 40rem"
                                    class="mb-4"
                                >
                                    <b-row align-v="center">
                                        <b-col>
                                            <h4
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                            >
                                                <i
                                                    v-if="
                                                        selectedCluster.name !==
                                                            ''
                                                    "
                                                    class="fas fa-server fa-fw text-warning"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="fas fa-server fa-fw"
                                                ></i>
                                                Cluster
                                            </h4>
                                        </b-col>
                                    </b-row>
                                    <div>
                                        <b
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            Select a cluster to submit this run
                                            to.
                                        </b>
                                        <b-tabs
                                            class="mt-2"
                                            vertical
                                            pills
                                            nav-class="bg-transparent"
                                            active-nav-item-class="bg-secondary text-dark"
                                        >
                                            <b-tab
                                                title="Your clusters"
                                                :title-link-class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark m-0 p-3'
                                                        : 'theme-light m-0 p-3'
                                                "
                                            >
                                                <b-row
                                                    class="text-right"
                                                    v-for="cluster in clusters"
                                                    v-bind:key="cluster.name"
                                                >
                                                    <b-col md="auto"
                                                        ><b-button
                                                            size="md"
                                                            class="text-left pt-2"
                                                            @click="
                                                                clusterSelected(
                                                                    cluster
                                                                )
                                                            "
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'dark'
                                                                    : 'white'
                                                            "
                                                            :disabled="
                                                                clusterUnsupported(
                                                                    cluster
                                                                ) ||
                                                                    cluster.disabled
                                                            "
                                                            >{{
                                                                cluster.name
                                                            }}</b-button
                                                        ></b-col
                                                    >
                                                    <b-col align-self="end">
                                                        <small
                                                            >{{
                                                                cluster.max_cores
                                                            }}
                                                            cores,
                                                            {{
                                                                cluster.max_processes
                                                            }}
                                                            processes, </small
                                                        ><span
                                                            v-if="
                                                                parseInt(
                                                                    cluster.max_mem
                                                                ) >=
                                                                    parseInt(
                                                                        getWorkflow
                                                                            .config
                                                                            .resources
                                                                            .mem
                                                                    ) &&
                                                                    parseInt(
                                                                        cluster.max_mem
                                                                    ) > 0
                                                            "
                                                            >{{
                                                                cluster.max_mem
                                                            }}
                                                            GB memory</span
                                                        >
                                                        <span
                                                            v-else-if="
                                                                parseInt(
                                                                    cluster.max_mem
                                                                ) > 0
                                                            "
                                                            class="text-danger"
                                                            >{{
                                                                cluster.max_mem
                                                            }}
                                                            GB memory</span
                                                        >
                                                        <span
                                                            v-else-if="
                                                                parseInt(
                                                                    cluster.max_mem
                                                                ) === -1
                                                            "
                                                            >virtual
                                                            memory</span
                                                        ><span
                                                            v-if="cluster.gpu"
                                                        >
                                                            , GPU
                                                        </span>
                                                        <span v-else
                                                            >, No GPU
                                                        </span></b-col
                                                    >
                                                </b-row>
                                                <b-row
                                                    align-h="center"
                                                    class="text-center"
                                                    v-if="
                                                        !publicClustersLoading &&
                                                            clusters.length ===
                                                                0
                                                    "
                                                >
                                                    <b-col>
                                                        None to show.
                                                    </b-col>
                                                </b-row>
                                            </b-tab>
                                            <b-tab
                                                title="Public clusters"
                                                :title-link-class="
                                                    profile.darkMode
                                                        ? 'text-white'
                                                        : 'text-dark'
                                                "
                                                :class="
                                                    profile.darkMode
                                                        ? 'theme-dark m-0 p-3'
                                                        : 'theme-light m-0 p-3'
                                                "
                                            >
                                                <b-row
                                                    class="text-right"
                                                    v-for="tgt in publicClusters"
                                                    v-bind:key="tgt.name"
                                                >
                                                    <b-col md="auto"
                                                        ><b-button
                                                            size="md"
                                                            class="text-left pt-2"
                                                            @click="
                                                                clusterSelected(
                                                                    tgt
                                                                )
                                                            "
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'dark'
                                                                    : 'white'
                                                            "
                                                            :disabled="
                                                                clusterUnsupported(
                                                                    tgt
                                                                ) ||
                                                                    tgt.disabled
                                                            "
                                                            >{{
                                                                tgt.name
                                                            }}</b-button
                                                        ></b-col
                                                    >
                                                    <b-col align-self="end">
                                                        <small
                                                            >{{ tgt.max_cores }}
                                                            cores,
                                                            {{
                                                                tgt.max_processes
                                                            }}
                                                            processes, </small
                                                        ><span
                                                            v-if="
                                                                parseInt(
                                                                    tgt.max_mem
                                                                ) >=
                                                                    parseInt(
                                                                        getWorkflow
                                                                            .config
                                                                            .resources
                                                                            .mem
                                                                    ) &&
                                                                    parseInt(
                                                                        tgt.max_mem
                                                                    ) > 0
                                                            "
                                                            >{{
                                                                tgt.max_mem
                                                            }}
                                                            GB memory</span
                                                        >
                                                        <span
                                                            v-else-if="
                                                                parseInt(
                                                                    tgt.max_mem
                                                                ) > 0
                                                            "
                                                            class="text-danger"
                                                            >{{
                                                                tgt.max_mem
                                                            }}
                                                            GB memory</span
                                                        >
                                                        <span
                                                            v-else-if="
                                                                parseInt(
                                                                    tgt.max_mem
                                                                ) === -1
                                                            "
                                                            >virtual
                                                            memory</span
                                                        ><span v-if="tgt.gpu">
                                                            , GPU
                                                        </span>
                                                        <span v-else
                                                            >, No GPU
                                                        </span></b-col
                                                    >
                                                </b-row>
                                                <b-row
                                                    align-h="center"
                                                    class="text-center"
                                                    v-if="
                                                        !clustersLoading &&
                                                            publicClusters.length ===
                                                                0
                                                    "
                                                >
                                                    <b-col>
                                                        None to show.
                                                    </b-col>
                                                </b-row>
                                            </b-tab>
                                        </b-tabs>
                                        <b-row
                                            align-h="center"
                                            v-if="clustersLoading"
                                        >
                                            <b-spinner
                                                type="grow"
                                                label="Loading..."
                                                variant="secondary"
                                            ></b-spinner>
                                        </b-row>
                                        <b-alert
                                            v-else
                                            class="mt-1"
                                            :variant="
                                                selectedCluster.name !== ''
                                                    ? 'success'
                                                    : 'danger'
                                            "
                                            :show="true"
                                            >Selected:
                                            {{
                                                selectedCluster.name !== ''
                                                    ? selectedCluster.name
                                                    : 'None'
                                            }}
                                            <i
                                                v-if="
                                                    selectedCluster.name !== ''
                                                "
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
                    <!--<b-row
                        ><b-col align-self="end"
                            ><h5 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                                Delayed Runs
                            </h5></b-col
                        ></b-row
                    >
                    <b-list-group class="text-left m-0 p-0">
                        <b-row v-if="delayedRuns.length === 0"
                            ><b-col
                                ><small
                                    >You haven't scheduled any delayed
                                    {{ flow.config.name }} runs.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="task in delayedRuns"
                            v-bind:key="task.id"
                            :class="
                                profile.darkMode
                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                            "
                        >
                            <b-row class="pt-1">
                                <b-col align-self="end"
                                    >{{
                                        `After ${task.interval.every} ${task.interval.period} on ${task.cluster.name}`
                                    }}<br /><b-row
                                        ><b-col
                                            md="auto"
                                            align-self="end"
                                            class="mb-1"
                                            ></b-col
                                        >
                                    </b-row></b-col
                                >
                                <b-col
                                    md="auto"
                                    align-self="start"
                                    class="mb-1"
                                    ><b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="deleteDelayed(task)"
                                        ><i class="fas fa-trash fa-fw"></i>
                                        Cancel</b-button
                                    ></b-col
                                >
                            </b-row>
                        </b-list-group-item>
                    </b-list-group>
                    <hr />-->
                    <b-row
                        ><b-col align-self="end"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                Periodic Runs
                            </h5></b-col
                        ></b-row
                    >
                    <b-list-group class="text-left m-0 p-0">
                        <b-row v-if="repeatingRuns.length === 0"
                            ><b-col
                                ><small
                                    >You haven't scheduled any repeating
                                    {{ getWorkflow.config.name }} runs.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="task in repeatingRuns"
                            v-bind:key="task.id"
                            :class="
                                profile.darkMode
                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                            "
                        >
                            <b-row class="pt-1">
                                <b-col
                                    >{{
                                        `Every ${task.interval.every} ${task.interval.period} on ${task.cluster.name}`
                                    }}<br /><b-row
                                        ><b-col
                                            md="auto"
                                            align-self="end"
                                            class="mb-1"
                                            ><!--<small v-if="task.enabled"
                                    >Next running {{ cronTime(task)
                                    }}<br /></small
                                >--><small v-if="task.last_run !== null"
                                                >Last ran
                                                {{
                                                    prettify(task.last_run)
                                                }}</small
                                            ><small v-else
                                                >Task has not run yet</small
                                            ></b-col
                                        >
                                    </b-row></b-col
                                >
                                <b-col md="auto" align-self="start"
                                    ><!--<b-form-checkbox
                                        class="text-right"
                                        v-model="task.enabled"
                                        @change="toggleRepeating(task)"
                                        switch
                                        size="md"
                                    >
                                    </b-form-checkbox
                                    >--><b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="deleteRepeating(task)"
                                        ><i class="fas fa-trash fa-fw"></i>
                                        Remove</b-button
                                    ></b-col
                                >
                            </b-row>
                        </b-list-group-item>
                    </b-list-group>
                    <hr />
                    <b-row
                        ><b-col align-self="end"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                Recent Runs
                            </h5></b-col
                        ><!--<b-col class="mb-1" align-self="start" md="auto"
                            ><b-button
                                :variant="profile.darkMode ? 'outline-light' : 'white'"
                                size="sm"
                                v-b-tooltip.hover
                                title="Create Periodic Task"
                                :disabled="cluster.role !== 'own'"
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
                                    {{ getWorkflow.config.name }} yet.</small
                                ></b-col
                            ></b-row
                        >
                        <b-list-group-item
                            variant="default"
                            style="box-shadow: -2px 2px 2px #adb5bd"
                            v-for="run in runs"
                            v-bind:key="run.id"
                            :class="
                                profile.darkMode
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
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
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
                                run.cluster
                            }}</b-badge
                            ><small
                                v-if="run.job_status === 'Scheduled'"
                            ></small
                            ><small v-else> {{ prettify(run.updated) }}</small>
                            <!--<br />
                                    <small class="mr-1"
                                        ><a
                                            :class="
                                                profile.darkMode
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
            <b-modal
                id="authenticate"
                :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
                centered
                close
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                :title="'Authenticate with ' + this.selectedCluster.name"
                @ok="onStart"
            >
                <b-form-input
                    v-model="authenticationUsername"
                    type="text"
                    placeholder="Your username"
                    required
                ></b-form-input>
                <b-form-input
                    v-model="authenticationPassword"
                    type="password"
                    placeholder="Your password"
                    required
                ></b-form-input>
            </b-modal>
        </b-container>
    </div>
</template>

<script>
import workflowdetail from '../components/workflow-detail';
import runinput from '../components/run-input';
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '../router';
import Multiselect from 'vue-multiselect';
import moment from 'moment';
import cronstrue from 'cronstrue';

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

export default {
    name: 'workflow',
    components: {
        Multiselect,
        workflowdetail,
        runinput
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
            submitted: false,
            authenticationUsername: '',
            authenticationPassword: '',
            currentClusterTab: 0,
            showStatusAlert: false,
            statusAlertMessage: '',
            submitType: 'Now',
            crontime: '* */5 * * *',
            delayValue: 10,
            delayUnits: 'Minutes',
            runs: [],
            delayedRuns: [],
            repeatingRuns: [],
            workflowLoading: true,
            workflowValid: false,
            workflowValidationErrors: [],
            tags: [],
            tagOptions: [],
            params: [],
            input: {
                kind: '',
                from: '',
                filetypes: []
            },
            inputSelectedPatterns: [],
            outputCollection: false,
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
            selectedCluster: {
                name: ''
            },
            clusters: [],
            publicClusters: [],
            clustersLoading: false,
            clusterFields: [
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
    async mounted() {
        await Promise.all([
            this.$store.dispatch('users/loadAll'),
            this.$store.dispatch('workflows/refresh', {
                owner: this.$router.currentRoute.params.username,
                name: this.$router.currentRoute.params.name
            }),
            this.validate(),
            this.loadClusters(),
            this.loadPublicClusters(),
            this.loadRuns(),
            this.loadDelayedRuns(),
            this.loadRepeatingRuns()
        ]);
        this.populateComponents();
    },
    methods: {
        async refreshWorkflow() {
          this.workflowLoading = true;
            await this.$store.dispatch('workflows/refresh', {
                owner: this.$router.currentRoute.params.username,
                name: this.$router.currentRoute.params.name
            });
            this.workflowLoading = false;
        },
        deleteDelayed(task) {
            return axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/remove_delayed/${this.name}/?name=${task.name}`
                )
                .then(() => {
                    this.loadDelayedRuns();
                    this.statusAlertMessage = `Deleted delayed run`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.statusAlertMessage = `Failed to delete delayed run`;
                    this.showStatusAlert = true;
                    throw error;
                });
        },
        deleteRepeating(task) {
            return axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/remove_repeating/${this.name}/?name=${task.name}`
                )
                .then(() => {
                    this.loadRepeatingRuns();
                    this.statusAlertMessage = `Deleted periodic run`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.statusAlertMessage = `Failed to delete periodic run`;
                    this.showStatusAlert = true;
                    throw error;
                });
        },
        toggleRepeating: function(task) {
            axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/toggle_repeating/${this.name}/?name=${task.name}`
                )
                .then(response => {
                    this.statusAlertMessage = `${
                        response.data.enabled ? 'Enabled' : 'Disabled'
                    } periodic run (every ${
                        response.data.interval.every
                    } ${response.data.interval.period.toLowerCase()} on ${
                        response.data.cluster.name
                    })`;
                    this.showStatusAlert = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.statusAlertMessage = `Failed to disable repeating run ${task.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    }
                });
        },
        parseCronTime(time) {
            let cron = cronstrue.toString(time);
            return cron.charAt(0).toLowerCase() + cron.slice(1);
        },
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
        async validate() {
            await axios
                .get(
                    `/apis/v1/workflows/${this.username}/${this.name}/validate/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    this.workflowValid = response.data.result;
                    if (!this.workflowValid)
                        this.workflowValidationErrors = response.data.errors;
                    this.workflowLoading = false;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        async loadRuns() {
            await axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/get_by_user_and_workflow/${this.name}/0/`,
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
        async loadDelayedRuns() {
            await axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/get_delayed_by_user_and_workflow/${this.name}/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    this.delayedRuns = response.data.filter(
                        t => t.last_run === null
                    );
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        async loadRepeatingRuns() {
            await axios
                .get(
                    `/apis/v1/runs/${this.profile.djangoProfile.username}/get_repeating_by_user_and_workflow/${this.name}/`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + this.githubToken
                        }
                    }
                )
                .then(response => {
                    this.repeatingRuns = response.data;
                })
                .catch(error => {
                    if (error.status_code === 401) {
                        this.login = true;
                    } else {
                        throw error;
                    }
                });
        },
        mapParam(param) {
            if (param.type === 'string')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : ''
                };
            else if (param.type === 'select')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : null,
                    options: param.options
                };
            else if (param.type === 'number')
                return {
                    name: param.name,
                    type: param.type,
                    value: param.default !== undefined ? param.default : 0,
                    min: param.min,
                    max: param.max,
                    step: param.step
                };
            else if (param.type === 'boolean')
                return {
                    name: param.name,
                    type: param.type,
                    value:
                        param.default !== undefined
                            ? param.default.toString().toLowerCase() === 'false'
                            : false
                };
        },
        populateComponents() {
            // if a local input path is specified, set it
            if (
                'input' in this.getWorkflow.config &&
                this.getWorkflow.config.input !== undefined &&
                this.getWorkflow.config.input.path !== undefined &&
                this.getWorkflow.config.input.kind !== undefined
            ) {
                this.input.from =
                    this.getWorkflow.config.input.path !== null
                        ? this.getWorkflow.config.input.path
                        : '';
                this.input.kind = this.getWorkflow.config.input.kind;
                this.input.filetypes =
                    this.getWorkflow.config.input.filetypes !== undefined &&
                    this.getWorkflow.config.input.filetypes !== null
                        ? this.getWorkflow.config.input.filetypes
                        : [];
                if (this.input.filetypes.length > 0)
                    this.inputSelectedPatterns = this.input.filetypes;
            }

            // if a local output path is specified, add it to included files
            if (
                this.getWorkflow.config.output !== undefined &&
                this.getWorkflow.config.output.path !== undefined
            ) {
                this.output.from =
                    this.getWorkflow.config.output.path !== null
                        ? this.getWorkflow.config.output.path
                        : '';
                if (
                    this.getWorkflow.config.output.include !== undefined &&
                    this.getWorkflow.config.output.include.names !== undefined
                )
                    this.output.include.names = this.getWorkflow.config.output.include.names;
                if (
                    this.getWorkflow.config.output.include !== undefined &&
                    this.getWorkflow.config.output.include.patterns !==
                        undefined
                )
                    this.output.include.patterns = this.getWorkflow.config.output.include.patterns;
                if (
                    this.getWorkflow.config.output.exclude !== undefined &&
                    this.getWorkflow.config.output.exclude.names !== undefined
                )
                    this.output.exclude.names = this.getWorkflow.config.output.exclude.names;
                if (
                    this.getWorkflow.config.output.exclude !== undefined &&
                    this.getWorkflow.config.output.exclude.patterns !==
                        undefined
                )
                    this.output.exclude.patterns = this.getWorkflow.config.output.exclude.patterns;
            }

            // if params are specified, set them
            if ('params' in this.getWorkflow['config'])
                this.params = this.getWorkflow['config']['params'].map(param =>
                    this.mapParam(param)
                );

            // if we have pre-configured values for this flow, populate them
            if (
                `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}` in
                this.workflowsRecentlyRun
            ) {
                let flowConfig = this.workflowsRecentlyRun[
                    `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`
                ];
                this.params =
                    flowConfig.params !== undefined
                        ? flowConfig.params
                        : this.params;
                this.input = flowConfig.input;
                this.output = flowConfig.output;
                this.selectedCluster = flowConfig.cluster;
            }
        },
        inputSelected(node) {
            this.input.from = node.path;
        },
        outputSelected(node) {
            this.output.to = node.path;
        },
        clusterSelected(cluster) {
            this.selectedCluster = cluster;
        },
        clusterUnsupported(cluster) {
            return (
                (parseInt(cluster.max_mem) !== -1 &&
                    parseInt(cluster.max_mem) <
                        parseInt(this.getWorkflow.config.resources.mem)) ||
                parseInt(cluster.max_cores) <
                    parseInt(this.getWorkflow.config.resources.cores) ||
                parseInt(cluster.max_processes) <
                    parseInt(this.getWorkflow.config.resources.processes)
            );
            // TODO walltime
        },
        async loadClusters() {
            this.clustersLoading = true;
            return await axios
                .get(`/apis/v1/clusters/get_by_username/`)
                .then(response => {
                    this.clusters = response.data.clusters;
                    this.clustersLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadPublicClusters() {
            this.publicClustersLoading = true;
            return await axios
                .get(`/apis/v1/clusters/get_all/`)
                .then(response => {
                    this.publicClusters = response.data.clusters;
                    this.publicClustersLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        onTryStart() {
            if (this.mustAuthenticate) this.showAuthenticateModal();
            else this.onStart();
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        async onStart() {
            if (
                !this.getWorkflow.config.resources &&
                this.selectedCluster.name !== 'Sandbox'
            ) {
                alert('This flow can only run in the Sandbox.');
                return;
            }

            // prepare run definition
            this.params['config'] = {};
            this.params['config']['api_url'] = '/apis/v1/runs/status/';
            let cluster = this.selectedCluster;
            if (this.getWorkflow.config.resources)
                cluster['resources'] = this.getWorkflow.config.resources;
            let config = {
                name: this.getWorkflow.config.name,
                image: this.getWorkflow.config.image,
                parameters: this.params,
                cluster: cluster,
                commands: this.getWorkflow.config.commands,
                tags: this.tags
            };
            if ('gpu' in this.getWorkflow.config)
                config['gpu'] = this.getWorkflow.config.gpu;
            if ('branch' in this.getWorkflow.config)
                config['branch'] = this.getWorkflow.config.branch;
            if (this.getWorkflow.config.mount !== null)
                config['mount'] = this.getWorkflow.config.mount;
            if (this.input !== undefined && this.input.from) {
                config.input = this.input;
                config.input.patterns =
                    this.inputSelectedPatterns.length > 0
                        ? this.inputSelectedPatterns
                        : this.input.filetypes;
            }
            if (this.output !== undefined) {
                config.output = this.output;
                if (!this.outputCollection) delete config.output['to'];
            }

            // save config
            this.$store.dispatch('workflows/setRecentlyRun', {
                name: this.workflowKey,
                config: config
            });

            let data = {
                repo: this.getWorkflow.repo,
                config: config,
                type: this.submitType
            };
            if (this.mustAuthenticate)
                data['auth'] = {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                };

            this.submitted = true;
            if (this.submitType === 'Now')
                // submit run immediately
                await axios({
                    method: 'post',
                    url: `/apis/v1/runs/`,
                    data: data,
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
            else if (this.submitType === 'After')
                // schedule run after delay
                await axios({
                    method: 'post',
                    url: `/apis/v1/runs/`,
                    data: {
                        repo: this.getWorkflow.repo,
                        config: config,
                        type: this.submitType,
                        delayUnits: this.delayUnits,
                        delayValue: this.delayValue
                    },
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => {
                        this.statusAlertMessage =
                            response.status === 200 && response.data.created
                                ? `Scheduled run ${this.$router.currentRoute.params.name} on ${config.cluster.name}`
                                : `Failed to schedule run ${this.$router.currentRoute.params.name} on ${config.cluster.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.statusAlertMessage = `Failed to schedule run ${this.createTaskForm.name} on ${this.selectedCluster.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    });
            else if (this.submitType === 'Every')
                // schedule run periodically
                await axios({
                    method: 'post',
                    url: `/apis/v1/runs/`,
                    data: {
                        repo: this.getWorkflow.repo,
                        config: config,
                        type: this.submitType,
                        delayUnits: this.delayUnits,
                        delayValue: this.delayValue
                    },
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => {
                        this.loadRepeatingRuns();
                        this.statusAlertMessage =
                            response.status === 200 && response.data.created
                                ? `Scheduled repeating run ${this.$router.currentRoute.params.name} on ${config.cluster.name}`
                                : `Failed to schedule repeating run ${this.$router.currentRoute.params.name} on ${config.cluster.name}`;
                        this.showStatusAlert = true;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.statusAlertMessage = `Failed to schedule run ${this.createTaskForm.name} on ${this.selectedCluster.name}`;
                        this.showStatusAlert = true;
                        throw error;
                    });
        }
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['workflow', 'workflowsLoading', 'workflowsRecentlyRun']),
        getWorkflow() {
            return this.workflow(
                this.$router.currentRoute.params.username,
                this.$router.currentRoute.params.name
            );
        },
        mustAuthenticate() {
            return !this.selectedCluster.policies.some(
                p =>
                    p.user === this.profile.djangoProfile.username &&
                    (p.role.toLowerCase() === 'use' ||
                        p.role.toLowerCase() === 'own')
            );
        },
        scheduledTime: function() {
            return `${this.submitType === 'After' ? 'in' : 'every'} ${
                this.delayValue
            } ${this.delayUnits.toLowerCase()}`;
            // else return `${this.parseCronTime(this.crontime)}`;  TODO allow direct cron editing
        },
        workflowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        },
        inputFiletypeSelected: function() {
            return this.inputSelectedPatterns.some(pattern => pattern !== '');
        },
        paramsReady: function() {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.params !== undefined &&
                this.getWorkflow.config.params.length !== 0
            )
                return this.params.every(
                    param =>
                        param !== undefined &&
                        param.value !== undefined &&
                        param.value !== ''
                );
            else return true;
        },
        inputReady: function() {
            if (
                this.getWorkflow !== null &&
                this.getWorkflow.config.input !== undefined
            )
                return (
                    this.getWorkflow.config.input.path !== undefined &&
                    this.input.from !== '' &&
                    this.input.kind !== '' &&
                    this.inputFiletypeSelected
                );
            return true;
        },
        outputReady: function() {
            if (
                this.outputCollection &&
                this.getWorkflow &&
                this.getWorkflow.config &&
                this.getWorkflow.config.input !== undefined &&
                this.getWorkflow.config.output.path !== undefined
            )
                return this.output.to !== '';
            return true;
        },
        flowReady: function() {
            return (
                !this.workflowLoading &&
                this.workflowValid &&
                this.paramsReady &&
                this.inputReady &&
                this.outputReady &&
                this.selectedCluster.name !== ''
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
