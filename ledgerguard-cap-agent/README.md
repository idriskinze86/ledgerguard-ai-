# LedgerGuard-CAP-Agent
A secure, AI-native financial reconciliation agent built for the CROO Agent Protocol.

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


