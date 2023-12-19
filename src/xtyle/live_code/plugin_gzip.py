import json
import gzip
from io import BytesIO
from types import SimpleNamespace


class PluginGzip:
    @staticmethod
    def load_json(json_data: dict, namespacing: bool = True) -> SimpleNamespace:
        if namespacing:
            return json.loads(json_data, object_hook=lambda x: SimpleNamespace(**x))
        return json.loads(json_data)

    @classmethod
    def compress_json(cls, export_json_data: dict) -> BytesIO:
        """
        Compresses JSON data into Gzip format.

        Args:
            export_json_data (dict): JSON data to be compressed.

        Returns:
            BytesIO: Gzip-compressed binary data.
        """
        # Compress JSON data into a Gzip file
        compressed_data = BytesIO()
        with gzip.GzipFile(fileobj=compressed_data, mode="wb") as zip_file:
            json_data = json.dumps(export_json_data)
            zip_file.write(json_data.encode("utf-8"))

        return compressed_data.getvalue()

    @classmethod
    def extract_json(cls, json_gzip_binary: bytes, namespacing: bool = True) -> dict:
        """
        Extracts JSON data from a Gzip-compressed binary.

        Args:
            json_gzip_binary (bytes): Gzip-compressed binary containing JSON data.

        Returns:
            dict: Extracted JSON data.
        """
        try:
            return cls._extract_json(json_gzip_binary, namespacing=namespacing)
        except:
            return None

    @classmethod
    def _extract_json(cls, json_gzip_binary: bytes, namespacing: bool = True) -> dict:
        # Create a BytesIO object to store the content of the gzip file
        gzip_content = BytesIO(json_gzip_binary)

        # Create a GzipFile object
        with gzip.GzipFile(fileobj=gzip_content, mode="rb") as gzip_ref:
            json_data = gzip_ref.read().decode("utf-8")

        # Load the JSON data
        return cls.load_json(json_data, namespacing=namespacing)
