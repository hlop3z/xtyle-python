import pathlib
from collections import namedtuple

# sample_codes_path = pathlib.Path(__file__).parent / "sample-codes"
templates_codes_path = pathlib.Path(__file__).parent / "templates-tools"
component_codes_path = pathlib.Path(__file__).parent / "component-samples"


File = namedtuple("File", ["name", "text"], module="xtyle")


def get_samples(root_path):
    files_dict = {}

    for item in root_path.rglob("*"):
        key = item.name.replace(".", "_").replace("-", "_")
        with open(item, "r", encoding="utf-8") as file:
            files_dict[key] = File(
                name=item.name,
                text=file.read(),
            )

    SampleFiles = namedtuple("Files", list(files_dict.keys()), module="xtyle")
    sample_files = SampleFiles(**files_dict)

    return sample_files


# sample = get_samples(sample_codes_path)
component = get_samples(component_codes_path)
templates_tools = get_samples(templates_codes_path)
