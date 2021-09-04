# Changelog

<!--next-version-placeholder-->

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
