import pandas as pd
import plotly.graph_objects as go
from .indicators.abstract import AbstractIndicator
from quansinvest.data.constants import ADJ_CLOSE_PRICE_COLUMN_NAME


class IndicatorRelation:
    def __init__(self, *indicator: AbstractIndicator):
        self.indicators = list(indicator)
        self.data = self.prepare_data()

    def prepare_data(self):
        min_date = min([indicator.data.index.min() for indicator in self.indicators])
        max_date = max([indicator.data.index.max() for indicator in self.indicators])
        date_template = pd.DataFrame(index=pd.bdate_range(min_date, max_date))
        alldata = date_template
        columns = []

        for indicator in self.indicators:
            columns.append(indicator.name)
            alldata = pd.merge(
                alldata,
                indicator.data[[ADJ_CLOSE_PRICE_COLUMN_NAME]],
                how="left",
                left_index=True,
                right_index=True,
            ).fillna(method="ffill")
            alldata.columns = columns

        return alldata

    def plot(self, name1, name2):
        df1 = self.data[[name1]]
        df2 = self.data[[name2]]
        indicator1 = go.Scatter(x=df1.index, y=df1[name1], yaxis="y1", name=name1)
        indicator2 = go.Scatter(x=df2.index, y=df2[name2], yaxis="y2", name=name2)
        data = [indicator1, indicator2]

        layout = dict(
            xaxis=dict(
                rangeslider=dict(visible=True),
                type='date',
            ),
            yaxis=dict(
                title=name1,
                titlefont=dict(
                    color="#1f77b4"
                ),
                tickfont=dict(
                    color="#1f77b4"
                )
            ),
            yaxis2=dict(
                title=name2,
                titlefont=dict(
                    color="#ff7f0e"
                ),
                tickfont=dict(
                    color="#ff7f0e"
                ),
                overlaying="y",
                side="right",
            ),
        )

        fig = go.FigureWidget(data=data, layout=layout)

        def zoom(layout, xrange):
            df1_in_view = df1.loc[fig.layout.xaxis.range[0]: fig.layout.xaxis.range[1]]
            df2_in_view = df2.loc[fig.layout.xaxis.range[0]: fig.layout.xaxis.range[1]]
            fig.layout.yaxis.range = [
                min(df1_in_view.name1.min(), df2_in_view.name2.min()),
                max(df1_in_view.name1.max(), df2_in_view.name2.max()),
            ]

        fig.layout.on_change(zoom, "xaxis.range")

        return fig
