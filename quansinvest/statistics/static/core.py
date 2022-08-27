import plotly.graph_objects as go
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME
)


class StaticStatistics:
    def __init__(self, data, *static_indicators):
        self.data = data
        self.static_indicators = static_indicators

    def plot(self, indicator_value_scale=1.1):
        lines = [go.Scatter(x=self.data.index, y=self.data[ADJ_CLOSE_PRICE_COLUMN_NAME], name="original")]
        for indicator in self.static_indicators:
            lines.append(
                go.Scatter(
                    x=indicator.data.index,
                    y=indicator.data[ADJ_CLOSE_PRICE_COLUMN_NAME]*indicator_value_scale,
                    name=indicator.name,
                )
            )
        layout = dict(
            xaxis=dict(
                rangeslider=dict(visible=True),
                type='date',
            ),
            yaxis=dict(
                title="close price",
                titlefont=dict(
                    color="#1f77b4"
                ),
                tickfont=dict(
                    color="#1f77b4"
                )
            ),
        )

        fig = go.FigureWidget(data=lines, layout=layout)

        def zoom(layout, xrange):
            in_view = self.data.loc[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
            fig.layout.yaxis.range = [
                in_view[ADJ_CLOSE_PRICE_COLUMN_NAME].min(),
                in_view[ADJ_CLOSE_PRICE_COLUMN_NAME].max(),
            ]

        fig.layout.on_change(zoom, "xaxis.range")

        return fig
