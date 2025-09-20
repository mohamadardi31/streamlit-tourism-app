import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import unquote

st.set_page_config(page_title="Tourism Data Dashboard", layout="wide")
st.title("Tourism Data Interactive Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
	df = pd.read_csv(uploaded_file)
	df.columns = [c.strip() for c in df.columns]
	# Clean and convert columns
	df["Tourism Index"] = pd.to_numeric(df["Tourism Index"], errors="coerce")
	df["Total number of hotels"] = pd.to_numeric(df["Total number of hotels"], errors="coerce")
	df["Total number of cafes"] = pd.to_numeric(df["Total number of cafes"], errors="coerce")
	df["Total number of restaurants"] = pd.to_numeric(df["Total number of restaurants"], errors="coerce")
	df["Total number of guest houses"] = pd.to_numeric(df["Total number of guest houses"], errors="coerce")
	# Extract District from refArea if needed
	if "refArea" in df.columns:
		df["District"] = df["refArea"].astype(str).str.rsplit("/", n=1).str[-1].apply(unquote).str.replace("_", " ")

	# Search/filter box for towns and districts
	st.sidebar.header("Filter Data")
	search_town = st.sidebar.text_input("Search Town")
	search_district = st.sidebar.text_input("Search District")
	filtered_df = df.copy()
	if search_town:
		filtered_df = filtered_df[filtered_df["Town"].str.contains(search_town, case=False, na=False)]
	if "District" in filtered_df.columns and search_district:
		filtered_df = filtered_df[filtered_df["District"].str.contains(search_district, case=False, na=False)]

	# Tabs for each visualization
	tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
		"Data Preview", "Tourism Index Histogram", "Top Towns by Hotels", "Stacked Bars by District", "Exploitable Attractions Pie", "Infrastructure Heatmap"])

	with tab1:
		st.write("## Data Preview", filtered_df.head(50))
		st.write("### Download Filtered Data")
		st.download_button("Download CSV", filtered_df.to_csv(index=False), "filtered_data.csv")
		st.write("### Summary Statistics")
		st.write(filtered_df.describe(include='all'))

	with tab2:
		st.subheader("Distribution of Tourism Index Across Towns")
		min_index = float(filtered_df["Tourism Index"].min())
		max_index = float(filtered_df["Tourism Index"].max())
		bins = st.slider("Number of bins", min_value=5, max_value=50, value=20)
		index_range = st.slider("Tourism Index Range", min_value=min_index, max_value=max_index, value=(min_index, max_index))
		filtered = filtered_df[(filtered_df["Tourism Index"] >= index_range[0]) & (filtered_df["Tourism Index"] <= index_range[1])]
		fig, ax = plt.subplots(figsize=(8,5))
		filtered["Tourism Index"].dropna().plot(kind="hist", bins=bins, ax=ax)
		ax.set_title("Distribution of Tourism Index Across Towns")
		ax.set_xlabel("Tourism Index")
		ax.set_ylabel("Number of Towns")
		st.pyplot(fig)
		

	with tab3:
		st.subheader("Top Towns by Number of Hotels")
		top_n = st.slider("Number of towns to show", min_value=5, max_value=20, value=10)
		hotels_top = filtered_df[["Town", "Total number of hotels"]].dropna().sort_values("Total number of hotels", ascending=False).head(top_n)
		fig_bar, ax_bar = plt.subplots(figsize=(10,5))
		ax_bar.bar(hotels_top["Town"], hotels_top["Total number of hotels"])
		ax_bar.set_title("Top Towns by Number of Hotels")
		ax_bar.set_xticklabels(hotels_top["Town"], rotation=35, ha="right")
		st.pyplot(fig_bar)
		        st.pyplot(fig_bar)

        # Insights for Tab 3
        st.markdown("""
**Insight:** Highlights which towns have the most hotels and the ranking order. Being able to now increase and decrease the number of cities viewed can make it easier for analysts to compare the number of hotels across a smaller or greater horizon. This can make it simpler to find discrepancies across towns.

- **Bqerqacha leads significantly**
- With **20 hotels**, Bqerqacha stands out as the top town, indicating it is likely a strong tourism or lodging hub compared to the others.
- **Concentration in the top few towns**
- The top 3 towns (**Bqerqacha, Zgharta-Ehden, Bcharreh**) together account for **over 50%** of the hotels among the top 10, showing a concentration of hospitality infrastructure in a few areas.
- **Gradual decline after the top tier**
- After **Bcharreh (15 hotels)**, the numbers drop more sharply, with towns like **Jbeil** and **Kfar Dibiane** only having around **8 hotels**, showing a clear second tier of smaller hotel markets.
- **Smaller towns still make the list**
- Towns like **Shawagheer El-Faouqa, Zahleh El-Maallaqa, and Lala** only have **5 hotels** each, but they still rank among the top 10, suggesting that the overall hotel distribution across towns is relatively low and competitive.
        """)


	with tab4:
		st.subheader("Tourism Infrastructure by District (Top 12)")
		infra_cols = ["Total number of hotels","Total number of cafes","Total number of restaurants"]
		selected_infra = st.multiselect("Select infrastructure types", infra_cols, default=infra_cols)
		infra = filtered_df.groupby("District")[selected_infra].sum()
		infra["Total"] = infra.sum(axis=1)
		infra = infra.sort_values("Total", ascending=False).head(12)
		x = np.arange(len(infra))
		fig_stack, ax_stack = plt.subplots(figsize=(11,6))
		bottom = np.zeros(len(infra))
		for col in selected_infra:
			ax_stack.bar(x, infra[col], bottom=bottom, label=col)
			bottom += infra[col].values
		ax_stack.set_xticks(x)
		ax_stack.set_xticklabels(infra.index, rotation=35, ha="right")
		ax_stack.set_title("Tourism Infrastructure by District (Top 12)")
		ax_stack.legend()
		st.pyplot(fig_stack)

	with tab5:
		st.subheader("Towns with Exploitable Attractions")
		if "Existence of touristic attractions prone to be exploited and developed - exists" in filtered_df.columns:
			counts = filtered_df["Existence of touristic attractions prone to be exploited and developed - exists"].fillna(0).astype(int).value_counts()
			fig_pie, ax_pie = plt.subplots(figsize=(6,6))
			ax_pie.pie([counts.get(0,0), counts.get(1,0)], labels=["No","Yes"], autopct="%1.1f%%", startangle=90)
			ax_pie.set_title("Towns with Exploitable Attractions")
			st.pyplot(fig_pie)
		else:
			st.info("Column for exploitable attractions not found.")

	with tab6:
		st.subheader("Tourism Infrastructure by District (Heatmap)")
		infra_columns = ["Total number of hotels","Total number of cafes","Total number of restaurants","Total number of guest houses"]
		selected_columns = st.multiselect("Select infrastructure columns for heatmap", infra_columns, default=infra_columns)
		if "District" in filtered_df.columns:
			districts = filtered_df["District"].unique().tolist()
			selected_districts = st.multiselect("Select districts for heatmap", districts, default=districts)
			heatmap_data = filtered_df[filtered_df["District"].isin(selected_districts)].groupby("District")[selected_columns].sum().fillna(0)
			data = heatmap_data.to_numpy()
			fig2, ax2 = plt.subplots(figsize=(14,10))
			im = ax2.imshow(data, cmap="YlOrRd", aspect="equal")
			ax2.set_xticks(range(len(heatmap_data.columns)))
			ax2.set_xticklabels(heatmap_data.columns, rotation=30, ha="right")
			ax2.set_yticks(range(len(heatmap_data.index)))
			ax2.set_yticklabels(heatmap_data.index)
			ax2.set_title("Tourism Infrastructure by District (Heatmap)")
			for i in range(data.shape[0]):
				for j in range(data.shape[1]):
					ax2.text(j, i, int(data[i,j]), ha="center", va="center", color="black")
			fig2.colorbar(im, ax=ax2, label="Count")
			st.pyplot(fig2)
		    st.pyplot(fig_bar)

        # Insights for Tab 3
            st.markdown("""
**Insight:** Highlights which towns have the most hotels and the ranking order. Being able to now increase and decrease the number of cities viewed can make it easier for analysts to compare the number of hotels across a smaller or greater horizon. This can make it simpler to find discrepancies across towns.

- **Bqerqacha leads significantly**
- With **20 hotels**, Bqerqacha stands out as the top town, indicating it is likely a strong tourism or lodging hub compared to the others.
- **Concentration in the top few towns**
- The top 3 towns (**Bqerqacha, Zgharta-Ehden, Bcharreh**) together account for **over 50%** of the hotels among the top 10, showing a concentration of hospitality infrastructure in a few areas.
- **Gradual decline after the top tier**
- After **Bcharreh (15 hotels)**, the numbers drop more sharply, with towns like **Jbeil** and **Kfar Dibiane** only having around **8 hotels**, showing a clear second tier of smaller hotel markets.
- **Smaller towns still make the list**
- Towns like **Shawagheer El-Faouqa, Zahleh El-Maallaqa, and Lala** only have **5 hotels** each, but they still rank among the top 10, suggesting that the overall hotel distribution across towns is relatively low and competitive.
        """)

		else:
			st.info("District column not found. Please check your data.")
else:
	st.info("Please upload a CSV file with the required columns.")
