FROM node
RUN mkdir /app
WORKDIR /app
COPY dockerfiles/slackin/package.json yarn.lock ./
RUN yarn install
COPY dockerfiles/slackin/index.js dockerfiles/slackin/redirect.js ./
CMD node index.js
EXPOSE 3001