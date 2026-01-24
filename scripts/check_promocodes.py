#!/usr/bin/env python3
"""
Script to check promocode validity
Usage: python scripts/check_promocodes.py [code1] [code2] ...
"""

import requests
import sys
import argparse
from typing import List

BACKEND_URL = "http://localhost:8000"


def check_promocode(code: str) -> dict:
    """Check if promocode is valid"""
    url = f"{BACKEND_URL}/api/promocodes/{code}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "valid": True,
                "code": data.get("code"),
                "amount": data.get("amount"),
                "is_used": data.get("is_used"),
                "used_at": data.get("used_at"),
                "used_by_user_id": data.get("used_by_user_id"),
                "created_at": data.get("created_at")
            }
        elif response.status_code == 404:
            return {
                "valid": False,
                "error": "Promocode not found"
            }
        else:
            return {
                "valid": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def check_multiple_promocodes(codes: List[str]):
    """Check multiple promocodes"""
    print("Promocode Validation Check")
    print("=" * 60)
    print()
    
    valid_count = 0
    invalid_count = 0
    
    for code in codes:
        result = check_promocode(code.upper())
        
        if result["valid"]:
            valid_count += 1
            status = "USED" if result["is_used"] else "AVAILABLE"
            print(f"[VALID] {result['code']}")
            print(f"   Amount: {result['amount']} points")
            print(f"   Status: {status}")
            if result["is_used"]:
                print(f"   Used at: {result['used_at']}")
                print(f"   Used by user ID: {result['used_by_user_id']}")
            print(f"   Created: {result['created_at']}")
        else:
            invalid_count += 1
            print(f"[INVALID] {code.upper()}")
            print(f"   Error: {result['error']}")
        
        print()
    
    print("=" * 60)
    print(f"Summary: {valid_count} valid, {invalid_count} invalid")
    print(f"Total checked: {len(codes)}")


def list_all_promocodes(limit: int = 50):
    """List all promocodes from API"""
    url = f"{BACKEND_URL}/api/promocodes/list"
    params = {"limit": limit}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            promocodes = response.json()
            print(f"All Promocodes (showing {len(promocodes)}):")
            print("=" * 60)
            print()
            
            for pc in promocodes:
                status = "USED" if pc["is_used"] else "AVAILABLE"
                print(f"{pc['code']} - {pc['amount']} points - {status}")
            
            print()
            print(f"Total: {len(promocodes)} promocodes")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Check promocode validity")
    parser.add_argument(
        "codes",
        nargs="*",
        help="Promocode(s) to check"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all promocodes"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Limit for list command (default: 50)"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_all_promocodes(limit=args.limit)
    elif args.codes:
        check_multiple_promocodes(args.codes)
    else:
        print("Usage:")
        print("  python scripts/check_promocodes.py CODE1 CODE2 ...")
        print("  python scripts/check_promocodes.py --list")
        print()
        print("Examples:")
        print("  python scripts/check_promocodes.py TL6FA1DY TEST123")
        print("  python scripts/check_promocodes.py --list")


if __name__ == "__main__":
    main()
