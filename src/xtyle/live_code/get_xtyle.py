from ..external_plugins import requests, requests_available


URL = "https://www.unpkg.com/xtyle@latest/dist/index.d.ts"


def get_xtyle_declarations(file_url=URL):
    script_contents = None
    if requests_available:
        response = requests.get(file_url)
        if response.status_code == 200:
            script_contents = response.text
            print("Successfully Downloaded Xtyle Types")
        else:
            print(
                f"Failed to fetch script from {file_url}, status code: {response.status_code}"
            )
    return script_contents
