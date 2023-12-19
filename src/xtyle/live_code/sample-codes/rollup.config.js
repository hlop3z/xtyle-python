
// rollup.config.js
import fs from "fs";
import terser from "@rollup/plugin-terser";

// Read the package.json
const pkg = JSON.parse(fs.readFileSync("./package.json", "utf-8"));
const packageName = pkg.name.replace(/-/g, "_");

export default {
  input: "dist/index.js",
  output: {
    file: `dist/index.min.js`,
    format: "iife",
    name: packageName,
    plugins: [terser()],
  },
};
