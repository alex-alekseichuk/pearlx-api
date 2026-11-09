/// <reference types="cypress" />

import { utils } from '../../support/utils';

const {
  rootEmail,
  rootPassword,
  email,
  password,
} = utils;

describe('Users API', () => {
  let testUserId;

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
    let testUserJwt;

    before(() => {
      utils.login(email, password).then(jwt => {
        testUserJwt  = jwt;

        cy.request({
          method: 'GET',
          url: '/auth/me',
          headers: {
            'Authorization': `Bearer ${testUserJwt}`,
          },
          failOnStatusCode: false
        }).then(response => {
          expect(response.status).to.eq(200);
          testUserId = response.body.id;
        });
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
    let defaultAdminJwt;

    before(() => {
      utils.login(rootEmail, rootPassword)
        .then(token => {
          defaultAdminJwt = token;
        });
    });

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
          enabled: false,
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
            enabled: true,
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

    // it('Can Delete (DELETE) a user', () => {
    //   cy.request({
    //     method: 'DELETE',
    //     url: `/users/${testUserId}`,
    //     headers: {
    //       'Authorization': `Bearer ${defaultAdminJwt}`,
    //     },
    //     failOnStatusCode: false
    //   }).then(response => {
    //     expect(response.status).to.eq(204);
    //   });
    // });
  });
});
