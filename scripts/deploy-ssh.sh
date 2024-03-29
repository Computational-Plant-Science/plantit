#!/bin/bash

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

echo "Deploying $CONFIG"
ssh -v -o StrictHostKeyChecking=no -p $PORT -i $SSH_KEY_PATH "$USER@$SSH_HOST" <<EOF
  cd $DIRECTORY
  chmod +x scripts/deploy.sh
  scripts/deploy.sh $CONFIG $HOST $EMAIL
EOF