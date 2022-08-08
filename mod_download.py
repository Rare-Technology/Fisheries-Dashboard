from dash import dcc, html

download_button = html.Button("Download data", id = "btn-download")
download_component = dcc.Download(id = "download-data")

download_div = html.Div([
    download_button,
    download_component
])
