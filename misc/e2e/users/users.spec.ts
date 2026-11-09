/// <reference types="cypress" />

import { utils } from "../../../e2e-cypress-test/cypress/support/utils";

describe('Users API', () => {
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
    it('Can\'t Create (POST) an user', () => {
      cy.request({
        method: 'POST',
        url: '/users',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(405);
        utils.checkResponseHeaders(response);
        // expect(response.body.status).to.eq(405);
        expect(response.body.message).to.eq('The method is not allowed for the requested URL.');
      });
    });

    it('Can\'t Read (GET) all user', () => {
      cy.request({
        method: 'GET',
        url: '/users',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });

    it('Can\'t Read (GET) a single user', () => {
      cy.request({
        method: 'GET',
        url: '/users/some-user-id',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });

    it('Can\'t update (PATCH) a single user', () => {
      cy.request({
        method: 'PATCH',
        url: '/users/some-user-id',
        body: {
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });

    it('Can\'t Delete (DELETE) a user', () => {
      cy.request({
        method: 'DELETE',
        url: '/users/some-user-id',
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

    it('Can\'t Create (POST) an user', () => {
      cy.request({
        method: 'POST',
        url: '/users',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(405);
        utils.checkResponseHeaders(response);
        // expect(response.body.status).to.eq(405);
        expect(response.body.message).to.eq('The method is not allowed for the requested URL.');
      });
    });

    it('Can\'t Read (GET) all user', () => {
      cy.request({
        method: 'GET',
        url: '/users',
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

    it('Can Read (GET) a single user', () => {
      cy.request({
        method: 'GET',
        url: `/users/${testUserId}`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can update (PATCH) a single user', () => {
      cy.request({
        method: 'PATCH',
        url: `/users/${testUserId}`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          firstname: 'first',
          lastname: 'last',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Delete (DELETE) a user', () => {
      cy.request({
        method: 'DELETE',
        url: `/users/${testUserId}`,
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
    it('Can\'t Create (POST) an user', () => {
      cy.request({
        method: 'POST',
        url: '/users',
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(405);
        utils.checkResponseHeaders(response);
        // expect(response.body.status).to.eq(405);
        expect(response.body.message).to.eq('The method is not allowed for the requested URL.');
      });
    });

    it('Can Read (GET) all users', () => {
      cy.request({
        method: 'GET',
        url: '/users',
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const users = response.body;
        expect(users).to.be.a('array');
        expect(users).to.have.lengthOf.above(0);

        users.forEach(user => {
          console.log(`Found user id=${user.id} name=${user.firstname} ${user.lastname}`)
        });
      });
    });

    it('Can Read (GET) a single user', () => {
      cy.request({
        method: 'GET',
        url: `/users/${testUserId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can update (PATCH) a single user', () => {
      cy.request({
        method: 'PATCH',
        url: `/users/${testUserId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        body: {
          firstname: 'first',
          lastname: 'last',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can enable/disable (POST) a single user', () => {
      cy.request({
        method: 'POST',
        url: `/users/${testUserId}/enable`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        body: {
          enabled: true,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        cy.request({
          method: 'POST',
          url: `/users/${testUserId}/enable`,
          headers: {
            'Authorization': `Bearer ${defaultAdminJwt}`,
          },
          body: {
            enabled: false,
          },
          failOnStatusCode: false
        }).then(response => {
          expect(response.status).to.eq(200);
          utils.checkResponseHeaders(response);
        });
      });
    });

    it('Can make admin/non-admin (POST) a single user', () => {
      cy.request({
        method: 'POST',
        url: `/users/${testUserId}/admin`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        body: {
          is_admin: true,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        cy.request({
          method: 'POST',
          url: `/users/${testUserId}/admin`,
          headers: {
            'Authorization': `Bearer ${defaultAdminJwt}`,
          },
          body: {
            is_admin: false,
          },
          failOnStatusCode: false
        }).then(response => {
          expect(response.status).to.eq(200);
          utils.checkResponseHeaders(response);
        });
      });
    });

    it('Can Delete (DELETE) a user', () => {
      cy.request({
        method: 'DELETE',
        url: `/users/${testUserId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);
      });
    });
  });
});
