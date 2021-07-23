<template>
    <div>
        <b-container class="vl" fluid>
            <b-row
                no-gutters
                v-if="
                    getAgent.role !== 'admin' &&
                        getAgent.role !== 'guest' &&
                        !getAgent.public
                "
                ><b-col class="text-center"
                    ><p
                        :class="
                            profile.darkMode
                                ? 'text-center text-white'
                                : 'text-center text-dark'
                        "
                    >
                        <i class="fas fa-exclamation-circle fa-3x fa-fw"></i>
                        <br />
                        <br />
                        You do not have access to this agent.
                        <br />
                        <!--<b-button
                            v-if="!accessRequested"
                            class="ml-0"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            :title="'Request guest access for ' + getAgent.name"
                            @click="requestAccess"
                        >
                            <i class="fas fa-key fa-fw"></i>
                            Request Guest Access
                        </b-button>
                        <b-button
                            v-else
                            class="ml-0"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="sm"
                            v-b-tooltip.hover
                            :disabled="true"
                        >
                            <i class="fas fa-key fa-fw"></i>
                            You requested guest access
                            {{ prettify(accessRequest.created) }}. Your request
                            is pending.
                        </b-button>-->
                    </p></b-col
                ></b-row
            >
            <div v-else>
                <b-row no-gutters class="mt-3">
                    <b-col v-if="alertEnabled">
                        <b-alert
                            :show="alertEnabled"
                            :variant="
                                alertMessage.startsWith('Failed')
                                    ? 'danger'
                                    : 'success'
                            "
                            dismissible
                            @dismissed="alertEnabled = false"
                        >
                            {{ alertMessage }}
                        </b-alert>
                    </b-col>
                </b-row>
                <b-row v-if="agentLoading">
                    <b-col
                        ><b-spinner
                            small
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><span
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            >Loading agent...</span
                        ></b-col
                    >
                </b-row>
                <b-row v-else>
                    <b-col
                        ><b-card
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="default"
                            :header-border-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                        >
                            <div
                                :class="
                                    profile.darkMode
                                        ? 'theme-dark'
                                        : 'theme-light'
                                "
                            >
                                <b-img
                                    v-if="getAgent.logo"
                                    rounded
                                    class="card-img-right overflow-hidden"
                                    style="max-height: 5rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                    right
                                    :src="getAgent.logo"
                                ></b-img>
                                <b-row no-gutters>
                                    <b-col>
                                        <b-row>
                                            <b-col>
                                                <h2
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-server fa-fw"
                                                    ></i>
                                                    {{ getAgent.name }}
                                                </h2>
                                                <b-badge
                                                    v-if="
                                                        getAgent.role ===
                                                            'guest'
                                                    "
                                                    variant="info"
                                                    >Guest</b-badge
                                                >
                                                <b-badge
                                                    v-else-if="
                                                        getAgent.role ===
                                                            'admin'
                                                    "
                                                    variant="warning"
                                                    >Owner</b-badge
                                                >
                                                <br />
                                                <small>{{
                                                    getAgent.description
                                                }}</small>
                                            </b-col>
                                        </b-row>
                                        <hr />
                                        <b-row
                                            ><b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Executor Configuration
                                                </h5>
                                                <b-row>
                                                    <b-col>
                                                        <small>executor</small>
                                                    </b-col>
                                                    <b-col cols="9">
                                                        <b class="ml-3">
                                                            {{
                                                                getAgent.executor
                                                            }}
                                                        </b>
                                                    </b-col>
                                                </b-row>
                                                <b-row>
                                                    <b-col>
                                                        <small
                                                            >working
                                                            directory</small
                                                        >
                                                    </b-col>
                                                    <b-col cols="9">
                                                        <b class="ml-3">
                                                            {{
                                                                getAgent.workdir
                                                            }}
                                                        </b>
                                                    </b-col>
                                                </b-row>
                                                <b-row>
                                                    <b-col>
                                                        <small
                                                            >pre-commands</small
                                                        >
                                                    </b-col>
                                                    <b-col cols="9"
                                                        ><b class="ml-3"
                                                            ><code>{{
                                                                getAgent.pre_commands
                                                            }}</code></b
                                                        ></b-col
                                                    >
                                                </b-row>
                                            </b-col>
                                            <b-col>
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Resources Available
                                                    <small
                                                        >(per container)</small
                                                    >
                                                </h5>
                                                <b>{{ getAgent.max_cores }}</b>
                                                <small> core(s)</small>
                                                <br />
                                                <b>{{
                                                    getAgent.max_processes
                                                }}</b>
                                                <small> process(es)</small>
                                                <br />
                                                <span
                                                    v-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) < 0
                                                    "
                                                >
                                                    <small
                                                        >Virtual memory</small
                                                    ></span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) > 0
                                                    "
                                                    >{{ getAgent.max_mem
                                                    }}<small>
                                                        GB memory</small
                                                    ></span
                                                >
                                                <span
                                                    v-else-if="
                                                        parseInt(
                                                            getAgent.max_mem
                                                        ) === -1
                                                    "
                                                    ><small
                                                        >virtual memory</small
                                                    ></span
                                                >
                                                <br />
                                                <span v-if="getAgent.gpu">
                                                    <i
                                                        :class="
                                                            getAgent.gpu
                                                                ? 'text-warning'
                                                                : ''
                                                        "
                                                        class="far fa-check-circle"
                                                    ></i>
                                                    <small>GPU</small>
                                                </span>
                                                <span v-else
                                                    ><small>
                                                        No GPU
                                                    </small></span
                                                >
                                            </b-col>
                                        </b-row>
                                        <hr />
                                        <b-row>
                                            <b-col
                                                v-if="ownsAgent"
                                                class="mr-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-form-checkbox
                                                    v-model="getAgent.public"
                                                    :disabled="
                                                        getAgent.authentication ===
                                                            'password'
                                                    "
                                                    button
                                                    class="mr-0"
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :title="
                                                        getAgent.authentication ===
                                                            'password' &&
                                                        !getAgent.public
                                                            ? `To make ${getAgent.name} public you must enable key authentication`
                                                            : `Make ${
                                                                  getAgent.name
                                                              } ${
                                                                  getAgent.public
                                                                      ? 'private'
                                                                      : 'public'
                                                              }`
                                                    "
                                                    :button-variant="
                                                        getAgent.public
                                                            ? 'warning'
                                                            : 'info'
                                                    "
                                                    @change="togglePublic"
                                                >
                                                    <i
                                                        v-if="getAgent.public"
                                                        class="fas fa-lock-open fa-fw"
                                                    ></i>
                                                    <i
                                                        v-else
                                                        class="fas fa-lock fa-fw"
                                                    ></i>
                                                    {{
                                                        getAgent.public
                                                            ? 'Public'
                                                            : 'Private'
                                                    }}
                                                </b-form-checkbox>
                                            </b-col>
                                            <!--<b-col
                                                v-else-if="
                                                    getAgent.role === 'none' &&
                                                        !accessRequested
                                                "
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :title="
                                                        'Request access to ' +
                                                            getAgent.name
                                                    "
                                                    @click="requestAccess"
                                                >
                                                    <i
                                                        class="fas fa-key fa-fw"
                                                    ></i>
                                                    Request Guest Access
                                                </b-button></b-col
                                            >-->
                                            <b-col
                                                v-if="
                                                    getAgent.role === 'admin' &&
                                                        getAgent.authentication ===
                                                            'key'
                                                "
                                                class="m-0"
                                                align-self="end"
                                                md="auto"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="View your public key"
                                                    @click="getKey"
                                                >
                                                    <b-spinner
                                                        small
                                                        v-if="gettingKey"
                                                        label="Loading..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="ml-2 mb-1"
                                                    ></b-spinner>
                                                    <i
                                                        v-else
                                                        class="fas fa-eye fa-fw"
                                                    ></i>
                                                    View Key
                                                </b-button></b-col
                                            >
                                            <b-col
                                                v-if="getAgent.role === 'admin'"
                                                class="m-0"
                                                align-self="end"
                                                md="auto"
                                                ><b-dropdown
                                                    :disabled="getAgent.public"
                                                    v-b-tooltip.hover
                                                    size="sm"
                                                    :title="
                                                        getAgent.public
                                                            ? `To select a different authentication strategy you must make ${getAgent.name} private`
                                                            : 'Select an authentication strategy'
                                                    "
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    ><template #button-content
                                                        ><span
                                                            v-if="
                                                                getAgent.authentication ===
                                                                    'password'
                                                            "
                                                            ><i
                                                                class="fas fa-pen fa-fw fa-1x"
                                                            ></i>
                                                            Password</span
                                                        ><span v-else
                                                            ><i
                                                                class="fas fa-key fa-fw fa-1x"
                                                            ></i>
                                                            Key</span
                                                        >
                                                        Authentication</template
                                                    ><b-dropdown-text
                                                        >Select an
                                                        authentication
                                                        strategy.</b-dropdown-text
                                                    ><b-dropdown-item-button
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'outline-light'
                                                                : 'dark'
                                                        "
                                                        :active="
                                                            getAgent.authentication ===
                                                                'password'
                                                        "
                                                        :disabled="
                                                            getAgent.authentication ===
                                                                'password'
                                                        "
                                                        @click="
                                                            setAuthStrategy(
                                                                'password'
                                                            )
                                                        "
                                                        ><template #default
                                                            ><span
                                                                ><i
                                                                    class="fas fa-pen fa-fw fa-1x"
                                                                ></i>
                                                                Password</span
                                                            ></template
                                                        ></b-dropdown-item-button
                                                    ><b-dropdown-item-button
                                                        :active="
                                                            getAgent.authentication ===
                                                                'key'
                                                        "
                                                        :disabled="
                                                            getAgent.authentication ===
                                                                'key'
                                                        "
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'outline-light'
                                                                : 'dark'
                                                        "
                                                        @click="
                                                            setAuthStrategy(
                                                                'key'
                                                            )
                                                        "
                                                        ><template #default
                                                            ><span
                                                                ><i
                                                                    class="fas fa-key fa-fw fa-1x"
                                                                ></i>
                                                                Key</span
                                                            ></template
                                                        ></b-dropdown-item-button
                                                    ></b-dropdown
                                                ></b-col
                                            >
                                            <b-col
                                                v-if="getAgent.role !== 'none'"
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :title="
                                                        'Verify that PlantIT can connect to ' +
                                                            getAgent.name
                                                    "
                                                    :disabled="
                                                        getAgent.role ===
                                                            'none' ||
                                                            checkingConnection
                                                    "
                                                    @click="preCheckConnection"
                                                >
                                                    <i
                                                        class="fas fa-wave-square fa-fw"
                                                    ></i>
                                                    Check Connection<b-spinner
                                                        small
                                                        v-if="
                                                            checkingConnection
                                                        "
                                                        label="Loading..."
                                                        :variant="
                                                            profile.darkMode
                                                                ? 'light'
                                                                : 'dark'
                                                        "
                                                        class="ml-2 mb-1"
                                                    ></b-spinner> </b-button
                                            ></b-col>
                                            <b-col></b-col>
                                            <b-col
                                                v-if="getAgent.role === 'admin'"
                                                class="m-0"
                                                align-self="end"
                                                md="auto"
                                                ><b-button
                                                    @click="
                                                        showUnbindAgentModal
                                                    "
                                                    v-b-tooltip.hover
                                                    :title="
                                                        'Unbind ' +
                                                            getAgent.name
                                                    "
                                                    size="sm"
                                                    variant="outline-danger"
                                                    ><i
                                                        class="fas fa-times-circle fa-fw fa-1x"
                                                    ></i>
                                                    Unbind</b-button
                                                ></b-col
                                            >
                                            <!--<b-col
                                                v-if="
                                                    getAgent.role === 'none' &&
                                                        accessRequested
                                                "
                                                class="ml-0"
                                                md="auto"
                                                align-self="end"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    :disabled="true"
                                                >
                                                    <i
                                                        class="fas fa-key fa-fw"
                                                    ></i>
                                                    You requested access
                                                    {{
                                                        prettify(
                                                            accessRequest.created
                                                        )
                                                    }}. Your request is pending.
                                                </b-button></b-col
                                            >-->
                                            <!--<b-col></b-col>
                                            <b-col md="auto"
                                                ><b-button
                                                    class="ml-0"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    :disabled="
                                                        (session !== null &&
                                                            session !==
                                                                undefined) ||
                                                            sessionLoading
                                                    "
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="Start interactive datasets"
                                                    @click="
                                                        tryOpenDataset
                                                    "
                                                >
                                                    <i
                                                        class="fas fa-tasks fa-fw"
                                                    ></i>
                                                    Start Session
                                                </b-button></b-col
                                            >-->
                                        </b-row>
                                    </b-col>
                                </b-row>
                            </div>
                        </b-card>
                        <br />
                        <div v-if="getAgent.role === 'admin'">
                            <b-row no-gutters>
                                <b-col align-self="end" md="auto" class="mr-1"
                                    ><h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Users
                                    </h5></b-col
                                ><b-col md="auto" class="ml-1 mb-1"
                                    ><b-button
                                        size="sm"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        :disabled="authorizingWorkflow"
                                        title="Authorize a user"
                                        v-b-tooltip.hover
                                        @click="specifyAuthorizedUser"
                                        ><i class="fas fa-plus fa-fw"></i
                                        >Authorize</b-button
                                    ></b-col
                                >
                            </b-row>
                            <b-row
                                ><b-col align-self="end">
                                    <b-row
                                        v-if="
                                            !agentLoading &&
                                                getAgent.users_authorized
                                                    .length === 0
                                        "
                                        ><b-col
                                            ><small
                                                >You are this agent's only
                                                user.</small
                                            ></b-col
                                        ></b-row
                                    >
                                    <b-row
                                        class="mt-1"
                                        v-else
                                        v-for="user in authorizedUsers"
                                        v-bind:key="user.username"
                                    >
                                        <b-col
                                            ><b-img
                                                v-if="user.github_profile"
                                                class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                                                style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                                                rounded="circle"
                                                :src="
                                                    user.github_profile
                                                        ? user.github_profile
                                                              .avatar_url
                                                        : ''
                                                "
                                            ></b-img>
                                            <i
                                                v-else
                                                class="far fa-user mr-1"
                                            ></i>
                                            <b
                                                >{{ user.first_name }}
                                                {{ user.last_name }}</b
                                            >
                                            ({{ user.username }})</b-col
                                        ><b-col
                                            class="ml-0"
                                            md="auto"
                                            align-self="end"
                                            ><b-button
                                                class="ml-0"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                :title="
                                                    'Revoke access from ' +
                                                        user.username
                                                "
                                                @click="unauthorizeUser(user)"
                                            >
                                                <i
                                                    class="fas fa-lock fa-fw"
                                                ></i>
                                                Revoke Access
                                            </b-button></b-col
                                        >
                                    </b-row>
                                </b-col>
                            </b-row>
                            <hr />
                        </div>
                        <div v-if="ownsAgent">
                            <b-row no-gutters>
                                <b-col align-self="end" md="auto" class="mr-1"
                                    ><h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Workflow Policies
                                    </h5></b-col
                                ><b-col class="ml-1" md="auto"
                                    ><b-dropdown
                                        v-if="workflowPolicyType === 'none'"
                                        class="mb-1"
                                        size="sm"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        v-b-tooltip.hover
                                        :title="
                                            `Configure workflow policies for ${getAgent.name}`
                                        "
                                        :text="workflowPolicyType"
                                        v-model="workflowPolicyType"
                                    >
                                        <template #button-content>
                                            <span
                                                ><i
                                                    class="fas fa-cog fa-fw"
                                                ></i>
                                                Configure</span
                                            >
                                        </template>
                                        <b-dropdown-item
                                            @click="specifyAuthorizedWorkflow"
                                            >Specify authorized
                                            workflows</b-dropdown-item
                                        >
                                        <b-dropdown-item
                                            @click="specifyBlockedWorkflow"
                                            >Specify blocked
                                            workflows</b-dropdown-item
                                        > </b-dropdown
                                    ><b-button
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-dark'
                                                : 'white'
                                        "
                                        :disabled="authorizingWorkflow"
                                        title="Authorize another workflow"
                                        v-b-tooltip.hover
                                        v-else-if="
                                            workflowPolicyType === 'authorized'
                                        "
                                        @click="specifyAuthorizedWorkflow"
                                        ><i class="fas fa-plus fa-fw"></i
                                        >Authorize</b-button
                                    ><b-button
                                        :disabled="blockingWorkflow"
                                        title="Block another workflow"
                                        v-b-tooltip.hover
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-dark'
                                                : 'white'
                                        "
                                        v-else
                                        @click="specifyBlockedWorkflow"
                                        ><i class="fas fa-plus fa-fw"></i
                                        >Block</b-button
                                    ></b-col
                                >
                            </b-row>
                            <b-row v-if="workflowPolicyType === 'none'"
                                ><b-col
                                    ><small
                                        >No restrictions (all workflows
                                        permitted).</small
                                    ></b-col
                                ></b-row
                            >
                            <b-row v-else
                                ><b-col align-self="end">
                                    <b-row class="mb-2">
                                        <b-col>
                                            <small>{{
                                                workflowPolicyType === 'none'
                                                    ? ''
                                                    : workflowPolicyType ===
                                                      'authorized'
                                                    ? 'Only the following workflows can run on this agent. To select particular workflows to block instead (and allow all others), first remove all authorized workflows.'
                                                    : 'All workflows except the following can run on this agent. To select particular workflows to permit instead (and block all others), first remove all blocked workflows.'
                                            }}</small>
                                        </b-col>
                                    </b-row>
                                    <div
                                        v-if="
                                            workflowPolicyType === 'authorized'
                                        "
                                    >
                                        <b-card
                                            :bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            :header-bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            border-variant="default"
                                            :header-border-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            :text-variant="
                                                profile.darkMode
                                                    ? 'white'
                                                    : 'dark'
                                            "
                                            class="overflow-hidden"
                                            v-for="workflow in getAgent.workflows_authorized"
                                            v-bind:key="workflow.config.name"
                                            no-body
                                            ><b-card-body
                                                class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                                ><blurb
                                                    :linkable="false"
                                                    :workflow="workflow"
                                                ></blurb
                                                ><b-row class="mt-2">
                                                    <b-col class="text-right"
                                                        ><b-button
                                                            :disabled="
                                                                authorizingWorkflow
                                                            "
                                                            variant="outline-danger"
                                                            @click="
                                                                unauthorizeWorkflow(
                                                                    workflow
                                                                )
                                                            "
                                                            >Unauthorize</b-button
                                                        ></b-col
                                                    >
                                                </b-row></b-card-body
                                            ></b-card
                                        >
                                    </div>
                                    <div
                                        v-else-if="
                                            workflowPolicyType === 'blocked'
                                        "
                                    >
                                        <b-card
                                            :bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            :header-bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            border-variant="default"
                                            :header-border-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            :text-variant="
                                                profile.darkMode
                                                    ? 'white'
                                                    : 'dark'
                                            "
                                            class="overflow-hidden"
                                            v-for="workflow in getAgent.workflows_blocked"
                                            v-bind:key="workflow.config.name"
                                            no-body
                                            ><b-card-body
                                                class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                                ><blurb
                                                    :linkable="false"
                                                    :workflow="workflow"
                                                ></blurb
                                                ><b-row class="mt-2">
                                                    <b-col class="text-right"
                                                        ><b-button
                                                            :disabled="
                                                                blockingWorkflow
                                                            "
                                                            variant="outline-danger"
                                                            @click="
                                                                unblockWorkflow(
                                                                    workflow
                                                                )
                                                            "
                                                            >Unblock</b-button
                                                        ></b-col
                                                    >
                                                </b-row></b-card-body
                                            ></b-card
                                        >
                                    </div>
                                </b-col>
                            </b-row>
                        </div>
                        <!--<b-col md="auto">
                        <b-row
                            ><b-col align-self="end"
                                ><h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    Periodic Tasks
                                </h5></b-col
                            ><b-col class="mb-1" align-self="start" md="auto"
                                ><b-button
                                    :variant="
                                        profile.darkMode
                                            ? 'outline-light'
                                            : 'white'
                                    "
                                    size="sm"
                                    v-b-tooltip.hover
                                    title="Create Periodic Task"
                                    :disabled="getAgent.role !== 'admin'"
                                    v-b-modal.createTask
                                >
                                    <i class="fas fa-plus fa-fw"></i>
                                    Create
                                </b-button></b-col
                            ></b-row
                        >
                        <div
                            v-for="task in getAgent.tasks"
                            v-bind:key="task.name"
                            class="pb-2"
                        >
                            <b-row class="pt-1">
                                <b-col
                                    md="auto"
                                    v-if="getAgent.role === 'admin'"
                                    align-self="end"
                                    :class="
                                        profile.darkMode
                                            ? 'text-white mb-1'
                                            : 'text-dark mb-1'
                                    "
                                >
                                    <b-form-checkbox
                                        v-model="task.enabled"
                                        @change="toggleTask(task)"
                                        switch
                                        size="md"
                                    >
                                    </b-form-checkbox
                                ></b-col>
                                <b-col align-self="end" class="mb-1">{{
                                    task.name
                                }}</b-col>
                                <b-col
                                    md="auto"
                                    align-self="end"
                                    v-if="getAgent.role === 'admin'"
                                    ><b-button
                                        size="sm"
                                        variant="outline-danger"
                                        @click="deleteTask(task)"
                                        ><i class="fas fa-trash fa-fw"></i>
                                        Remove</b-button
                                    ></b-col
                                ></b-row
                            >
                            <b-row
                                ><b-col md="auto" align-self="end" class="mb-1"
                                    ><small v-if="task.enabled"
                                        >Next running {{ cronTime(task)
                                        }}<br /></small
                                    ><small v-if="task.last_run !== null"
                                        >Last ran
                                        {{ prettify(task.last_run) }}</small
                                    ><small v-else
                                        >Task has not run yet</small
                                    ></b-col
                                >
                            </b-row>
                        </div>
                    </b-col>-->
                    </b-col>
                </b-row>
            </div>
        </b-container>
        <b-modal
            id="authorizeUser"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            size="lg"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            hide-header
            hide-header-close
            hide-footer
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Select a user
                    </h4></b-col
                >
                <b-col md="auto"
                    ><b-button
                        :disabled="usersLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Rescan users"
                        @click="refreshUsers"
                        class="text-right"
                    >
                        <b-spinner
                            small
                            v-if="usersLoading"
                            label="Rescanning..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i>Rescan
                        Users</b-button
                    ></b-col
                >
            </b-row>
            <div v-if="otherUsers.length !== 0">
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    Select a user to authorize for
                    <i class="fas fa-server fa-fw"></i>
                    {{ getAgent.name }}.
                </p>
                <b-row class="mb-2"
                    ><b-col
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><small
                            >{{ otherUsers.length }} user(s) found</small
                        ></b-col
                    ></b-row
                >
                <b-row v-for="user in otherUsers" v-bind:key="user.username">
                    <b-col
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    >
                        <b-img
                            v-if="user.github_profile"
                            class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                            style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                            rounded="circle"
                            :src="
                                user.github_profile
                                    ? user.github_profile.avatar_url
                                    : ''
                            "
                        ></b-img>
                        <i v-else class="far fa-user"></i>
                        <b>{{ user.first_name }} {{ user.last_name }}</b> ({{
                            user.username
                        }})
                    </b-col>
                    <b-col md="auto" align-self="center"
                        ><b-button
                            :disabled="authorizingUser"
                            variant="warning"
                            @click="authorizeUser(user)"
                            >Select</b-button
                        ></b-col
                    >
                </b-row>
            </div>
            <div class="text-center" v-else>
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    <i class="fas fa-exclamation-circle fa-fw fa-2x"></i
                    ><br />No unauthorized users found.
                </p>
            </div>
        </b-modal>
        <b-modal
            id="authorizeWorkflow"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            size="lg"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            hide-header
            hide-header-close
            hide-footer
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Select a workflow
                    </h4></b-col
                ><b-col md="auto"
                    ><b-button
                        :disabled="publicWorkflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Rescan workflows"
                        @click="refreshWorkflows"
                        class="text-right"
                    >
                        <b-spinner
                            small
                            v-if="publicWorkflowsLoading"
                            label="Rescanning..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i>Rescan
                        Workflows</b-button
                    ></b-col
                ></b-row
            >
            <b-tabs content-class="mt-2">
                <b-tab title="Yours">
                    <div v-if="personalWorkflowsLoading">
                        <b-row>
                            <b-col class="text-center">
                                <b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner>
                            </b-col>
                        </b-row>
                    </div>
                    <div v-else-if="boundWorkflows.length !== 0">
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Select a personal workflow to authorize on
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }}. All users with access to
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }} will be able to use this
                            workflow.
                        </p>
                        <p>
                            <b-row class="mb-1"
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    ><small
                                        >{{
                                            unauthorizedBoundWorkflows.length
                                        }}
                                        unauthorized workflow(s) found</small
                                    ></b-col
                                ></b-row
                            >
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
                                v-for="workflow in unauthorizedBoundWorkflows"
                                v-bind:key="workflow.config.name"
                                no-body
                                ><b-card-body
                                    class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                >
                                    <blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb>
                                    <b-row class="mt-2">
                                        <b-col
                                            ><b-button
                                                :disabled="authorizingWorkflow"
                                                block
                                                variant="warning"
                                                @click="
                                                    authorizeWorkflow(workflow)
                                                "
                                                >Select</b-button
                                            ></b-col
                                        >
                                    </b-row>
                                </b-card-body>
                            </b-card>
                        </p>
                    </div>
                    <div class="text-center" v-else>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            No workflows found.
                        </p>
                    </div></b-tab
                >
                <b-tab title="Public">
                    <div v-if="publicWorkflowsLoading">
                        <b-row>
                            <b-col class="text-center">
                                <b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner>
                            </b-col>
                        </b-row>
                    </div>
                    <div v-else-if="publicWorkflows.length !== 0">
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Select a public workflow to authorize on
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }}. All users with access to
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }} will be able to use this
                            workflow.
                        </p>
                        <p>
                            <b-row class="mb-1"
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    ><small
                                        >{{
                                            unauthorizedPublicWorkflows.length
                                        }}
                                        unauthorized workflow(s) found</small
                                    ></b-col
                                ></b-row
                            >
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
                                v-for="workflow in unauthorizedPublicWorkflows"
                                v-bind:key="workflow.config.name"
                                no-body
                                ><b-card-body
                                    class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                >
                                    <blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb>
                                    <b-row class="mt-2">
                                        <b-col
                                            ><b-button
                                                :disabled="authorizingWorkflow"
                                                block
                                                variant="warning"
                                                @click="
                                                    authorizeWorkflow(workflow)
                                                "
                                                >Select</b-button
                                            ></b-col
                                        >
                                    </b-row>
                                </b-card-body>
                            </b-card>
                        </p>
                    </div>
                    <div class="text-center" v-else>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            No workflows found.
                        </p>
                    </div></b-tab
                >
            </b-tabs>
        </b-modal>
        <b-modal
            id="blockWorkflow"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            size="lg"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            hide-header
            hide-header-close
            hide-footer
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Select a workflow
                    </h4></b-col
                ><b-col md="auto"
                    ><b-button
                        :disabled="publicWorkflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Rescan workflows"
                        @click="refreshWorkflows"
                        class="text-right"
                    >
                        <b-spinner
                            small
                            v-if="publicWorkflowsLoading"
                            label="Rescanning..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i>Rescan
                        Workflows</b-button
                    ></b-col
                ></b-row
            >
            <b-tabs content-class="mt-2">
                <b-tab title="Yours">
                    <div v-if="personalWorkflowsLoading">
                        <b-row>
                            <b-col class="text-center">
                                <b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner>
                            </b-col>
                        </b-row>
                    </div>
                    <div v-else-if="boundWorkflows.length !== 0">
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Select a personal workflow to block on
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }}. All users with access to
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }} will be prevented from using
                            this workflow.
                        </p>
                        <p>
                            <b-row class="mb-1"
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    ><small
                                        >{{
                                            unblockedBoundWorkflows.length
                                        }}
                                        unblocked workflow(s) found</small
                                    ></b-col
                                ></b-row
                            >
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
                                v-for="workflow in unblockedBoundWorkflows"
                                v-bind:key="workflow.config.name"
                                no-body
                                ><b-card-body
                                    class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                >
                                    <blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb>
                                    <b-row class="mt-2">
                                        <b-col
                                            ><b-button
                                                :disabled="blockingWorkflow"
                                                block
                                                variant="warning"
                                                @click="blockWorkflow(workflow)"
                                                >Select</b-button
                                            ></b-col
                                        >
                                    </b-row>
                                </b-card-body>
                            </b-card>
                        </p>
                    </div>
                    <div class="text-center" v-else>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            No workflows found.
                        </p>
                    </div></b-tab
                >
                <b-tab title="Public">
                    <div v-if="publicWorkflowsLoading">
                        <b-row>
                            <b-col class="text-center">
                                <b-spinner
                                    type="grow"
                                    label="Loading..."
                                    variant="secondary"
                                ></b-spinner>
                            </b-col>
                        </b-row>
                    </div>
                    <div v-else-if="publicWorkflows.length !== 0">
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Select a public workflow to block on
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }}. All users with access to
                            <i class="fas fa-server fa-fw"></i>
                            {{ getAgent.name }} will be prevented from using
                            this workflow.
                        </p>
                        <p>
                            <b-row class="mb-1"
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    ><small
                                        >{{
                                            unblockedPublicWorkflows.length
                                        }}
                                        unblocked workflow(s) found</small
                                    ></b-col
                                ></b-row
                            >
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
                                v-for="workflow in unblockedPublicWorkflows"
                                v-bind:key="workflow.config.name"
                                no-body
                                ><b-card-body
                                    class="mr-1 mt-2 mb-2 ml-2 p-1 pt-2"
                                >
                                    <blurb
                                        :workflow="workflow"
                                        :linkable="false"
                                    ></blurb>
                                    <b-row class="mt-2">
                                        <b-col
                                            ><b-button
                                                :disabled="blockingWorkflow"
                                                block
                                                variant="warning"
                                                @click="blockWorkflow(workflow)"
                                                >Select</b-button
                                            ></b-col
                                        >
                                    </b-row>
                                </b-card-body>
                            </b-card>
                        </p>
                    </div>
                    <div class="text-center" v-else>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            No workflows found.
                        </p>
                    </div></b-tab
                >
            </b-tabs>
        </b-modal>
        <b-modal
            id="key"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="`Public key for ${this.getAgent.name}`"
            ok-only
            @ok="hideKeyModal"
            ok-variant="success"
        >
            <b-row
                ><b-col style="word-wrap: break-word;">
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Here is your public key. Copy it into the
                        <code>~/.ssh/authorized_keys</code> file on your agent.
                    </p>
                    <b-form-textarea
                        plaintext
                        :value="publicKey"
                        max-rows="15"
                        class="p-1"
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    ></b-form-textarea
                    ><b-button
                        block
                        class="text-center"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Copy key to clipboard"
                        @click="copyPublicKey"
                        ><i class="fas fa-copy fa-fw"></i>Copy</b-button
                    ></b-col
                ></b-row
            >
        </b-modal>
        <b-modal
            id="unbind"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="`Unbind ${this.getAgent.name}?`"
            @ok="unbindAgent"
            ok-variant="danger"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                You {{ getAgent.public ? 'and others' : '' }} will no longer be
                able to use this agent (although you can re-bind it anytime).
            </p>
        </b-modal>
        <b-modal
            centered
            id="createTask"
            title="Create Periodic Task"
            @ok="createTask"
            size="xl"
        >
            <b-form @submit="createTask" @reset="resetCreateTaskForm">
                <b-form-group id="input-group-1" label-for="input-1">
                    <b-input-group size="md" prepend="Name">
                        <b-form-input
                            id="input-1"
                            v-model="createTaskForm.name"
                            required
                        ></b-form-input>
                        <b-form-invalid-feedback
                            :state="this.createTaskForm.name !== ''"
                        >
                            Give this task a name.
                        </b-form-invalid-feedback>
                    </b-input-group>
                </b-form-group>
                <b-form-group id="input-group-3" label-for="input-3">
                    <b-input-group size="md" prepend="Command">
                        <b-form-input
                            id="input-3"
                            v-model="createTaskForm.command"
                            required
                        ></b-form-input>
                        <b-form-invalid-feedback
                            :state="this.createTaskForm.command !== ''"
                        >
                            Enter a command for this task to run.
                        </b-form-invalid-feedback>
                    </b-input-group>
                </b-form-group>
                <b-form-group
                    id="input-group-4"
                    label-for="input-4"
                    description="Configure when this task should run."
                >
                    <VueCronEditorBuefy
                        v-model="createTaskForm.time"
                    ></VueCronEditorBuefy>
                </b-form-group>
            </b-form>
        </b-modal>
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
            :title="'Authenticate with ' + getAgent.name"
            @ok="submitAuthentication"
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
    </div>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';
import VueCronEditorBuefy from 'vue-cron-editor-buefy';
import parser from 'cron-parser';
import { guid } from '@/utils';
import router from '@/router';
import blurb from '@/components/workflows/workflow-blurb.vue';

export default {
    name: 'agent',
    components: {
        VueCronEditorBuefy,
        blurb
    },
    data: function() {
        return {
            authenticationUsername: '',
            authenticationPassword: '',
            checkingConnection: false,
            alertEnabled: false,
            alertMessage: '',
            createTaskForm: {
                name: '',
                description: '',
                command: '',
                once: '',
                time: ''
            },
            sessionSocket: null,
            togglingPublic: false,
            publicKey: '',
            gettingKey: false,
            workflowPolicyType: 'none',
            workflowSearchName: '',
            workflowSearchResultInvalid: false,
            searchWorkflows: false,
            authorizingWorkflow: false,
            blockingWorkflow: false,
            authorizingUser: false
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('workflows', [
            'recentlyRunWorkflows',
            'personalWorkflowsLoading',
            'boundWorkflows',
            'publicWorkflowsLoading',
            'publicWorkflows'
        ]),
        ...mapGetters('agents', [
            'agent',
            'personalAgentsLoading',
            'publicAgentsLoading'
        ]),
        authorizedUsers() {
            return this.getAgent.users_authorized.filter(
                p => p.user !== this.profile.djangoProfile.username
            );
        },
        otherUsers() {
            return this.allUsers.filter(
                u =>
                    u.username !== this.profile.djangoProfile.username &&
                    !this.getAgent.users_authorized.some(
                        ua => ua.username === u.username
                    )
            );
        },
        unauthorizedBoundWorkflows() {
            return this.boundWorkflows.filter(
                wf =>
                    !this.getAgent.workflows_authorized.some(
                        b =>
                            b.repo.owner.login === wf.repo.owner.login &&
                            b.config.name === wf.config.name
                    )
            );
        },
        unauthorizedPublicWorkflows() {
            return this.publicWorkflows.filter(
                wf =>
                    !this.getAgent.workflows_authorized.some(
                        b =>
                            b.repo.owner.login === wf.repo.owner.login &&
                            b.config.name === wf.config.name
                    )
            );
        },
        unblockedBoundWorkflows() {
            return this.boundWorkflows.filter(
                wf =>
                    !this.getAgent.workflows_blocked.some(
                        b =>
                            b.repo.owner.login === wf.repo.owner.login &&
                            b.config.name === wf.config.name
                    )
            );
        },
        unblockedPublicWorkflows() {
            return this.publicWorkflows.filter(
                wf =>
                    !this.getAgent.workflows_blocked.some(
                        b =>
                            b.repo.owner.login === wf.repo.owner.login &&
                            b.config.name === wf.config.name
                    )
            );
        },
        agentLoading() {
            return this.publicAgentsLoading || this.personalAgentsLoading;
        },
        ownsAgent() {
            return (
                this.getAgent.user !== undefined &&
                this.getAgent.user === this.profile.djangoProfile.username
            );
        },
        getAgent() {
            return this.agent(this.$router.currentRoute.params.name);
        },
        mustAuthenticate() {
            return (
                this.getAgent.role !== 'admin' ||
                this.getAgent.authentication === 'password'
            );
        }
    },
    mounted: function() {
        this.workflowPolicyType =
            this.getAgent.workflows_authorized.length > 0
                ? 'authorized'
                : this.getAgent.workflows_blocked.length > 0
                ? 'blocked'
                : 'none';
    },
    watch: {
        workflowPolicyType() {
            // noop
        },
        getAgent() {
            // noop
        },
        agent() {
            // noop
        }
    },
    methods: {
        copyPublicKey() {
            const el = document.createElement('textarea');
            el.value = this.publicKey;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            this.$bvToast.toast(`Copied public key to clipboard`, {
                autoHideDelay: 3000,
                appendToast: false,
                noCloseButton: true
            });
        },
        async refreshWorkflows() {
            await Promise.all([
                this.$store.dispatch('workflows/refreshPublic'),
                this.$store.dispatch(
                    'workflows/refreshPersonal',
                    this.profile.githubProfile.login
                )
            ]);
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
        specifyAuthorizedUser() {
            this.$bvModal.show('authorizeUser');
        },
        specifyAuthorizedWorkflow() {
            this.$bvModal.show('authorizeWorkflow');
        },
        specifyBlockedWorkflow() {
            this.$bvModal.show('blockWorkflow');
        },
        showKeyModal() {
            this.$bvModal.show('key');
        },
        hideKeyModal() {
            this.$bvModal.hide('key');
            this.publicKey = '';
        },
        showUnbindAgentModal() {
            this.$bvModal.show('unbind');
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        async authorizeUser(user) {
            this.authorizingUser = true;
            let data = { user: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/authorize_user/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Authorized user ${user.username} for agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to authorize user ${user.username} for agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.$bvModal.hide('authorizeUser');
                    this.authorizingUser = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to authorize user ${user.username} for agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.$bvModal.hide('authorizeUser');
                    this.authorizingUser = false;
                    throw error;
                });
        },
        async unauthorizeUser(user) {
            this.authorizingUser = true;
            let data = { user: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/unauthorize_user/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Revoked user ${user.username}'s access to agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to revoke user ${user.username}'s access to agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.authorizingUser = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to revoke user ${user.username}'s access to agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.authorizingUser = false;
                    throw error;
                });
        },
        async authorizeWorkflow(workflow) {
            this.authorizingWorkflow = true;
            let data = {
                owner: workflow.repo.owner.login,
                name: workflow.repo.name
            };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/authorize_workflow/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Authorized workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                        this.workflowPolicyType = 'authorized';
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to authorize workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.$bvModal.hide('authorizeWorkflow');
                    this.authorizingWorkflow = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to authorize workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.$bvModal.hide('authorizeWorkflow');
                    this.authorizingWorkflow = false;
                    throw error;
                });
        },
        async unauthorizeWorkflow(workflow) {
            this.authorizingWorkflow = true;
            let data = {
                owner: workflow.repo.owner.login,
                name: workflow.repo.name
            };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/unauthorize_workflow/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unauthorized workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                        if (this.getAgent.workflows_authorized.length === 0)
                            this.workflowPolicyType = 'none';
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to unauthorize workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.authorizingWorkflow = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unauthorize workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.authorizingWorkflow = false;
                    throw error;
                });
        },
        async blockWorkflow(workflow) {
            this.blockingWorkflow = true;
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/block_workflow/`,
                data: {
                    owner: workflow.repo.owner.login,
                    name: workflow.repo.name
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Blocked workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                        this.workflowPolicyType = 'blocked';
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to block workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.$bvModal.hide('blockWorkflow');
                    this.blockingWorkflow = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to block workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.gettingKey = false;
                    this.blockingWorkflow = false;
                    throw error;
                });
        },
        async unblockWorkflow(workflow) {
            this.blockingWorkflow = true;
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/unblock_workflow/`,
                data: {
                    owner: workflow.repo.owner.login,
                    name: workflow.repo.name
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unblocked workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                        if (this.getAgent.workflows_authorized.length === 0)
                            this.workflowPolicyType = 'none';
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to unblock workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                            guid: guid().toString()
                        });
                    }
                    this.blockingWorkflow = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unblock workflow ${workflow.config.name} on agent ${this.getAgent.name}`,
                        guid: guid().toString()
                    });
                    this.blockingWorkflow = false;
                    throw error;
                });
        },
        async getKey() {
            this.gettingKey = true;
            await axios
                .get(`/apis/v1/users/get_key/`)
                .then(async response => {
                    if (response.status === 200) {
                        this.publicKey = response.data.public_key;
                        this.showKeyModal();
                        // await this.$store.dispatch('alerts/add', {
                        //     variant: 'success',
                        //     message: `Retrieved public key`,
                        //     guid: guid().toString()
                        // });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to retrieve public key`,
                            guid: guid().toString()
                        });
                    }
                    this.gettingKey = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to retrieve public key`,
                        guid: guid().toString()
                    });
                    this.gettingKey = false;
                    throw error;
                });
        },
        async setAuthStrategy(strategy) {
            let data = {
                strategy: strategy
            };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/auth/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'agents/setPersonal',
                            response.data.agents
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Configured agent ${this.$router.currentRoute.params.name} for ${this.getAgent.authentication} authentication`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to set authentication strategy for agent ${this.$router.currentRoute.params.name}`,
                            guid: guid().toString()
                        });
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to set authentication strategy for agent ${this.$router.currentRoute.params.name}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        submitAuthentication() {
            this.checkConnection();
        },
        async unbindAgent() {
            await axios({
                method: 'delete',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/`,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (response.status === 200) {
                        this.$store.dispatch(
                            'agents/setPersonal',
                            response.data.agents
                        );
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed binding for agent ${this.$router.currentRoute.params.name}`,
                            guid: guid().toString()
                        });
                        router.push({
                            name: 'agents'
                        });
                    } else {
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove binding for agent ${this.$router.currentRoute.params.name}`,
                            guid: guid().toString()
                        });
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove binding for agent ${this.$router.currentRoute.params.name}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        async togglePublic() {
            if (!this.ownsAgent) return;
            this.togglingPublic = true;
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$router.currentRoute.params.name}/public/`,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'agents/setPersonal',
                                response.data.agents
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Made ${
                                    this.$router.currentRoute.params.name
                                } ${
                                    response.data.agents.find(
                                        agent =>
                                            agent.name === this.getAgent.name
                                    ).public
                                        ? 'public'
                                        : 'private'
                                }`,
                                guid: guid().toString(),
                                time: moment().format()
                            })
                        ]);
                        this.togglingPublic = false;
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to make ${
                                this.$router.currentRoute.params.name
                            } ${this.getAgent.public ? 'private' : 'public'}`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                        this.togglingPublic = false;
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to make ${
                            this.$router.currentRoute.params.name
                        } ${this.getAgent.public ? 'private' : 'public'}`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    throw error;
                });
        },
        cronTime(task) {
            if (
                task.crontab === null ||
                task.crontab === undefined ||
                task.crontab === 'None'
            )
                return '';
            return moment(
                parser
                    .parseExpression(task.crontab)
                    .next()
                    .toString()
            ).format('MMMM Do YYYY, h:mm a');
        },
        deleteTask(task) {
            return axios
                .get(`/apis/v1/agents/remove_task/?name=${task.name}`)
                .then(() => {
                    this.loadTarget();
                    this.alertMessage = `Deleted task ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.checkingConnection = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to delete ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.checkingConnection = false;
                    throw error;
                });
        },
        createTask(event) {
            event.preventDefault();
            axios({
                method: 'post',
                url: `/apis/v1/agents/create_task/`,
                data: {
                    name: this.createTaskForm.name,
                    agent: this.getAgent.name,
                    description: this.createTaskForm.description,
                    command: this.createTaskForm.command,
                    delay: this.createTaskForm.time
                    // delay: moment
                    //     .duration(
                    //         this.createTaskForm.timeIntervalValue,
                    //         this.createTaskForm.timeInterval
                    //     )
                    //     .asSeconds()
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    this.alertMessage =
                        response.status === 200 && response.data.created
                            ? `Created task ${this.createTaskForm.name} on ${this.getAgent.name}`
                            : response.status === 200 && !response.data.created
                            ? `Task ${this.createTaskForm.name} already exists on ${this.getAgent.name}`
                            : `Failed to create task ${this.createTaskForm.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.checkingConnection = false;
                    this.$bvModal.hide('createTask');
                    this.loadTarget();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to create task ${this.createTaskForm.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                    this.checkingConnection = false;
                    this.$bvModal.hide('createTask');
                    throw error;
                });
        },
        resetCreateTaskForm() {
            this.form = {
                name: '',
                description: '',
                command: '',
                interval: moment.duration(1, 'days')
            };
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        preCheckConnection() {
            if (this.getAgent.authentication === 'password') {
                this.$bvModal.show('authenticate');
            } else this.checkConnection();
        },
        async checkConnection() {
            this.checkingConnection = true;
            let data =
                this.getAgent.authentication === 'password'
                    ? {
                          auth: {
                              username: this.authenticationUsername,
                              password: this.authenticationPassword
                          }
                      }
                    : {
                          auth: {
                              username: this.authenticationUsername
                          }
                      };
            await axios({
                method: 'post',
                url: `/apis/v1/agents/${this.$route.params.name}/health/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200 && response.data.healthy)
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Connection to ${this.getAgent.name} succeeded`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                    else
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to connect to ${this.getAgent.name}`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                    this.checkingConnection = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect to ${this.getAgent.name}`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    this.checkingConnection = false;
                    throw error;
                });
        },
        toggleTask: function(task) {
            axios
                .get(`/apis/v1/agents/toggle_task/?name=${task.name}`)
                .then(response => {
                    this.loadTarget();
                    this.alertMessage = `${
                        response.data.enabled ? 'Enabled' : 'Disabled'
                    } task ${task.name} on ${this.getAgent.name}`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) {
                        this.alertMessage = `Failed to disable task ${task.name} on ${this.getAgent.name}`;
                        this.alertEnabled = true;
                        throw error;
                    }
                });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
