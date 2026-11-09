Run cypress e2e tests against local server:

```
cd e2e-cypress-test
docker run -it -v $PWD:/e2e -w /e2e -e CYPRESS_VIDEO=false --name cypress-test --rm --network=host cypress/included:10.8.0
```
