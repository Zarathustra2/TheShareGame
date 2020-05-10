// const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  chainWebpack(config) {
    config.plugins.delete('prefetch');

    config.plugin('CompressionPlugin').use(CompressionPlugin);
  },
  configureWebpack: {
    plugins: [
      // new BundleAnalyzerPlugin(),
    ],
  },
  lintOnSave: false,
};
