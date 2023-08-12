import zipfile
import pathlib


BASE_DIR = pathlib.Path(__file__).parent


def unzip_component(extract_to):
    with zipfile.ZipFile(BASE_DIR / "component.zip", "r") as zip_ref:
        zip_ref.extractall(extract_to)


# Example usage
# zip_file_path = "my_archive.zip"
# extract_to = "output_folder"
# unzip_file(zip_file_path, extract_to)
