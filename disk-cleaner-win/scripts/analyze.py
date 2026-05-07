#!/usr/bin/env python3
"""
Windows Disk Space Analyzer
Recursively scans directories, identifies large space consumers, and categorizes
items by safety level (safe to clean / cache / app data / critical).
Outputs a ranked report in terminal and JSON.
"""
import os, json, sys
from pathlib import Path
from collections import defaultdict

# Known paths that are safe to clean or can be cleaned with caution
SAFE_PATTERNS = [
    r"AppData\Local\Temp",
    r"AppData\Local\pip\cache",
    r"Windows\Temp",
    r"\$Recycle\.Bin",
    r"AppData\Local\npm-cache",
    r"\.cache",
]

APP_CACHE_PATTERNS = [
    r"AppData\Roaming\baidu",
    r"AppData\Roaming\Tencent",
    r"AppData\Roaming\kingsoft",
    r"AppData\Roaming\bilibili",
    r"AppData\Roaming\douyin",
    r"AppData\Roaming\SodaMusic",
    r"AppData\Roaming\thunder",
    r"AppData\Roaming\npm",
]

CRITICAL_PATTERNS = [
    r"Windows\System32",
    r"Program Files$",
    r"Program Files \(x86\)$",
    r"Users\\[^\\]+\Documents",
    r"Users\\[^\\]+\Desktop",
]


def get_size_mb(path: Path) -> float:
    """Get directory size in megabytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass
    return total / (1024 * 1024)


def classify_path(path_str: str) -> str:
    """Classify a path by safety level."""
    import re
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return "safe"
    for pattern in APP_CACHE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return "cache"
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return "critical"
    return "unknown"


def analyze_drive(drive: str = "C:", max_depth: int = 3, min_size_mb: float = 50):
    """Analyze a drive and return categorized results."""
    root = Path(drive + "/")
    results = defaultdict(list)

    # Scan user directories
    user_dirs = [
        root / "Users",
        root / "Windows" / "Temp",
        root / "$Recycle.Bin",
    ]

    # Also scan Users subdirectories
    users_path = root / "Users"
    if users_path.exists():
        for user_dir in users_path.iterdir():
            if user_dir.is_dir():
                appdata = user_dir / "AppData"
                if appdata.exists():
                    for sub in ["Local", "Roaming"]:
                        subpath = appdata / sub
                        if subpath.exists():
                            try:
                                for item in subpath.iterdir():
                                    if item.is_dir():
                                        size = get_size_mb(item)
                                        if size > min_size_mb:
                                            cat = classify_path(str(item))
                                            results[cat].append({
                                                "path": str(item),
                                                "size_mb": round(size, 1),
                                                "size_gb": round(size / 1024, 2),
                                            })
                            except PermissionError:
                                pass

    # Sort each category by size descending
    for cat in results:
        results[cat].sort(key=lambda x: x["size_mb"], reverse=True)

    return dict(results)


def print_report(results: dict):
    """Print a formatted analysis report."""
    print("\n" + "=" * 70)
    print("  Windows Disk Space Analysis Report")
    print("=" * 70)

    icons = {"safe": "[SAFE TO CLEAN]", "cache": "[APP CACHE]", "critical": "[DO NOT TOUCH]", "unknown": "[REVIEW]"}

    for cat in ["safe", "cache", "unknown", "critical"]:
        items = results.get(cat, [])
        if not items:
            continue
        total = sum(i["size_mb"] for i in items)
        print(f"\n  {icons[cat]}  Total: {total/1024:.1f} GB ({len(items)} items)")
        print(f"  {'-'*60}")
        for item in items[:10]:  # Top 10 per category
            print(f"  {item['size_gb']:>6.1f} GB  {item['path']}")

    total_all = sum(sum(i["size_mb"] for i in items) for items in results.values())
    print(f"\n  TOTAL ANALYZED: {total_all/1024:.1f} GB")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    drive = sys.argv[1] if len(sys.argv) > 1 else "C:"
    output = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Analyzing {drive} drive...")
    results = analyze_drive(drive)
    print_report(results)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Full report saved to: {output}")
