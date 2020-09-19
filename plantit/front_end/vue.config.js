const GoogleFontsPlugin = require('google-fonts-webpack-plugin');

module.exports = {
    assetsDir: 'assets/',
    pluginOptions: {
        'style-resources-loader': {
            preProcessor: 'sass',
            patterns: []
        },
        'google-fonts-webpack-plugin': {
            fonts: [
                { family: 'Source Sans Pro' },
                { family: 'Roboto', variants: ['400'] }
            ]
        }
    },
    chainWebpack(config) {
        //Allow npm build watch to work: https://github.com/vuejs/vue-cli/issues/1120
        config.output.filename('assets/js/[name].js');
        config.module
            .rule('raw')
            .test(/\.md$/i)
            .use('raw-loader')
            .loader('raw-loader')
            .end();
    }
};
