class ImportResult:

    def __init__(self, p_imported: int, p_skipped: int, p_errors: int):
        self.imported = p_imported
        self.skipped = p_skipped
        self.errors = p_errors