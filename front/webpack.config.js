const webpack = require('webpack');
const HtmlWebPackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const AntdDayjsWebpackPlugin = require('antd-dayjs-webpack-plugin');
const path = require('path');

const ROOT_PATH = path.resolve(__dirname, '../');
const APP_PATH = path.resolve(ROOT_PATH, 'front/src');
const BUILD_PATH = path.resolve(ROOT_PATH, 'back/web/static');

module.exports = (env, arg) => {
  const config = {
    mode: arg.mode === 'production' ? 'production' : 'development',
    devtool:
      arg.mode === 'production' ? 'hidden-source-map' : 'inline-source-map',
    optimization:
      arg.mode !== 'production'
        ? {}
        : {
            minimize: true,
            minimizer: [
              new TerserPlugin({
                extractComments: false,
                terserOptions: {
                  compress: {
                    drop_console: false,
                  },
                },
              }),
            ],
            splitChunks: {
              chunks: 'all',
            },
          },
    entry: {
      vendors: ['@babel/polyfill', 'react', 'react-dom'],
      app: path.resolve(APP_PATH, 'index.jsx'),
    },
    output: {
      path: BUILD_PATH,
      publicPath: '/',
      filename: 'js/[name].[chunkhash].js',
    },
    cache: { type: 'filesystem' },
    resolve: {
      extensions: ['.js', '.jsx'],
      fallback: {
        fs: false,
        path: false,
        stream: require.resolve('stream-browserify'),
      },
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: ['babel-loader', 'eslint-loader'],
        },
        {
          test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/, /\.svg$/],
          use: [
            {
              loader: 'url-loader',
              options: {
                limit: 10000,
                name: 'static/media/[name].[chunkhash].[ext]',
              },
            },
          ],
        },
        {
          test: /\.(sa|sc|c)ss$/,
          use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
        },
        {
          // write files under 10k to inline or copy files over 10k
          test: /\.woff2$/,
          use: [
            {
              loader: 'url-loader',
              options: {
                limit: 10000,
                fallback: 'file-loader',
                name: 'fonts/[name].[ext]',
              },
            },
          ],
        },
      ],
    },
    devServer: {
      contentBase: BUILD_PATH,
      inline: true,
      hot: true,
      proxy: {
        '/api': 'http://localhost:5000',
      },
      historyApiFallback: true,
      //open: 'chrome',
    },
    plugins: [
      /*
			new webpack.LoaderOptionsPlugin({
				// minimize: true,
			}),
			new webpack.optimize.ModuleConcatenationPlugin(),
			new webpack.DefinePlugin({
				"process.env.NODE_ENV": JSON.stringify("production")
			}),
			new webpack.optimize.UglifyJsPlugin({
				sourceMap: true,
				compress: {
					warnings: true,
				}
			}),
			*/
      new CleanWebpackPlugin(),
      new AntdDayjsWebpackPlugin(),
      new MiniCssExtractPlugin({ filename: 'css/[name].[fullhash].css' }),
      new CopyPlugin({
        patterns: [
          { from: path.resolve(APP_PATH, 'static/not_support.svg'), to: './' },
        ],
      }),
      new HtmlWebPackPlugin({
        template: path.resolve(APP_PATH, 'static/index.html'),
        filename: path.resolve(BUILD_PATH, 'index.html'),
        favicon: path.resolve(APP_PATH, 'static/favicon.ico'),
        inject: 'true',
        attributes: {
          charset: 'UTF-8',
        },
      }),
      new HtmlWebPackPlugin({
        template: path.resolve(APP_PATH, 'static/notsupport.html'),
        filename: path.resolve(BUILD_PATH, 'notsupport.html'),
        favicon: path.resolve(APP_PATH, 'static/favicon.ico'),
        inject: 'true',
        attributes: {
          charset: 'UTF-8',
        },
      }),
    ],
  };

  return config;
};
