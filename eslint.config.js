const js = require("@eslint/js");
const globals = require("globals");

module.exports = [
  {
    ignores: ["core/src/zeit/crop/browser/resources/ui4w.js"],
  },
  {
    files: ["**/*.{js,cjs}"],
    plugins: { js },
    ...js.configs.recommended,
    rules: {
      "no-undef": "off",
      "no-unused-vars": "off",
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        ...globals.browser,
        ...globals.jquery,
        zeit: "readonly",
        gocept: "readonly",
        MochiKit: "readonly",
      },
    },
  },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
];
