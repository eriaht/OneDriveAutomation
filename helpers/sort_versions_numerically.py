def sort_versions_numerically(versions):
    """
    Sort a list of version strings numerically.
    Example input: ["25.155.0811.0002", "25.155.0811.0001"]
    """
    return sorted(
        versions,
        key=lambda v: [int(part) for part in v.split('.')]
    )
