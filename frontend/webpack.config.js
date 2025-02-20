// const SpeedMeasurePlugin = require("speed-measure-webpack-plugin");
//
// const smp = new SpeedMeasurePlugin();

var path = require("path");

module.exports = {
    entry: "./src/index.js",
    mode: "production",
    output: {
        path: path.join(__dirname, "dist","assets"),
        filename: "bundle.js",
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules)/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["@babel/preset-env", "@babel/preset-react"],
                    },
                },
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.(png|jpg)$/i,
                use: ['url-loader?limit=1000000'],
            }
        ],
    },
    devtool : "source-map",
    resolve: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
        alias: {
          '@components': path.resolve(__dirname, 'src/components/'),
        },
      },
};