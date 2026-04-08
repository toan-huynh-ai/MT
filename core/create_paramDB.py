from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _load_json(path: Path) -> Dict[str, Any]:
	with path.open("r", encoding="utf-8") as handle:
		return json.load(handle)


def _normalize_description(description: str) -> str:
	return " ".join(description.split())


def _extract_module_from_path(path: str) -> str:
	"""Extract module name from path (first segment before first dot)."""
	if not isinstance(path, str) or "." not in path:
		return ""
	return path.split(".")[0]


def extract_parameters(rta_data: Dict[str, Any]) -> Dict[str, Any]:
	extracted: Dict[str, Any] = {}
	for item in rta_data.get("parameters", []):
		if not isinstance(item, dict):
			continue
		shortname = item.get("shortname")
		description = item.get("description")
		path = item.get("path")
		if not shortname:
			continue
		
		# Build entry with module info
		entry = {}
		if isinstance(description, str) and description.strip():
			entry["description"] = _normalize_description(description)
		
		# Extract module from path
		if isinstance(path, str):
			module = _extract_module_from_path(path)
			if module:
				entry["module"] = module
		
		# Only add if we have at least description
		if entry:
			extracted[shortname] = entry
	return extracted


def merge_param_db(existing: Dict[str, Any], extracted: Dict[str, Any]) -> Dict[str, Any]:
	merged = dict(existing)
	for key, value in extracted.items():
		if key not in merged or not _is_entry_valid(merged[key]):
			merged[key] = value
		else:
			# Merge entries: add module info if not present
			if isinstance(value, dict) and isinstance(merged[key], dict):
				if "module" in value and "module" not in merged[key]:
					merged[key]["module"] = value["module"]
	return dict(sorted(merged.items(), key=lambda item: item[0].lower()))


def _is_entry_valid(entry: Any) -> bool:
	"""Check if an entry has meaningful content."""
	if isinstance(entry, str):
		return bool(entry.strip())
	if isinstance(entry, dict):
		return bool(entry.get("description") or entry.get("module"))
	return bool(entry)


def parse_args() -> argparse.Namespace:
	base_dir = Path(__file__).resolve().parents[2]
	default_input = base_dir / "input" / "RTA-FLOW_DB_full.json"
	default_output = base_dir / "ParamsFolder" / "paramDB.json"

	parser = argparse.ArgumentParser(
		description="Generate/extend paramDB.json from RTA-FLOW_DB_full.json"
	)
	parser.add_argument("--input", type=Path, default=default_input)
	parser.add_argument("--output", type=Path, default=default_output)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	if not args.input.exists():
		raise FileNotFoundError(f"Input file not found: {args.input}")

	rta_data = _load_json(args.input)
	extracted = extract_parameters(rta_data)

	existing: Dict[str, str] = {}
	if args.output.exists():
		existing = _load_json(args.output)

	merged = merge_param_db(existing, extracted)
	args.output.parent.mkdir(parents=True, exist_ok=True)

	with args.output.open("w", encoding="utf-8") as handle:
		json.dump(merged, handle, ensure_ascii=False, indent=4)
		handle.write("\n")

	print(
		f"paramDB.json updated: {len(existing)} existing, {len(extracted)} extracted, {len(merged)} total"
	)
	print(f"Output path: {args.output}")


if __name__ == "__main__":
	main()
