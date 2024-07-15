import plotly.graph_objects as go
import plotly.figure_factory as ff

table_data = [
    ['Coin', 'Month', 'Params', 'Timeframe'],
    ['BTC', '01', '2.3/1.8', '30m'],
    ['ETH', '01', '2.3/1.8', '30m'],
    ['RUNE', '01', '2.3/1.8', '30m'],
    ['TIA', '01', '2.3/1.8', '30m'],
]

fig = ff.create_table(table_data, height_constant=60)

coins = [
    'BTCUSDT', 'ETHUSDT', 'ADAUSDT',
]
months_name = ['Янв', 'Февр', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Октб', 'Нояб', 'Дек']
data = {}
for coin in coins:
    data[coin] = [1,2,3,4,5,6,7,8,9,10,11,12]


for coin in coins:
    trace = go.Bar(x=months_name, y=data[coin], xaxis='x3', yaxis='y3', marker=dict(color='#0099ff'), name=coin)
    fig.add_trace([trace])


# initialize xaxis2 and yaxis2
fig['layout']['xaxis2'] = {}
fig['layout']['yaxis2'] = {}

# Edit layout for subplots
fig.layout.yaxis.update({'domain': [0, .45]})
fig.layout.yaxis2.update({'domain': [.6, 1]})


# The graph's yaxis2 MUST BE anchored to the graph's xaxis2 and vice versa
fig.layout.yaxis2.update({'anchor': 'x2'})
fig.layout.xaxis2.update({'anchor': 'y2'})
fig.layout.yaxis2.update({'title': 'Goals'})

# Update the margins to add a title and see graph x-labels.
fig.layout.margin.update({'t':75, 'l':50})
fig.layout.update({'title': '2016 Hockey Stats'})

# Update the height because adding a graph vertically will interact with
# the plot height calculated for the table
fig.layout.update({'height':800})

# Plot!
fig.show()









