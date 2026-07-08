const fs = require('fs');

// Load our finalized data schemas
const invoices = require('./company_invoices.json');
const transactions = require('./blockchain_txs.json');

console.log("==================================================");
const dateTimeStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
console.log(`🤖 LEDGERGUARD AI: AUTONOMOUS RECONCILIATION RUN - ${dateTimeStr}`);
console.log("==================================================\n");

let discrepancies = [];
let reconciledCount = 0;

// Match invoices with transactions
invoices.forEach(invoice => {
    // Find a transaction matching the client's wallet address
    const matchedTx = transactions.find(tx => 
        tx.from_address.toLowerCase() === invoice.client_wallet.toLowerCase()
    );

    if (!matchedTx) {
        // Condition 1: No payment trace found
        discrepancies.push({
            invoice_id: invoice.invoice_id,
            vendor: invoice.vendor_name,
            issue: "UNPAID",
            details: `Expected ${invoice.amount_due} ${invoice.currency}, but no on-chain transaction was found for this wallet.`
        });
    } else {
        // Condition 2: Check for currency or amount mismatches
        const amountDiff = invoice.amount_due - matchedTx.amount_paid;
        
        if (invoice.currency !== matchedTx.token_symbol) {
            discrepancies.push({
                invoice_id: invoice.invoice_id,
                vendor: invoice.vendor_name,
                issue: "CURRENCY_MISMATCH",
                details: `Invoice requests ${invoice.currency}, but payment was settled in ${matchedTx.token_symbol}.`
            });
        } else if (amountDiff > 0) {
            discrepancies.push({
                invoice_id: invoice.invoice_id,
                vendor: invoice.vendor_name,
                issue: "UNDERPAYMENT (SHORTFALL)",
                details: `Shortfall of ${amountDiff.toFixed(2)} ${invoice.currency}. Expected ${invoice.amount_due}, Paid ${matchedTx.amount_paid}. (Likely unallocated gas/network fee slip).`
            });
        } else {
            reconciledCount++;
        }
    }
});

// Output Autonomous Audit Report
console.log("📊 --- SUMMARY REPORT ---");
console.log(`✅ Successfully Reconciled: ${reconciledCount} Invoice(s)`);
console.log(`⚠️ Flagged Discrepancies: ${discrepancies.length}\n`);

if (discrepancies.length > 0) {
    console.log("🚨 --- DETECTED ANOMALIES ---");
    discrepancies.forEach((d, index) => {
        console.log(`[${index + 1}] ID: ${d.invoice_id} | ${d.vendor}`);
        console.log(`    TYPE: ${d.issue}`);
        console.log(`    LOG:  ${d.details}\n`);
    });
}

console.log("==================================================");
console.log("🎯 Audit Complete. Report ready to sign and broadcast to OKX Task Marketplace.");
console.log("==================================================");
