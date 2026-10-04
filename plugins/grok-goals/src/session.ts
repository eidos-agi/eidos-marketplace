import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createGoalsServer } from "./server.js";
import { SERVER_VERSION } from "./version.js";

export async function connectGoalsClient(packRoot: string): Promise<{
  client: Client;
  close: () => Promise<void>;
}> {
  const { server } = await createGoalsServer({ packRoot });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client(
    { name: "grok-goals-client", version: SERVER_VERSION },
    { capabilities: {} },
  );
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return {
    client,
    close: async () => {
      await client.close();
      await server.close();
    },
  };
}
