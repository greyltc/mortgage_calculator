#!/usr/bin/env python3

import humanfriendly as hf
import sys
import mortgage_calculator
import argparse
from typing import Optional, Sequence
from fpdf import FPDF
import time
import pathlib


def _get_main_parser() -> argparse.ArgumentParser:
    """Construct the main parser."""
    parser = argparse.ArgumentParser(description="crunch mortgage numbers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--size",
        "-s",
        type=float,
        default=mortgage_calculator.MortgageCalculator.size,
        help="mortgage size",
    )
    parser.add_argument(
        "--rate",
        "-r",
        type=float,
        default=mortgage_calculator.MortgageCalculator.rate,
        help="advertised interest rate [percent]",
    )
    parser.add_argument(
        "--compound-period",
        "-c",
        type=float,
        default=mortgage_calculator.MortgageCalculator.compound_period,
        help="compoind period [s]",
    )
    parser.add_argument(
        "--max-payment-size",
        "-p",
        type=float,
        default=mortgage_calculator.MortgageCalculator.max_payment_size,
        help="fix the upper limit for a single payment",
    )
    parser.add_argument(
        "--payment-period",
        "-i",
        type=float,
        default=mortgage_calculator.MortgageCalculator.payment_period,
        help="time between regular payments [s]",
    )
    parser.add_argument(
        "--duration",
        "-d",
        default=hf.format_timespan(mortgage_calculator.MortgageCalculator.duration),
        help="fix the duration of the loan",
    )
    parser.add_argument(
        "--unit",
        "-u",
        default=mortgage_calculator.MortgageCalculator.unit,
        help="monetary unit",
    )
    parser.add_argument(
        "--bank-name",
        "-b",
        help="name of loaner",
    )
    parser.add_argument(
        "--borrower-name",
        "-w",
        help="name of borrower",
    )
    parser.add_argument(
        "--register-new-payment",
        "-n",
        nargs=3,
        type=float,
        metavar=("last_timestamp", "last_remaining", "payment_size"),
        help="register a payment against an existing loan and generate a payment report pdf",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="print more details",
    )

    return parser


def _main(cli_args: Sequence[str], program: Optional[str] = None) -> None:
    """Process arguments and do calcs"""
    parser = _get_main_parser()
    if program:
        parser.prog = program
    args = parser.parse_args(cli_args)

    inputs = {}
    inputs["size"] = args.size
    inputs["rate"] = args.rate
    inputs["compound_period"] = args.compound_period
    inputs["max_payment_size"] = args.max_payment_size
    inputs["payment_period"] = args.payment_period
    inputs["duration"] = hf.parse_timespan(args.duration)
    inputs["unit"] = args.unit
    inputs["debug"] = args.verbose

    mc = mortgage_calculator.MortgageCalculator(**inputs)
    if args.register_new_payment:
        # register a single payment and generate a report for it
        then, remaining, payment = args.register_new_payment
        remaining = round(remaining * 100)
        payment = round(payment * 100)

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(w=0, text="LOAN REPAYMENT REPORT", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(size=12)
        if args.borrower_name and args.bank_name:
            pdf.cell(text=f"This report records a payment from {args.borrower_name} to The Bank of The {args.bank_name}.", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(text=f"It concerns a loan with an Effective Annual Interest Rate of {mc.EAR*100:0.3f}%.", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

        if not payment:  # if payment is zero, then take this to be the initial report
            now = then
        else:
            now = mc.now()
        dt = now - then

        pdf.set_font(style="B")
        pdf.cell(text=f"Time of this payment: ")
        pdf.set_font(style="")
        pdf.cell(text=time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(now)), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(style="B")
        pdf.cell(text=f"Time of previous payment: ")
        pdf.set_font(style="")
        pdf.cell(text=time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(then)), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(style="B")
        pdf.cell(text=f"Time between payments: ")
        pdf.set_font(style="")
        pdf.cell(text= f"{int(dt)} seconds (or approximately {hf.format_timespan(dt)})", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(style="B")
        pdf.cell(text=f"Amount remaining after previous payment: ")
        pdf.set_font(style="")
        pdf.cell(text=f"{remaining/100:,.2f} {mc.unit}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

        payment, new_remaining = mc.process_payment(dt, remaining, maxp=payment)
        principal_paydown = remaining - new_remaining
        if principal_paydown > 0:
            interest_paid = payment - principal_paydown
        else:
            interest_paid = payment

        pdf.set_font(style="B")
        pdf.cell(text=f"Value of this payment: ")
        pdf.set_font(style="")
        pdf.cell(text=f"{payment/100:,.2f} {mc.unit}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(style="B")
        pdf.cell(text=f"Amount of this payment that went to interest: ")
        pdf.set_font(style="")
        pdf.cell(text=f"{interest_paid/100:,.2f} {mc.unit}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(text=" ", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(style="B")
        pdf.cell(text=f"Total left to pay: ")
        pdf.set_font(style="")
        pdf.cell(text=f"{new_remaining/100:,.2f} {mc.unit}", new_x="LMARGIN")

        pdf.set_y(-25)
        pdf.set_font("helvetica", size=6)
        lnk = "https://github.com/greyltc/mortgage_calculator"
        pdf.write_html(f'Made with <a href="{lnk}">{lnk}</a>')

        pdf.set_y(-28)
        if program:
            teh_cli = " ".join([program] + list(cli_args))
        else:
            teh_cli = " ".join(cli_args)

        pdf.cell(w=0, text=f"Via: {teh_cli}", align="R", new_y="NEXT")
        pdf.cell(w=0, text=f"Next: -n {now} {new_remaining/100} X", align="R")

        iso_date = time.strftime("%Y-%m-%d", time.gmtime(now))
        name_list = [iso_date]
        if args.borrower_name:
            name_list += args.borrower_name.split()
        name_list.append("paid")
        name_list.append(f"{payment/100:.0f}{mc.unit}")
        report_file_name = "_".join(name_list)
        report_file_name += ".pdf"
        out_path = pathlib.Path(".") / report_file_name
        pdf.output(str(out_path.resolve()))
        print(f"Payment Report file written to file://{out_path.resolve()}")

        payments = []
    else:
        # do mortgage simulations
        payments = mc.run()

    if mc.debug:
        print(f"#\tTimestamp\tPayment [{mc.unit}]\tInterest [{mc.unit}]\tRemaining [{mc.unit}]")
        for i, (t, payment, interest, remaining) in enumerate(payments):
            print(f"{i+1}\t{t:.0f}\t{payment:.2f}\t{interest:.2f}\t{remaining:.2f}")


if __name__ == "__main__":
    _main(sys.argv[1:], "python3 -m mortgage_calculator")
