# Frontend


#### Table of Contents
- [Code Distribution](#code-distribution)
- [Commands](#commands)

## Code Distribution
Code is distributed in the following "apps":
 - [assets](src/assets) - Contains assets such as static images
 - [Components](src/components) - Contains all the components which are reused by other components
 - [Service](src/service) - Contains functionality such as the [api urls](src/service/api.js), [error handlers](src/service/errors.js), [utils](src/service/utils.js) etc.
 - [Store](src/store) - Contains everything related to Vuex 
 - [Views](src/views) - Contains the views
 - [Tests](tests) - Contains all the tests for the views and components


## Commands

####  Start the Dev Serer
```bash
make runserver
```

#### Fix Linting
```bash
make fmt
```

#### Run unit tests
```bash
make test
```
