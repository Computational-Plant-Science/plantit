module.exports = {
    verbose: true,
    moduleFileExtensions: ['js', 'json', 'vue'],
    moduleNameMapper: {
        '^\\@/(.*)': '<rootDir>/src/$1',
    },
    transform: {
        '^.+\\.js$': 'babel-jest',
        '^.+\\.vue$': 'vue-jest',
    },
    collectCoverage: true,
    collectCoverageFrom: ['src/components/*.{js,vue}', '!**/node_modules/**'],
    coverageReporters: ['html', 'text-summary'],
};
