"""
Test script to verify trading bot implementation
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from src.config.trading_config import TradingConfig
from src.config.system_config import SystemConfig
from src.environment.trading_env import TradingEnvironment
from src.models.trading_model import CustomPPO
from src.models.sentiment_model import SentimentAnalyzer
from src.utils.technical_indicators import TechnicalIndicators
from src.utils.risk_manager import RiskManager

def create_sample_data():
    """Create sample market data for testing"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='H')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.normal(100, 10, len(dates)),
        'high': np.random.normal(105, 10, len(dates)),
        'low': np.random.normal(95, 10, len(dates)),
        'close': np.random.normal(100, 10, len(dates)),
        'volume': np.random.normal(1000000, 100000, len(dates))
    })
    
    # Ensure high is highest and low is lowest
    data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
    data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
    
    return data

def test_components():
    """Test all components of the trading bot"""
    try:
        logger.info("Starting component testing...")
        
        # Test configurations
        logger.info("Testing configurations...")
        trading_config = TradingConfig()
        system_config = SystemConfig()
        
        # Test technical indicators
        logger.info("Testing technical indicators...")
        data = create_sample_data()
        indicators = TechnicalIndicators()
        data_with_indicators = indicators.add_all_indicators(data)
        logger.info(f"Added {len(TechnicalIndicators.get_feature_names())} technical indicators")
        
        # Test sentiment analyzer
        logger.info("Testing sentiment analyzer...")
        sentiment_analyzer = SentimentAnalyzer()
        sample_text = "The company reported strong earnings growth this quarter."
        sentiment = sentiment_analyzer.analyze_text(sample_text)
        logger.info(f"Sentiment analysis result: {sentiment}")
        
        # Test risk manager
        logger.info("Testing risk manager...")
        risk_manager = RiskManager(trading_config)
        position_size = risk_manager.calculate_position_size(
            capital=10000,
            entry_price=100,
            stop_loss=95
        )
        logger.info(f"Calculated position size: {position_size}")
        
        # Test trading environment
        logger.info("Testing trading environment...")
        env = TradingEnvironment(data_with_indicators, trading_config)
        observation = env.reset()
        logger.info(f"Environment observation shape: {observation.shape}")
        
        # Test trading model
        logger.info("Testing trading model...")
        model = CustomPPO(env, trading_config)
        
        # Test a few steps
        logger.info("Testing trading simulation...")
        for i in range(5):
            action = model.predict(observation)
            observation, reward, done, info = env.step(action)
            logger.info(f"Step {i+1}: Action={action}, Reward={reward:.4f}")
            
            if done:
                break
        
        logger.info("All components tested successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    # Setup logging
    logger.add("test_results.log", rotation="1 MB")
    
    # Run tests
    success = test_components()
    
    if success:
        logger.info("All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("Tests failed!")
        sys.exit(1)
