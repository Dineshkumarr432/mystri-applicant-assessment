alrear# Handover

- Name: R.Dinesh Kumar
- Email used for this application: dineshkumarr432@gmail.com
- Chosen track: Track A
- Why this track (one or two sentences):I chose this track to gain practical experience debugging and improving a real-world application involving APIs, databases, validation, and payment processing.
- Approximate total time, including setup and handover: Almost 4 hours

## Run and verify

From the `track-a` directory:

```powershell
python app.py
```

The application starts at:

```text
http://127.0.0.1:8787
```

To run the automated tests:

```powershell
python -m unittest discover -s tests -v
```

Final test result:

```text
Ran 8 tests in 0.327s

OK
```

The supplied existing register was also restored and verified with:

- Total invoices: 9
- Open invoices: 7
- Outstanding: ₹3,698.19

Manual import scenarios were tested for valid imports, duplicate records, conflicting records, unmatched payments, overpayments, invalid headers, invalid data rows, and persistence after application restart.

## What I delivered

I repaired the ClearLedger invoice and payment import and reporting behavior to follow the provided specification.

Key changes include:

- Prevented duplicate invoices using `(customer_id, invoice_number)` as the invoice identity.
- Identical invoice re-imports are skipped.
- Invoice identity conflicts with different amount or due date are rejected.
- Prevented duplicate payment IDs.
- Identical payment re-imports are skipped.
- Conflicting payment IDs are rejected.
- Corrected payment matching to use both customer ID and invoice number instead of amount alone.
- Preserved valid unmatched payments for review.
- Correctly calculated invoice paid amount, balance, and status.
- Correctly handled overpayments as paid invoices with negative balances.
- Preserved open/paid filtering behavior.
- Preserved the required HTTP API routes and response fields.
- Improved import result handling so imported, skipped, and rejected counts are reported.
- Verified that imported data survives an application restart.

## Evidence and limits

### Evidence

The final automated test suite passed all 8 available tests:

```text
test_export_has_header ... ok
test_one_valid_invoice ... ok
test_open_filter_returns_only_positive_balance_invoices ... ok
test_overpaid_invoice_is_paid_not_open ... ok
test_payment_matches_by_customer_and_invoice_not_amount ... ok
test_payment_reference_when_amount_is_unique ... ok
test_seed_is_repeatable ... ok
test_seed_summary ... ok
```

Result:

```text
Ran 8 tests in 0.327s
OK
```

The supplied register was restored and verified with 9 invoices, 7 open invoices, and ₹3,698.19 outstanding.

Manual verification also confirmed duplicate handling, conflicting-record rejection, unmatched payments, overpayments, import validation, and restart persistence.

### Limits

The following remain outside the scope of this assessment:

- Tax
- FX
- Credit notes
- Due-date aging
- Authentication
- Production deployment
- Huge datasets
- Simultaneous writers
- Malformed CSV quoting and embedded-newline handling
- Automatic rematching of previously unmatched payments

The specification explicitly states that automatically rematching an unmatched payment after a future invoice import is outside scope.

## Tools and judgment

### Tools used

- Python 3.14
- SQLite
- Python `unittest`
- PowerShell
- Browser-based ClearLedger UI
- Git/project source files provided with the assessment

No additional third-party Python packages were required.

### Engineering judgment

The existing public HTTP API and response field names were preserved.

Changes were focused on correcting the underlying invoice identity, payment identity, payment matching, balance calculation, import validation, and duplicate-handling behavior rather than replacing the application architecture.

The supplied existing register was preserved during verification. Temporary test records created during manual testing were cleaned up before restoring the supplied fixture for final verification.

The final implementation was validated through both the provided automated tests and manual end-to-end import/restart checks.