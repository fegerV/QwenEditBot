#!/usr/bin/env python3
"""Test script to verify Qwen workflow simplification"""

import sys
import os
sys.path.append('/home/engine/project')

def test_qwen_workflow_simplification():
    """Test that Qwen workflow is simplified correctly"""
    
    print("🔍 Testing Qwen workflow simplification...")
    
    # Test 1: Check that factory files are deleted
    factory_files = [
        '/home/engine/project/worker/workflows/__init__.py',
        '/home/engine/project/worker/workflows/standard.py'
    ]
    
    for file_path in factory_files:
        if os.path.exists(file_path):
            print(f"❌ Factory file still exists: {file_path}")
            return False
        else:
            print(f"✅ Factory file removed: {file_path}")
    
    # Test 2: Check that only qwen_edit_2511.py exists
    workflow_dir = '/home/engine/project/worker/workflows'
    workflow_files = [f for f in os.listdir(workflow_dir) if not f.startswith('__pycache__')]
    if 'qwen_edit_2511.py' not in workflow_files:
        print("❌ qwen_edit_2511.py not found")
        return False
    elif len(workflow_files) != 1:
        print(f"❌ Unexpected files in workflow directory: {workflow_files}")
        return False
    else:
        print("✅ Only qwen_edit_2511.py exists")
    
    # Test 3: Check Job model simplification
    with open('/home/engine/project/backend/app/models.py', 'r') as f:
        models_content = f.read()
    
    if 'workflow_type' in models_content:
        print("❌ Job model still contains workflow_type")
        return False
    else:
        print("✅ Job model doesn't contain workflow_type")
    
    if 'workflow_config' in models_content:
        print("❌ Job model still contains workflow_config")
        return False
    else:
        print("✅ Job model doesn't contain workflow_config")
    
    # Test 4: Check Preset model simplification
    if 'workflow_type' in models_content and 'Preset' in models_content:
        # Need to check if it's specifically in Preset model
        preset_section = models_content.split('class Preset')[1].split('class')[0]
        if 'workflow_type' in preset_section:
            print("❌ Preset model still contains workflow_type")
            return False
        else:
            print("✅ Preset model doesn't contain workflow_type")
    
    # Test 5: Check schemas simplification
    with open('/home/engine/project/backend/app/schemas.py', 'r') as f:
        schemas_content = f.read()
    
    if 'workflow_type' in schemas_content:
        print("❌ Schemas still contain workflow_type")
        return False
    else:
        print("✅ Schemas don't contain workflow_type")
    
    # Test 6: Check that get_workflow is not imported anywhere (excluding test files)
    import subprocess
    result = subprocess.run([
        'grep', '-r', 'get_workflow', '/home/engine/project', '--include=*.py', '--exclude=test_*.py'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"❌ get_workflow still found in: {result.stdout}")
        return False
    else:
        print("✅ get_workflow function not found anywhere")
    
    # Test 7: Check that build_workflow function exists
    with open('/home/engine/project/worker/workflows/qwen_edit_2511.py', 'r') as f:
        workflow_content = f.read()
    
    if 'def build_workflow' not in workflow_content:
        print("❌ build_workflow function not found")
        return False
    else:
        print("✅ build_workflow function exists")
    
    # Test 8: Check that parameters are hardcoded
    if 'scale_megapixels = 2' in workflow_content and 'steps = 20' in workflow_content:
        print("✅ Parameters are hardcoded (scale_megapixels=2, steps=20)")
    else:
        print("❌ Parameters are not hardcoded as expected")
        return False
    
    # Test 9: Check API simplification
    with open('/home/engine/project/backend/app/api/jobs.py', 'r') as f:
        api_content = f.read()
    
    if 'preset_id' in api_content and 'workflow_type' not in api_content:
        print("✅ API simplified - no workflow_type, but preset_id might still be there")
    elif 'workflow_type' not in api_content:
        print("✅ API simplified - no workflow_type")
    else:
        print("❌ API still contains workflow_type")
        return False
    
    print("\n🎉 All tests passed! Qwen workflow simplification is successful!")
    return True

if __name__ == "__main__":
    try:
        success = test_qwen_workflow_simplification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)