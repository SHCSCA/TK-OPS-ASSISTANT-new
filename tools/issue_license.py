#!/usr/bin/env python3
"""License Issuer CLI — run on YOUR machine to generate keys for customers.

Usage
-----
  python tools/issue_license.py <machine_id_short_or_full> [--days N] [--tier pro]

Examples
--------
  # Permanent pro license for machine 829D-598A-6587-A85A
  python tools/issue_license.py 829D-598A-6587-A85A

  # 365-day enterprise license
  python tools/issue_license.py 829D-598A-6587-A85A --days 365 --tier enterprise

  # Show this machine's ID (for testing)
  python tools/issue_license.py --self
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from desktop_app.services.fingerprint import get_machine_id, get_machine_id_short, get_compound_id
from desktop_app.services.license_codec import issue_license, verify_license, VALID_TIERS, _is_compound_id


def main() -> None:
    parser = argparse.ArgumentParser(description="TK-OPS License Issuer")
    parser.add_argument("machine_id", nargs="?", help="Machine ID (short XXXX-XXXX-XXXX-XXXX or full 64-hex)")
    parser.add_argument("--days", type=int, default=0, help="Validity in days (0 = permanent)")
    parser.add_argument("--tier", choices=VALID_TIERS, default="pro", help="License tier")
    parser.add_argument("--self", action="store_true", dest="show_self", help="Show this machine's ID")
    parser.add_argument("--verify", metavar="KEY", help="Verify a license key against a machine ID")

    args = parser.parse_args()

    if args.show_self:
        print(f"Machine ID (full):     {get_machine_id()}")
        print(f"Machine ID (short):    {get_machine_id_short()}")
        print(f"Compound ID (v2):      {get_compound_id()}")
        return

    if args.verify:
        if not args.machine_id:
            print("Error: provide machine_id to verify against", file=sys.stderr)
            raise SystemExit(1)
        mid = _resolve_machine_id(args.machine_id)
        try:
            info = verify_license(args.verify, mid)
            print(f"✓ Valid — tier={info.tier}, expiry={info.expiry or 'permanent'}, remaining={info.days_remaining}")
        except Exception as e:
            print(f"✗ Invalid — {e}", file=sys.stderr)
            raise SystemExit(1)
        return

    if not args.machine_id:
        parser.print_help()
        raise SystemExit(1)

    mid = _resolve_machine_id(args.machine_id)
    expiry = dt.date.today() + dt.timedelta(days=args.days) if args.days > 0 else None

    key = issue_license(mid, expiry=expiry, tier=args.tier)

    print("=" * 60)
    print(f"  Machine ID:  {args.machine_id}")
    print(f"  Tier:        {args.tier}")
    print(f"  Expiry:      {expiry.isoformat() if expiry else 'permanent'}")
    print(f"  License Key:")
    print()
    print(f"  {key}")
    print()
    print("=" * 60)


def _resolve_machine_id(raw: str) -> str:
    """Accept compound (v2), short (XXXX-XXXX-XXXX-XXXX) or full 64-hex form."""
    # Compound v2 format: cpu16:board16:disk16:mac16
    if _is_compound_id(raw):
        return raw
    clean = raw.replace("-", "").replace(" ", "").lower()
    if len(clean) == 64:
        return clean
    if len(clean) == 16:
        # Short form — auto-expand to compound ID from local machine
        local_full = get_machine_id()
        if local_full[:16] == clean:
            return get_compound_id()
        print(f"Error: short ID '{raw}' does not match this machine.", file=sys.stderr)
        print("Remote license issuance requires the full 64-char or compound machine_id.", file=sys.stderr)
        raise SystemExit(2)
    return clean


if __name__ == "__main__":
    main()
