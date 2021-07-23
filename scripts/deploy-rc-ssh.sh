#!/bin/bash

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

echo "Running deploy script..."
echo "SSH Host: $RC_SSH_HOST"
echo "Web Host: $RC_HOST"
echo "Port: $RC_PORT"
echo "User: $RC_USER"
echo "Email: $RC_EMAIL"
echo "Directory: $RC_DIRECTORY"
ssh -o StrictHostKeyChecking=no -p $RC_PORT "$RC_USER@$RC_SSH_HOST" <<EOF
  cd $RC_DIRECTORY
  chmod +x scripts/deploy-rc.sh
  scripts/deploy-rc.sh $RC_HOST $RC_EMAIL
EOF