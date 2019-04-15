//Some Ideas: https://github.com/Plortinus/vue-multiple-pages/blob/master/vue.config.js
module.exports = {
  assetsDir: 'static',
  pages: {
    job_list: {
      entry: 'src/job_manager/job_list/main.js',
      template: 'src/job_manager/job_list/job_list.html',
      inject: false,
      filename: 'templates/job_manager/job_list.html',
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    },
    add_files: {
      entry: 'src/collection/add_files/main.js',
      template: 'src/collection/add_files/add_files.html',
      filename: 'templates/collection/add_files.html',
      chunks: ['chunk-vendors', 'chunk-common', 'add_files'],
      inject: false
    },
    collection_list: {
      entry: 'src/collection/collection_list/main.js',
      template: 'src/collection/collection_list/collection_list.html',
      filename: 'templates/collection/collection_list.html',
      chunks: ['chunk-vendors', 'chunk-common', 'collection_list'],
      inject: false
    }
  },
}
