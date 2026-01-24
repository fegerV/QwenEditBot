#!/usr/bin/env python3
"""
Script to generate promocodes and save them to a file.
Usage: python scripts/generate_promocodes.py
"""

import requests
import json
import argparse
from typing import List

BACKEND_URL = "http://localhost:8000"


def generate_single_promocode(amount: int, custom_code: str = None):
    """Generate a single promocode"""
    url = f"{BACKEND_URL}/api/promocodes/generate"
    params = {"amount": amount}
    if custom_code:
        params["custom_code"] = custom_code
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def batch_generate_promocodes(amounts: List[int]):
    """Generate multiple promocodes and save to file"""
    url = f"{BACKEND_URL}/api/promocodes/batch-generate"
    data = {"amounts": amounts}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate promocodes")
    parser.add_argument(
        "--single",
        type=int,
        help="Generate single promocode with specified amount (points)"
    )
    parser.add_argument(
        "--custom-code",
        type=str,
        help="Custom code for single promocode"
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        type=int,
        help="Generate batch of promocodes with specified amounts (e.g., --batch 100 200 300)"
    )
    
    args = parser.parse_args()
    
    if args.single:
        # Generate single promocode
        print(f"Generating promocode for {args.single} points...")
        result = generate_single_promocode(args.single, args.custom_code)
        
        if result:
            print("\n[OK] Promocode generated successfully!")
            print(f"   Code: {result['code']}")
            print(f"   Amount: {result['amount']} points")
            print(f"   Status: {'USED' if result['is_used'] else 'AVAILABLE'}")
            print(f"   Created: {result['created_at']}")
    
    elif args.batch:
        # Generate batch of promocodes
        print(f"Generating {len(args.batch)} promocodes...")
        result = batch_generate_promocodes(args.batch)
        
        if result:
            print("\n[OK] Promocodes generated successfully!")
            print(f"   Total: {result['count']} promocodes")
            print(f"   File: {result['file_path']}")
            print("\nGenerated promocodes:")
            for pc in result['promocodes']:
                print(f"   {pc['code']} - {pc['amount']} points")
    
    else:
        # Interactive mode
        print("Promocode Generator")
        print("=" * 40)
        print("Valid amounts: 100, 200, 300, 400, 500, 1000, 2000, 3000, 5000 points")
        print()
        
        choice = input("Mode (single/batch): ").strip().lower()
        
        if choice == "single":
            amount = int(input("Enter amount: "))
            custom_code = input("Enter custom code (optional, press Enter to skip): ").strip() or None
            
            result = generate_single_promocode(amount, custom_code)
            
            if result:
                print("\n[OK] Promocode generated successfully!")
                print(f"   Code: {result['code']}")
                print(f"   Amount: {result['amount']} points")
        
        elif choice == "batch":
            amounts_input = input("Enter amounts separated by spaces (e.g., 100 200 300 500): ").strip()
            amounts = [int(x) for x in amounts_input.split()]
            
            result = batch_generate_promocodes(amounts)
            
            if result:
                print("\n[OK] Promocodes generated successfully!")
                print(f"   Total: {result['count']} promocodes")
                print(f"   File: {result['file_path']}")
        
        else:
            print("Invalid choice. Use 'single' or 'batch'.")


if __name__ == "__main__":
    main()
