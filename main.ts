// news-image-20261118: "The World in One Day" — Wednesday 18 November 2026.
// The poster is pre-rendered by tools/render.py into assets/poster.png;
// this entrypoint only copies it to /output/entry.png (Node stdlib only,
// no network, deterministic).
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(root, "assets", "poster.png"), join(outDir, "entry.png"));
