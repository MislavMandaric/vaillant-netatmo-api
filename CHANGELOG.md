# Changelog

<!--next-version-placeholder-->

## v0.2.0 (2021-10-17)
### Feature
* Adds new retry policy to all requests with new library ([`23a48c1`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/23a48c1ec86e5bfd1358299eb45528b44d3bef40))
* Adds retry policy to all requests ([`f9875a6`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/f9875a6974412de9a59c3adbb0c5f2e2472a4561))
* Wrapping http calls with the error handler ([`4d7011f`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/4d7011fbb82eaae9a5ae36453d7c8f9d76e33696))
* Using and exporting new error models ([`1d8677c`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/1d8677c1169902952f47a5751d2232b1c165eb81))
* Adds whole new error hierarchy module. ([`947cd95`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/947cd95139bc5220fdd246a9ad3842315249be93))

### Fix
* Increases default timeout for all api calls to 30s. This should hopefully fix current timeout issues. If this fixes a problem, it needs to be revisited and better mechanism should be put in place (eg. in combination with retries, each subsequent call can have increased timeout) ([`af5e1c8`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/af5e1c8155b8e582c6a883a4bb5c4db107790bdc))

## v0.1.2 (2021-09-09)
### Fix
* Updates authlib dependency to new beta to fix header length issue ([`eb7616f`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/eb7616f2141308331fa669890d8865fda9912d87))

## v0.1.1 (2021-09-04)
### Fix
* Fixes an unsupported argument exception when deactivating minor mode ([`72c5525`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/72c55255ebd0b2b5035da11aec53fa6352a26b4c))

## v0.1.0 (2021-09-04)
### Feature
* Changes naming and structure to align with pip convention of having dashes instead of underscores. ([`11bd52d`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/11bd52d1d418879bd794b14ad6075ad8f56892a2))
* Adds context manager for both auth and thermostat client ([`b5f97c0`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/b5f97c05fb2f6c92eff95bfc477d6988b422b652))
* Initial version of the API wrapper without any test ([`a1d2764`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/a1d2764e67df041f6536b224c62eab21913709dd))

### Fix
* Fixes a problem with authlib 0.15.4 and httpx 0.18.2+ where default client import changed. ([`ed61dec`](https://github.com/MislavMandaric/vaillant-netatmo-api/commit/ed61dec52c63c92b20257537a93e8da6c5ee56b3))
