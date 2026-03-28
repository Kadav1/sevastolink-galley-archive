"""
Media domain schemas.
"""
from pydantic import BaseModel


class MediaAssetOut(BaseModel):
    id: str
    asset_kind: str
    original_filename: str | None
    mime_type: str | None
    relative_path: str
    byte_size: int | None
    created_at: str

    model_config = {"from_attributes": True}
