/// <reference types='cypress' />

import { utils } from '../../../e2e-cypress-test/cypress/support/utils';

describe('Organizations API', () => {
  let defaultAdminJwt;
  let userJwt;
  let testOrgId;
  let testUserId;
  let organizations;


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
          ).then(user => {
            testUserId = user.id;

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
    it('Can\'t Create (POST) an organization', () => {
      cy.request({
        method: 'POST',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
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
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
      });
    });

    it('Can\'t Read (GET) a single organization as per contract', () => {
      // TODO: add 200 for owner
      cy.request({
        method: 'GET',
        url: `/organizations/${Math.random()}`,
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
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
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
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
        headers: {
          'Authorization': `Bearer ${userJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(401);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(401);
        expect(response.body.message).to.eq('Unauthenticated');
      });
    });
  });

  describe('Admin role', () => {
    it('Can Create (POST) a new organization as per contract', () => {
      cy.request({
        method: 'POST', 
        url: `/organizations`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
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
          'Authorization': `Bearer ${defaultAdminJwt}`,
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
          'Authorization': `Bearer ${defaultAdminJwt}`,
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
          'Authorization': `Bearer ${defaultAdminJwt}`,
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
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(500);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(500);
        expect(response.body.message).to.eq('Can\'t get organization by ID');
      });
    });

    it('Can Update (PUT) to update an organization as per contract', () => {
      cy.request({
        method: 'PUT',
        url: `/organizations/${testOrgId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
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
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(409);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(409);
        // expect(response.body.message).to.eq('Can\'t update organization');
      });
    });

    it('Can Delete (DELETE) all organizations except PearlX and Alamgam', () => {
      utils.removeNotNeededOrganizations(defaultAdminJwt);
    });

    it('Can\'t Delete (DELETE) an organization with invalid id', () => {
      cy.request({
        method: 'DELETE',
        url: '/organizations/some_id',
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(500);
        utils.checkResponseHeaders(response);
        expect(response.body.status).to.eq(500);
        expect(response.body.message).to.eq('Can\'t delete organization');
      });
    });
  });
});
