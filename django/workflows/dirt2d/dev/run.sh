set -e

job_pk=${1}
task_pk=${2}
token=${3}
params=${4:-}

WORKFLOW_SHARED_DIR="$(pwd)/../"
mkdir -p $WORKFLOW_SHARED_DIR
export SINGULARITY_CACHEDIR=$WORKFLOW_SHARED_DIR

reportErrors() {
  # Usage: reportErrors cmd
  #
  # Runs command cmd. If exit code of cmd is not 0, the cmd output
  # is reported to the server, the job is marked as failed, and the script exits
  #
  cmnd="$@"

  res=$( { eval $cmnd; } 2>&1)
  ret_code=$?

  if [ $ret_code != 0 ]; then
    MSG="Error when trying to run: $cmd: [$ret_code] $res"
    echo "$MSG" > error.log
    ./server_update status "$job_pk" FAILED "Unable to execute commands on cluster." "$token"
    exit $ret_code
  fi
}

execute() {
  #
  # Wraps command execution with reproting to the server
  #
  ./server_update status "$job_pk" OK "Running" "$token"

  reportErrors "$@" &&

  ./server_update task_complete "$job_pk" "$task_pk" "$token"
}

execute singularity run \
  --containall --home `pwd` \
  shub://cottersci/DIRT2_Workflows:dirt2d \
  --in="files/*" \
  --traits="`pwd`/traits.csv" \
  $params
