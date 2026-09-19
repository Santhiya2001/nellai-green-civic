/**
 * Builds a Wikimedia Commons hotlink via Special:FilePath, which resolves
 * (and, given `width`, thumbnails) a file by its exact title without
 * needing to hand-construct the upload.wikimedia.org hash-prefixed path.
 * All images referenced this way are CC0/public domain or CC-BY(-SA) --
 * see each call site's comment for the required photo credit.
 */
export function wikimediaFile(title: string, width?: number): string {
  const encoded = encodeURIComponent(title);
  return `https://commons.wikimedia.org/wiki/Special:FilePath/${encoded}${width ? `?width=${width}` : ""}`;
}
