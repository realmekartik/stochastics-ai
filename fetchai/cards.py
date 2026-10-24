"""
ASI:One Interactive Card Builder for StockPulse AI Agent.
Constructs rich, dynamic Agentverse Element-Tree UI cards with interactive
action buttons, badges, groups, and carousels directly inside ASI:One.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    MetadataContent,
    TextContent,
)
from stock_client import StockQuote
from technical_analysis import TechnicalReport, generate_technical_report

CARD_PROTOCOL_VERSION = "1"


def build_stock_overview_card(quote: StockQuote) -> Dict[str, Any]:
    """
    Builds the main interactive Stock Overview card with action buttons.
    """
    is_positive = quote.percent_change >= 0
    change_symbol = "+" if is_positive else ""
    badge_variant = "success" if is_positive else "danger"

    card_payload = {
        "root": {
            "type": "section",
            "title": f"{quote.symbol} - {quote.name}",
            "subtitle": f"Live Quote: ${quote.price:.2f} {quote.currency}",
            "children": [
                {
                    "type": "group",
                    "direction": "row",
                    "gap": 12,
                    "children": [
                        {
                            "type": "badge",
                            "label": f"{change_symbol}{quote.change:.2f} ({change_symbol}{quote.percent_change:.2f}%)",
                            "variant": badge_variant,
                        },
                        {
                            "type": "badge",
                            "label": f"Mkt Cap: {quote.market_cap}",
                            "variant": "info",
                        },
                        {
                            "type": "badge",
                            "label": f"P/E: {quote.pe_ratio:.1f}",
                            "variant": "warning",
                        },
                    ],
                },
                {
                    "type": "divider"
                },
                {
                    "type": "text",
                    "value": (
                        f"📊 52-Wk Range: ${quote.low_52w:.2f} - ${quote.high_52w:.2f} | "
                        f"Volume: {quote.volume} | Avg: {quote.avg_volume}\n\n"
                        f"{quote.description}"
                    ),
                    "style": "body",
                },
                {
                    "type": "group",
                    "direction": "row",
                    "gap": 8,
                    "children": [
                        {
                            "type": "button",
                            "label": "📈 Technicals",
                            "primary": True,
                            "action": {
                                "selection": {
                                    "action": "tech_indicators",
                                    "symbol": quote.symbol,
                                }
                            },
                        },
                        {
                            "type": "button",
                            "label": "⚡ AI Verdict",
                            "primary": True,
                            "action": {
                                "selection": {
                                    "action": "ai_verdict",
                                    "symbol": quote.symbol,
                                }
                            },
                        },
                        {
                            "type": "button",
                            "label": "🏢 Fundamentals",
                            "primary": False,
                            "action": {
                                "selection": {
                                    "action": "fundamentals",
                                    "symbol": quote.symbol,
                                }
                            },
                        },
                        {
                            "type": "button",
                            "label": "🔄 Compare Peers",
                            "primary": False,
                            "action": {
                                "selection": {
                                    "action": "compare_peers",
                                    "symbol": quote.symbol,
                                }
                            },
                        },
                    ],
                },
            ],
        }
    }
    return card_payload


def build_technical_card(report: TechnicalReport, quote: StockQuote) -> Dict[str, Any]:
    """
    Builds the Technical Analysis drill-down card.
    """
    rsi_variant = "danger" if report.rsi > 70 else ("success" if report.rsi < 35 else "info")

    card_payload = {
        "root": {
            "type": "section",
            "title": f"📈 Technical Indicators: {report.symbol}",
            "subtitle": f"Price: ${quote.price:.2f} | Trend: {report.trend_signal}",
            "children": [
                {
                    "type": "group",
                    "direction": "column",
                    "gap": 10,
                    "children": [
                        {
                            "type": "badge",
                            "label": f"RSI (14): {report.rsi} - {report.rsi_signal}",
                            "variant": rsi_variant,
                        },
                        {
                            "type": "badge",
                            "label": f"MACD: {report.macd_val:.2f} (Signal: {report.macd_signal:.2f}) -> {report.macd_bias}",
                            "variant": "info",
                        },
                        {
                            "type": "text",
                            "value": (
                                f"• SMA 20: ${report.sma_20:.2f}\n"
                                f"• SMA 50: ${report.sma_50:.2f}\n"
                                f"• SMA 200: ${report.sma_200:.2f}\n"
                                f"• Key Support Floor: ${report.support_level:.2f}\n"
                                f"• Resistance Target: ${report.resistance_level:.2f}"
                            ),
                            "style": "body",
                        },
                    ],
                },
                {
                    "type": "divider"
                },
                {
                    "type": "group",
                    "direction": "row",
                    "gap": 8,
                    "children": [
                        {
                            "type": "button",
                            "label": "⚡ View AI Verdict",
                            "primary": True,
                            "action": {
                                "selection": {
                                    "action": "ai_verdict",
                                    "symbol": report.symbol,
                                }
                            },
                        },
                        {
                            "type": "button",
                            "label": "◀ Back to Overview",
                            "primary": False,
                            "action": {
                                "selection": {
                                    "action": "overview",
                                    "symbol": report.symbol,
                                }
                            },
                        },
                    ],
                },
            ],
        }
    }
    return card_payload


def build_verdict_card(report: TechnicalReport, quote: StockQuote) -> Dict[str, Any]:
    """
    Builds the AI Trading Verdict and Recommendation card.
    """
    verdict_variant = "success" if "BUY" in report.verdict else ("warning" if "HOLD" in report.verdict else "danger")

    card_payload = {
        "root": {
            "type": "section",
            "title": f"⚡ AI Investment Verdict: {report.symbol}",
            "subtitle": f"Confidence Score: {report.confidence}% | Risk Profile: {report.risk_level}",
            "children": [
                {
                    "type": "badge",
                    "label": f"SIGNAL: {report.verdict}",
                    "variant": verdict_variant,
                },
                {
                    "type": "text",
                    "value": (
                        f"🎯 Price: ${quote.price:.2f}\n"
                        f"🛡️ Recommended Entry/Stop Support: ${report.support_level:.2f}\n"
                        f"🚀 Target Resistance: ${report.resistance_level:.2f}\n\n"
                        f"📝 AI Synthesis:\n{report.ai_reasoning}"
                    ),
                    "style": "body",
                },
                {
                    "type": "divider"
                },
                {
                    "type": "group",
                    "direction": "row",
                    "gap": 8,
                    "children": [
                        {
                            "type": "button",
                            "label": "📈 Technical Breakdown",
                            "primary": True,
                            "action": {
                                "selection": {
                                    "action": "tech_indicators",
                                    "symbol": report.symbol,
                                }
                            },
                        },
                        {
                            "type": "button",
                            "label": "◀ Back to Overview",
                            "primary": False,
                            "action": {
                                "selection": {
                                    "action": "overview",
                                    "symbol": report.symbol,
                                }
                            },
                        },
                    ],
                },
            ],
        }
    }
    return card_payload


def build_peer_comparison_card(quote: StockQuote) -> Dict[str, Any]:
    """
    Builds an interactive Peer Comparison card.
    """
    peers_map = {
        "NVDA": [("AMD", 156.40, 1.4), ("INTC", 22.80, -0.8), ("QCOM", 168.20, 0.9)],
        "AAPL": [("MSFT", 428.50, 0.5), ("GOOGL", 168.90, 1.1), ("AMZN", 188.30, 2.1)],
        "TSLA": [("BYD", 34.20, 1.2), ("RIVN", 10.45, -2.1), ("LCID", 2.85, -1.8)],
    }
    peer_list = peers_map.get(quote.symbol, [("SPY", 582.40, 0.6), ("QQQ", 495.10, 0.9), ("IWM", 222.10, 0.3)])

    items = []
    for sym, pr, chg in peer_list:
        items.append({
            "children": [
                {
                    "type": "group",
                    "direction": "row",
                    "gap": 10,
                    "children": [
                        {"type": "heading", "value": sym, "level": 3},
                        {"type": "badge", "label": f"${pr:.2f} ({'+' if chg >= 0 else ''}{chg}%)", "variant": "info" if chg >= 0 else "danger"},
                        {
                            "type": "button",
                            "label": f"Analyze {sym}",
                            "primary": True,
                            "action": {
                                "selection": {
                                    "action": "overview",
                                    "symbol": sym,
                                }
                            }
                        }
                    ]
                }
            ]
        })

    card_payload = {
        "root": {
            "type": "section",
            "title": f"🔄 Peer Comparison for {quote.symbol}",
            "subtitle": f"Tap any peer below to load complete AI stock intelligence",
            "children": [
                {
                    "type": "list",
                    "items": items
                },
                {
                    "type": "divider"
                },
                {
                    "type": "button",
                    "label": f"◀ Back to {quote.symbol} Overview",
                    "primary": False,
                    "action": {
                        "selection": {
                            "action": "overview",
                            "symbol": quote.symbol,
                        }
                    }
                }
            ]
        }
    }
    return card_payload


def wrap_card_message(preamble_text: str, card_payload: Dict[str, Any]) -> ChatMessage:
    """
    Constructs a dual-content ACP ChatMessage containing:
    1. TextContent: Human-readable markdown text intro
    2. MetadataContent: ASI:One dynamic element-tree interactive card
    """
    return ChatMessage(
        content=[
            TextContent(text=preamble_text),
            MetadataContent(
                metadata={
                    "card_protocol_version": CARD_PROTOCOL_VERSION,
                    "card_kind": "custom",
                    "card_payload": json.dumps(card_payload),
                }
            ),
        ]
    )
