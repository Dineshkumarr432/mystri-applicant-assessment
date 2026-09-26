"""Starter checks exercise basic setup. They are not complete acceptance coverage."""
import tempfile
import unittest
from pathlib import Path
from ledger import storage, reporting, importing


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = storage.connect(Path(self.tmp.name) / 'demo.sqlite3')
        storage.seed(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_seed_is_repeatable(self):
        storage.seed(self.db)
        self.assertEqual(len(reporting.invoices(self.db)), 6)

    def test_seed_summary(self):
        summary = reporting.overview(self.db)['summary']
        self.assertEqual(summary['invoice_count'], 6)
        self.assertEqual(summary['outstanding'], 3209.99)

    def test_one_valid_invoice(self):
        result = importing.import_csv(self.db, 'customer_id,invoice_number,amount,due_date\nHARBOR,SMOKE-1,25.00,2026-09-09\n', 'invoices')
        self.assertEqual(result['imported'], 1)

    def test_payment_reference_when_amount_is_unique(self):
        result = importing.import_csv(self.db, 'payment_id,customer_id,invoice_number,amount\nSMOKE-P1,HARBOR,INV-100,20.00\n', 'payments')
        self.assertEqual(result['imported'], 1)
        invoice = next(r for r in reporting.invoices(self.db) if r['invoice_number'] == 'INV-100')
        self.assertEqual(invoice['paid'], 20.00)

    def test_open_filter_returns_only_positive_balance_invoices(self):
        result = reporting.invoices(self.db, status='open')

        self.assertTrue(result)

        for invoice in result:
            self.assertGreater(invoice['balance'], 0)

        self.assertEqual(len(result), 5)

    def test_overpaid_invoice_is_paid_not_open(self):
        result = importing.import_csv(
            self.db,
            'customer_id,invoice_number,amount,due_date\n'
            'HARBOR,OVERPAY-1,100.00,2026-09-20\n',
            'invoices'
        )
        self.assertEqual(result['imported'], 1)

        payment_result = importing.import_csv(
            self.db,
            'payment_id,customer_id,invoice_number,amount\n'
            'OVERPAY-P1,HARBOR,OVERPAY-1,120.00\n',
            'payments'
        )
        self.assertEqual(payment_result['imported'], 1)

        invoice = next(
            r for r in reporting.invoices(self.db)
            if r['invoice_number'] == 'OVERPAY-1'
        )

        self.assertEqual(invoice['balance'], -20.00)
        self.assertEqual(invoice['status'], 'paid')

    def test_export_has_header(self):
        self.assertTrue(reporting.export_csv(self.db).startswith('customer_id,invoice_number,amount,paid,balance,status'))

    def test_payment_matches_by_customer_and_invoice_not_amount(self):
        result = importing.import_csv(
            self.db,
            'payment_id,customer_id,invoice_number,amount\n'
            'MATCH-P1,HARBOR,INV-100,100.00\n',
            'payments'
        )

        self.assertEqual(result['imported'], 1)

        invoices = reporting.invoices(self.db)

        harbor = next(
            r for r in invoices
            if r['customer_id'] == 'HARBOR'
            and r['invoice_number'] == 'INV-100'
        )

        north = next(
            r for r in invoices
            if r['customer_id'] == 'NORTH'
            and r['invoice_number'] == 'INV-301'
        )

        self.assertEqual(harbor['paid'], 100.00)
        self.assertEqual(harbor['balance'], 1150.00)

        self.assertEqual(north['paid'], 0.00)
        self.assertEqual(north['balance'], 100.00)

if __name__ == '__main__':
    unittest.main()
