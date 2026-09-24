/**
 * FastAPI error responses come in two shapes that look identical at the
 * type level (`err.response.data.detail`) but are structurally different:
 *   - A raised HTTPException: detail is a plain string.
 *   - A 422 Pydantic validation error: detail is an ARRAY of
 *     {loc, msg, type} objects.
 * Rendering the array case directly as JSX crashes the whole page (React
 * can't render a plain object as a child, and this app has no error
 * boundary), which is exactly what a blank white screen after a failed
 * form submission usually means. Always route error extraction through
 * this helper instead of reading `.detail` directly.
 */
export function extractErrorMessage(err: unknown, fallback: string): string {
  const detail = (err as any)?.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : undefined;
        const msg = item?.msg || "Invalid value";
        return field ? `${field}: ${msg}` : msg;
      })
      .join("; ");
  }

  return fallback;
}
