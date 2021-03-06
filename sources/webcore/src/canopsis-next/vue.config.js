module.exports = {
  baseUrl: process.env.NODE_ENV === 'production' ? '/en/static/canopsis-next/dist/' : '/',
  lintOnSave: false,
  chainWebpack: (config) => {
    config.resolve.alias.store.set('handlebars', 'handlebars/dist/handlebars.js');

    return config;
  },
  devServer: {
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_HOST,
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
        secure: false,
        cookieDomainRewrite: '',
      },
    },
  },
};
