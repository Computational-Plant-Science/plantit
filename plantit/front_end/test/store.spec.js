// mutations.spec.js
// import { describe, it } from 'mocha';
// import { expect } from 'chai';
// import { users, workflows } from '@/store';

const mocha = require('mocha');
const chai = require('chai');
const store = require('@/store');
// const sinon = require('sinon');

mocha.describe('users.mutations', () => {
    mocha.it('setUser', () => {
        const state = {
            user: 0,
            userGitHubProfile: null,
            users: [],
            darkMode: false
        };
        const test_user = {
            username: 'wbonelli',
            email: 'wbonelli@uga.edu'
        };
        store.users.mutations.setUser(state, test_user);
        chai.expect(state.user).to.equal(test_user);
    });
});

mocha.describe('workflows.mutations', () => {
    mocha.it('setWorkflows', () => {
        const state = {
            workflows: []
        };
        const test_workflows = [
            {
                id: 276718317,
                node_id: 'MDEwOlJlcG9zaXRvcnkyNzY3MTgzMTc=',
                name: 'plantit-examples-hello-shell',
                full_name:
                    'Computational-Plant-Science/plantit-examples-hello-shell',
                private: false,
                owner: {
                    login: 'Computational-Plant-Science',
                    id: 22278194,
                    node_id: 'MDEyOk9yZ2FuaXphdGlvbjIyMjc4MTk0',
                    avatar_url:
                        'https://avatars3.githubusercontent.com/u/22278194?v=4',
                    gravatar_id: '',
                    url:
                        'https://api.github.com/users/Computational-Plant-Science',
                    html_url: 'https://github.com/Computational-Plant-Science',
                    followers_url:
                        'https://api.github.com/users/Computational-Plant-Science/followers',
                    following_url:
                        'https://api.github.com/users/Computational-Plant-Science/following{/other_user}',
                    gists_url:
                        'https://api.github.com/users/Computational-Plant-Science/gists{/gist_id}',
                    starred_url:
                        'https://api.github.com/users/Computational-Plant-Science/starred{/owner}{/repo}',
                    subscriptions_url:
                        'https://api.github.com/users/Computational-Plant-Science/subscriptions',
                    organizations_url:
                        'https://api.github.com/users/Computational-Plant-Science/orgs',
                    repos_url:
                        'https://api.github.com/users/Computational-Plant-Science/repos',
                    events_url:
                        'https://api.github.com/users/Computational-Plant-Science/events{/privacy}',
                    received_events_url:
                        'https://api.github.com/users/Computational-Plant-Science/received_events',
                    type: 'Organization',
                    site_admin: false
                },
                html_url:
                    'https://github.com/Computational-Plant-Science/plantit-examples-hello-shell',
                description: 'A simple shell workflow.',
                fork: false,
                url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell',
                forks_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/forks',
                keys_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/keys{/key_id}',
                collaborators_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/collaborators{/collaborator}',
                teams_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/teams',
                hooks_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/hooks',
                issue_events_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/issues/events{/number}',
                events_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/events',
                assignees_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/assignees{/user}',
                branches_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/branches{/branch}',
                tags_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/tags',
                blobs_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/git/blobs{/sha}',
                git_tags_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/git/tags{/sha}',
                git_refs_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/git/refs{/sha}',
                trees_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/git/trees{/sha}',
                statuses_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/statuses/{sha}',
                languages_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/languages',
                stargazers_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/stargazers',
                contributors_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/contributors',
                subscribers_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/subscribers',
                subscription_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/subscription',
                commits_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/commits{/sha}',
                git_commits_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/git/commits{/sha}',
                comments_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/comments{/number}',
                issue_comment_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/issues/comments{/number}',
                contents_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/contents/{+path}',
                compare_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/compare/{base}...{head}',
                merges_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/merges',
                archive_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/{archive_format}{/ref}',
                downloads_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/downloads',
                issues_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/issues{/number}',
                pulls_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/pulls{/number}',
                milestones_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/milestones{/number}',
                notifications_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/notifications{?since,all,participating}',
                labels_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/labels{/name}',
                releases_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/releases{/id}',
                deployments_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-shell/deployments'
            },
            {
                id: 276748680,
                node_id: 'MDEwOlJlcG9zaXRvcnkyNzY3NDg2ODA=',
                name: 'plantit-examples-hello-python',
                full_name:
                    'Computational-Plant-Science/plantit-examples-hello-python',
                private: false,
                owner: {
                    login: 'Computational-Plant-Science',
                    id: 22278194,
                    node_id: 'MDEyOk9yZ2FuaXphdGlvbjIyMjc4MTk0',
                    avatar_url:
                        'https://avatars3.githubusercontent.com/u/22278194?v=4',
                    gravatar_id: '',
                    url:
                        'https://api.github.com/users/Computational-Plant-Science',
                    html_url: 'https://github.com/Computational-Plant-Science',
                    followers_url:
                        'https://api.github.com/users/Computational-Plant-Science/followers',
                    following_url:
                        'https://api.github.com/users/Computational-Plant-Science/following{/other_user}',
                    gists_url:
                        'https://api.github.com/users/Computational-Plant-Science/gists{/gist_id}',
                    starred_url:
                        'https://api.github.com/users/Computational-Plant-Science/starred{/owner}{/repo}',
                    subscriptions_url:
                        'https://api.github.com/users/Computational-Plant-Science/subscriptions',
                    organizations_url:
                        'https://api.github.com/users/Computational-Plant-Science/orgs',
                    repos_url:
                        'https://api.github.com/users/Computational-Plant-Science/repos',
                    events_url:
                        'https://api.github.com/users/Computational-Plant-Science/events{/privacy}',
                    received_events_url:
                        'https://api.github.com/users/Computational-Plant-Science/received_events',
                    type: 'Organization',
                    site_admin: false
                },
                html_url:
                    'https://github.com/Computational-Plant-Science/plantit-examples-hello-python',
                description: 'A simple Python workflow.',
                fork: false,
                url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python',
                forks_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/forks',
                keys_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/keys{/key_id}',
                collaborators_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/collaborators{/collaborator}',
                teams_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/teams',
                hooks_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/hooks',
                issue_events_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/issues/events{/number}',
                events_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/events',
                assignees_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/assignees{/user}',
                branches_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/branches{/branch}',
                tags_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/tags',
                blobs_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/git/blobs{/sha}',
                git_tags_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/git/tags{/sha}',
                git_refs_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/git/refs{/sha}',
                trees_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/git/trees{/sha}',
                statuses_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/statuses/{sha}',
                languages_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/languages',
                stargazers_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/stargazers',
                contributors_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/contributors',
                subscribers_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/subscribers',
                subscription_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/subscription',
                commits_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/commits{/sha}',
                git_commits_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/git/commits{/sha}',
                comments_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/comments{/number}',
                issue_comment_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/issues/comments{/number}',
                contents_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/contents/{+path}',
                compare_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/compare/{base}...{head}',
                merges_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/merges',
                archive_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/{archive_format}{/ref}',
                downloads_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/downloads',
                issues_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/issues{/number}',
                pulls_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/pulls{/number}',
                milestones_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/milestones{/number}',
                notifications_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/notifications{?since,all,participating}',
                labels_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/labels{/name}',
                releases_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/releases{/id}',
                deployments_url:
                    'https://api.github.com/repos/Computational-Plant-Science/plantit-examples-hello-python/deployments'
            }
        ];
        store.workflows.mutations.setWorkflows(state, test_workflows);
        chai.expect(state.workflows).to.equal(test_workflows);
    });
});
