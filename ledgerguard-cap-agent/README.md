# LedgerGuard-CAP-Agent
An autonomous, local-first Financial Reconciliation Agent designed for secure Web3 corporate accounting.

## Overview
Reconciling high-volume crypto payments against corporate invoices typically creates data leaks, compliance bottlenecks, and human error. LedgerGuard AI automates this by locally matching business ledgers with blockchain transactions to parse currency types, trace wallet histories, and immediately isolate financial discrepancies.

## Core Features
* **Privacy-Centric Architecture**: Runs locally to keep internal financial structures, client names, and balance sheets private.
* **Discrepancy Engine**: Autonomously tracks and flags accounting anomalies including:
    * **Underpayment Shortfalls**: Catches gas/network fee slips (e.g., matching expected tokens vs. actual received amount).
    * **Unpaid Records**: Flags expected invoices with missing on-chain history.
* **Agile Integration**: Designed to seamlessly expose local verification reports via lightweight API endpoints for marketplace auditing.

## Installation
1. Clone the repository:
   `git clone https://github.com/idriskinze86/ledgerguard-cap-agent`
2. Install dependencies:
   `npm install`

## Environment Setup
Create a `.env` file in the root directory and add your `BASE_RPC_URL`, `AGENT_PRIVATE_KEY`, `CROO_SERVICE_ID`, and `CROO_API_KEY`.

## Usage
To start the reconciliation polling daemon:
```bash
node src/agent.js
'''

To trigger a manual test reconciliation:
```bash
node src/test-trigger.js
'''


