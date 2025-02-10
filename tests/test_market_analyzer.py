"""Tests for market analysis functionality"""
from datetime import datetime, timedelta
import pytest

from space_traders_api_client.models.activity_level import ActivityLevel
from space_traders_api_client.models.market import Market
from space_traders_api_client.models.market_trade_good import (
    MarketTradeGood
)
from space_traders_api_client.models.market_trade_good_type import (
    MarketTradeGoodType
)
from space_traders_api_client.models.supply_level import SupplyLevel
from space_traders_api_client.models.trade_symbol import TradeSymbol

from game.market_analyzer import (
    MarketAnalyzer,
    MarketPriceHistory,
    TradeOpportunity
)


@pytest.fixture
def mock_market_trade_good():
    """Create a mock market trade good"""
    return MarketTradeGood(
        symbol=TradeSymbol.IRON_ORE,
        type_=MarketTradeGoodType.EXPORT,
        trade_volume=100,
        supply=SupplyLevel.HIGH,
        activity=ActivityLevel.STRONG,
        purchase_price=50,
        sell_price=100
    )


@pytest.fixture
def mock_market():
    """Create a mock market"""
    return Market(
        symbol="TEST_MARKET",
        exports=[],
        imports=[],
        exchange="TEST_EXCHANGE",
        trade_goods=[
            MarketTradeGood(
                symbol=TradeSymbol.IRON_ORE,
                type_=MarketTradeGoodType.EXPORT,
                trade_volume=100,
                supply=SupplyLevel.HIGH,
                activity=ActivityLevel.STRONG,
                purchase_price=50,
                sell_price=100
            ),
            MarketTradeGood(
                symbol=TradeSymbol.PRECIOUS_STONES,
                type_=MarketTradeGoodType.IMPORT,
                trade_volume=50,
                supply=SupplyLevel.LIMITED,
                activity=ActivityLevel.WEAK,
                purchase_price=200,
                sell_price=300
            )
        ]
    )


def test_market_price_history_initialization():
    """Test MarketPriceHistory initialization"""
    history = MarketPriceHistory(
        market_symbol="TEST_MARKET",
        trade_symbol=TradeSymbol.IRON_ORE,
        purchase_prices=[],
        sell_prices=[],
        volumes=[],
        supply_levels=[],
        activity_levels=[]
    )

    assert history.market_symbol == "TEST_MARKET"
    assert history.trade_symbol == TradeSymbol.IRON_ORE
    assert len(history.purchase_prices) == 0
    assert len(history.sell_prices) == 0


def test_market_price_history_add_snapshot(mock_market_trade_good):
    """Test adding market data snapshots"""
    history = MarketPriceHistory(
        market_symbol="TEST_MARKET",
        trade_symbol=TradeSymbol.IRON_ORE,
        purchase_prices=[],
        sell_prices=[],
        volumes=[],
        supply_levels=[],
        activity_levels=[]
    )

    timestamp = datetime.now()
    history.add_snapshot(mock_market_trade_good, timestamp)

    assert len(history.purchase_prices) == 1
    assert history.purchase_prices[0] == (timestamp, 50)
    assert len(history.sell_prices) == 1
    assert history.sell_prices[0] == (timestamp, 100)
    assert history.supply_levels[0] == (timestamp, SupplyLevel.HIGH)


def test_market_price_history_get_price_trend():
    """Test price trend calculation"""
    history = MarketPriceHistory(
        market_symbol="TEST_MARKET",
        trade_symbol=TradeSymbol.IRON_ORE,
        purchase_prices=[],
        sell_prices=[],
        volumes=[],
        supply_levels=[],
        activity_levels=[]
    )

    # Add price data over time
    base_time = datetime.now() - timedelta(hours=24)
    history.purchase_prices = [
        (base_time, 100),
        (base_time + timedelta(hours=12), 150),
        (base_time + timedelta(hours=24), 200)
    ]

    trend = history.get_price_trend(window_hours=24)
    assert trend > 0  # Should show upward trend

    # Test with insufficient data
    history.purchase_prices = []
    assert history.get_price_trend() == 0.0


def test_trade_opportunity_calculations():
    """Test TradeOpportunity profit calculations"""
    opportunity = TradeOpportunity(
        trade_symbol=TradeSymbol.IRON_ORE,
        source_market="MARKET_A",
        target_market="MARKET_B",
        purchase_price=50,
        sell_price=100,
        trade_volume=100,
        source_supply=SupplyLevel.HIGH,
        target_demand=SupplyLevel.LIMITED,
        distance=10
    )

    assert opportunity.profit_per_unit == 50
    assert opportunity.total_potential_profit == 5000

    score = opportunity.score()
    assert 0 <= score <= 100
    assert score > 0  # noqa: B001  # Should be profitable


def test_market_analyzer_initialization():
    """Test MarketAnalyzer initialization"""
    analyzer = MarketAnalyzer()
    assert len(analyzer.price_history) == 0
    assert len(analyzer.market_cache) == 0


def test_market_analyzer_update_market_data(mock_market):
    """Test updating market data"""
    analyzer = MarketAnalyzer()
    timestamp = datetime.now()

    analyzer.update_market_data(mock_market, timestamp)

    assert mock_market.symbol in analyzer.market_cache
    assert mock_market.symbol in analyzer.price_history
    assert len(analyzer.price_history[mock_market.symbol]) == 2


def test_market_analyzer_get_trade_opportunities():
    """Test finding trade opportunities between markets"""
    analyzer = MarketAnalyzer()

    # Create test markets with complementary trade goods
    market_a = Market(
        symbol="MARKET_A",
        exports=[],
        imports=[],
        exchange="TEST_EXCHANGE",
        trade_goods=[
            MarketTradeGood(
                symbol=TradeSymbol.IRON_ORE,
                type_=MarketTradeGoodType.EXPORT,
                trade_volume=100,
                supply=SupplyLevel.HIGH,
                activity=ActivityLevel.STRONG,
                purchase_price=50,
                sell_price=75
            )
        ]
    )

    market_b = Market(
        symbol="MARKET_B",
        exports=[],
        imports=[],
        exchange="TEST_EXCHANGE",
        trade_goods=[
            MarketTradeGood(
                symbol=TradeSymbol.IRON_ORE,
                type_=MarketTradeGoodType.IMPORT,
                trade_volume=100,
                supply=SupplyLevel.LIMITED,
                activity=ActivityLevel.STRONG,
                purchase_price=90,
                sell_price=100
            )
        ]
    )

    opportunities = analyzer.get_trade_opportunities([market_a, market_b])

    assert len(opportunities) > 0
    assert opportunities[0].source_market == "MARKET_A"
    assert opportunities[0].target_market == "MARKET_B"
    assert opportunities[0].trade_symbol == TradeSymbol.IRON_ORE


def test_market_analyzer_get_market_insights(mock_market):
    """Test market insights generation"""
    analyzer = MarketAnalyzer()

    # Add some historical data
    timestamp_base = datetime.now() - timedelta(hours=2)
    analyzer.update_market_data(mock_market, timestamp_base)
    analyzer.update_market_data(
        mock_market,
        timestamp_base + timedelta(hours=1)
    )
    analyzer.update_market_data(mock_market, datetime.now())

    insights = analyzer.get_market_insights(mock_market.symbol)

    assert "price_trends" in insights
    assert "trading_volume" in insights
    assert "supply_levels" in insights
    assert "recommendations" in insights

    # Verify insights for IRON_ORE
    iron_ore = TradeSymbol.IRON_ORE.value
    assert iron_ore in insights["price_trends"]
    assert iron_ore in insights["trading_volume"]
    assert iron_ore in insights["supply_levels"]
