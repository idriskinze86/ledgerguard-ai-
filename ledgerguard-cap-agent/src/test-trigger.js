const { AgentClient } = require('@croo-network/sdk');
require('dotenv').config();

async function triggerTestOrder() {
  const client = new AgentClient({
    baseURL: 'https://api.croo.network',
    wsURL: 'wss://api.croo.network/ws',
    // Using an alternative wallet string so you are a buyer, not the service owner
    privateKey: '0x1111111111111111111111111111111111111111111111111111111111111111',
    rpcUrl: process.env.BASE_RPC_URL
  }, process.env.CROO_API_KEY);

  console.log("🚀 Triggering test job from buyer perspective...");
  
  try {
    const res = await client.negotiateOrder({
      serviceId: process.env.CROO_SERVICE_ID,
      payload: {
        transactionId: "TX-99823",
        amount: 20000,
        currency: "NGN",
        description: "LedgerGuard-AI validation payload"
      }
    });
    console.log("🎯 Test job posted successfully:", res);
  } catch (error) {
    console.error("🔴 Trigger response:", error.message);
  }
}

triggerTestOrder();
