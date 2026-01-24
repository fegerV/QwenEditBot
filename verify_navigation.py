#!/usr/bin/env python3
"""
Verification script for button navigation and callback handlers
"""

import re
from pathlib import Path

def parse_callbacks(file_path):
    """Parse callback handlers from menu.py"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all @router.callback_query decorators
    pattern = r'@router\.callback_query\(F\.data == "([^"]+)"\)'
    return set(re.findall(pattern, content))


def parse_buttons(file_path):
    """Parse button callback_data from keyboards.py"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all callback_data values
    pattern = r'callback_data="([^"]+)"'
    return set(re.findall(pattern, content))


def is_dynamic_callback(callback_data):
    """Check if callback is handled dynamically (prefix-based)"""
    dynamic_prefixes = [
        'as_style_',  # Artistic styles
        'pay_',       # Payment options
        'hairstyle_', # Hairstyles (dynamically matched)
    ]
    return any(callback_data.startswith(prefix) for prefix in dynamic_prefixes)


def main():
    menu_file = Path("c:/QwenEditBot/bot/handlers/menu.py")
    keyboard_file = Path("c:/QwenEditBot/bot/keyboards.py")
    
    callbacks = parse_callbacks(menu_file)
    buttons = parse_buttons(keyboard_file)
    
    print("=" * 80)
    print("NAVIGATION VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    # Filter out dynamic callbacks
    static_buttons = {b for b in buttons if not is_dynamic_callback(b)}
    dynamic_buttons = {b for b in buttons if is_dynamic_callback(b)}
    
    # Check for orphaned buttons (no handler)
    orphaned = static_buttons - callbacks
    if orphaned:
        print("[ERROR] ORPHANED BUTTONS (no handler): {}".format(len(orphaned)))
        for btn in sorted(orphaned):
            print("   - {}".format(btn))
        print()
    else:
        print("[OK] No orphaned buttons found")
        print()
    
    # Check for unused handlers
    unused = callbacks - buttons
    if unused:
        print("[WARNING] UNUSED HANDLERS (no button): {}".format(len(unused)))
        for handler in sorted(unused):
            print("   - {}".format(handler))
        print()
    else:
        print("[OK] All handlers are used")
        print()
    
    # Statistics
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print("Total callbacks defined: {}".format(len(callbacks)))
    print("Total static buttons: {}".format(len(static_buttons)))
    print("Total dynamic buttons: {}".format(len(dynamic_buttons)))
    print("Matched static callbacks: {}".format(len(callbacks & static_buttons)))
    print()
    
    # Coverage for static buttons
    coverage = (len(callbacks & static_buttons) / len(static_buttons) * 100) if static_buttons else 0
    print("Static Navigation Coverage: {:.1f}%".format(coverage))
    
    print()
    print("=" * 80)
    print("DYNAMIC CALLBACKS HANDLED BY PREFIX MATCHING")
    print("=" * 80)
    for prefix in ['as_style_', 'pay_', 'hairstyle_']:
        count = len([b for b in dynamic_buttons if b.startswith(prefix)])
        print("{}: {} buttons".format(prefix, count))
    
    if len(orphaned) == 0 and len(unused) <= 2:
        print()
        print("[PASS] VERIFICATION PASSED - Navigation is properly configured!")
        return 0
    else:
        print()
        print("[FAIL] VERIFICATION FAILED - Please fix the issues above")
        return 1


if __name__ == "__main__":
    exit(main())

