"""
Agent Chat Protocol (ACP) implementation for StockPulse AI Agent.
Handles incoming ACP ChatMessages, extracts intent/symbols, processes
interactive card button selections, and replies with dynamic UI cards.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple
from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from cards import (
    build_peer_comparison_card,
    build_stock_overview_card,
    build_technical_card,
    build_verdict_card,
    wrap_card_message,
)
from stock_client import StockQuote, fetch_stock_quote
from technical_analysis import generate_technical_report

logger = logging.getLogger("ChatProto")
chat_proto = Protocol(spec=chat_protocol_spec)

# Session tracking constants
CURRENT_SYMBOL_KEY = "stock:current_symbol"


def parse_action_or_symbol(text: str) -> Tuple[str, str]:
    """
    Parses incoming message text which can either be:
    1. A raw JSON selection from an ASI:One button click: {"selection": {"action": "...", "symbol": "..."}}
    2. A plain text natural language query: "Analyze NVDA", "Check Apple", "TSLA stock price"
    """
    clean_text = text.strip()

    # 1. Check for JSON button click payload
    if "selection" in clean_text or clean_text.startswith("{"):
        try:
            # If payload is wrapped in prose, find the json part
            start = clean_text.find("{")
            end = clean_text.rfind("}") + 1
            if start != -1 and end != 0:
                data = json.loads(clean_text[start:end])
                sel = data.get("selection", data)
                action = sel.get("action", "overview")
                symbol = sel.get("symbol", "NVDA").upper()
                return action, symbol
        except Exception as e:
            logger.debug(f"JSON parse error on card selection: {e}")

    # 2. Extract potential stock ticker symbol using regex
    # Common words exclusion list
    STOPWORDS = {"ANALYZE", "CHECK", "STOCK", "PRICE", "SHARE", "BUY", "SELL", "WHAT", "HOW", "IS", "THE", "PLEASE", "SHOW", "ME", "FOR", "OF"}
    tokens = re.findall(r"\b[A-Za-z]{1,5}\b", clean_text.upper())
    candidate_symbol = None
    for token in tokens:
        if token not in STOPWORDS and len(token) >= 2:
            candidate_symbol = token
            break

    # Natural language company name aliases
    lower = clean_text.lower()
    if "nvidia" in lower:
        candidate_symbol = "NVDA"
    elif "apple" in lower:
        candidate_symbol = "AAPL"
    elif "tesla" in lower:
        candidate_symbol = "TSLA"
    elif "microsoft" in lower:
        candidate_symbol = "MSFT"
    elif "google" in lower or "alphabet" in lower:
        candidate_symbol = "GOOGL"

    symbol = candidate_symbol or "NVDA"
    return "overview", symbol


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Primary ACP message handler.
    Receives chat messages from ASI:One users or coordinating agents,
    orchestrates financial analysis tools, and renders interactive cards.
    """
    # 1. Send immediate delivery acknowledgement to ASI:One
    await ctx.send(sender, ChatAcknowledgement(message_id=msg.message_id))

    # 2. Extract text content from incoming ACP message
    incoming_text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            incoming_text += item.text
        elif isinstance(item, StartSessionContent):
            logger.info("Session started with sender: %s", sender)

    if not incoming_text.strip():
        # Default welcome prompt if session starts with empty prompt
        incoming_text = "NVDA"

    # 3. Determine requested action & ticker symbol
    action, symbol = parse_action_or_symbol(incoming_text)
    ctx.storage.set(CURRENT_SYMBOL_KEY, symbol)
    logger.info(f"Processing query | Action: {action} | Symbol: {symbol} | From: {sender}")

    # 4. Fetch market data & compute quantitative indicators
    quote: StockQuote = fetch_stock_quote(symbol)
    report = generate_technical_report(quote)

    # 5. Route to appropriate ASI:One card view
    if action == "tech_indicators":
        preamble = (
            f"Here is the deep technical analysis for **{quote.symbol}** (${quote.price:.2f}). "
            f"RSI currently registers at {report.rsi} with {report.macd_bias.lower()}."
        )
        card_payload = build_technical_card(report, quote)

    elif action == "ai_verdict":
        preamble = (
            f"⚡ **AI Investment Verdict for {quote.symbol}**: **{report.verdict}** "
            f"(Confidence: {report.confidence}%, Risk: {report.risk_level})."
        )
        card_payload = build_verdict_card(report, quote)

    elif action == "compare_peers":
        preamble = f"Here is how **{quote.symbol}** compares against its industry peers and benchmarks:"
        card_payload = build_peer_comparison_card(quote)

    elif action == "fundamentals":
        preamble = (
            f"🏢 **Fundamental Health for {quote.name} ({quote.symbol})**:\n"
            f"• Market Capitalization: {quote.market_cap}\n"
            f"• P/E Ratio: {quote.pe_ratio:.1f}\n"
            f"• 52-Week Range: ${quote.low_52w:.2f} - ${quote.high_52w:.2f}\n"
            f"• 24h Volume: {quote.volume}"
        )
        card_payload = build_stock_overview_card(quote)

    else:
        # Default: Main Interactive Overview Card
        preamble = (
            f"I have analyzed **{quote.name} ({quote.symbol})** currently trading at **${quote.price:.2f} {quote.currency}** "
            f"({'+' if quote.percent_change >= 0 else ''}{quote.percent_change:.2f}%). "
            f"Tap any button on the card below to explore technicals, AI signals, or peer comparisons."
        )
        card_payload = build_stock_overview_card(quote)

    # 6. Send the rich interactive card back to ASI:One
    response_msg = wrap_card_message(preamble, card_payload)
    await ctx.send(sender, response_msg)
