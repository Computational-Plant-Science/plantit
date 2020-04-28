#!/bin/sh

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 ~/.ssh/id_rsa # Allow read access to the private key
ssh-add ~/.ssh/id_rsa # Add the private key to SSH

#git config --global push.default matching
#git remote add deploy ssh://$SSH_USER@$SSH_HOST:$SSH_PORT$SSH_DIRECTORY
#git push deploy master

scp -r -o StrictHostKeyChecking=no -P $SSH_PORT "$SSH_USER@$SSH_HOST$SSH_DIRECTORY" $LOCAL_DIRECTORY

ssh -o StrictHostKeyChecking=no -p $SSH_PORT "$SSH_USER@$SSH_HOST" <<EOF
  cd $SSH_DIRECTORY
  chmod +x ./dev/post-deploy.ssh
  ./dev/post-deploy.sh $SSH_HOST
EOF