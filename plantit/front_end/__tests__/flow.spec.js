/* eslint-disable no-undef */
import { createLocalVue, mount } from '@vue/test-utils';
import { user, users, workflows, data } from '@/store/store';
import Vuex from 'vuex';
import flow from '../src/views/flow';
import Cookies from 'js-cookie';
import axios from 'axios';

const localVue = createLocalVue();

localVue.use(Vuex);

describe('flows.vue', () => {
    it('shows invalid flow alert when flow is invalid', () => {
        const wrapper = mount(flow, {
            localVue,
            propsData: {
                username: 'Computational-Plant-Science',
                name: 'plantit-hello-world'
            },
            mocks: {
                $store: {
                    getters: {
                        csrfToken: Cookies.get(axios.defaults.xsrfCookieName),
                        darkMode: false
                    },

                }
            }
        });
        expect(wrapper.find('.flowInvalid').exists()).toBe(true);
    });
});

// const data = {
//     flow: {},
//     flowLoading: false,
//     flowValidated: false,
//     flowValidationErrors: ['Error 1', 'Error 2'],
//     params: [],
//     input: {
//         kind: '',
//         from: '',
//         pattern: ''
//     },
//     outputSpecified: false,
//     output: {
//         from: '',
//         to: '',
//         pattern: ''
//     },
//     target: {
//         name: ''
//     },
//     fields: [
//         {
//             key: 'name',
//             label: 'Name'
//         },
//         {
//             key: 'value',
//             label: 'Value'
//         }
//     ]
// };
