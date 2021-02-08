# DynatraceSyntheticConverter

This project aims to provide a CLI for downloading, generating, validating, and uploading synthetic monitors from Dynatrace JSON schema to python scripts directly usable in AppDynamics synthetics.

## Usage

DynatraceSyntheticConverter can be invoked with the command `python3 DynatraceSyntheticConverter.py`
```
Usage: dynatraceSyntheticConverter.py [OPTIONS] COMMAND [ARGS]...

  DT synthetic commands

Options:
  --help  Show this message and exit.

Commands:
  generate  Generate python scripts from Dynatrace synthetic monitor JSON.
  upload    Upload generated scripts to AppD.
  validate  Validates generated scripts by running them locally.
```
### Commands


It is advised to execute the script with commands in the following order:
1. generate
2. validate
3. upload

Generate
```
Usage: dynatraceSyntheticConverter.py generate [OPTIONS]

  Generate python scripts from Dynatrace synthetic monitor JSON. Generated
  scripts are placed in the output directory and will overwrite existing
  scripts of the same name.

Options:
  --help  Show this message and exit.
```

Validate
```
Usage: dynatraceSyntheticConverter.py validate [OPTIONS]

  Validates generated scripts by running them locally. Creates report.csv in
  the output directory.

Options:
  --help  Show this message and exit.
```

Upload
```
Usage: DynatraceSyntheticConverter.py upload [OPTIONS]

  Upload generated scripts to AppD. If only-useful-scripts is chosen, only
  scripts from the output/report.csv which ranSuccessfully will be uploaded.

Options:
  --host TEXT                acme.saas.appdynamics.com
  --port TEXT                SaaS: 443 On Prem: 8090
  --ssl / --no-ssl
  --account TEXT             SaaS: first segment of controller host On Prem:
                             customer1

  --username TEXT            must use local account
  --password TEXT
  --only-successful-scripts  Only scripts from the output/report.csv which
                             ranSuccessfully will be uploaded.

  --overwrite                Overwrite scripts on destination controller with
                             the same name.

  --help                     Show this message and exit.
```
## Input

The `upload` step requires the file `input/mapping.csv` to contain a line entry for every synthetic job.
The file `input/mapping.csv` contains the following modifiable fields.
- jobName
    - Name of synthetic monitor
- eumApplicationId
    - EUM Application ID (not EUM key) on which to upload the synthetic script
- browserCodes
    - Chrome
    - Firefox
    - IE11
- locationCodes
    - NET - Amsterdam, Noord-Holland, Netherlands (new)
    - IAD - Ashburn, Virginia, United States
    - M50 - Boardman, Oregon, United States
    - SIC - Chennai, Tamil Nadu, India (new)
    - DUB - Dublin, Dublin, Ireland
    - FRA - Frankfurt, Hessen, Germany
    - HON - Hong Kong, Hong Kong, China
    - LON - London, United Kingdom, United Kingdom
    - ASV - Melbourne, Victoria, Australia (new)
    - MIL - Milan (new), Lombardy, Italy
    - MON - Montreal, Québec, Canada
    - BOM - Mumbai, Maharashtra, India
    - PAR - Paris, Ile-de-France, France
    - SAN - San Antonio, Texas, United States (new)
    - SFO - San Francisco, California, United States
    - GRU - Sao Paulo, Sao Paulo, Brazil
    - ICN - Seoul, Seoul, South Korea
    - SIN - Singapore, Singapore, Singapore
    - SYD - Sydney, New South Wales, Australia
    - NRT - Tokyo, Tokyo, Japan
    - CAC - Toronto, Ontario, Canada (new)
- timeoutSeconds
    - integer value of maximum script runtime
- executionRateValue
    - how frequently the script triggers
- executionRateUnit
    - MINUTES
    - HOURS
    - DAYS

## Output
Executing `generate` will read all Dynatrace synthetic monitor JSON files from the `input` directory and create corresponding `.py` files in the `output` directory.

Executing `validate` will generate 'report.csv' in the `output` directory containing for each job whether it ran successfully and whether it contains custom code to be hand implemented. 

## Requirements
- python3
- chromedriver installed to your PATH

## Support
Please email bradley.hjelmar@appdynamics.com for any issues.
