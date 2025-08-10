# mortgage_calculator
A tool that crunches mortgage numbers

## Installation
```
python3 -m pip install --upgrade https://github.com/greyltc/mortgage_calculator/releases/latest/download/mortgage_calculator-py3-none-any.whl
```

## Usage
```
$ python -m mortgage_calculator --help
usage: python -m mortgage_calculator [-h] [--size SIZE] [--rate RATE]
                                     [--compound-period COMPOUND_PERIOD]
                                     [--max-payment-size MAX_PAYMENT_SIZE]
                                     [--payment-period PAYMENT_PERIOD]
                                     [--duration DURATION] [--unit UNIT]
                                     [--bank-name BANK_NAME]
                                     [--borrower-name BORROWER_NAME]
                                     [--register-new-payment last_timestamp last_remaining payment_size]
                                     [--verbose]

crunch mortgage numbers

options:
  -h, --help            show this help message and exit
  --size, -s SIZE       mortgage size (default: 100000)
  --rate, -r RATE       advertised interest rate [percent] (default: 4.5)
  --compound-period, -c COMPOUND_PERIOD
                        compoind period [s] (default: 31449600.0)
  --max-payment-size, -p MAX_PAYMENT_SIZE
                        fix the upper limit for a single payment (default:
                        10000)
  --payment-period, -i PAYMENT_PERIOD
                        time between regular payments [s] (default: 2620800.0)
  --duration, -d DURATION
                        fix the duration of the loan (default: 0 seconds)
  --unit, -u UNIT       monetary unit (default: EUR)
  --bank-name, -b BANK_NAME
                        name of loaner (default: None)
  --borrower-name, -w BORROWER_NAME
                        name of borrower (default: None)
  --register-new-payment, -n last_timestamp last_remaining payment_size
                        register a payment against an existing loan and
                        generate a payment report pdf (default: None)
  --verbose, -v         print more details (default: False)
```
