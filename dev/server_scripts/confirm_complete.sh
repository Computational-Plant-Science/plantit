##
# A exmaple executor submission script.
#
# When called it sets the submission id and the status of the job to Completed
#
# Depnds on:
#   update_status.sh
#
##
job_pk=${1}
task_pk=${2}
token=${3}

./server_update sub_id $job_pk "$RANDOM" "$token"
./server_update task_complete $job_pk $task_pk "$token"
