module.exports = {
  extends: ['../.eslintrc.js'],
  env: {
    jest: true,
    node: true,
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-non-null-assertion': 'off',
  },
}; 