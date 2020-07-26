#!/bin/bash

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

echo "Copying files to deployment target..."
scp -o StrictHostKeyChecking=no -rp -P $SSH_PORT plantit "$SSH_USER@$SSH_HOST:$SSH_DIRECTORY"
scp -o StrictHostKeyChecking=no -rp -P $SSH_PORT config "$SSH_USER@$SSH_HOST:$SSH_DIRECTORY"
scp -o StrictHostKeyChecking=no -P $SSH_PORT docker-compose.prod.yml "$SSH_USER@$SSH_HOST:$SSH_DIRECTORY/docker-compose.prod.yml"
scp -o StrictHostKeyChecking=no -P $SSH_PORT dev/deploy.sh "$SSH_USER@$SSH_HOST:$SSH_DIRECTORY/deploy.sh"

echo "Running deploy script..."
ssh -o StrictHostKeyChecking=no -p $SSH_PORT "$SSH_USER@$SSH_HOST" <<EOF
  cd $SSH_DIRECTORY
  chmod +x ./deploy.sh
  ./deploy.sh $SSH_HOST
EOF