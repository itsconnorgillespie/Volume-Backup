import os
import pathlib
import sys
import zipfile
from fnmatch import fnmatch
from zipfile import ZipFile
from datetime import datetime, timezone
from src.logger import get_logger
from src.settings import Settings
from src.storage import get_s3_client, upload_s3_file

logger = get_logger()


def get_filename(prefix: str | None) -> str:
    """ Build the filename using current UTC time and prefix. """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}{timestamp}.zip" if prefix else f"{timestamp}.zip"


def check_excluded(name: str, exclude_patterns: list[str]) -> bool:
    """ Check if the provided filename or directory matches any configured glob pattern. """
    return any(fnmatch(name, pattern) for pattern in exclude_patterns)


def create_zip(source_directory: str, destination_directory: str, exclude_patterns: list[str] | None = None) -> None:
    """ Creates a lossless zip archive of the provided source directory in the provided destination directory. """
    source = pathlib.Path(source_directory)
    if not source.is_dir():
        logger.error(f"Source directory {source} does not exist.")
        sys.exit(1)

    files = 0
    with ZipFile(destination_directory, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root, directories, filenames in os.walk(source):
            kept = []
            for directory in directories:
                if check_excluded(directory, exclude_patterns):
                    logger.info(f"Skipping excluded directory. | {directory}")
                else:
                    kept.append(directory)
            directories[:] = kept

            for filename in filenames:
                if check_excluded(filename, exclude_patterns):
                    logger.info(f"Skipping excluded filename. | {filename}")
                    continue
                full_path = pathlib.Path(root) / filename
                arcname = full_path.relative_to(source)
                archive.write(str(full_path), str(arcname))
                files += 1

    if files == 0:
        logger.error(f"Source directory {source} does not contain any files.")
        sys.exit(1)

    megabytes = os.path.getsize(destination_directory) / (1024 * 1024)
    logger.info(f"Zipped a total of {files} files with a size of {megabytes:.1f} MiB.")


def main() -> None:
    settings = Settings.from_env()
    os.makedirs(settings.TEMPORARY_DIRECTORY, exist_ok=True)

    filename = get_filename(settings.S3_PREFIX)
    path = os.path.join(settings.TEMPORARY_DIRECTORY, filename)

    logger.info(f"Zipping. | {settings.DATA_DIRECTORY} -> {settings.TEMPORARY_DIRECTORY}")
    create_zip(settings.DATA_DIRECTORY, path, settings.EXCLUDE_PATTERNS)

    client = get_s3_client(settings)
    if not upload_s3_file(client, settings, path, filename):
        os.remove(path)
        sys.exit(1)

    os.remove(path)
    logger.info("Finished.")


if __name__ == "__main__":
    main()
