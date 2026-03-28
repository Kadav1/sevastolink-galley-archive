const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export interface MediaAssetOut {
  id: string;
  asset_kind: string;
  original_filename: string | null;
  mime_type: string | null;
  relative_path: string;
  byte_size: number | null;
  created_at: string;
}

async function _uploadMedia(url: string, file: File): Promise<{ data: MediaAssetOut }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(url, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(body?.detail ?? `Upload failed: ${res.status}`);
  }
  return res.json() as Promise<{ data: MediaAssetOut }>;
}

/**
 * Attach a source image or PDF to an existing intake job.
 * Accepted types: image/jpeg, image/png, image/webp, application/pdf. Max 20 MB.
 */
export function attachIntakeMedia(jobId: string, file: File): Promise<{ data: MediaAssetOut }> {
  return _uploadMedia(`${API_BASE}/api/v1/intake-jobs/${jobId}/media`, file);
}

/**
 * Attach a cover image or PDF to an existing recipe.
 * Accepted types: image/jpeg, image/png, image/webp, application/pdf. Max 20 MB.
 */
export function attachRecipeMedia(idOrSlug: string, file: File): Promise<{ data: MediaAssetOut }> {
  return _uploadMedia(`${API_BASE}/api/v1/recipes/${idOrSlug}/media`, file);
}

/**
 * Retrieve metadata for a stored media asset.
 */
export async function getMediaAsset(assetId: string): Promise<{ data: MediaAssetOut }> {
  const res = await fetch(`${API_BASE}/api/v1/media-assets/${assetId}`);
  if (!res.ok) throw new Error(`Media asset not found: ${assetId}`);
  return res.json() as Promise<{ data: MediaAssetOut }>;
}

/**
 * Returns the URL to serve the raw binary of a media asset.
 * Use as <img src={mediaFileUrl(id)} /> or similar.
 */
export function mediaFileUrl(assetId: string): string {
  return `${API_BASE}/api/v1/media-assets/${assetId}/file`;
}
