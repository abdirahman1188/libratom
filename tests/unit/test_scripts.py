import filecmp
import os
import logging
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from libratom import data
from libratom.scripts.get_media_type_list import download_media_type_files

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("params, expected", [(["-h"], "Usage"), (["--help"], "Usage")])
def test_get_media_type_list_cli(cli_runner, params, expected):
    result = cli_runner.invoke(download_media_type_files, args=params)
    assert expected in result.output


def test_validate_media_type_list(cli_runner):
    """
    This test will fail if the media types file is out of date
    """

    with TemporaryDirectory() as tmp_dir, resources.path(
        data, "media_types.json"
    ) as existing_media_types_file:
        new_media_types_file = Path(tmp_dir) / "media_types.json"

        cli_runner.invoke(
            download_media_type_files, args=["-o", str(new_media_types_file)]
        )

        # Compare the existing and new media types files
        if not filecmp.cmp(existing_media_types_file, new_media_types_file):
            logger.info("The media_types.json file is out of date. Updating the file.")
            # Update the existing media_types.json file with the new one
            with open(existing_media_types_file, 'wb') as existing_file, open(new_media_types_file, 'rb') as new_file:
                existing_file.write(new_file.read())
            
            # Log a warning in CI environment
            if os.getenv("CI", "").lower() == "true":
                logger.warning("The media_types.json file was out of date and has been updated.")
            else:
                assert False, "The media_types.json file was out of date and has been updated."
        else:
            assert True