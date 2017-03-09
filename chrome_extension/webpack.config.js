var webpack = require("webpack"),
    path = require("path"),
    fileSystem = require("fs"),
    env = require("./utils/env"),
    HtmlWebpackPlugin = require("html-webpack-plugin"),
    WriteFilePlugin = require("write-file-webpack-plugin"),
    CopyWebpackPlugin = require('copy-webpack-plugin');
// load the secrets
var alias = {};

var secretsPath = path.join(__dirname, ("secrets." + env.NODE_ENV + ".js"));

if (fileSystem.existsSync(secretsPath)) {
    alias["secrets"] = secretsPath;
}

module.exports = {
    entry: {
        popup: path.join(__dirname, "src", "js", "popup.js"),
        main: path.join(__dirname, "src", "js", "main.js")
    },
    output: {
        path: path.join(__dirname, "build"),
        filename: "[name].bundle.js"
    },
    module: {
        rules: [
            {test: /\.js$/, loader: "babel-loader"},
            {test: /\.css$/, loader: "style-loader!css-loader"}
        ]
    },
    resolve: {
        alias: alias
    },
    plugins: [
        // expose and write the allowed env vars on the compiled bundle
        new webpack.DefinePlugin({
            "process.env.NODE_ENV": JSON.stringify(env.NODE_ENV)
        }),
        new HtmlWebpackPlugin({
            template: path.join(__dirname, "src", "popup.html"),
            filename: "popup.html",
            chunks: ["popup"]
        }),
        new WriteFilePlugin(),
        new CopyWebpackPlugin([
            //icon
            {from: 'src/icon.ico'},
        ])
    ]
};