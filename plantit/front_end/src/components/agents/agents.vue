<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent">
        <div v-if="isRootPath">
            <b-row
                ><b-col
                    ><h2 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-server fa-fw"></i>
                        Agents
                    </h2></b-col
                >
                <b-col align-self="center" class="mb-1" md="auto">
                    <b-dropdown
                        dropleft
                        id="switch-agents-context"
                        :disabled="agentsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        class="ml-0 mt-0 mr-0"
                        :title="publicContext ? '' : ''"
                        ><template #button-content>
                            <span v-if="!publicContext"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Public</span
                            >
                        </template>
                        <b-dropdown-item @click="toggleContext"
                            ><i class="fas fa-user fa-fw"></i>
                            Yours</b-dropdown-item
                        >
                        <b-dropdown-item @click="toggleContext"
                            ><i class="fas fa-users fa-fw"></i>
                            Public</b-dropdown-item
                        >
                    </b-dropdown>
                    <b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topleft"
                        target="switch-agents-context"
                        title="Agent Context"
                        >Click here to toggle between public agents and your
                        own.</b-popover
                    >
                </b-col>
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="bind-agent"
                        :disabled="agentsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        @click="showBindAgentModal"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="agentsLoading || bindingAgent"
                            label="Connecting..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-plug mr-1"></i
                        >Connect</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="bottom"
                        target="bind-agent"
                        title="Bind Agent"
                        >Click here to connect a new agent. This can be a
                        server, cluster, supercomputer &mdash; anything you can
                        access with SSH and password or key
                        authentication.</b-popover
                    ></b-col
                >
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="refresh-agents"
                        :disabled="agentsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        title="Refresh agents"
                        @click="refreshAgents"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="agentsLoading"
                            label="Refreshing..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i
                        >Refresh</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topright"
                        target="refresh-agents"
                        title="Refresh Agents"
                        >Click here to refresh the list of agents.</b-popover
                    ></b-col
                >
            </b-row>
            <b-row v-if="agentsLoading" class="mt-2">
                <b-col>
                    <b-spinner
                        small
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading
                        {{ publicContext ? 'public' : 'your' }} agents...</span
                    >
                </b-col>
            </b-row>
            <b-card-group deck columns v-else-if="getAgents.length !== 0">
                <b-card
                    v-for="agent in getAgents"
                    v-bind:key="agent.name"
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="secondary"
                    :header-border-variant="
                        profile.darkMode ? 'secondary' : 'default'
                    "
                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                    style="min-width: 30rem"
                    class="overflow-hidden mb-4"
                >
                    <b-row style="z-index: 10">
                        <b-col cols="10">
                            <h2>
                                <b-link
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    variant="outline-dark"
                                    :to="{
                                        name: 'agent',
                                        params: {
                                            name: agent.name,
                                        },
                                    }"
                                >
                                    {{ agent.name }}
                                </b-link>
                                <small>
                                    <i
                                        v-if="agent.is_healthy"
                                        title="Healthy"
                                        class="fas fa-heartbeat text-success fa-fw"
                                    ></i
                                    ><i
                                        v-else
                                        title="Unhealthy"
                                        class="fas fa-heart-broken text-danger fa-fw"
                                    ></i
                                    ><i
                                        v-if="agent.disabled"
                                        title="Disabled"
                                        class="fas fa-exclamation-circle text-secondary fa-fw"
                                    ></i
                                ></small>
                            </h2>
                            <b-badge
                                v-if="!agent.public"
                                class="mr-1"
                                variant="warning"
                                ><i class="fas fa-lock fa-fw"></i>
                                Private</b-badge
                            >
                            <b-badge v-else variant="success" class="mr-1"
                                ><i class="fas fa-lock-open fa-fw"></i>
                                Public</b-badge
                            >
                            <b-badge
                                :variant="
                                    agent.role === 'admin'
                                        ? agent.user ===
                                          profile.djangoProfile.username
                                            ? 'success'
                                            : 'success'
                                        : 'warning'
                                "
                                >{{
                                    agent.role === 'admin'
                                        ? agent.user ===
                                          profile.djangoProfile.username
                                            ? 'Owner'
                                            : 'Admin'
                                        : 'Guest'
                                }}</b-badge
                            >

                            <br />
                            <small>
                                {{ agent.description }}
                            </small>
                            <br />
                        </b-col>
                        <b-col cols="1"></b-col>
                    </b-row>
                    <b-img
                        v-if="agent.logo"
                        rounded
                        class="card-img-right overflow-hidden"
                        style="
                            max-height: 4rem;
                            position: absolute;
                            right: 20px;
                            top: 20px;
                            z-index: 1;
                        "
                        right
                        :src="agent.logo"
                    ></b-img>
                </b-card>
            </b-card-group>
            <b-row v-else
                ><b-col
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >{{
                            publicContext
                                ? 'No public agents available.'
                                : "You haven't connected any agents yet."
                        }}</span
                    >
                    <br /> </b-col
            ></b-row>
        </div>
        <router-view
            v-else
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
        <b-modal
            id="bindAgent"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            size="lg"
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            title="Bind a new agent"
            @ok="showAuthenticateModal"
            @close="resetAgentInfo"
            :ok-disabled="!agentValid"
            ok-title="Bind"
            hide-header
            hide-footer
            hide-header-close
        >
            <b-row v-if="agentBindingStage === 'details'"
                ><b-col>
                    <b-row class="mb-2" v-if="agentBindingStage === 'details'"
                        ><b-col
                            ><h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Enter agent details
                            </h4></b-col
                        >
                    </b-row>
                    <b-alert variant="danger" :show="agentNameExists"
                        >This name is already in use. Please pick
                        another.</b-alert
                    >
                    <b-form-group>
                        <template #description
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                >A name for this agent.</span
                            ></template
                        >
                        <b-form-input
                            :class="
                                profile.darkMode ? 'input-dark' : 'input-light'
                            "
                            :state="agentNameValid"
                            v-model="agentName"
                            type="text"
                            placeholder="Enter a name"
                            required
                            @input="onAgentNameChange"
                        ></b-form-input>
                    </b-form-group>
                    <b-form-group>
                        <template #description
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                >A plain-text description of this agent.</span
                            ></template
                        >
                        <b-form-textarea
                            :class="
                                profile.darkMode ? 'input-dark' : 'input-light'
                            "
                            :state="agentDescriptionValid"
                            v-model="agentDescription"
                            placeholder="Enter a description"
                            required
                        ></b-form-textarea> </b-form-group
                    ><b-row>
                        <b-col
                            ><b-button
                                :disabled="
                                    !(agentNameValid && agentDescriptionValid)
                                "
                                block
                                variant="success"
                                @click="changeAgentBindingStage('connection')"
                                ><i class="fas fa-arrow-right fa-fw fa-1x"></i>
                                Next: Connection</b-button
                            ></b-col
                        >
                    </b-row>
                </b-col></b-row
            >
            <b-row v-if="agentBindingStage === 'connection'"
                ><b-col>
                    <b-row class="mb-2"
                        ><b-col
                            ><h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Connect to <b>{{ agentName }}</b>
                            </h4></b-col
                        >
                    </b-row>
                    <b-row v-if="agentConnectionComplete !== true">
                        <b-col>
                            <b-row
                                ><b-col>
                                    <p
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        Your agent must be reachable by SSH.
                                    </p>
                                </b-col></b-row
                            >
                            <b-row
                                ><b-col>
                                    <!--<b-alert
                                        variant="danger"
                                        :show="agentHostExists"
                                        >This host is already in use.</b-alert
                                    >-->
                                    <b-form-group>
                                        <template #description
                                            ><span
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                >This agent's FQDN or IP
                                                address.</span
                                            ></template
                                        >
                                        <b-form-input
                                            :class="
                                                profile.darkMode
                                                    ? 'input-dark'
                                                    : 'input-light'
                                            "
                                            :state="agentHostValid"
                                            v-model="agentHost"
                                            type="text"
                                            placeholder="Enter a host or IP address"
                                            required
                                        ></b-form-input>
                                    </b-form-group>
                                    <b-form-group>
                                        <template #description
                                            ><span
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                >This agent's SSH port.</span
                                            ></template
                                        >
                                        <b-form-input
                                            :class="
                                                profile.darkMode
                                                    ? 'input-dark'
                                                    : 'input-light'
                                            "
                                            :state="agentPortValid"
                                            v-model="agentPort"
                                            type="number"
                                            placeholder="Enter a port"
                                            required
                                        ></b-form-input> </b-form-group></b-col
                            ></b-row>
                            <b-row
                                ><b-col>
                                    <b-form-group>
                                        <template #description
                                            ><span
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                >Your username on this
                                                agent.</span
                                            ></template
                                        >
                                        <b-form-input
                                            :class="
                                                profile.darkMode
                                                    ? 'input-dark'
                                                    : 'input-light'
                                            "
                                            :state="agentUsernameValid"
                                            v-model="agentUsername"
                                            type="text"
                                            placeholder="Enter a username"
                                            required
                                        ></b-form-input>
                                    </b-form-group> </b-col
                            ></b-row>
                            <b-row
                                ><b-col>
                                    <b-form-group>
                                        <template #description
                                            ><span
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                >Select an authentication
                                                strategy.</span
                                            ></template
                                        >
                                        <b-form-select
                                            v-model="agentAuthentication"
                                            :options="
                                                agentAuthenticationOptions
                                            "
                                            type="text"
                                            placeholder="Select an authentication strategy"
                                            required
                                            @change="handleAuthenticationChange"
                                        ></b-form-select
                                    ></b-form-group> </b-col
                            ></b-row>
                        </b-col>
                    </b-row>
                    <b-row
                        v-if="
                            agentAuthentication === 'key' &&
                            !agentConnectionComplete
                        "
                        style="word-wrap: break-word"
                        class="mb-3 p-1"
                    >
                        <b-col>
                            <b-spinner
                                small
                                v-if="gettingKey"
                                label="Loading..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="ml-2 mb-1"
                            ></b-spinner>
                            <div v-else-if="publicKey !== ''">
                                <span
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        Here is your public key.
                                    </h5>
                                    Copy it into the
                                    <code>~/.ssh/authorized_keys</code> file on
                                    your agent, then click
                                    <b-badge
                                        size="sm"
                                        class="m-0 p-1 mr-1"
                                        disabled
                                        variant="success"
                                        ><i
                                            class="fas fa-wave-square fa-fw fa-1x"
                                        ></i>
                                        Check Connection</b-badge
                                    >
                                    to make sure your agent is reachable.
                                </span>
                                <b-form-textarea
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    plaintext
                                    :value="publicKey"
                                    max-rows="15"
                                    class="p-1"
                                ></b-form-textarea></div></b-col
                    ></b-row>
                    <b-row class="text-center mb-3 p-1"
                        ><b-col v-if="agentConnectionComplete === true"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-check fa-fw mr-1 text-success"
                                ></i
                                >Connection to {{ agentName }} succeeded!
                            </h5>
                            <b-button
                                @click="resetAgentConnection"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                ><i class="fas fa-redo fa-fw fa-1x"></i> Select
                                another authentication strategy</b-button
                            ></b-col
                        ><b-col v-else-if="agentConnectionComplete === false"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-times-circle fa-fw mr-1 text-danger"
                                ></i
                                >Connection to {{ agentName }} failed
                            </h5>
                            <small
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                v-if="agentAuthentication === 'key'"
                                >Are you sure you've copied your key to the
                                agent?</small
                            ><br /></b-col
                    ></b-row>
                    <b-row>
                        <b-col>
                            <b-button
                                block
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                @click="changeAgentBindingStage('details')"
                                ><i class="fas fa-arrow-left fa-fw fa-1x"></i>
                                Back: Details</b-button
                            ></b-col
                        >
                        <b-col v-if="!gettingKey && !agentConnectionComplete">
                            <b-button
                                :disabled="
                                    !(agentHostValid && agentUsernameValid) ||
                                    checkingConnection
                                "
                                block
                                variant="success"
                                @click="preCheckAgentConnection"
                                ><b-spinner
                                    small
                                    v-if="checkingConnection"
                                    label="Checking connection..."
                                    variant="dark"
                                    class="mr-1"
                                ></b-spinner
                                ><i
                                    v-else
                                    class="fas fa-wave-square fa-fw fa-1x"
                                ></i>
                                Check Connection</b-button
                            ></b-col
                        >
                        <b-col v-if="agentConnectionComplete">
                            <b-button
                                block
                                variant="success"
                                @click="changeAgentBindingStage('workdir')"
                                ><i class="fas fa-arrow-right fa-fw fa-1x"></i>
                                Next: Working Directory</b-button
                            ></b-col
                        >
                    </b-row>
                </b-col>
            </b-row>
            <b-row v-if="agentBindingStage === 'workdir'"
                ><b-col>
                    <b-row class="mb-2"
                        ><b-col
                            ><h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Select a working directory for agent
                                <b>{{ agentName }}</b>
                            </h4></b-col
                        >
                    </b-row>
                    <b-row v-if="agentWorkdirComplete !== true">
                        <b-col>
                            <b-row
                                ><b-col>
                                    <p
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        You must have write permissions in the
                                        chosen directory. A hidden directory
                                        named <code>.plantit</code> will be
                                        created and used to store your tasks.
                                    </p>
                                </b-col></b-row
                            ></b-col
                        ></b-row
                    >
                    <b-row v-if="agentWorkdirComplete !== true"
                        ><b-col>
                            <b-form-group>
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Enter a directory path.</span
                                    ></template
                                >
                                <b-form-input
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    v-model="agentWorkdir"
                                    type="text"
                                    placeholder="$HOME/.plantit"
                                    required
                                ></b-form-input>
                            </b-form-group> </b-col
                    ></b-row>
                    <b-row class="text-center mb-3 p-1"
                        ><b-col v-if="agentWorkdirComplete === true"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-check fa-fw mr-1 text-success"
                                ></i
                                >Created working directory!
                            </h5>
                            <b-button
                                @click="resetAgentWorkdir"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                ><i class="fas fa-redo fa-fw fa-1x"></i> Select
                                another working directory</b-button
                            ></b-col
                        ><b-col v-else-if="agentWorkdirComplete === false"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-times-circle fa-fw mr-1 text-danger"
                                ></i
                                >Failed to create working directory
                            </h5>
                            <small
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                v-if="agentAuthentication === 'key'"
                                ><span v-if="agentWorkdir !== ''"
                                    >Are you sure the directory you've selected
                                    exists? </span
                                ><span v-else
                                    >Do you have write permissions in your home
                                    directory?</span
                                ></small
                            ><br /></b-col
                    ></b-row>
                    <b-row>
                        <b-col>
                            <b-button
                                block
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                @click="changeAgentBindingStage('connection')"
                                ><i class="fas fa-arrow-left fa-fw fa-1x"></i>
                                Back: Connection</b-button
                            ></b-col
                        >
                        <b-col v-if="!gettingKey && !agentWorkdirComplete">
                            <b-button
                                :disabled="
                                    !(agentHostValid && agentUsernameValid) ||
                                    creatingWorkdir
                                "
                                block
                                variant="success"
                                @click="preCreateAgentWorkdir"
                                ><b-spinner
                                    small
                                    v-if="creatingWorkdir"
                                    label="Creating working directory..."
                                    variant="dark"
                                    class="mr-1"
                                ></b-spinner
                                ><i
                                    v-else
                                    class="fas fa-folder fa-fw fa-1x"
                                ></i>
                                Use Directory
                                <b>{{
                                    this.agentWorkdirValid
                                        ? this.agentWorkdir
                                        : '$HOME/.plantit'
                                }}</b></b-button
                            ></b-col
                        ><b-col v-if="agentWorkdirComplete">
                            <b-button
                                block
                                variant="success"
                                @click="changeAgentBindingStage('executor')"
                                ><i class="fas fa-arrow-right fa-fw fa-1x"></i>
                                Next: Executor</b-button
                            ></b-col
                        ></b-row
                    ></b-col
                ></b-row
            >
            <b-row v-if="agentBindingStage === 'executor'"
                ><b-col>
                    <b-row class="mb-2"
                        ><b-col
                            ><h4
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                Configure executor for <b>{{ agentName }}</b>
                            </h4></b-col
                        >
                    </b-row>
                    <b-row v-if="agentExecutorComplete !== true"
                        ><b-col>
                            <b-row
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    >Configure the
                                    <code>plantit-cli</code> executor for this
                                    agent.</b-col
                                ></b-row
                            >
                            <hr />
                            <b-form-group>
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Commands to run before user commands
                                        (e.g., loading modules, setting
                                        environment variables). Frequently
                                        useful but not required.</span
                                    ></template
                                >
                                <b-form-textarea
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    v-model="agentPrecommands"
                                    type="text"
                                    rows="3"
                                    :placeholder="agentPrecommands"
                                    required
                                ></b-form-textarea>
                            </b-form-group>
                            <b-form-group
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum runtime (in minutes) permitted
                                        before the workflow is aborted.</span
                                    ></template
                                ><b-form-spinbutton
                                    v-model="agentMaxTime"
                                    value="10"
                                    min="1"
                                    max="1440"
                                ></b-form-spinbutton
                            ></b-form-group>
                            <b-form-group>
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Select an executor to orchestrate
                                        workflows.</span
                                    ></template
                                >
                                <b-form-select
                                    v-model="agentExecutor"
                                    :options="agentExecutorOptions"
                                    type="text"
                                    placeholder="Select an executor"
                                    required
                                ></b-form-select
                            ></b-form-group>
                            <b-form-group v-if="isSLURM(agentExecutor)"
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Should this SLURM agent use job arrays
                                        for parallelization instead of
                                        Dask?</span
                                    ></template
                                ><b-form-checkbox
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    v-model="agentJobArray"
                                >
                                    Enable job arrays
                                </b-form-checkbox>
                            </b-form-group>
                            <b-form-group v-if="isSLURM(agentExecutor)">
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Should this SLURM agent use the TACC
                                        launcher instead of Dask?</span
                                    ></template
                                >
                                <b-form-checkbox
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    v-model="agentLauncher"
                                >
                                    Enable TACC launcher parameter sweep utility
                                    (for Dask-incompatible hosts)
                                </b-form-checkbox>
                            </b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)">
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Enter a scheduler queue to use.</span
                                    ></template
                                >
                                <b-form-input
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    v-model="agentQueue"
                                    :state="agentQueue !== ''"
                                    type="text"
                                    placeholder="Enter a queue name"
                                    required
                                ></b-form-input
                            ></b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)">
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Enter a project name or allocation
                                        number (optional on some
                                        schedulers).</span
                                    ></template
                                >
                                <b-form-input
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    v-model="agentProject"
                                    type="text"
                                    placeholder="Enter a project name"
                                    required
                                ></b-form-input
                            ></b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)"
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum walltime (in minutes) workflows
                                        can request from the agent
                                        scheduler.</span
                                    ></template
                                ><b-form-spinbutton
                                    v-model="agentMaxWalltime"
                                    value="10"
                                    min="1"
                                    max="1440"
                                ></b-form-spinbutton
                            ></b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)"
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum number of processes workflows
                                        can request from the agent
                                        scheduler.</span
                                    ></template
                                ><b-form-spinbutton
                                    v-model="agentMaxProcesses"
                                    value="1"
                                    min="1"
                                    max="100"
                                ></b-form-spinbutton
                            ></b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)">
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum number of cores workflows can
                                        request from the agent scheduler.</span
                                    ></template
                                >
                                <b-form-spinbutton
                                    v-model="agentMaxCores"
                                    value="1"
                                    min="1"
                                    max="1000"
                                ></b-form-spinbutton
                            ></b-form-group>
                            <b-form-group v-if="isJobQueue(agentExecutor)"
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum number of nodes workflows can
                                        request from the agent scheduler.</span
                                    ></template
                                ><b-form-spinbutton
                                    v-model="agentMaxNodes"
                                    value="1"
                                    min="1"
                                    max="1000"
                                ></b-form-spinbutton
                            ></b-form-group>
                            <b-form-group v-if="isSLURM(agentExecutor)"
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Does this agent have virtual
                                        memory?</span
                                    ></template
                                ><b-form-checkbox
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    v-model="agentVirtualMemory"
                                >
                                    Virtual memory
                                </b-form-checkbox>
                            </b-form-group>
                            <b-form-group
                                v-if="
                                    isJobQueue(agentExecutor) &&
                                    !agentVirtualMemory
                                "
                                ><template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >Maximum memory (in GB) workflows can
                                        request from the agent scheduler.</span
                                    ></template
                                ><b-form-spinbutton
                                    v-model="agentMaxMem"
                                    value="1"
                                    min="1"
                                    max="1000"
                                ></b-form-spinbutton
                            ></b-form-group> </b-col
                    ></b-row>
                    <b-row class="text-center mb-3 p-1"
                        ><b-col v-if="agentExecutorComplete === true"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-check fa-fw mr-1 text-success"
                                ></i
                                >Executor configured on {{ agentName }}!
                            </h5>
                            <b-button
                                @click="resetAgentExecutor"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                ><i class="fas fa-redo fa-fw fa-1x"></i>
                                Reconfigure executor</b-button
                            ></b-col
                        ><b-col v-else-if="agentExecutorComplete === false"
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    class="fas fa-times-circle fa-fw mr-1 text-danger"
                                ></i
                                >Executor check failed on {{ agentName }}
                            </h5>
                            <small
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                v-if="agentAuthentication === 'key'"
                                >Are you sure you've installed the
                                <b-link
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    href="https://github.com/Computational-Plant-Science/plantit-cli"
                                    >PlantIT CLI</b-link
                                >? You may also need to use pre-commands (e.g.,
                                to load modules).</small
                            ><br /></b-col
                    ></b-row>
                    <!--<b-row v-if="executorCheckOutput.length > 0" class="mb-3"
                        ><b-col
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            ><span
                                v-for="line in executorCheckOutput"
                                v-bind:key="line"
                                v-show="line !== undefined && line !== null"
                                >{{ line + '\n' }}</span
                            ></b-col
                        ></b-row
                    >-->
                    <b-row>
                        <b-col>
                            <b-button
                                block
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                @click="changeAgentBindingStage('workdir')"
                                ><i class="fas fa-arrow-left fa-fw fa-1x"></i>
                                Back: Working Directory</b-button
                            ></b-col
                        >
                        <b-col v-if="agentExecutorComplete !== true">
                            <b-button
                                :disabled="
                                    !agentWorkdirValid || checkingExecutor
                                "
                                block
                                variant="success"
                                @click="preCheckAgentExecutor"
                                ><b-spinner
                                    small
                                    v-if="checkingExecutor"
                                    label="Checking executor..."
                                    variant="dark"
                                    class="mr-1"
                                ></b-spinner
                                ><i
                                    v-else
                                    class="fas fa-terminal fa-fw fa-1x"
                                ></i>
                                Check Executor</b-button
                            ></b-col
                        >
                        <b-col v-if="agentExecutorComplete">
                            <b-button block variant="success" @click="bindAgent"
                                ><i class="fas fa-plug fa-fw fa-1x"></i> Bind
                                {{ agentName }}</b-button
                            ></b-col
                        >
                    </b-row></b-col
                ></b-row
            >
            <!--<template #modal-footer
                ><b-row v-if="agentValid"
                    ><b-col md="auto"
                        ><b-button
                            :disabled="bindingAgent"
                            variant="warning"
                            @click="changeAgentBindingStage('details')"
                            ><i class="fas fa-arrow-left fa-fw"></i
                            ><br />Details</b-button
                        ></b-col
                    ><b-col md="auto"
                        ><b-button
                            :disabled="bindingAgent"
                            variant="warning"
                            @click="changeAgentBindingStage('connection')"
                            ><i class="fas fa-arrow-left fa-fw"></i
                            ><br />Connection</b-button
                        ></b-col
                    ><b-col
                        ><b-button variant="success" @click="bindAgent"
                            ><i
                                v-if="!bindingAgent"
                                class="fas fa-check fa-fw"
                            ></i
                            ><b-spinner
                                small
                                v-else
                                label="Binding..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><br />Bind</b-button
                        ></b-col
                    ></b-row
                ><b-row v-else></b-row
            ></template>-->
        </b-modal>
        <b-modal
            v-if="isRootPath"
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
            :title="'Authenticate with ' + this.agentName"
            @ok="submitAuthentication"
        >
            <!--<b-form-input
                v-model="authenticationUsername"
                type="text"
                placeholder="Your username"
                required
            ></b-form-input>-->
            <b-form-group description="Enter your password.">
                <b-form-input
                    :class="profile.darkMode ? 'input-dark' : 'input-light'"
                    v-model="authenticationPassword"
                    type="password"
                    placeholder="Your password"
                    required
                ></b-form-input>
            </b-form-group>
        </b-modal>
    </b-container>
</template>

<script>
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { mapGetters } from 'vuex';
import moment from 'moment';
import { guid } from '@/utils';

export default {
    name: 'agents',
    data: function () {
        return {
            /* new agent binding stages:
              - details
              - connection
              - workdir
              - executor
              
              state transitions:
              details <-> connection <-> workdir <-> executor -> submit (if fails, start again from left)
           */
            agentBindingStage: 'details',
            agentDetailsComplete: null, // we use null to distinguish between 'incomplete' and 'failed' (false)
            agentConnectionComplete: null,
            agentWorkdirComplete: null,
            agentExecutorComplete: null,
            // new agent properties
            agentNameLoading: false,
            agentNameExists: false,
            agentName: '',
            agentHostLoading: false,
            agentHostExists: false,
            agentHost: '',
            agentPort: 22,
            agentUsername: '',
            agentDescription: '',
            agentWorkdir: '$HOME',
            agentPrecommands:
                'export LC_ALL=en_US.utf8 && export LANG=en_US.utf8',
            agentMaxTime: 60,
            agentExecutor: 'Local',
            agentExecutorOptions: [
                { value: 'Local', text: 'Local' },
                { value: 'SLURM', text: 'SLURM' },
                { value: 'PBS', text: 'PBS' },
            ],
            agentAuthentication: 'password',
            agentAuthenticationOptions: [
                { value: 'password', text: 'Password' },
                { value: 'key', text: 'Key' },
            ],
            agentQueue: '',
            agentProject: '',
            agentMaxWalltime: 60,
            agentMaxMem: 1,
            agentVirtualMemory: false,
            agentMaxCores: 1,
            agentMaxProcesses: 1,
            agentMaxNodes: 1,
            agentHeaderSkip: '',
            agentLauncher: false,
            agentJobArray: false,
            agentPublic: false,
            agentLogo: '',
            // for new agents with password auth
            authenticationUsername: '',
            authenticationPassword: '',
            // flags
            publicContext: true,
            togglingContext: false,
            bindingAgent: false,
            checkingConnection: false,
            creatingWorkdir: false,
            checkingExecutor: false,
            // public key
            publicKey: '',
            gettingKey: false,
            // misc
            executorCheckOutput: [],
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('agents', [
            'personalAgents',
            'personalAgentsLoading',
            'guestAgents',
            'publicAgents',
            'publicAgentsLoading',
        ]),
        isRootPath() {
            return this.$route.name === 'agents';
        },
        getAgents() {
            return this.publicContext
                ? this.publicAgents
                : this.personalAgents.concat(this.guestAgents);
        },
        agentsLoading() {
            return this.publicContext
                ? this.publicAgentsLoading
                : this.personalAgentsLoading;
        },
        agentNameValid() {
            return this.agentName !== '' && !this.agentNameExists;
        },
        agentDescriptionValid() {
            return this.agentDescription !== '';
        },
        agentHostValid() {
            return this.agentHost !== '';
        },
        agentPortValid() {
            return this.agentPort !== 0;
        },
        agentUsernameValid() {
            return this.agentUsername !== '';
        },
        agentWorkdirValid() {
            return this.agentWorkdir !== '';
        },
        agentExecutorValid() {
            return (
                this.agentExecutor !== 'Local' &&
                (this.agentQueue === '' ||
                    // this.agentProject === '' ||   not all SLURM configurations require this
                    this.agentMaxWalltime <= 0 ||
                    this.agentMaxProcesses <= 0 ||
                    this.agentMaxCores <= 0 ||
                    this.agentMaxNodes <= 0 ||
                    this.agentMaxMem <= 0)
            );
        },
        agentValid() {
            return (
                this.agentNameValid &&
                this.agentDescriptionValid &&
                this.agentHostValid &&
                this.agentPortValid &&
                this.agentUsernameValid &&
                this.agentWorkdirValid &&
                this.agentExecutorValid
            );
        },
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        publicContext: function (_) {
            this.refreshAgents();
        },
    },
    methods: {
        async getKey() {
            this.gettingKey = true;
            await axios
                .get(`/apis/v1/users/get_key/`)
                .then(async (response) => {
                    if (response.status === 200) {
                        this.publicKey = response.data.public_key;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Retrieved public key`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to retrieve public key`,
                            guid: guid().toString(),
                        });
                    }
                    this.gettingKey = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to retrieve public key`,
                        guid: guid().toString(),
                    });
                    this.gettingKey = false;
                    throw error;
                });
        },
        submitAuthentication() {
            if (this.agentBindingStage === 'details') return;
            else if (this.agentBindingStage === 'connection')
                this.checkAgentConnection();
            else if (this.agentBindingStage === 'workdir')
                this.createAgentWorkdir();
            else if (!this.agentExecutorComplete) this.checkAgentExecutor();
            else this.bindAgent();
        },
        changeAgentBindingStage(stage) {
            this.agentBindingStage = stage;
        },
        preCheckAgentConnection() {
            if (this.agentAuthentication === 'password')
                this.$bvModal.show('authenticate');
            else this.checkAgentConnection();
        },
        preCreateAgentWorkdir() {
            if (this.agentAuthentication === 'password')
                this.$bvModal.show('authenticate');
            else this.createAgentWorkdir();
        },
        preCheckAgentExecutor() {
            if (this.agentAuthentication === 'password')
                this.$bvModal.show('authenticate');
            else this.checkAgentExecutor();
        },
        async checkAgentConnection() {
            this.checkingConnection = true;
            let data =
                this.agentAuthentication === 'password'
                    ? {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                          password: this.authenticationPassword,
                      }
                    : {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                      };
            await axios({
                method: 'post',
                url: `/apis/v1/users/check_connection/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.success) {
                        this.agentConnectionComplete = true;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Connection to ${this.agentName} succeeded`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    } else {
                        this.agentConnectionComplete = false;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to connect to ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    }
                    this.checkingConnection = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect to ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.agentConnectionComplete = false;
                    this.checkingConnection = false;
                    throw error;
                });
        },
        async createAgentWorkdir() {
            this.creatingWorkdir = true;
            var data =
                this.agentAuthentication === 'password'
                    ? {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                          password: this.authenticationPassword,
                      }
                    : {
                          hostname: this.agentHost,
                          port: this.agentPort,
                          username: this.agentUsername,
                      };

            data['workdir'] = this.agentWorkdir;

            await axios({
                method: 'post',
                url: `/apis/v1/users/create_workdir/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        this.agentWorkdirComplete = true;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Created working directory ${response.data.workdir} on ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    } else {
                        this.agentWorkdirComplete = false;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to create working directory ${this.agentWorkdir} on ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    }
                    this.creatingWorkdir = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to create working directory ${this.agentWorkdir} on ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.agentWorkdirComplete = false;
                    this.creatingWorkdir = false;
                    throw error;
                });
        },
        async checkAgentExecutor() {
            this.checkingExecutor = true;
            var data = {
                hostname: this.agentHost,
                username: this.agentUsername,
                precommand: this.agentPrecommands,
                executor: this.agentExecutor,
                workdir: this.agentWorkdir,
            };

            if (this.agentAuthentication === 'password')
                data['password'] = this.authenticationPassword;

            await axios({
                method: 'post',
                url: `/apis/v1/users/check_executor/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200 && response.data.success) {
                        this.agentExecutorComplete = true;
                        this.executorCheckOutput = response.data.output;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Executor check succeeded on ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    } else {
                        this.agentExecutorComplete = false;
                        this.executorCheckOutput = response.data.output;
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Executor check failed on ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    }
                    this.checkingExecutor = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Executor check failed on ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.agentExecutorComplete = false;
                    this.checkingExecutor = false;
                    throw error;
                });
        },
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        toggleContext() {
            this.togglingContext = true;
            this.publicContext = !this.publicContext;
            this.togglingContext = false;
        },
        onAgentNameChange() {
            this.agentNameLoading = true;
            return axios
                .get(`/apis/v1/agents/${this.agentName}/exists/`)
                .then((response) => {
                    this.agentNameExists = response.data.exists;
                    this.agentNameLoading = false;
                    this.$emit('input', this.name);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.agentNameLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        onAgentHostChange() {
            this.agentHostLoading = true;
            return axios
                .get(`/apis/v1/agents/${this.agentHost}/host_exists/`)
                .then((response) => {
                    this.agentHostExists = response.data.exists;
                    this.agentHostLoading = false;
                    this.$emit('input', this.name);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.agentHostLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        handleAuthenticationChange() {
            if (this.agentAuthentication === 'key') {
                this.getKey();
            }
        },
        resetAgentDetails() {
            this.agentDetailsComplete = null;
            this.agentNameLoading = false;
            this.agentNameExists = false;
            this.agentName = '';
            this.agentDescription = '';
        },
        resetAgentConnection() {
            this.agentConnectionComplete = null;
            this.agentHostLoading = false;
            this.agentHostExists = false;
            this.agentHost = '';
            this.agentPort = 22;
            this.agentUsername = '';
        },
        resetAgentWorkdir() {
            this.agentWorkdirComplete = null;
            this.agentWorkdir = '$HOME';
        },
        resetAgentExecutor() {
            this.agentExecutorComplete = null;
            this.agentPrecommands =
                'export LC_ALL=en_US.utf8 && export LANG=en_US.utf8';
            this.agentMaxTime = 60;
            this.agentExecutor = 'Local';
            this.agentAuthentication = 'password';
            this.agentQueue = '';
            this.agentProject = '';
            this.agentMaxWalltime = 1;
            this.agentMaxMem = 1;
            this.agentVirtualMemory = false;
            this.agentMaxCores = 1;
            this.agentMaxProcesses = 1;
            this.agentMaxNodes = 1;
            this.agentLauncher = false;
            this.agentJobArray = false;
            this.agentPublic = false;
            this.agentLogo = '';
        },
        resetAgentInfo() {
            this.agentBindingStage = 'details';
            this.resetAgentDetails();
            this.resetAgentConnection();
            this.resetAgentWorkdir();
            this.resetAgentExecutor();
        },
        refreshAgents() {
            if (this.publicContext) this.$store.dispatch('agents/loadPublic');
            else
                this.$store.dispatch(
                    'agents/loadPersonal',
                    this.profile.djangoProfile.username
                );
            this.$store.dispatch(
                'agents/loadGuest',
                this.profile.djangoProfile.username
            );
        },
        showAuthenticateModal() {
            this.$bvModal.show('authenticate');
        },
        showBindAgentModal() {
            this.$bvModal.show('bindAgent');
        },
        hideBindAgentModal() {
            this.$bvModal.hide('bindAgent');
        },
        async bindAgent() {
            this.bindingAgent = true;
            var auth = {
                username: this.agentUsername,
                hostname: this.agentHost,
                port: this.agentPort,
            };
            if (this.agentAuthentication === 'password')
                auth['password'] = this.authenticationPassword;
            let data = {
                auth: auth,
                config: {
                    name: this.agentName,
                    description: this.agentDescription,
                    workdir: this.agentWorkdir,
                    username: this.profile.djangoProfile.username,
                    hostname: this.agentHost,
                    port: this.agentPort,
                    pre_commands: this.agentPrecommands,
                    max_time: this.agentMaxTime,
                    public: this.agentPublic,
                    logo: this.agentLogo,
                    executor: this.agentExecutor,
                    authentication: this.agentAuthentication,
                    max_walltime: this.agentMaxWalltime,
                    max_mem: this.agentVirtualMemory ? -1 : this.agentMaxMem,
                    max_cores: this.agentMaxCores,
                    max_nodes: this.agentMaxNodes,
                    queue: this.agentQueue,
                    project: this.agentProject,
                    header_skip: this.agentHeaderSkip,
                    // gpu: this.agentGPU,
                    // gpu_queue: this.agentGPUQueue,
                    job_array: this.agentJobArray,
                    launcher: this.agentLauncher,
                },
            };

            await axios({
                method: 'post',
                url: `/apis/v1/agents/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    this.publicContext = false;
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'agents/addOrUpdate',
                                response.data.agent
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Created binding for agent ${response.data.agent.name}`,
                                guid: guid().toString(),
                                time: moment().format(),
                            }),
                        ]);
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to bind agent ${this.agentName}`,
                            guid: guid().toString(),
                            time: moment().format(),
                        });
                    }
                    this.resetAgentInfo();
                    this.hideBindAgentModal();
                    this.bindingAgent = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to bind agent ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    this.hideBindAgentModal();
                    this.bindingAgent = false;
                    throw error;
                });
        },
        isJobQueue(executor) {
            return executor !== 'Local';
        },
        isSLURM(executor) {
            return executor === 'SLURM';
        },
    },
};
</script>

<style scoped></style>
