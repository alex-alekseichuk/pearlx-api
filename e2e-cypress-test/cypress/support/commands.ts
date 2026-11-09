/// <reference types="cypress" />
import 'cypress-mailhog';


Cypress.Commands.add('dataCy', (value: string) => {
  return cy.get(`[data-cy=${value}]`);
});
