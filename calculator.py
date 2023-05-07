#!/usr/bin/env python3

import humanfriendly as hf


class MortgageCalculator:
    debug = False
    size: float = 100000  # initial loan size
    rate: float = 4.5  # advertized rate in percent
    compound_period: float = hf.parse_timespan("1 year") / 2  # how often interest is compounded
    max_payment_size: float = 10000  # fixed payment size
    payment_period: float = hf.parse_timespan("1 year") / 12  # how often a payment is made
    period: float = hf.parse_timespan("0 years")  # duration of the mortgage TODO: calculate payment from duration

    def __init__(self, size: float = size, rate: float = rate, compound_period: float = compound_period, max_payment_size: float = max_payment_size, payment_period: float = payment_period, period: float = period):
        self.size = size
        print(f"Borrowed: {self.size}")
        self.rate = rate
        self.compound_period = compound_period
        self.max_payment_size = max_payment_size
        if self.max_payment_size:
            print(f"Pre-set payment: {self.max_payment_size}")
        self.payment_period = payment_period
        self.period = period
        if self.period:
            print(f"Pre-set mortgage length: {hf.format_timespan(period)}")
        assert not (self.period and self.max_payment_size), "Over constrained. Specifying both period and payment size is a no-no."
        compounds_per_year = hf.parse_timespan("1 year") / compound_period
        years_per_payment_period = self.payment_period / hf.parse_timespan("1year")
        self.EAR = (1 + self.rate / 100 / compounds_per_year) ** compounds_per_year - 1
        print(f"Effective Annual Rate (EAR): {self.EAR*100} [percent]")
        self.rate_for_payment = (1 + self.EAR) ** (years_per_payment_period) - 1

    def run(self):
        remaining = self.size
        t = 0
        total_paid = 0
        while remaining > 0:
            t = t + self.payment_period
            new_from_interest = self.rate_for_payment * remaining
            if self.debug:
                print(f"{new_from_interest=}")

            remaining = new_from_interest + remaining
            if remaining > self.max_payment_size:
                payment = self.max_payment_size
            else:
                payment = remaining

            if self.debug:
                print(f"Payment @{t=} is {payment}")
            remaining = remaining - payment
            total_paid += payment

        print(f"Total paid after {hf.format_timespan(t)}: {total_paid}")
        print(f"With payments made every {hf.format_timespan(self.payment_period)}")


def main():
    mc = MortgageCalculator(size=100000, rate=6.0, max_payment_size=639.81)
    mc.run()


if __name__ == "__main__":
    main()
