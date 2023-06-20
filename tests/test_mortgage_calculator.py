#!/usr/bin/env python3

import unittest
from typing import TypedDict
import humanfriendly as hf
import mortgage_calculator
from mortgage_calculator.__main__ import _main as mortgage_calculator_main


class MortgageCalculaotrTestCase(unittest.TestCase):
    """mortgage_calculator testing"""

    def test_cli(self):
        with_these_args = "--size 200000 --rate 3.0 -p 0 -d 10y"
        mortgage_calculator_main(with_these_args.split())

    def test_help(self):
        mortgage_calculator_main(["--help"])

    def test_fixed_duration(self):
        class Inputs(TypedDict, total=False):
            size: float
            rate: float
            compound_period: float
            max_payment_size: float
            payment_period: float
            duration: float
            unit: str

        inputs: Inputs = {}
        inputs["size"] = 100000
        inputs["rate"] = 6.0
        inputs["compound_period"] = hf.parse_timespan("1 year") / 2
        inputs["max_payment_size"] = 639.81
        inputs["payment_period"] = hf.parse_timespan("1 year") / 12
        inputs["duration"] = 0
        inputs["unit"] = "HKD"

        mc = mortgage_calculator.MortgageCalculator(**inputs)
        payments = mc.run()

        if mc.debug:
            print(f"#\tTimestamp\tPayment [{mc.unit}]\tInterest [{mc.unit}]\tRemaining [{mc.unit}]")
            for i, (t, payment, interest, remaining) in enumerate(payments):
                print(f"{i+1}\t{t:.0f}\t{payment:.2f}\t{interest:.2f}\t{remaining:.2f}")

    def test_fixed_payment(self):
        class Inputs(TypedDict, total=False):
            size: float
            rate: float
            compound_period: float
            max_payment_size: float
            payment_period: float
            duration: float
            unit: str

        inputs: Inputs = {}
        inputs["size"] = 100000
        inputs["rate"] = 6.0
        inputs["compound_period"] = hf.parse_timespan("1 year") / 2
        inputs["max_payment_size"] = 0
        inputs["payment_period"] = hf.parse_timespan("1 year") / 12
        inputs["duration"] = hf.parse_timespan("25 years")
        inputs["unit"] = "HKD"

        mc = mortgage_calculator.MortgageCalculator(**inputs)
        payments = mc.run()

        if mc.debug:
            print(f"#\tTimestamp\tPayment [{mc.unit}]\tInterest [{mc.unit}]\tRemaining [{mc.unit}]")
            for i, (t, payment, interest, remaining) in enumerate(payments):
                print(f"{i+1}\t{t:.0f}\t{payment:.2f}\t{interest:.2f}\t{remaining:.2f}")


if __name__ == "__main__":
    unittest.main()
