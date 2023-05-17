# mortgage_calculator

## Usage
```
$ python -m mortgage_calculator --help
usage: python -m mortgage_calculator [-h] [--size SIZE] [--rate RATE] [--compound-period COMPOUND_PERIOD] [--max-payment-size MAX_PAYMENT_SIZE]
                                     [--payment-period PAYMENT_PERIOD] [--duration DURATION] [--unit UNIT] [--bank-name BANK_NAME]
                                     [--borrower-name BORROWER_NAME] [--register-new-payment last_timestamp last_remaining payment_size] [--verbose]

crunch mortgage numbers

options:
  -h, --help            show this help message and exit
  --size SIZE, -s SIZE  mortgage size (default: 100000)
  --rate RATE, -r RATE  advertised interest rate [percent] (default: 4.5)
  --compound-period COMPOUND_PERIOD, -c COMPOUND_PERIOD
                        compoind period [s] (default: 31449600.0)
  --max-payment-size MAX_PAYMENT_SIZE, -p MAX_PAYMENT_SIZE
                        fix the upper limit for a single payment (default: 10000)
  --payment-period PAYMENT_PERIOD, -i PAYMENT_PERIOD
                        time between regular payments [s] (default: 2620800.0)
  --duration DURATION, -d DURATION
                        fix the duration of the loan [s] (default: 0.0)
  --unit UNIT, -u UNIT  monetary unit (default: EUR)
  --bank-name BANK_NAME, -b BANK_NAME
                        name of loaner (default: None)
  --borrower-name BORROWER_NAME, -w BORROWER_NAME
                        name of borrower (default: None)
  --register-new-payment last_timestamp last_remaining payment_size, -n last_timestamp last_remaining payment_size
                        register a payment against an existing loan and generate a payment report pdf (default: None)
  --verbose, -v         print more details (default: False)
```