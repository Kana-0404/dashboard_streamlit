import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ページの設定
st.set_page_config(
    page_title="Japan Visitors App",
    page_icon="🗺️",
    initial_sidebar_state="expanded",  # サイドバーを最初から表示
    )

# データの読み込み
df = pd.read_csv('2017-2023_訪日外国客数推移_.csv')

# Streamlitアプリケーションの作成
st.title("✈️訪日外客数の推移📈")

# 関数: ラインプロットとランキングを作成する
def create_line_plot(data, x, y, hue, title, xlabel, ylabel, country_column):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
    
    # ラインプロットを作成
    sns.set_palette("pastel")
    sns.lineplot(x=x, y=y, hue=hue, data=data, marker='o', sort=False, ax=ax1)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    
    # ランキングを作成
    ranking_df = data.groupby(country_column)[y].sum().sort_values(ascending=False).reset_index()
    ranking_df['Rank'] = ranking_df[y].rank(ascending=False, method='min').astype(int)  # Rank列を追加

    # フォントサイズを指定してHTMLを埋め込む
    st.write("<h2 style='font-size:20px; line-height:1.0;'>Top5 ランキング</h2>", unsafe_allow_html=True)
    st.write("<h2 style='font-size:10px; line-height:0.5;'>※選択した国でランキング表示します。</h2>", unsafe_allow_html=True)
    
    # 表示するテーブル
    col1, col2 = st.columns(2)
    
    with col1:
        st.table(ranking_df[['Rank', country_column, y]].head(5).reset_index(drop=True).style.set_properties(**{'background-color': 'transparent'}))

    with col2:
        # バープロットを作成
        ax2.barh(ranking_df[country_column], ranking_df[y], color='skyblue')  # Country/Areaを縦軸に
        ax2.set_xlabel(ylabel)
        ax2.set_ylabel(country_column)
        ax2.set_title(f'{ylabel} Ranking')

        # 1位から3位までのアイコンを表示
        for i in range(3):
            if i < len(ranking_df) and ranking_df.iloc[i]['Rank'] <= 3:
                icon = '🥇' if ranking_df.iloc[i]['Rank'] == 1 else '🥈' if ranking_df.iloc[i]['Rank'] == 2 else '🥉'
                st.markdown(f"{icon} {ranking_df.iloc[i]['Rank']}st Place: {ranking_df.iloc[i][country_column]}")

    return fig

# 出身国のチェックボックス
selected_countries = st.multiselect("国を選択", df['Country/Area_jp'].unique())

# Show Monthに関係なく、年ごとのラインプロットとランキングを作成
st.write(f"## 年単位の推移 - 2017年-2023年")
all_years_df = df[df['Country/Area_jp'].isin(selected_countries)]
fig_all_years = create_line_plot(all_years_df, 'Year', 'Visitor Arrivals', 'Country/Area',
                                 'Number of Foreign Visitors to Japan by Year',
                                 'Year', 'Visitor Arrivals', 'Country/Area')
st.pyplot(fig_all_years)

# Show Monthのチェックボックス
show_month = st.checkbox("月毎の推移を表示")

# Show Monthにチェックが入った場合、Select Yearを表示
if show_month:
    # 年の選択を追加
    selected_year = st.selectbox("年を選択", sorted(df['Year'].unique()))

    # 選択されたデータをフィルタリング
    filtered_df = df[(df['Country/Area_jp'].isin(selected_countries)) & (df['Year'] == selected_year)]

    # 月ごとのラインプロットとランキングを作成
    st.write(f"## 月単位の推移 - {selected_year}年")
    fig_monthly = create_line_plot(filtered_df, 'Month (abbr)', 'Visitor Arrivals', 'Country/Area',
                                   f'Number of foreign visitors to Japan in {selected_year} ',
                                   'Month', 'Visitor Arrivals', 'Country/Area')
    st.pyplot(fig_monthly)
    
# Streamlit + Plotly
# 年の一覧を取得
years = df['Year'].unique()

# 年の選択を追加
selected_year = st.selectbox("年を選択してください", years)

# 選択された年のデータをフィルタリング
filtered_df = df[df['Year'] == selected_year]

# バブルチャートを作成
bubble_fig = px.scatter_geo(
    filtered_df,
    locations="Country/Area",
    locationmode="country names",
    color="Visitor Arrivals",
    size="Visitor Arrivals",
    animation_frame="Month (abbr)",
    projection="natural earth",
    title=f"{selected_year}年 - 国別訪日外国人数",
    labels={'Visitor Arrivals': '訪問者数'},
    color_continuous_scale="Viridis"
)

# バブルチャートの地図データを取得
bubble_map_data = px.data.gapminder()

# ベースの地図に色をつける
base_map_fig = px.choropleth(
    bubble_map_data,
    locations="iso_alpha",  # 国コード
    color="continent",
    projection="natural earth",
    title="世界地図",
    labels={'continent': '大陸'},
)

# バブルチャートとベースの地図を合成
combined_fig = px.scatter_geo(
    filtered_df,
    locations="Country/Area",
    locationmode="country names",
    color="Visitor Arrivals",
    size="Visitor Arrivals",
    animation_frame="Month (abbr)",
    projection="natural earth",
    title=f"{selected_year}年 - 国別訪日外国人数",
    labels={'Visitor Arrivals': '訪問者数'},
    color_continuous_scale="Viridis" 
).update_geos(
    showocean=True, 
    oceancolor="LightBlue", 
    showland=True, 
    landcolor="LightGray"
)

# バブルチャートとベースの地図を表示
st.plotly_chart(combined_fig)