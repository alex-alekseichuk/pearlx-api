/// <reference types="cypress" />

import { utils } from '../../support/utils';

const {
  rootEmail,
  rootPassword,
  email,
  password,
} = utils;

describe('Ders API', () => {
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
    let testUserJwt;

    before(() => {
      utils.login(email, password).then(jwt => {
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
    let testUserJwt;

    before(() => {
      utils.login(rootEmail, rootPassword).then(jwt => {
        testUserJwt  = jwt;
      });
    });

    it('Can Refresh (POST) ders', () => {
      cy.request({
        method: 'POST',
        url: '/ders/refresh',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
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
