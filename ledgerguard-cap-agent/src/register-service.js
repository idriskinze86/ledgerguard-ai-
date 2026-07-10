const { AgentClient } = require('@croo-network/sdk');
require('dotenv').config();

async function registerAgentService() {
  // Use your newly generated master key here
  const client = new AgentClient({
    baseURL: 'https://api.croo.network',
    wsURL: 'wss://api.croo.network/ws',
    privateKey: process.env.AGENT_PRIVATE_KEY,
    rpcUrl: process.env.BASE_RPC_URL
  }, process.env.CROO_API_KEY);

  console.log("🛠️ Registering LedgerGuard-AI service on CROO Network...");

  try {
    // Calling the core endpoint to register your agent profile capability
    const res = await client.hc.do({
      method: 'POST',
      path: '/services',
      authType: 'sdk-key',
      authVal: client.sdkKey,
      body: {
        name: "LedgerGuard-AI Audit Service",
        description: "Autonomous real-time financial reconciliation and transaction auditing provider.",
        price: "0.5", // Standard USDC interaction fee on Base
        sla: "0h30m",
        deliverableType: "text",
        requirements: "text"
      }
    });

    console.log("\n🎯 Registration Successful!");
    console.log("=========================================");
    console.log("Your New CROO_SERVICE_ID is:", res.id || res.service?.id);
    console.log("=========================================");
  } catch (error) {
    console.error("🔴 Registration failed:", error.message);
  }
}

registerAgentService();
