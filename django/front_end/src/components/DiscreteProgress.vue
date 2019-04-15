<template>
    <div class="discrete-progress-bar">
        <div v-for="task in tasks" class="section">
            <div v-if="task.complete" class="progress complete">
                <i class="fas fa-check"></i>
            </div>
            <div v-else class="progress queued"></div>
            <span v-if="showName">{{ task.name }}</span>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DiscreteProgress',
    props: {
        tasks: {
            // tasks: An array of objects that make up the sections in the
            // progress bar. One object per section:
            // tasks:[
            //        {
            //          complete: false //is the task complete
            //          name: "Task name" //name of the tasks
            //         },
            //         ..., {complete: true, name: "other Task"}
            //        ]
            type: Array,
            required: true
        },
        showName:{
          //Show the name of the task under each progress section
          type: Boolean,
          require: false,
          default: true
        }
    }
};
</script>

<style scoped>
.discrete-progress-bar {
    display: inline-flex;
    width: 100%;
    justify-content: center;
}

.discrete-progress-bar .section {
    flex-grow: 1;
    width: 1px;
}

.discrete-progress-bar .progress {
    border-radius: 0;
    border-right: 2px solid gray;
    text-align: center;
}

.discrete-progress-bar .progress i {
    display: inline-block;
    font-size: 100%;
    width: 100%;
    height: 100%;
    text-align: center;
    vertical-align: center;
    color: $color-highlight;
}

.discrete-progress-bar div:first-child .progress {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}

.discrete-progress-bar div:last-child .progress {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    border-right: 0;
}
.discrete-progress-bar .complete {
    background-color: #303030;
}

.discrete-progress-bar .queued {
    background-color: #d3f74f;
}
</style>
