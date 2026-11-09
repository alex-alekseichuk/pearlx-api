/// <reference types='cypress' />

import { utils } from '../../support/utils';

const {
  rootEmail,
  rootPassword,
  email,
  password,
} = utils;

describe('Organizations API', () => {
  describe('Anonymous role', () => {
    it('Can\'t Create (POST) an organization', () => {
      cy.request({
        method: 'POST',
        url: '/organizations',
        body: {
          name: 'xxxxx',
          address: 'yyyyy',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });

    it('Can\'t GET all organizations', () => {
      cy.request({
        method: 'GET',
        url: '/organizations',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Read (GET) a single organization as per contract', () => {
      cy.request({
        method: 'GET',
        url: `/organizations/${Math.random()}`,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Update (PUT) an organization', () => {
      cy.request({
        method: 'PUT',
        url: '/organizations/some_id',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });

    it('Can\'t Delete (DELETE) an organization', () => {
      cy.request({
        method: 'DELETE',
        url: '/organizations/some_id',
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });
  });
  
  describe('User role', () => {
    let testUserJwt;

    before(() => {
      utils.login(email, password).then(jwt => {
        testUserJwt  = jwt;
      });
    });

    it('Can\'t Create (POST) an organization', () => {
      cy.request({
        method: 'POST',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          name: 'xxxxx',
          address: 'yyyyy',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(403);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(403);
        expect(response.body.message).to.eq('Forbidden');
      });
    });

    it('Can\'t GET all organizations', () => {
      cy.request({
        method: 'GET',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(403);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Read (GET) a single organization as per contract', () => {
      // TODO: add 200 for owner
      cy.request({
        method: 'GET',
        url: `/organizations/${Math.random()}`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(403);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Update (PUT) an organization', () => {
      cy.request({
        method: 'PUT',
        url: '/organizations/some_id',
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

    it('Can\'t Delete (DELETE) an organization', () => {
      cy.request({
        method: 'DELETE',
        url: '/organizations/some_id',
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
    let testOrgId;
    let organizations;

    before(() => {
      utils.login(rootEmail, rootPassword).then(jwt => {
        testUserJwt  = jwt;
      });
    });

    it('Can Create (POST) a new organization as per contract', () => {
      cy.request({
        method: 'POST', 
        url: `/organizations`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          name: 'XYZ Inc',
          address: 'TX, USA',
        }
      }).then(response => {
        expect(response.status).to.eq(201);
        utils.checkResponseHeaders(response);

        const organization = response.body;
        expect(organization).to.be.a('object');

        testOrgId = organization.id;

        expect(organization).to.have.own.property('id');
        expect(organization.id).to.be.a('string').to.have.lengthOf(36);

        expect(organization).to.have.own.property('name');
        expect(organization.name).to.be.a('string').to.have.lengthOf.above(0);

        expect(organization).to.have.own.property('address');
        expect(organization.address).to.be.a('string');

        expect(organization).to.have.own.property('phone');
      });
    });

    it('Can\'t Create (POST) an organization with an existing name', () => {
      cy.request({
        method: 'POST',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          name: 'XYZ Inc',
          address: 'TX, USA',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(409);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(409);
        expect(response.body.message).to.eq('Can\'t create organization, duplicate record with name `XYZ Inc` already exists.');
      });
    });

    it('Can Read (GET) all organizations as per contract', () => {
      cy.request({
        method: 'GET',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        organizations = response.body;
        expect(organizations).to.be.a('array');
        expect(organizations).to.have.lengthOf.above(0);

        organizations.forEach(organization => {
          console.log(`Found organization id=${organization.id} name=${organization.name}`)
        });
      });
    });

    it('Can Read (GET) a single organization as per contract', () => {
      cy.request({
        method: 'GET',
        url: `/organizations/${organizations[0].id}`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const organization = response.body;
        expect(organization).to.be.a('object');

        expect(organization).to.have.own.property('id');
        expect(organization.id).to.be.a('string').to.have.lengthOf(36);

        expect(organization).to.have.own.property('name');
        expect(organization.name).to.be.a('string').to.have.lengthOf.above(0);

        expect(organization).to.have.own.property('address');
        expect(organization.address).to.be.a('string');

        expect(organization).to.have.own.property('phone');
      });
    });

    it('Can\'t Read (GET) an organization with invalid id', () => {
      cy.request({
        method: 'GET',
        url: '/organizations/some_id',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(404);
        // expect(response.body.message).to.eq('Can\'t get organization by ID');
      });
    });

    it('Can Update (PUT) to update an organization as per contract', () => {
      cy.request({
        method: 'PUT',
        url: `/organizations/${testOrgId}`,
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          name: 'ABC Inc',
          address: 'TX, USA',
        },
        failOnStatusCode: false
      }).then(response => {
        console.log(`organizationId=${JSON.stringify(testOrgId)}`)

        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const organization = response.body;
        expect(organization).to.be.a('object');

        testOrgId = organization.id;

        expect(organization).to.have.own.property('id');
        expect(organization.id).to.be.a('string').to.have.lengthOf(36);

        expect(organization).to.have.own.property('name');
        expect(organization.name).to.be.a('string').to.have.lengthOf.above(0);

        expect(organization).to.have.own.property('address');
        expect(organization.address).to.be.a('string');

        expect(organization).to.have.own.property('phone');
      });
    });

    it('Can\'t Update (PUT) an organization with invalid id', () => {
      cy.request({
        method: 'PUT',
        url: '/organizations/some_id',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        body: {
          name: "some name"
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(404);
        // expect(response.body.message).to.eq('Can\'t update organization');
      });
    });

    it('Can Delete (DELETE) all organizations except PearlX and Alamgam', () => {
      utils.removeNotNeededOrganizations(testUserJwt);
    });

    it('Can\'t Delete (DELETE) an organization with invalid id', () => {
      cy.request({
        method: 'DELETE',
        url: '/organizations/some_id',
        headers: {
          'Authorization': `Bearer ${testUserJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(404);
        // expect(response.body.message).to.eq('Can\'t delete organization');
      });
    });
  });
});
