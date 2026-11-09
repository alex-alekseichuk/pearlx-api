/// <reference types="cypress" />

import { utils } from '../../support/utils';

const {
  rootEmail,
  rootPassword,
  email,
  password,
} = utils;

describe('Sites API', () => {
  const checkSite = (site) => {
    // console.log(`$$$$$$ site=${JSON.stringify(site)}`);

    expect(site).to.be.a('object');
  
    expect(site).to.have.own.property('id');
    expect(site.id).to.be.a('string');
    expect(site.id.length).to.equal(36);

    expect(site).to.have.own.property('enabled');
    expect(site.enabled).to.be.a('boolean');
    expect(site.enabled).to.equal(true);

    expect(site).to.have.own.property('site_name');
    expect(site.site_name).to.be.a('string');
    expect(site.site_name.length).to.have.greaterThan(0);

    expect(site).to.have.own.property('site_address');
    expect(site.site_address).to.be.a('string');
    expect(site.site_address.length).to.have.greaterThan(0);

    expect(site).to.have.own.property('system_id');
    expect(site.system_id).to.be.a('string');
    expect(site.system_id.length).equal(36);
  }

  const checkDer = (der) => {
    // console.log(`$$$$$$ der=${JSON.stringify(der)}`);

    expect(der).to.be.a('object');
  
    expect(der).to.have.own.property('id');
    expect(der.id).to.be.a('string');
    expect(der.id.length).to.equal(36);

    expect(der).to.have.own.property('enabled');
    expect(der.enabled).to.be.a('boolean');
    expect(der.enabled).to.equal(true);

    expect(der).to.have.own.property('der_type');
    expect(der.der_type).to.be.a('string');
    expect(der.der_type.length).to.have.greaterThan(0);

    expect(der).to.have.own.property('site_id');
    expect(der.site_id).to.be.a('string');
    expect(der.site_id.length).equal(36);
  }

  const checkSiteProps = (siteProps) => {
    console.log(`$$$$$$ siteProps=${JSON.stringify(siteProps)}`);

    expect(siteProps).to.be.a('object');

    expect(siteProps).to.have.own.property('system_timezone');
    expect(siteProps.system_timezone).to.be.a('string');
    expect(siteProps.system_timezone.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('site_name');
    expect(siteProps.site_name).to.be.a('string');
    expect(siteProps.site_name.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('derid_system');
    expect(siteProps.derid_system).to.be.a('string');
    expect(siteProps.derid_system.length).to.equal(36);

    expect(siteProps).to.have.own.property('location_latitude');
    expect(siteProps.location_latitude).to.be.a('string');
    expect(siteProps.location_latitude.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('location_longitude');
    expect(siteProps.location_longitude).to.be.a('string');
    expect(siteProps.location_longitude.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('site_address');
    expect(siteProps.site_address).to.be.a('string');
    expect(siteProps.site_address.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('iou_utility');
    expect(siteProps.iou_utility).to.be.a('string');
    expect(siteProps.iou_utility.length).to.have.greaterThan(0);

    expect(siteProps).to.have.own.property('iou_circuit_name');
    expect(siteProps.iou_circuit_name).to.be.a('string');
    expect(siteProps.iou_circuit_name.length).to.have.greaterThan(0);
  }

  const checkStorageProps = (storageProps) => {
    console.log(`$$$$$$ storageProps=${JSON.stringify(storageProps)}`);

    expect(storageProps).to.be.a('object');

    expect(storageProps).to.have.own.property('site_id');
    expect(storageProps.site_id).to.be.a('string');
    expect(storageProps.site_id.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('serial_number');
    expect(storageProps.serial_number).to.be.a('string');
    expect(storageProps.serial_number.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('derid_battery');
    expect(storageProps.derid_battery).to.be.a('string');
    expect(storageProps.derid_battery.length).to.equal(36);

    expect(storageProps).to.have.own.property('derid_storage');
    expect(storageProps.derid_storage).to.be.a('string');
    expect(storageProps.derid_storage.length).to.equal(36);

    expect(storageProps).to.have.own.property('derid_inverter');
    expect(storageProps.derid_inverter).to.be.a('string');
    expect(storageProps.derid_inverter.length).to.equal(36);

    expect(storageProps).to.have.own.property('batt_model');
    expect(storageProps.batt_model).to.be.a('string');
    expect(storageProps.batt_model.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('batt_manufacture');
    expect(storageProps.batt_manufacture).to.be.a('string');
    expect(storageProps.batt_manufacture.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('batt_rated_power');
    expect(storageProps.batt_rated_power).to.be.a('string');
    expect(storageProps.batt_rated_power.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('batt_rated_capacity');
    expect(storageProps.batt_rated_capacity).to.be.a('string');
    expect(storageProps.batt_rated_capacity.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('min_operating_temperature');
    expect(storageProps.min_operating_temperature).to.be.a('string');
    expect(storageProps.min_operating_temperature.length).to.have.greaterThan(0);

    expect(storageProps).to.have.own.property('batt_rte');
    expect(storageProps.batt_rte).to.be.a('string');
    expect(storageProps.batt_rte.length).to.have.greaterThan(0);
  }

  describe('Anonymous role', () => {
    it('Can\'t Refresh (POST) sites', () => {
      cy.request({
        method: 'POST',
        url: '/sites/refresh',
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

    it('Can\'t Refresh (POST) sites', () => {
      cy.request({
        method: 'POST',
        url: '/sites/refresh',
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

    let sites = [];
    let testSiteId = '';

    let ders = [];
    let testDerId = '';

    let batteryDer;
    let inverterDer;
    let storageDer;

    before(() => {
      utils.login(rootEmail, rootPassword)
        .then(token => {
            defaultAdminJwt = token;
        });
    });

    // beforeEach(() => {
    //   utils.refreshSites(defaultAdminJwt)
    //     .then(() => {});

    //   utils.refreshDers(defaultAdminJwt)
    //     .then(() => {});
    // });

    it('Can Refresh (POST) sites', () => {
      utils.refreshSites(defaultAdminJwt)
        .then(() => {});
    });

    it('Can Refresh (POST) ders', () => {
      utils.refreshDers(defaultAdminJwt)
        .then(() => {});
    });

    it('Can Read (GET) all sites', () => {
      cy.request({
        method: 'GET',
        url: '/sites',
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        sites = response.body;
        expect(sites).to.be.a('array');
        // expect(sites).to.have.lengthOf(1);

        for (let site of sites) {
          if (site.site_name === 'pearlsim, new_york') {
            checkSite(site);
            testSiteId = site.id;
          }
        }

        if (!testSiteId) {
          testSiteId = sites[0].id;
          checkSite(sites[0]);
        }
      });
    });

    it('Can Read (GET) a single site', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        checkSite(response.body);
        testSiteId = response.body.id;
      });
    });

    it('Can enable/disable (PATCH) a single site', () => {
      cy.request({
        method: 'PATCH',
        url: `/sites/${testSiteId}/enable`,
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
        expect(response.body.enabled).to.equal(false);

        cy.request({
          method: 'PATCH',
          url: `/sites/${testSiteId}/enable`,
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
          expect(response.body.enabled).to.equal(true);
        });
      });
    });

    it('Can Read (GET) all ders of a site', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/ders`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        ders = response.body;
        expect(ders).to.be.a('array');
        expect(ders).to.have.lengthOf.greaterThan(0);

        ders.forEach(der => checkDer(der));
        batteryDer = ders.filter(der => der.der_type === 'battery')[0];
        console.log(`$$$$$$ batteryDer=${JSON.stringify(batteryDer)}`);

        inverterDer = ders.filter(der => der.der_type === 'inverter')[0];
        console.log(`$$$$$$ inverterDer=${JSON.stringify(inverterDer)}`);

        storageDer = ders.filter(der => der.der_type === 'storage')[0];
        console.log(`$$$$$$ storageDer=${JSON.stringify(storageDer)}`);
        
        testDerId = ders[0].id;
      });
    });

    it('Can Read (GET) a single der of a site', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/ders/${testDerId}`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);
        checkDer(response.body);
        testDerId = response.body.id;
      });
    });

    it('Can enable/disable (PATCH) a single der within a site', () => {
      cy.request({
        method: 'PATCH',
        url: `/sites/${testSiteId}/ders/${testDerId}/enable`,
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
        expect(response.body.enabled).to.equal(false);

        cy.request({
          method: 'PATCH',
          url: `/sites/${testSiteId}/ders/${testDerId}/enable`,
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
          expect(response.body.enabled).to.equal(true);
        });
      });
    });

    it('Can Read (GET) site-properties of a single site', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/site-properties`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const siteProps = response.body;
        expect(siteProps).to.be.a('array');  // TODO: why response body is an array?
        expect(siteProps).to.have.lengthOf.greaterThan(0);

        siteProps.forEach(props => checkSiteProps(props));
      });
    });

    it('Can Read (GET) storage-properties of a single site', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/storage-properties`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const storageProps = response.body;
        expect(storageProps).to.be.a('array');
        expect(storageProps).to.have.lengthOf.greaterThan(0);

        storageProps.forEach(props => checkStorageProps(props));
      });
    });

    it('Can Read (GET) storage-data of a single battery', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/ders/${batteryDer.id}/storage-data`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        qs: {
          start_time: '2022-04-08T12:00:00.000Z',
          end_time: '2022-04-08T13:00:00.000Z',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const storageDatas = response.body;
        expect(storageDatas).to.be.a('array');
        // expect(storageDatas).to.have.lengthOf.greaterThan(0);

        // storageDatas.forEach(storageData => checkStorageData(storageData));
      });
    });

    it('Can Read (GET) inverter-data of a single inverter', () => {
      cy.request({
        method: 'GET',
        url: `/sites/${testSiteId}/ders/${inverterDer.id}/inverter-data`,
        headers: {
          'Authorization': `Bearer ${defaultAdminJwt}`,
        },
        qs: {
          start_time: '2022-04-08T12:00:00.000Z',
          end_time: '2022-04-08T13:00:00.000Z',
        },
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(200);
        utils.checkResponseHeaders(response);

        const storageDatas = response.body;
        expect(storageDatas).to.be.a('array');
        // expect(storageDatas).to.have.lengthOf.greaterThan(0);

        // storageDatas.forEach(storageData => checkInverterData(storageData));
      });
    });
  });
});
