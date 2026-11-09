const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    specPattern: 'cypress/integration/**/*.cy.{js,ts}',
    baseUrl: 'http://localhost:5000/api/v1',
    // baseUrl: 'https://pearlx-api-2091523486.us-east-2.elb.amazonaws.com/api/v1',
    // baseUrl: 'https://pearlx-api-staging-alb-622739544.us-east-2.elb.amazonaws.com/api/v1',
  }
});
