#!/bin/sh


# This block may be omitted if not packaging a repository with cron schedules
####################################################################################################
# see: https://unix.stackexchange.com/a/453053 - fixes inflated hard link count
touch /etc/crontab /etc/cron.*/*

service cron start

# Add all schedules
dagster schedule up -y plantit/jobs/dagster/repository.yaml

# Restart previously running schedules
dagster schedule restart -y plantit/jobs/dagster/repository.yaml --restart-all-running
####################################################################################################

dagit -y plantit/jobs/dagster/repository.yaml -h 0.0.0.0 -p 3000