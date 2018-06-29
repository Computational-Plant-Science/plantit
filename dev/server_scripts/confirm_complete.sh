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
token=${2}

./server_update sub_id $job_pk "$RANDOM" "$token"
./server_update status $job_pk 1 "Completed Confirmed" "$token"
