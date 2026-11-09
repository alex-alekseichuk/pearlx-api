/// <reference types="cypress" />

const default_admin_email = Cypress.env('default_admin_email') ?? 'admin@some.com';
const default_user_email = Cypress.env('default_user_email') ?? 'flexapi.user@pearlxinfra.com';
export const utils = {
  rootEmail: default_admin_email,
  rootPassword: 'add_pass',
  email: default_user_email,
  password: 'add_pass',

  checkResponseHeaders(response): void {
    expect(response.headers).to.be.a('object');
    expect(response.headers['content-type']).to.be.a('string').to.be.equal('application/json');
    expect(response.headers['content-length']).to.be.a('string').to.match(/\d*/);
  },

  async register(firstname: string, lastname: string, email: string, password: string, organizationId: string): Cypress.Promise<string> {
    const promise = new Cypress.Promise<string>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/auth/register',
        body: {
          firstname,
          lastname,
          email,
          password,
          'organization_id': organizationId,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(201);
        utils.checkResponseHeaders(response);

        const user = response.body;
        expect(user).to.be.a('object');
  
        expect(user).to.have.own.property('firstname');
        expect(user.firstname).to.be.a('string');
        expect(user.firstname.length).to.have.greaterThan(0);

        expect(user).to.have.own.property('firstname');
        expect(user.firstname).to.be.a('string');
        expect(user.firstname.length).to.have.greaterThan(0);

        expect(user).to.have.own.property('id');
        expect(user.id).to.be.a('string');
        expect(user.id.length).to.have.greaterThan(0);

        expect(user).to.have.own.property('email');
        expect(user.email).to.be.a('string');
        expect(user.email).to.equal(email);

        expect(user).to.have.own.property('organization_id');
        expect(user.organization_id).to.be.a('string');
        expect(user.organization_id).to.equal(organizationId);

        resolve(user.id);
      });
    });

    return promise;
  },

  async verify_email(email: string, token: string): Cypress.Promise<string> {
    const promise = new Cypress.Promise<string>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/auth/verify-email-token',
        body: {
          email,
          token,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        resolve();
      });
    });

    return promise;
  },

  async login(email: string, password: string): Cypress.Promise<string> {
    const promise = new Cypress.Promise<string>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/auth/login',
        body: {
          email,
          password,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
  
        const jwt = response.body;
        expect(jwt).to.be.a('object');
  
        expect(jwt).to.have.own.property('token');
        expect(jwt.token).to.be.a('string');
        expect(jwt.token.length).to.have.greaterThan(0);
  
        resolve(jwt.token);
      });
    });

    return promise;
  },

  async addOrganizaition(name: string, adminJwt: string): Cypress.Promise<string> {
    const promise = new Cypress.Promise<string>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${adminJwt}`,
        },
        body: {
          name: name,
          address: '',
        },
        failOnStatusCode: false,
        }).then(response => {
        expect(response.status).to.eq(201);
        utils.checkResponseHeaders(response);

        const organization = response.body;
        expect(organization).to.be.a('object');

        expect(organization).to.have.own.property('id');
        expect(organization.id).to.be.a('string').to.have.lengthOf(36);

        expect(organization).to.have.own.property('name');
        expect(organization.name).to.be.a('string').to.have.lengthOf.above(0);

        expect(organization).to.have.own.property('address');

        expect(organization).to.have.own.property('phone');

        resolve(organization.id);
      });
    });

    return promise;
  },

  removeNotNeededOrganizations(adminJwt: string): Cypress.Promise<void> {
    const promise = new Cypress.Promise<string>((resolve) => {
      cy.request({
        method: 'GET',
        url: '/organizations',
        headers: {
          'Authorization': `Bearer ${adminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        const organizations = response.body;
        organizations.forEach(organization => {
          if (organization.name !== 'PearlX Infrastructure LLC' && organization.name !== 'Amalgam Inc.') {
            console.log(`Deleting organization id=${organization.id} name=${organization.name}`)
            cy.request({
              method: 'DELETE',
              headers: {
                'Authorization': `Bearer ${adminJwt}`,
              },
              url: `/organizations/${organization.id}`,
              failOnStatusCode: false
            }).then(response => {
              expect(response.status).to.eq(204);
              resolve();
            });
          }
        });
      });
    });

    return promise;
  },

  async refreshSites(adminJwt: string): Cypress.Promise<void> {
    const promise = new Cypress.Promise<void>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/sites/refresh',
        headers: {
          'Authorization': `Bearer ${adminJwt}`,
        },
        failOnStatusCode: false,
        }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        expect(response.body).to.be.a('array');
        // expect(response.body).to.have.lengthOf.above(0);

        resolve();
      });
    });

    return promise;
  },

  async refreshDers(adminJwt: string): Cypress.Promise<void> {
    const promise = new Cypress.Promise<void>((resolve) => {
      cy.request({
        method: 'POST',
        url: '/ders/refresh',
        headers: {
          'Authorization': `Bearer ${adminJwt}`,
        },
        failOnStatusCode: false,
        }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        expect(response.body).to.be.a('array');
        // expect(response.body).to.have.lengthOf.above(0);
        
        resolve();
      });
    });

    return promise;
  },
};