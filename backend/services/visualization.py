import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
from backend.utils.logger import logger

class Visualizer:
    def __init__(self, df):
        self.df = df

    # ------------------------
    # Plotly Charts
    # ------------------------
    def plot_histogram(self, col, bins=30):
        logger.info(f"Generating Histogram | Column={col}")
        try:
            fig = px.histogram(self.df, x=col, nbins=bins, marginal="box", title=f"Histogram of {col}")
            fig.update_layout(bargap=0.2)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot histogram for {col}: {e}")

    def plot_boxplot(self, col):
        logger.info(f"Generating Boxplot | Column={col}")
        try:
            fig = px.box(self.df, y=col, title=f"Boxplot of {col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot boxplot for {col}: {e}")

    def plot_scatter(self, x, y, color=None, trendline=False):
        logger.info(
            f"Generating Scatter | X={x}, Y={y} | Trendline={trendline}"
        )

        try:
            trendline_type = None

            if trendline:
                try:
                    import statsmodels.api  # noqa: F401
                    trendline_type = "ols"
                except ImportError:
                    logger.warning(
                        "statsmodels is not installed. "
                        "Scatter plot will be generated without OLS trendline."
                    )

            fig = px.scatter(
                self.df,
                x=x,
                y=y,
                color=color if color else None,
                trendline=trendline_type,
                title=f"Scatter Plot: {x} vs {y}",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            return fig

        except Exception as e:
            logger.exception(e)
            st.warning(
                f"⚠️ Cannot plot scatter for {x} vs {y}: {e}"
            )
            return None

    def plot_line(self, x, y):
        logger.info(f"Generating Line Chart | X={x}, Y={y}")
        try:
            fig = px.line(self.df, x=x, y=y, title=f"Line Plot: {x} vs {y}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot line chart for {x} vs {y}: {e}")

    def plot_bar(self, x, y):
        logger.info(f"Generating Bar Chart | X={x}, Y={y}")
        try:
            fig = px.bar(self.df, x=x, y=y, title=f"Bar Chart: {x} vs {y}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot bar chart for {x} vs {y}: {e}")

    def plot_pie(self, col):
        logger.info(f"Generating Pie Chart | Column={col}")
        try:
            value_counts = self.df[col].value_counts().reset_index()
            value_counts.columns = [col, "count"]
            fig = px.pie(value_counts, names=col, values="count", title=f"Pie Chart of {col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot pie chart for {col}: {e}")

    def plot_violin(self, col):
        logger.info(f"Generating Violin Plot | Column={col}")
        try:
            fig = px.violin(self.df, y=col, box=True, points="all", title=f"Violin Plot of {col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot violin plot for {col}: {e}")

    def plot_density(self, col):
        logger.info(f"Generating Density Plot | Column={col}")
        try:
            fig = ff.create_distplot([self.df[col].dropna()], [col], show_hist=False)
            fig.update_layout(title=f"Density Plot of {col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot density for {col}: {e}")

    def plot_correlation(self):
        logger.info("Generating Correlation Heatmap")
        try:
            corr_matrix = self.df.corr(numeric_only=True)
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="viridis", ax=ax, cbar=True)
            plt.xticks(rotation=45, ha="right")
            plt.yticks(rotation=0)
            st.pyplot(fig)
        except Exception as e:
            logger.exception(e)
            st.warning(f"⚠️ Cannot plot correlation heatmap: {e}")
