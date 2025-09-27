# ------------------------------------------------------------------
# Connection details – replace only the server and database names.
# ------------------------------------------------------------------
server   = r'Don_PC\SQLEXPRESS'
database = 'Main'

# ------------------------------------------------------------------
# ODBC connection string (Windows auth)
# ------------------------------------------------------------------
conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

# ------------------------------------------------------------------
# Grab the FRED API key from the database
# ------------------------------------------------------------------
import pyodbc

def _get_fred_api_key():
    """
    Connects to the SQL Server instance specified in `conn_str`, queries
    Main.fred.LKP_API_KEY for the column named 'api', and returns that value.
    
    Raises:
        RuntimeError: if the query fails or no key is returned.
    """
    try:
        with pyodbc.connect(conn_str) as cnxn:
            cursor = cnxn.cursor()
            # We use a simple SELECT – adjust the schema/table names if they differ
            cursor.execute("""
                SELECT TOP 1 api
                FROM Main.fred.LKP_API_KEY
            """)
            row = cursor.fetchone()
            if not row or not row[0]:
                raise RuntimeError("No API key found in Main.fred.LKP_API_KEY.api")
            return row[0]
    except Exception as exc:
        # Wrap any error so the caller sees a consistent message
        raise RuntimeError(
            "Could not retrieve the FRED API key from the database.\n"
            f"Original exception: {exc}"
        ) from exc

# Pull the key once, cache it in a module‑level variable
fred_key = _get_fred_api_key()
