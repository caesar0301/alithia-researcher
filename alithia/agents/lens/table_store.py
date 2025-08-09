import os
from typing import Any, Dict, List, Optional

from supabase import create_client, Client


class SupabaseTableStore:
    def __init__(self, url_env: str = "SUPABASE_URL", key_env: str = "SUPABASE_ANON_KEY") -> None:
        url = os.getenv(url_env)
        key = os.getenv(key_env)
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY are required in environment for Lens table store")
        self.client: Client = create_client(url, key)

    def upsert_document(self, table: str, doc: Dict[str, Any]) -> None:
        self.client.table(table).upsert(doc).execute()

    def upsert_chunks(self, table: str, chunks: List[Dict[str, Any]]) -> None:
        if not chunks:
            return
        self.client.table(table).upsert(chunks).execute()

    def get_document(self, table: str, doc_id: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(table).select("*").eq("id", doc_id).limit(1).execute()
        data = getattr(res, "data", None) or res.get("data", None)
        if data:
            return data[0]
        return None