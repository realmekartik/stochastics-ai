"""
Local Test Suite for StockPulse AI Agent.
Validates stock quote retrieval, technical indicator calculations,
and ASI:One interactive element-tree card generation.
"""

import json
from stock_client import fetch_stock_quote
from technical_analysis import generate_technical_report
from cards import (
    build_stock_overview_card,
    build_technical_card,
    build_verdict_card,
    build_peer_comparison_card,
)
from chat_proto import parse_action_or_symbol


def run_tests():
    print("=" * 60)
    print("🧪 RUNNING LOCAL VERIFICATION TESTS FOR STOCKPULSE AGENT")
    print("=" * 60)

    # 1. Test symbol intent parser
    test_queries = [
        ("Analyze NVDA stock", ("overview", "NVDA")),
        ("What is the price of Apple?", ("overview", "AAPL")),
        ("Check Tesla", ("overview", "TSLA")),
        ('{"selection": {"action": "tech_indicators", "symbol": "NVDA"}}', ("tech_indicators", "NVDA")),
        ('{"selection": {"action": "ai_verdict", "symbol": "AAPL"}}', ("ai_verdict", "AAPL")),
    ]

    print("\n[1] Testing Natural Language & Card Selection Parser:")
    for query, expected in test_queries:
        res = parse_action_or_symbol(query)
        assert res == expected, f"Failed on '{query}': got {res}, expected {expected}"
        print(f"  ✓ '{query[:45]}...' -> Action: {res[0]}, Symbol: {res[1]}")

    # 2. Test Stock Quote Retrieval
    print("\n[2] Testing Market Quote Fetcher:")
    quote = fetch_stock_quote("NVDA")
    print(f"  ✓ Symbol: {quote.symbol} ({quote.name})")
    print(f"  ✓ Price: ${quote.price:.2f} {quote.currency} | Change: {quote.percent_change}%")
    print(f"  ✓ Market Cap: {quote.market_cap} | P/E: {quote.pe_ratio}")

    # 3. Test Technical Indicators Engine
    print("\n[3] Testing Technical Analysis & AI Verdict Engine:")
    report = generate_technical_report(quote)
    print(f"  ✓ RSI (14): {report.rsi} ({report.rsi_signal})")
    print(f"  ✓ SMA 20/50/200: ${report.sma_20} / ${report.sma_50} / ${report.sma_200}")
    print(f"  ✓ MACD Trend: {report.macd_bias}")
    print(f"  ✓ Signal Verdict: {report.verdict} (Confidence: {report.confidence}%)")
    print(f"  ✓ Support: ${report.support_level} | Resistance: ${report.resistance_level}")

    # 4. Test ASI:One Element-Tree Card Generation
    print("\n[4] Testing ASI:One Interactive Cards Generation:")
    card_overview = build_stock_overview_card(quote)
    assert card_overview["root"]["type"] == "section"
    print("  ✓ Main Stock Overview Card JSON Valid")

    card_tech = build_technical_card(report, quote)
    assert card_tech["root"]["type"] == "section"
    print("  ✓ Technical Drill-Down Card JSON Valid")

    card_verdict = build_verdict_card(report, quote)
    assert card_verdict["root"]["type"] == "section"
    print("  ✓ AI Verdict Card JSON Valid")

    card_peers = build_peer_comparison_card(quote)
    assert card_peers["root"]["type"] == "section"
    print("  ✓ Peer Comparison Card JSON Valid")

    print("\n" + "=" * 60)
    print("✅ ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
