#!/usr/bin/env node
/**
 * Kimi Agent — interactive CLI chat client
 * Run: npm run chat
 */

import readline from "readline";
import { KimiAgentClient } from "./api/client.js";

const client = new KimiAgentClient();

async function main() {
  // Health check
  try {
    const health = await client.health();
    console.log(`\n🤖 Kimi Agent ready  (model: ${health.model})\n`);
  } catch {
    console.error("❌ Cannot reach API at", process.env.API_BASE_URL || "http://localhost:8000");
    console.error("   Make sure the backend is running: uvicorn main:app --reload");
    process.exit(1);
  }

  const sessionId = await client.newSession();
  console.log(`📝 Session: ${sessionId}`);
  console.log('Type "exit" to quit, "history" to view chat, "clear" to reset session.\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const ask = () => {
    rl.question("You: ", async (input) => {
      const trimmed = input.trim();
      if (!trimmed) return ask();

      if (trimmed === "exit") {
        console.log("\n👋 Bye!");
        rl.close();
        return;
      }

      if (trimmed === "history") {
        const hist = await client.getHistory(sessionId);
        console.log(`\n--- History (${hist.total} messages) ---`);
        hist.messages.forEach((m) => console.log(`[${m.role}] ${m.content.slice(0, 120)}...`));
        console.log("---\n");
        return ask();
      }

      if (trimmed === "clear") {
        await client.clearSession(sessionId);
        console.log("🗑️  Session cleared.\n");
        return ask();
      }

      try {
        process.stdout.write("Kimi: ");
        const res = await client.chat({
          session_id: sessionId,
          message: trimmed,
          use_search: true,
        });
        console.log(res.reply);
        if (res.sources?.length) {
          console.log("\n🔗 Sources:", res.sources.slice(0, 3).join("\n         "));
        }
        console.log();
      } catch (err: any) {
        console.error("Error:", err.message);
      }

      ask();
    });
  };

  ask();
}

main();
