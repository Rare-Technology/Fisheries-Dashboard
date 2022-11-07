from dash import dcc, html

def start_download_button():
    download_button = html.Button(
        "Download data",
        id = "btn-download",
        className = "btn btn-info",
        type = "button"
    )
    download_component = dcc.Download(id = "download-data")

    download_div = html.Div(
        id = "download-container",
        children = [
            download_button,
            download_component
    ])

    return download_div
