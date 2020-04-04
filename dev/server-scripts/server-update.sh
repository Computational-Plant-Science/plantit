#!/usr/bin/env bash

#
# Script to interact with the DIRT2 Webserver via the REST API
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

# Set magic variables for current file & dir
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .sh)"
__root="$(cd "$(dirname "${__dir}")" && pwd)" # <-- change this as it depends on your app

function rest_command {
  # rest_command json job_pk token
  #
  # Submit a json paket to the server

  API_URL="172.19.211.159:80/jobs/api"
  JSON="${1}"
  JOB_PK=${2}
  TOKEN="${3:-}"

  URL="$API_URL/jobs/$JOB_PK/"
  RESULT=$((curl -Lsi -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" -X PATCH -d "$JSON" "$URL" 2>&1) )
  RESULT_CODE=$?

  #Check for cURL errors
  if [ !RESULT_CODE == 1 ]; then
    echo "FAILED WITH cURL MESSAGE:"
    echo "     $RESULT"
    exit 1
  fi

  #Extract header and body from curl results

  head=true
  while IFS= read -r line; do
      if $head; then
          if [[ $line = $'\r' ]]; then
              head=false
          else
              HEADERS+=("$line")
          fi
      else
          BODY+=("$line")
      fi
  done < <(echo "$RESULT")

  #Check for server errors
  success_str_contains="200 OK"
  if [[ $HEADERS =~ $success_str_contains ]]; then
    echo "Success";
  else
    echo "FAILED WITH SERVER MESSAGE:"
    printf "        %s\n" "${BODY[@]}"
    exit 1
  fi
}

function update_status {
  if [ "$#" -lt 4 ]; then
    echo "    Update the stats of the job"
    echo "    Usage: status job_id state desc token"
    echo "       job_id     the server assigned job id"
    echo "       state      job state (WARN, OK, FAILED)"
    echo "       desc       description explaining why the state was updated"
    echo "       token      authentication token provided by the webserver"
    exit 1
  fi

  JOB_PK=${2}
  STATE_STR="${3}"
  DESC="${4}"
  TOKEN="${5:-}"
  DATE_TIME=$(date +%Y-%m-%dT%H:%M:%S)

  case $STATE_STR in
    "OK")
        STATE=3
        ;;
    "WARN")
        STATE=4
        ;;
    "FAILED")
        STATE=2
        ;;
    *)
        echo "ERROR: job state not one of WARN, OK, FAILED"
        exit 1
  esac
  
  JSON="{
      \"submission_id\": \"\",
      \"task_set\": [],
      \"status_set\": [
          {
              \"state\": $STATE,
              \"date\": \"$DATE_TIME\",
              \"description\": \"$DESC\"
          }
      ]
  }"

  rest_command "$JSON" $JOB_PK "$TOKEN"
}

function task_complete {
  if [ "$#" -lt 4 ]; then
    echo "    Mark a task within a job complete"
    echo "    Usage: status job_id state desc token"
    echo "       job_id     the server assigned job id"
    echo "       task_id    the server assigned task id"
    echo "       token      authentication token provided by the webserver"
    exit 1
  fi

  JOB_PK=${2}
  TASK="${3}"
  TOKEN="${4:-}"
  JSON="{
      \"submission_id\": \"\",
      \"task_set\": [
          {
              \"pk\": $TASK,
              \"complete\": \"true\"
          }
      ],
      \"status_set\": []
  }"

  rest_command "$JSON" $JOB_PK "$TOKEN"
}

function update_sub_id {
  if [ "$#" -lt 3 ]; then
      echo "   Set the submission id of the job. This is the id assigned by the"
      echo "    cluster and is passsed to the server cancel script."
      echo "   Usage: submission_id job_id submission_id token"
      echo "       job_id        the server assigned job id"
      echo "       submission_id the submission id"
      echo "       token          authentication token provided by the webserver"
      exit 1
  fi

  JOB_PK=${2}
  SUB_ID="${3}"
  TOKEN="${4:-}"
  DATE_TIME=$(date +%Y-%m-%dT%H:%M:%S)
  JSON="{
    \"submission_id\": "$SUB_ID",
    \"task_set\": [],
    \"status_set\": []
  }"

  rest_command "$JSON" $JOB_PK "$TOKEN"
}

function help {
  echo "Usage: update_server.sh command [args]"
  echo "    Uses DIRT2 webserver REST API to update the status the given job"
  echo ""
  echo "Commands:"
  echo "  status:"
  echo "    Update the stats of the job"
  echo "    Usage: status job_id state desc token"
  echo "       job_id     the server assigned job id"
  echo "       state      state intiger to update the job to"
  echo "       desc       description explaining why the state was updated"
  echo "       token      authentication token provided by the webserver"
  echo ""
  echo "  sub_id:"
  echo "   Set the submission id of the job. This is the id assigned by the"
  echo "    cluster and is passsed to the server cancel script."
  echo "   Usage: submission_id job_id submission_id token"
  echo "       job_id        the server assigned job id"
  echo "       submission_id the submission id"
  echo "       token          authentication token provided by the webserver"
  echo ""
  echo " task_complete:"
  echo "    Mark a task within a job complete"
  echo "    Usage: status job_id state desc token"
  echo "       job_id     the server assigned job id"
  echo "       task_id    the server assigned task id"
  echo "       token      authentication token provided by the webserver"
}

function main {
  if [ "$#" -eq 0 ]; then
      help
      exit 1
  fi

  COMMAND=${1}
  case $COMMAND in
    status)
      update_status "$@"
      ;;
    sub_id)
      update_sub_id "$@"
      ;;
    task_complete)
      task_complete "$@"
      ;;
    help)
      help
      exit 0
      ;;
    *)
      help
      exit 1
      ;;
  esac
}

main "$@"