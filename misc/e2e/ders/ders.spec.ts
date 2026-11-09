/// <reference types="cypress" />

import { utils } from "../../../e2e-cypress-test/cypress/support/utils";

describe('Ders API', () => {
  let defaultAdminJwt;
  let testOrgId;
  let testUserJwt;
  let testUserId;


  before(() => {
    utils.login('admin@some.com', 'add_pass')
      .then(token => {
        defaultAdminJwt = token;

        utils.removeNotNeededOrganizations(defaultAdminJwt);

        utils.addOrganizaition('Test Organization', defaultAdminJwt).then(_organizationId => {
          testOrgId = _organizationId;

          utils.register(
            'test',
            'user',
            'test.user@amalgam-inc.com',
            'Testing123$',
            testOrgId,
          ).then(userId => {
            testUserId = userId;

            cy.mhGetMailsBySubject('Pearlx - Verify email request').mhFirst().mhGetBody().then(mail => {
              const parser = new DOMParser();
              const doc = parser.parseFromString(mail, 'text/html');
              const code = doc.querySelector('code').textContent;
              const token = code.match(/[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}/)[0];
              utils.verify_email('test.user@amalgam-inc.com', token);
            });
          });
        });
      }
    );
  });

  after(() => {
    utils.removeNotNeededOrganizations(defaultAdminJwt);

    cy.mhDeleteAll();
  });
  
  describe('Anonymous role', () => {
    it('Can\'t Refresh (POST) ders', () => {
      cy.request({
        method: 'POST',
        url: '/ders/refresh',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });
  });
  
  describe('Customer role', () => { 
    before(() => {
      utils.login('test.user@amalgam-inc.com', 'Testing123$').then(jwt => {
        testUserJwt  = jwt;
      });
    });

    it('Can\'t Refresh (POST) ders', () => {
      cy.request({
        method: 'POST',
        url: '/ders/refresh',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(403);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(403);
        expect(response.body.message).to.eq('Forbidden');
      });
    });
  });

  describe('Admin role', () => {
    it('Can Refresh (POST) ders', () => {
      cy.request({
        method: 'POST',
        url: '/ders/refresh',
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        const ders = response.body;
        expect(ders).to.be.a('array');
        // expect(ders).to.have.lengthOf.above(0);
      });
    });
  });
});
