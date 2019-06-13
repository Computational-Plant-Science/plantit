module.exports = {
    assetsDir: 'assets/',
    pluginOptions: {
        'style-resources-loader': {
            preProcessor: 'sass',
            patterns: []
        }
    },
    chainWebpack(config) {
        //Allow npm build watch to work: https://github.com/vuejs/vue-cli/issues/1120
        config.output.filename('assets/js/[name].js');
    }
};
