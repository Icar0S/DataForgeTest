module.exports = {
  jest: {
    configure: (jestConfig) => {
      jestConfig.roots = [
        '<rootDir>/src',
        '<rootDir>/../tests/frontend',
      ];
      jestConfig.testMatch = [
        '<rootDir>/../tests/frontend/**/*.test.{js,jsx,ts,tsx}',
      ];
      jestConfig.collectCoverageFrom = [
        'src/**/*.{js,jsx,ts,tsx}',
        '!src/index.js',
        '!src/reportWebVitals.js',
        '!src/**/*.test.{js,jsx,ts,tsx}',
      ];
      jestConfig.moduleNameMapper = {
        ...jestConfig.moduleNameMapper,
        '\\.(css|less|scss|sass)$': '<rootDir>/src/__mocks__/styleMock.js',
      };
      jestConfig.modulePaths = ['<rootDir>/node_modules'];
      return jestConfig;
    },
  },
};
