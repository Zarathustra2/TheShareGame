// const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');


const isCirleCi = () => {
  const { VUE_APP_CIRLCE_CI } = process.env;
  if (!VUE_APP_CIRLCE_CI) {
    return false;
  }
  return JSON.parse(VUE_APP_CIRLCE_CI.toLowerCase());
};

console.log(`Running on circleCI: ${isCirleCi()}`);

module.exports = {
  chainWebpack(config) {
    config.plugins.delete('prefetch');

    config.plugin('CompressionPlugin').use(CompressionPlugin);
  },
  configureWebpack: {
    plugins: [
      // new BundleAnalyzerPlugin(),
    ],
    optimization: {
      minimize: true,
      minimizer: [
        new TerserPlugin({
          // CirleCI has a memory problem when building the frontend.
          //
          // So we disable the parallel build, if we run on CircleCI.
          //
          // See: https://github.com/webpack-contrib/terser-webpack-plugin/issues/143
          // See: https://github.com/webpack-contrib/terser-webpack-plugin/issues/202
          parallel: !isCirleCi(),
        }),
      ],
    },
  },
  lintOnSave: false,
};
