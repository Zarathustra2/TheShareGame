// const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const os = require('os');


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
          // Disabling the parallel build is apparently not enough so we have to
          // set the amount of workers explicitly:
          //       If you use Circle CI or any other environment that doesn't provide real available
          //       count of CPUs then you need to setup explicitly number of
          //       CPUs to avoid Error: Call retries were exceeded
          //
          // See: https://github.com/webpack-contrib/terser-webpack-plugin/issues/143
          // See: https://github.com/webpack-contrib/terser-webpack-plugin/issues/202
          parallel: (!isCirleCi()) ? os.cpus().length - 1 : 1,
        }),
      ],
    },
  },
  lintOnSave: false,
};
