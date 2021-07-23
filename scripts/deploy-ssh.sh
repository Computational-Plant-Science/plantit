#!/bin/bash

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

echo "Deploying production"
ssh -o StrictHostKeyChecking=no -p $PORT "$USER@$SSH_HOST" <<EOF
  cd $DIRECTORY
  chmod +x scripts/deploy.sh
  scripts/deploy.sh $HOST $EMAIL
EOF