const express = require('express');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Main endpoint for the OKX Agent system to query
app.get('/api/reconcile', (req, res) => {
    try {
        const invoices = JSON.parse(fs.readFileSync('./company_invoices.json', 'utf8'));
        const transactions = JSON.parse(fs.readFileSync('./blockchain_txs.json', 'utf8'));
        
        let discrepancies = [];
        let reconciledCount = 0;

        invoices.forEach(invoice => {
            const matchedTx = transactions.find(tx => 
                tx.from_address.toLowerCase() === invoice.client_wallet.toLowerCase()
            );

            if (!matchedTx) {
                discrepancies.push({
                    invoice_id: invoice.invoice_id,
                    vendor: invoice.vendor_name,
                    issue: "UNPAID",
                    details: `Expected ${invoice.amount_due} ${invoice.currency}, but no on-chain transaction was found.`
                });
            } else {
                const amountDiff = invoice.amount_due - matchedTx.amount_paid;
                if (invoice.currency !== matchedTx.token_symbol) {
                    discrepancies.push({
                        invoice_id: invoice.invoice_id,
                        vendor: invoice.vendor_name,
                        issue: "CURRENCY_MISMATCH",
                        details: `Expected ${invoice.currency}, paid in ${matchedTx.token_symbol}.`
                    });
                } else if (amountDiff > 0) {
                    discrepancies.push({
                        invoice_id: invoice.invoice_id,
                        vendor: invoice.vendor_name,
                        issue: "UNDERPAYMENT",
                        details: `Shortfall of ${amountDiff.toFixed(2)} ${invoice.currency}.`
                    });
                } else {
                    reconciledCount++;
                }
            }
        });

        // Format response matching OKX AI Agent capabilities structure
        res.json({
            agent_status: "ACTIVE",
            agent_name: "LedgerGuard AI",
            timestamp: new Date().toISOString(),
            summary: {
                successfully_reconciled: reconciledCount,
                flagged_anomalies_count: discrepancies.length
            },
            anomalies: discrepancies
        });

    } catch (error) {
        res.status(500).json({ status: "ERROR", message: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`🤖 LedgerGuard Agent Service live on port ${PORT}`);
    console.log(`🔗 Target endpoint for OKX listing: http://localhost:${PORT}/api/reconcile`);
});
