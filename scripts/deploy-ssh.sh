#!/bin/bash

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

echo "Running deploy script..."
ssh -o StrictHostKeyChecking=no -p $SSH_PORT "$SSH_USER@$SSH_HOST" <<EOF
  cd $SSH_DIRECTORY
  chmod +x scripts/deploy.sh
  scripts/deploy.sh $SSH_HOST $EMAIL
EOF