#!/usr/bin/env python3
"""
Safe disk cleanup script for Windows.
Only cleans items classified as "safe" - pip cache, temp files, recycle bin.
Requires user confirmation before any deletion.
"""
import os, sys, shutil, subprocess
from pathlib import Path


def get_disk_usage(path="C:"):
    """Get current disk usage."""
    total, used, free = shutil.disk_usage(path)
    return {"total_gb": total // (1024**3), "used_gb": used // (1024**3), "free_gb": free // (1024**3)}


def clean_pip_cache():
    """Clear pip download cache."""
    print("[1/4] Clearing pip cache...")
    result = subprocess.run(["pip", "cache", "purge"], capture_output=True, text=True)
    print(f"  {result.stdout.strip()}")
    return "pip cache" in result.stdout.lower()


def clean_user_temp():
    """Clear user temporary files."""
    print("[2/4] Clearing user temp files...")
    tmp = Path(os.environ.get("TEMP", ""))
    if tmp.exists():
        count = 0
        for item in tmp.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
                count += 1
            except (OSError, PermissionError):
                pass
        print(f"  Removed {count} items from {tmp}")
        return True
    return False


def clean_windows_temp():
    """Clear Windows temp directory."""
    print("[3/4] Clearing Windows temp files...")
    tmp = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp"
    if tmp.exists():
        count = 0
        for item in tmp.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
                count += 1
            except (OSError, PermissionError):
                pass
        print(f"  Removed {count} items from {tmp}")
        return True
    return False


def clean_recycle_bin():
    """Empty Windows Recycle Bin."""
    print("[4/4] Emptying Recycle Bin...")
    try:
        import ctypes
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        print("  Recycle Bin emptied")
        return True
    except Exception:
        return False


def main():
    print("=" * 50)
    print("  Windows Disk Cleaner - Safe Mode")
    print("=" * 50)

    before = get_disk_usage()
    print(f"\nBefore: {before['free_gb']} GB free ({before['free_gb']/before['total_gb']*100:.1f}%)")
    print(f"Total: {before['total_gb']} GB | Used: {before['used_gb']} GB")

    print("\nThe following will be cleaned:")
    print("  1. pip cache (downloaded Python packages)")
    print("  2. User temporary files (%TEMP%)")
    print("  3. Windows temporary files")
    print("  4. Recycle Bin")
    print("\nThese are ALL safe to delete and will not affect any software.")

    confirm = input("\nProceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    results = []
    results.append(("pip cache", clean_pip_cache()))
    results.append(("User Temp", clean_user_temp()))
    results.append(("Windows Temp", clean_windows_temp()))
    results.append(("Recycle Bin", clean_recycle_bin()))

    after = get_disk_usage()
    freed = after["free_gb"] - before["free_gb"]

    print(f"\n{'='*50}")
    print("  Cleanup Complete")
    print(f"{'='*50}")
    for name, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\nBefore: {before['free_gb']} GB free")
    print(f"After:  {after['free_gb']} GB free")
    print(f"Freed:  +{freed} GB")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
