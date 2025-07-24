import dash
from dash import html, dcc
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Cargar datos y modificar dataset
data_url = "https://raw.githubusercontent.com/plotly/datasets/master/supermarket_Sales.csv"
sales = pd.read_csv(data_url)
sales['Date'] = pd.to_datetime(sales['Date'])
sales = sales.sort_values("Date").set_index("Date")
sales["Revenue"] = sales["Unit price"] * sales["Quantity"]
sales.rename(columns = {"Gross income" : "Income after costs and taxes"}, inplace = True)

# Adding graphs
daily_sales_number = (
    sales["Invoice ID"].groupby(sales.index.date).nunique().rename("Number of sales")
)

title_font_size = 30
figure_daily_sales_number = px.line(
    daily_sales_number, 
    title = "Daily number of sales"
).update_layout(title_font_size = title_font_size)

m7d_mean_revenue = (
    sales["Revenue"].groupby(sales.index.date).sum().rolling(7, min_periods = 7).mean()
)
figure_m7d_mean_revenue = px.line(
    m7d_mean_revenue,
    title = "7-day moving average of daily revenue"
).update_layout(title_font_size = title_font_size)

figure_product_line = px.pie(
    sales.groupby("Product line")["Revenue"].sum().reset_index(),
    names = "Product line",
    values = "Revenue",
    title = "Product lines ratio"
).update_layout(title_font_size = title_font_size)

figure_revenue_bycity = px.bar(
    sales.groupby(["City"])["Revenue"].sum(), title = "Revenue by city"
).update_layout(title_font_size = title_font_size)

sums = (
    sales[
        [
            "Revenue",
            "Tax 5%",
            "Cost of goods sold",
            "Income after costs and taxes",
        ]
    ]
    .sum()
    .rename("Value")
    .reset_index()
    .rename(columns = {"index" : "Item"})
)



# Cargar framework de app
sums_datatable = html.Div(
    [
        html.P(),
        html.Label(
            "Revenue breakdown",
            style = {"font-size": f"{title_font_size}px", "font-color" : "grey"},
        ),
        html.P(),
        DataTable(
            data=sums.to_dict("records"),
            columns=[{"name": col, "id": col} for col in ["Item", "Value"]],
            style_as_list_view=True, # <-- Estilo moderno
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'sans-serif'
            },
        ),
    ]
)

row_summary_metrics = dbc.Row(
    [
        dbc.Col("", width=1),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=figure_product_line,
                        style={"height": "400px", "width": "100%"}
                    )
                ])
            ]),
            width=4,
            style={"padding": "10px"}
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=figure_revenue_bycity,
                        style={"height": "400px", "width": "100%"}
                    )
                ])
            ]),
            width=4,
            style={"padding": "10px"}
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    sums_datatable
                ])
            ]),
            width=3,
            style={"padding": "10px"}
        ),
        dbc.Col("", width=0),
    ],
    justify="center",
    align="center",
    style={"marginBottom": "30px"}
)

navbar = dbc.NavbarSimple(
    brand="Panel de KPIs de Ventas",
    brand_href="#",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Github", href="https://github.com/Esteban8482")),
    ]
)

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.layout = html.Div([
        navbar,
        dbc.Container(
            [
                html.H1("Sales KPIs"),
                html.H2("Sales Dataset"),
                html.Ul(
                    [
                        html.Li(f"Number of cities: {sales['City'].nunique()}"),
                        html.Li(
                            f"Time period: {sales.index.date[0].isoformat()[:10]} - {sales.index.date[-1].isoformat()[:10]}"
                        ),
                        html.Li(["Data source: ", html.A(data_url, href = data_url)]),
                    ]
                ),
                row_summary_metrics,
                dcc.Graph(figure = figure_daily_sales_number),
                dcc.Graph(figure = figure_m7d_mean_revenue), 
            ],
            fluid=True,
            className="mt-4"
        )
    ],      
)

if __name__ == '__main__':
    app.run(debug = True) 