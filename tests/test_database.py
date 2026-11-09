from naviqra.database import Database, DatabaseConnection


class RecordingConnection:
    def __init__(self):
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append((sql, params))
        return self


def test_sqlite_database_health(tmp_path):
    database = Database(str(tmp_path / "db.sqlite"))
    with database.connect() as conn:
        conn.execute("CREATE TABLE sample (id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO sample VALUES (?)", ("one",))
        row = conn.execute("SELECT id FROM sample").fetchone()
    assert row["id"] == "one"
    database.check()


def test_postgres_placeholder_translation_and_schema_split():
    raw = RecordingConnection()
    conn = DatabaseConnection(raw, "postgresql")
    conn.execute("SELECT * FROM sample WHERE id=? AND tenant=?", ("a", "b"))
    conn.executescript("CREATE TABLE one (id TEXT); CREATE TABLE two (id TEXT);")
    assert raw.statements[0] == (
        "SELECT * FROM sample WHERE id=%s AND tenant=%s", ("a", "b")
    )
    assert raw.statements[1][0] == "CREATE TABLE one (id TEXT)"
    assert raw.statements[2][0] == "CREATE TABLE two (id TEXT)"
