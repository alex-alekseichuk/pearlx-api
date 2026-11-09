/// <reference types="cypress" />

import { utils } from '../../support/utils';

const {
  rootEmail,
  rootPassword,
  email,
  password,
} = utils;

describe('Auth API', () => {
  describe('Anonymous role', () => {
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
    let userJwt;

    before(() => {
      utils.login(email, password)
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
          'new-password': 'Testing223$',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(204);

        return cy.request({
          method: 'POST',
          url: '/auth/change-password',
          headers: {
            'Authorization': `Bearer ${userJwt}`,
          },
          body: {
            'new-password': 'Testing224$',
          },
          failOnStatusCode: false
        });
      }).then(response => {
        expect(response.status).to.eq(204);

        return cy.request({
          method: 'POST',
          url: '/auth/change-password',
          headers: {
            'Authorization': `Bearer ${userJwt}`,
          },
          body: {
            'new-password': 'Testing225$',
          },
          failOnStatusCode: false
        });
      }).then(response => {
        expect(response.status).to.eq(204);

        return cy.request({
          method: 'POST',
          url: '/auth/change-password',
          headers: {
            'Authorization': `Bearer ${userJwt}`,
          },
          body: {
            'new-password': 'add_pass',
          },
          failOnStatusCode: false
        });
      }).then(response => {
        expect(response.status).to.eq(204);
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
    let userJwt;
    let testUserId;

    before(() => {
      utils.login(rootEmail, rootPassword)
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
          'Authorization': `Bearer ${userJwt}`,
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

    it.skip('Change password for an admin', () => {
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
