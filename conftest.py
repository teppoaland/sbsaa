"""
Pytest Configuration with Azure DevOps Integration Hooks
File location: sbsaa/conftest.py

This file contains pytest fixtures and hooks that automatically integrate test results with Azure DevOps
"""

import os
import sys
import pytest
from pathlib import Path

# Add azure_integration to path
sys.path.append(str(Path(__file__).parent / "azure_integration"))
sys.path.append(str(Path(__file__).parent / "config"))

# Try to import Azure integration components
try:
    from azure_integration.azure_devops_client import AzureDevOpsClient, TestCaseMapper
    AZURE_INTEGRATION_AVAILABLE = True
    print("Azure DevOps integration loaded successfully")
except ImportError as e:
    AZURE_INTEGRATION_AVAILABLE = False
    print(f"Azure DevOps integration not available: {e}")


@pytest.fixture(autouse=True)
def azure_devops_integration_fixture(request):
    """
    Automatic fixture that runs for every test
    Sets up Azure DevOps integration context for each test
    """
    if not AZURE_INTEGRATION_AVAILABLE:
        return
    
    # Only initialize if we're in CI/CD environment (has Azure secrets)
    if not os.getenv('AZURE_DEVOPS_PAT'):
        print("Azure DevOps PAT not found - skipping integration (normal for local development)")
        return
    
    try:
        # Initialize Azure DevOps integration
        azure = AzureDevOpsClient()
        mapper = TestCaseMapper()
        
        # Get test function name
        test_name = request.node.name
        
        # Check if test has Azure work item mapping
        work_item_id = mapper.get_work_item_id(test_name)
        
        if work_item_id:
            print(f"Azure DevOps: Test {test_name} linked to work item {work_item_id}")
            
            # Store for use in test result reporting
            request.node.azure_work_item_id = work_item_id
            request.node.azure_integration = azure
        else:
            # Check if test has decorator work item ID
            test_func = getattr(request.node.obj, request.node.name, None) if hasattr(request.node, 'obj') else None
            if test_func and hasattr(test_func, 'azure_work_item_id'):
                decorator_id = test_func.azure_work_item_id
                print(f"Azure DevOps: Found decorator work item ID {decorator_id} for {test_name}")
                request.node.azure_work_item_id = decorator_id
                request.node.azure_integration = azure
            else:
                print(f"Azure DevOps: No work item mapping found for {test_name}")
                
    except Exception as e:
        print(f"Azure DevOps integration setup failed: {e}")


def pytest_runtest_logreport(report):
    """
    Pytest hook that runs after each test phase (setup, call, teardown)
    Automatically updates Azure DevOps based on test results
    """
    if not AZURE_INTEGRATION_AVAILABLE:
        return
        
    # Only process the main test execution phase.
    if report.when != "call":
        return
    
    print(f"DEBUG: Processing {report.nodeid}, has azure_work_item_id: {hasattr(report, 'azure_work_item_id')}")
    
    # Only run if we have Azure DevOps integration configured
    if not hasattr(report, 'azure_work_item_id') or not hasattr(report, 'azure_integration'):
        return
    
    azure = report.azure_integration
    work_item_id = report.azure_work_item_id
    
    try:
        print(f"Azure DevOps: Updating work item {work_item_id} with test results")
        
        # Determine test status and create execution details
        if report.passed:
            test_status = "PASSED"
            execution_details = f"""
            Test executed successfully on {report.start}
            Duration: {report.duration:.2f} seconds
            Test: {report.nodeid}
            """
            print(f"Azure DevOps: Test PASSED - updating work item {work_item_id}")
            
        elif report.failed:
            test_status = "FAILED"
            execution_details = f"""
            Test failed on {report.start}
            Duration: {report.duration:.2f} seconds
            Test: {report.nodeid}
            
            Error Details:
            {str(report.longrepr)}
            """
            print(f"Azure DevOps: Test FAILED - creating bug and updating work item {work_item_id}")
            
            # Create bug for failed test
            try:
                bug_id = azure.create_bug_from_test_failure(
                    test_name=report.nodeid,
                    error_details=str(report.longrepr),
                    test_file=str(report.fspath) if hasattr(report, 'fspath') else 'unknown',
                    linked_test_case_id=work_item_id
                )
                print(f"Azure DevOps: Created bug {bug_id} for failed test")
            except Exception as bug_error:
                print(f"Azure DevOps: Failed to create bug: {bug_error}")
            
        else:  # skipped
            test_status = "SKIPPED"
            execution_details = f"""
            Test was skipped on {report.start}
            Reason: {str(report.longrepr) if report.longrepr else 'No reason provided'}
            Test: {report.nodeid}
            """
            print(f"Azure DevOps: Test SKIPPED - updating work item {work_item_id}")
        
        # Update the work item with test result
        azure.update_test_result(work_item_id, test_status, execution_details)
        print(f"Azure DevOps: Successfully updated work item {work_item_id} with {test_status} result")
        
    except Exception as e:
        print(f"Azure DevOps: Failed to update work item {work_item_id}: {e}")


def pytest_collection_modifyitems(config, items):
    """
    Hook that runs after test collection
    Validates Azure DevOps integration setup and work item mappings
    """
    if not AZURE_INTEGRATION_AVAILABLE:
        return
        
    # Only run validation in CI/CD environment
    if not os.getenv('AZURE_DEVOPS_PAT'):
        return
    
    try:
        mapper = TestCaseMapper()
        mappings = mapper.get_all_mappings()
        
        print(f"Azure DevOps: Validating {len(items)} collected tests")
        
        for item in items:
            test_name = item.name
            
            # Check if test has mapping
            if test_name in mappings:
                work_item_id = mappings[test_name]['work_item_id']
                print(f"Azure DevOps: ✓ {test_name} -> Work Item {work_item_id}")
            else:
                # Check for decorator
                test_func = getattr(item.obj, test_name, None) if hasattr(item, 'obj') else None
                if test_func and hasattr(test_func, 'azure_work_item_id'):
                    decorator_id = test_func.azure_work_item_id
                    print(f"Azure DevOps: ✓ {test_name} -> Decorator Work Item {decorator_id}")
                else:
                    print(f"Azure DevOps: ! {test_name} has no work item mapping")
        
    except Exception as e:
        print(f"Azure DevOps: Validation failed: {e}")


def pytest_sessionstart(session):
    """
    Hook that runs at the start of the test session
    Reports Azure DevOps integration status
    """
    print("\n" + "="*80)
    print("PYTEST SESSION START - Azure DevOps Integration Status")
    print("="*80)
    
    if AZURE_INTEGRATION_AVAILABLE:
        if os.getenv('AZURE_DEVOPS_PAT'):
            print("✓ Azure DevOps integration: ACTIVE")
            print(f"  Organization: {os.getenv('AZURE_DEVOPS_ORG_URL', 'Not set')}")
            print(f"  Project: {os.getenv('AZURE_DEVOPS_PROJECT', 'Not set')}")
            print("  Test results will be automatically updated in Azure DevOps")
        else:
            print("○ Azure DevOps integration: AVAILABLE but INACTIVE (no PAT token)")
            print("  Running in local development mode")
    else:
        print("✗ Azure DevOps integration: NOT AVAILABLE")
        print("  Install dependencies: pip install azure-devops")
    
    print("="*80)


def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs at the end of the test session
    Reports Azure DevOps integration summary
    """
    print("\n" + "="*80)
    print("PYTEST SESSION FINISH - Azure DevOps Integration Summary")
    print("="*80)
    
    if AZURE_INTEGRATION_AVAILABLE and os.getenv('AZURE_DEVOPS_PAT'):
        print("✓ Azure DevOps integration completed")
        print("  Check Azure DevOps for updated work items and any new bugs")
        print(f"  Organization: https://dev.azure.com/ttapani-solutions")
        print(f"  Project: test-automation-framework")
    else:
        print("○ Azure DevOps integration was not active this session")
    
    print("="*80)