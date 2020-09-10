const CompressionPlugin = require("compression-webpack-plugin");
const Timestamp = new Date().getTime();

module.exports = {
  configureWebpack: {
    output: {
      filename: '[name].[hash].' + Timestamp + '.js',
      chunkFilename: '[name].[hash].' + Timestamp +'.js'
    }
  },
  configureWebpack: config => {
    if (process.env.NODE_ENV === 'production' || process.env.NODE_ENV === 'sand') {
      return {
        plugins: [
          new CompressionPlugin({
            test: /\.js$|\.html$|\.css/,
            // Compress files over 10kb
            threshold: 10240,
            deleteOriginalAssets: false
          })
        ]
      }
    }
  },
  publicPath: process.env.VUE_APP_BASE_URL,
  productionSourceMap: false
}