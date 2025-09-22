import js from "@eslint/js";
import globals from "globals";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["core/src/zeit/crop/browser/resources/ui4w.js"]),
  {
    files: ["**/*.{js,cjs}"],
    plugins: { js },
    extends: ["js/recommended"],
    rules: {
      "no-undef": "off",
      "no-unused-vars": "off"
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
