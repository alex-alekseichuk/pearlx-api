/// <reference types="cypress" />

import { utils } from "../../../e2e-cypress-test/cypress/support/utils";

describe('Auth API', () => {
  let defaultAdminJwt;
  let userJwt;
  let testOrgId;
  let testUserId;

  before(() => {
    utils.login('admin@some.com', 'add_pass')
      .then(token => {
        defaultAdminJwt = token;

        utils.removeNotNeededOrganizations(defaultAdminJwt);

        utils.addOrganizaition('Test Organization', defaultAdminJwt).then(_organizationId => {
          testOrgId = _organizationId;
        });
      }
    );
  });

  after(() => {
    utils.removeNotNeededOrganizations(defaultAdminJwt);

    cy.mhDeleteAll();
  });

  describe('Anonymous role', () => {
    it('Register an user', () => {
      utils.register(
        'test',
        'user',
        'test.user@amalgam-inc.com',
        'Testing123$',
        testOrgId,
      ).then(user => {
        testUserId = user.id;
      });
    });

    it('Verify an user', () => {
      cy.mhGetMailsBySubject('Pearlx - Verify email request').mhFirst().mhGetBody().then(mail => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(mail, 'text/html');
        const code = doc.querySelector('code').textContent;
        const token = code.match(/[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}/)[0];
        utils.verify_email('test.user@amalgam-inc.com', token);
      });
    });

    it('Login an user', () => {
      utils.login('test.user@amalgam-inc.com', 'Testing123$')
        .then(token => {
          userJwt = token;
        }
      );
    });

    it('Can\'t get an user details w/o jwt', () => {
      cy.request({
        method: 'GET',
        url: '/auth/me',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t change password for an user w/o jwt', () => {
      cy.request({
        method: 'POST',
        url: '/auth/change-password',
        body: {
          'new-password': 'Testing123$',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t logout an user w/o jwt', () => {
      cy.request({
        method: 'POST',
        url: '/auth/logout',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });
  });

  describe('Customer role', () => {
    it('Register an user', () => {
      utils.register(
        'test',
        'user2',
        'test.user2@amalgam-inc.com',
        'Testing123$',
        testOrgId,
      ).then(user => {
        testUserId = user.id;
      });
    });

    it('Verify an user', () => {
      cy.mhGetMailsBySubject('Pearlx - Verify email request').mhFirst().mhGetBody().then(mail => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(mail, 'text/html');
        const code = doc.querySelector('code').textContent;
        const token = code.match(/[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}/)[0];
        utils.verify_email('test.user2@amalgam-inc.com', token);
      });
    });

    it('Login an user', () => {
      utils.login('test.user2@amalgam-inc.com', 'Testing123$')
        .then(token => {
          userJwt = token;
        }
      );
    });

    it('Get an user details', () => {
      cy.request({
        method: 'GET',
        url: '/auth/me',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const user = response.body;
        expect(user).to.be.a('object');

        expect(user).to.have.own.property('id');
        expect(user.id).to.be.a('string').to.have.lengthOf(36);

        expect(user).to.have.own.property('firstname');
        expect(user.firstname).to.be.a('string').to.have.lengthOf.above(0);

        expect(user).to.have.own.property('lastname');
        expect(user.lastname).to.be.a('string');

        expect(user).to.have.own.property('email');
        expect(user.email).to.be.a('string').to.have.length.above(0);

        expect(user).to.have.own.property('enabled');
        expect(user.enabled).to.be.a('boolean').to.equal(true);

        expect(user).to.have.own.property('phone');

        expect(user).to.have.own.property('organization_id');
      });
    });

    it('Change password for an user', () => {
      cy.request({
        method: 'POST',
        url: '/auth/change-password',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        body: {
          'new-password': 'Testing123$',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);

        cy.request({
          method: 'POST',
          url: '/auth/change-password',
          headers: {
            'Authorization': `Bearer ${userJwt}`,
          },
          body: {
            'new-password': 'add_pass',
          },
          failOnStatusCode: false
        }).then(response => {
          expect(response.status).to.eq(204);
        });
      });
    });

    it('Logout an user', () => {
      cy.request({
        method: 'POST',
        url: '/auth/logout',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);
      });
    });
  });

  describe('Admin role', () => {
    it('Register an user', () => {
      utils.register(
        'test',
        'admin',
        'test.admin@amalgam-inc.com',
        'Testing123$',
        testOrgId,
      ).then(user => {
        testUserId = user.id;
      });
    });

    it('Verify an user', () => {
      cy.mhGetMailsBySubject('Pearlx - Verify email request').mhFirst().mhGetBody().then(mail => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(mail, 'text/html');
        const code = doc.querySelector('code').textContent;
        const token = code.match(/[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}/)[0];
        utils.verify_email('test.admin@amalgam-inc.com', token);
      });
    });

    it('Login an user', () => {
      utils.login('test.admin@amalgam-inc.com', 'Testing123$')
        .then(token => {
          userJwt = token;
        }
      );
    });

    it('Get an user details', () => {
      cy.request({
        method: 'GET',
        url: '/auth/me',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        testUserId = response.body.id;
        // expect(response.body.isAdmin).to.equal(false);
      });
    });

    it('Make an user an admin user', () => {
      cy.request({
        method: 'POST',
        url: `/users/${testUserId}/admin`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        body: {
          'is_admin': true,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
     });
    });

    it('Change password for an admin', () => {
      cy.request({
        method: 'POST',
        url: '/auth/change-password',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        body: {
          'new-password': 'Testing123$',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);

        cy.request({
          method: 'POST',
          url: '/auth/change-password',
          headers: {
            'Authorization': `Bearer ${userJwt}`,
          },
          body: {
            'new-password': 'add_pass',
          },
          failOnStatusCode: false
        }).then(response => {
          expect(response.status).to.eq(204);
        });
      });
    });

    it('Logout an admin', () => {
      cy.request({
        method: 'POST',
        url: '/auth/logout',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);
      });
    });
  });
});
