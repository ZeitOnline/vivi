import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,cjs}"],
    plugins: { js },
    extends: ["js/recommended"],
    rules: {
      "no-undef": "off"
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        ...globals.browser,
        ...globals.jquery,
        zeit: "readonly",
        gocept: "readonly",
        MochiKit: "readonly"
      }
    }
  },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
]);
