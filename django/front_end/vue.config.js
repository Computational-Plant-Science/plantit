//Some Ideas: https://github.com/Plortinus/vue-multiple-pages/blob/master/vue.config.js
module.exports = {
  assetsDir: 'static',
  pages: {
    job_list: {
      entry: 'src/job_manager/job_list/main.js',
      template: 'job_list.html',
      filename: 'templates/job_manager/job_list.html',
      title: 'Jobs Page',
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    }
  }
}
