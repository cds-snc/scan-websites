module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "jest", "security"],
  env: {
    "jest/globals": true,
  },
  extends: [
    "standard",
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "plugin:security/recommended",
    "prettier",
  ],
  rules: {
    "import/no-unresolved": "off",
    "security/detect-non-literal-fs-filename": "off",
    "@typescript-eslint/no-empty-interface": "off",
  },
};
