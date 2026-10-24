"""
StockPulse AI Agent - Main Entrypoint
Autonomous Market Intelligence & Technical Analysis Agent for ASI:One
Registered on Agentverse via Agent Chat Protocol (ACP).
"""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv
from uagents import Agent, Context

# Load environment configuration
load_dotenv()

from chat_proto import chat_proto
from stock_client import fetch_stock_quote

# Configure agent parameters
AGENT_NAME = os.getenv("AGENT_NAME", "StockPulse AI Agent")
AGENT_SEED = os.getenv("AGENT_SEED_PHRASE", "stockpulse-asi-agent-seed-2026")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))

# Initialize uAgent
agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=True,  # Enables Agentverse Mailbox for global discoverability on ASI:One
)

# Attach ACP (Agent Chat Protocol) and publish manifest
agent.include(chat_proto, publish_manifest=True)


@agent.on_event("startup")
async def startup_handler(ctx: Context):
    """
    Startup lifecycle hook.
    Displays agent address and registration status.
    """
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"🚀 {AGENT_NAME} is ONLINE!")
    ctx.logger.info(f"📍 Agent Address: {agent.address}")
    ctx.logger.info(f"🌐 Mailbox Endpoint Active: {agent.mailbox}")
    ctx.logger.info("💬 Agent Chat Protocol (ACP) Enabled")
    ctx.logger.info("📊 ASI:One Interactive Dynamic Cards Ready")
    ctx.logger.info("🔍 Discoverable on ASI:One via Agentverse")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
