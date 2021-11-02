module.exports = {
  preset: "ts-jest/presets/js-with-babel",
  clearMocks: true,
  testEnvironment: "node",
  roots: ["<rootDir>/src/"],
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
  },
};
