import logging
import pandas as pd
from lightgbm import LGBMRegressor
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from sklearn.metrics import mean_absolute_error
import lightgbm as lgb

logger = logging.getLogger(__name__)

from services.price_service import PriceService

def train_and_predict_data(symbol: str, data: DataFrame, prediction_time: str = None):
    # ===== 1. Create Safe Copies =====
    train_data = data.iloc[:-int(len(data)*0.2)].copy()
    test_data = data.iloc[-int(len(data)*0.2):].copy()

    # ===== 2. Target Engineering =====
    # Option 1: Binary classification (uncomment to use)
    # train_data['target'] = (train_data['price'].shift(-6) > train_data['price']).astype(int)
    # test_data['target'] = (test_data['price'].shift(-6) > test_data['price']).astype(int)
    
    # Option 2: Regression 
    price_mean = train_data['price'].mean()
    price_iqr = train_data['price'].quantile(0.75) - train_data['price'].quantile(0.25)

    # Scale targets to $0-$1 range
    train_data.loc[:, 'target'] = (train_data['price'].shift(-1) - price_mean) / price_iqr
    test_data.loc[:, 'target'] = (test_data['price'].shift(-1) - price_mean) / price_iqr

    # ===== 3. Clean Data =====
    # Drop rows with NaN targets (end of series)
    train_data = train_data.dropna(subset=['target'])
    test_data = test_data.dropna(subset=['target'])
    
    # ===== 4. Feature Selection =====
    # Separate features and target
    features = ['price', 'sma_6', 'sma_24', '6h_return', '24h_return', 'hour_of_day']
    X_train = train_data[features]
    y_train = train_data['target']
    X_test = test_data[features]
    y_test = test_data['target']
    
    # ===== 5. Model Training =====
    model =  LGBMRegressor(
        boosting_type='gbdt',
        data_sample_strategy='goss',
        num_leaves=15, 
        learning_rate=0.1, 
        min_data_in_leaf=50,
        n_estimators=150, # Increase to improve accuracy
        max_depth=5, 
        random_state=42, # For better reproducibility,
        verbose=-1
    )
    
    model.fit(
        X_train, 
        y_train, 
        eval_set=[(X_test, y_test)], 
        eval_metric='mae', 
        callbacks=[lgb.early_stopping(stopping_rounds=50)])
    
    # ===== 6. Evaluation =====
    test_preds = model.predict(X_test) * price_iqr + price_mean  # Correct
    actual_prices = test_data['price'].iloc[:len(test_preds)]
    mae = mean_absolute_error(actual_prices, test_preds)
    logger.info(f"6H Prediction MAE: ${mae:.4f} ({mae/price_mean} of avg price)")
    
    # ===== 7. Next 6H Prediction =====
    if prediction_time:
        # Predict at specific time (e.g., '14:00')
        pred_data = data[data.index.time == pd.to_datetime(prediction_time).time()].iloc[-1][features]
    else:
        # Predict using latest data
        pred_data = data.iloc[-1][features]
    
    # next_6h_price = model.predict(prediction_point)[0]
    next_6h_price = model.predict([pred_data])[0] * price_iqr + price_mean  # Rescale to original price
    current_price = data.iloc[-1]['price']
    logger.info(
        f"\n======={symbol} prediction======= \n"
        f"Prediction for {pd.Timestamp.now() + pd.Timedelta(hours=6)}:\n"
        f"Current: ${current_price:.4f} → Predicted: ${next_6h_price:.4f} "
        f"({(next_6h_price/current_price-1):.2%} change) \n"
        "==============================\n"
    )

    return model, next_6h_price

def test_fetch_price() -> list:

    price_service = PriceService()
    tokens = price_service.get_top_tokens(limit=3, page="1", sort_by="rank", sort_order="asc")

    token_list = []

    for token in tokens:
        price = price_service.get_price(token)

        # Short-term momentum (6h)
        price["6h_return"] = price["price"].pct_change(periods=6)

        # Rolling volatility (6h)
        price["24h_return"] = price["price"].rolling(6).std() / price["price"].rolling(6).mean()

        # Moving averages (6h vs 24h crossover)
        price['sma_6'] = price['price'].rolling(6).mean()
        price['sma_24'] = price['price'].rolling(24).mean()

        # Crypto often has intraday seasonality
        price['hour_of_day'] = price.index.hour 
        
        # logger.info("Price for %s: \n %s", token, price)
        token_list.append({"token": token, "price_data": price})

    logger.info("Fetched prices for tokens: %s", [token['token'] for token in token_list])
    return token_list

def plot_price_with_sma(df, title="XRP Price with Moving Averages"):
    """
    Plots price data with 6-period and 24-period SMAs
    
    Args:
        df (pd.DataFrame): DataFrame containing price, sma_6, and sma_24 columns
        title (str): Title for the plot
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot raw price data
    ax.plot(df.index, df['price'], 
            label='XRP Price', 
            color='#0068FF', 
            alpha=0.8, 
            linewidth=1.5)
    
    # Plot SMAs
    ax.plot(df.index, df['sma_6'], 
            label='6-Period SMA', 
            color='#FF7B00', 
            linestyle='--', 
            linewidth=1.8)
    
    ax.plot(df.index, df['sma_24'], 
            label='24-Period SMA', 
            color='#00B061', 
            linestyle='-.', 
            linewidth=1.8)
    
    # Add golden cross/death cross markers
    golden_cross = (df['sma_6'] > df['sma_24']) & (df['sma_6'].shift() <= df['sma_24'].shift())
    death_cross = (df['sma_6'] < df['sma_24']) & (df['sma_6'].shift() >= df['sma_24'].shift())

    ax.scatter(df[golden_cross].index, df[golden_cross]['price'], 
            color='gold', marker='^', s=100, label='Golden Cross')
    ax.scatter(df[death_cross].index, df[death_cross]['price'], 
            color='black', marker='v', s=100, label='Death Cross')
    
    # Formatting
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_ylabel('Price (USD)', fontsize=12)
    ax.legend(fontsize=12)
    
    # X-axis formatting for dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    
    # Y-axis formatting
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    
    # Add grid and tighten layout
    ax.grid(True, which='both', linestyle=':', linewidth=0.5)
    plt.tight_layout()
    
    return fig, ax
