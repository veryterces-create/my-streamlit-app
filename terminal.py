import streamlit as str
import yfinance as yf
import plotly.graph_objects as go

# 1. Настройка внешнего вида сайта
str.set_page_config(page_title="Сырьевой Терминал", layout="wide")
str.title("📊 Терминал Мировых Сырьевых Рынков & Финансовый Мониторинг")

# 2. Боковое меню (Выбор ресурса и Настройка Калькулятора)
str.sidebar.header("🎛️ Настройки терминала")
assets = {
    "Нефть Brent (Energy)": "BZ=F",
    "Природный газ (Energy)": "NG=F",
    "Золото (Minerals)": "GC=F",
    "Медь (Minerals)": "HG=F",
    "Платина (Minerals)": "PL=F"
}

selected_name = str.sidebar.selectbox("Выберите ресурс для графика:", list(assets.keys()))
ticker = assets[selected_name]
days = str.sidebar.slider("Период анализа (дней):", min_value=10, max_value=365, value=90)

# Блок калькулятора выручки (из вашего отчета!)
str.sidebar.markdown("---")
str.sidebar.header("💰 Калькулятор выручки экспортера")
volume = str.sidebar.number_input("Объем экспорта в месяц (баррелей/унций):", min_value=1000, value=600000, step=10000)
royalty_rate = str.sidebar.slider("Государственное роялти (налог %):", min_value=0, max_value=50, value=20)
loading_fee = str.sidebar.number_input("Сбор за налив/терминал ($ за единицу):", min_value=0.0, value=0.35, step=0.05)

# 3. Скачивание данных из интернета
data = yf.download(ticker, period=f"{days}d")

if not data.empty:
    data.columns = data.columns.get_level_values(0)
    
    # Расчет рыночных цен
    last_price = float(data['Close'].values[-1])
    prev_price = float(data['Close'].values[-2])
    price_change = last_price - prev_price
    percent_change = (price_change / prev_price) * 100

    # Расчет скользящей средней для прогноза
    data['SMA_5'] = data['Close'].rolling(window=5).mean()
    current_sma = float(data['SMA_5'].values[-1]) if not data['SMA_5'].empty else last_price
    
    if last_price > current_sma:
        forecast_text = "📈 РАСТЕТ (Покупка)"
        forecast_delta = "Тренд: Бычий"
    else:
        forecast_text = "📉 ПАДЕТ (Продажа)"
        forecast_delta = "Trend: Медвежий"

    # ЭКОНОМИЧЕСКИЙ РАСЧЕТ ПОД ОТЧЕТ [1]
    gross_revenue = volume * last_price
    total_royalty = gross_revenue * (royalty_rate / 100)
    total_fees = volume * loading_fee
    net_revenue = gross_revenue - total_royalty - total_fees
    net_price = net_revenue / volume

    # 4. Вывод биржевых показателей
    str.subheader("🎯 Актуальные биржевые показатели")
    col1, col2, col3 = str.columns(3)
    col1.metric(label=f"Текущая цена ({selected_name})", value=f"${last_price:,.2f}")
    col2.metric(label="Изменение за день", value=f"{price_change:+,.2f} ({percent_change:+.2f}%)", delta=percent_change)
    col3.metric(label="Авто-прогноз на завтра", value=forecast_text, delta=forecast_delta)

    # 5. Вывод интерактивного графика
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Цена"
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_5'], mode='lines', name='Линия тренда (SMA 5)', line=dict(color='orange', width=2)))
    fig.update_layout(title=f"График котировок для {selected_name}", yaxis_title="Цена в USD", template="plotly_dark")
    str.plotly_chart(fig, use_container_width=True)

    # 6. Блок финансовых результатов экспортера [1]
    str.markdown("---")
    str.subheader("📊 Экономика и чистая прибыль компании-экспортера")
    str.write(f"Расчет экономики выполнен автоматически на основе текущей рыночной цены **${last_price:,.2f}**")
    
    ec1, ec2, ec3, ec4 = str.columns(4)
    ec1.metric(label="Валовая (грязная) выручка", value=f"${gross_revenue:,.2f}")
    ec2.metric(label="Уплачено Роялти (налог)", value=f"-${total_royalty:,.2f}")
    ec3.metric(label="Затраты на логистику/терминал", value=f"-${total_fees:,.2f}")
    ec4.metric(label="Чистая прибыль (Нетбэк)", value=f"${net_revenue:,.2f}")
    
    str.info(f"💡 Реальная чистая цена, которую получает продавец на руки: **${net_price:,.2f}** за баррель/унцию (вместо биржевой стоимости ${last_price:,.2f}).")

else:
    str.error("Не удалось загрузить данные. Проверьте подключение к интернету.")
=