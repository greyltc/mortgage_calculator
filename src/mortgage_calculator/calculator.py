import humanfriendly as hf
from scipy.optimize import minimize_scalar
from typing import TypedDict

import socket
import struct
import time


class MortgageCalculator:
    debug = False
    size: float = 100000  # initial loan size
    rate: float = 4.5  # advertized rate in percent
    compound_period: float = hf.parse_timespan("1 year")  # how often interest is compounded
    max_payment_size: float = 10000  # fixed payment size
    payment_period: float = hf.parse_timespan("1 year") / 12  # how often a payment is made
    duration: float = hf.parse_timespan("0 years")  # duration of the mortgage
    unit: str = "EUR"
    seconds_per_year: float = hf.parse_timespan("1 year")

    def __init__(
        self,
        size: float = size,
        rate: float = rate,
        compound_period: float = compound_period,
        max_payment_size: float = max_payment_size,
        payment_period: float = payment_period,
        duration: float = duration,
        unit: str = unit,
        debug: bool = debug,
    ):
        self.size = size
        print(f"Borrowed: {self.size} {self.unit}")
        self.rate = rate
        self.compound_period = compound_period
        self.max_payment_size = max_payment_size
        if self.max_payment_size:
            print(f"Pre-set maximum payment: {self.max_payment_size} {self.unit}")
        self.payment_period = payment_period
        self.duration = duration
        if self.duration:
            print(f"Pre-set maximum mortgage length: {hf.format_timespan(duration)}")
        assert not (self.duration and self.max_payment_size), "Over constrained. Specifying both duration and payment size is a no-no."
        assert self.duration or self.max_payment_size, "Under constrained. One of duration or payment size must be given."
        self.unit = unit
        compounds_per_year = hf.parse_timespan("1 year") / compound_period
        years_per_payment_period = self.payment_period / hf.parse_timespan("1 year")
        self.EAR = (1 + self.rate / 100 / compounds_per_year) ** compounds_per_year - 1
        print(f"Effective Annual Rate (EAR): {self.EAR*100} percent")
        self.rate_for_payment = (1 + self.EAR) ** (years_per_payment_period) - 1
        self.max_payment_size_i = round(self.max_payment_size * 100)
        self.debug = debug

    def process_payment(self, dt: float, remaining: int, maxp: int, force=False) -> tuple[int, int]:
        """process one payment"""
        rate_for_payment = (1 + self.EAR) ** (dt / self.seconds_per_year) - 1
        new_from_interest = round(rate_for_payment * remaining)

        if self.debug:
            print(f"{new_from_interest/100=} {self.unit}")

        remaining = new_from_interest + remaining
        if (remaining > maxp) or (force):
            payment: int = maxp
        else:
            payment: int = remaining

        return (payment, remaining - payment)

    def now(self) -> float:
        """returns number of seconds since 1970 started"""
        addr = "pool.ntp.org"
        REF_TIME_1970 = 2208988800  # Reference time
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b"\x1b" + 47 * b"\0"
        try:
            client.sendto(data, (addr, 123))
            data, address = client.recvfrom(1024)
            t = struct.unpack("!12I", data)[10]
            t -= REF_TIME_1970
        except:
            t = time.time()

        # pt = time.ctime(t)
        return t

    def run(self) -> list[tuple[float, float, float, float]]:
        # we're gonna do all these calcs with intiger data types in hundreths of a monetary unit
        # to avoid machine precision/rounding issues
        remaining: int = round(self.size * 100)
        t = self.now()
        t0 = t
        total_paid: int = 0

        if self.duration:  # a mortgage simulation with a user-set duration
            n_payments = int(self.duration / self.payment_period)
            print(f"Maximum duration loan of {hf.format_timespan(self.duration)}")
            print(f"With payments made every {hf.format_timespan(self.payment_period)}")
            print(f"Results in {n_payments} payments and an actual duration of {hf.format_timespan(n_payments*self.payment_period)}")

            # a function for the optimizer
            def do_fixed(at_most: int, tdelta: float, left: int) -> int:
                for i in range(n_payments):
                    payment, left = self.process_payment(tdelta, left, at_most, force=True)
                return left

            res = minimize_scalar(lambda x: abs(do_fixed(x, self.payment_period, remaining)))
            if res.success:
                self.max_payment_size_i = round(res.x)
                print(f"Discovered payment value: {self.max_payment_size_i/100} {self.unit}")
            else:
                raise RuntimeError("Unable to discover appropraite payment to complete the loan in the target time.")

        # now do the simulation
        payments = []
        while remaining > 0:
            dt = self.payment_period
            t += dt
            payment, new_remaining = self.process_payment(dt, remaining, self.max_payment_size_i)
            principal_paydown = remaining - new_remaining
            assert principal_paydown > 0, "This loan will never end."
            interest = payment - principal_paydown
            payments.append((t, payment / 100, interest / 100, new_remaining / 100))
            remaining = new_remaining
            if self.debug:
                print(f"Payment @{t=} is {payment/100} {self.unit}")

            total_paid = total_paid + payment

        print(f"Total paid after {hf.format_timespan(t-t0)}: {total_paid/100} {self.unit}")
        print(f"With payments made every {hf.format_timespan(self.payment_period)}")

        return payments
