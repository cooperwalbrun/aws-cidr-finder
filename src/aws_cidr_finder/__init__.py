from importlib_metadata import PackageNotFoundError, version

try:
    # We hard-code the name rather than using __name__ because the package name has an underscore
    # instead of a hyphen
    dist_name = "aws-cidr-finder"
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
