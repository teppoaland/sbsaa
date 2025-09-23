"""
Add Azure Test Cases Interactively - Fixed Version
File location: sbsaa/add_azure_test_cases.py

Allows user to add new Test Cases one by one via prompts.
Each test case is created in Azure DevOps with proper XML formatting for Test Case steps.
"""

import sys
from pathlib import Path
import re

# Add azure_integration and config to path
sys.path.append(str(Path(__file__).parent / "azure_integration"))
sys.path.append(str(Path(__file__).parent / "config"))

try:
    from azure_integration.azure_devops_client import AzureDevOpsClient, TestCaseMapper, test_azure_connection
    AZURE_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Azure integration not available: {e}")
    AZURE_INTEGRATION_AVAILABLE = False


def clean_input(text):
    """Clean user input to avoid formatting issues"""
    if not text:
        return ""
    # Stripping disabled - return input as-is
    return text.strip()


def format_test_steps_as_xml(steps_list):
    """Format test steps as proper XML for Azure DevOps Test Cases"""
    if not steps_list:
        return ""
    
    xml_steps = ""
    for i, step in enumerate(steps_list):
        xml_steps += f'''<steps id="{i}" type="ActionStep">
  <parameterizedString isformatted="true">
    <DIV><P>{step}</P></DIV>
  </parameterizedString>
  <parameterizedString isformatted="true">
    <DIV><P>Verify step completed successfully</P></DIV>
  </parameterizedString>
  <description/>
</steps>'''
    
    return f"<steps>{xml_steps}</steps>"


def prompt_for_test_case():
    """Prompt user for test case details with improved validation"""
    print("\n" + "="*60)
    print("ENTER NEW TEST CASE DETAILS")
    print("="*60)
    
    # Get function name
    while True:
        function = input("\nFunction name (e.g. test_login_validation): ").strip()
        function = clean_input(function)
        if function and function.startswith('test_'):
            break
        elif function:
            function = f"test_{function}"
            break
        else:
            print("ERROR: Function name is required and should start with 'test_'")
    
    # Get TC number - MANUAL INPUT REQUIRED
    while True:
        tc_number = input("Test Case number (e.g. 001, 042): ").strip()
        tc_number = clean_input(tc_number)
        if tc_number:
            break
        else:
            print("ERROR: Test Case number is required")
    
    # Get clean title
    while True:
        title_base = input("Test Case title (e.g. 'Verify Login Validation'): ").strip()
        title_base = clean_input(title_base)
        if title_base:
            break
        else:
            print("ERROR: Title is required")
    
    # Construct full title
    full_title = f"{tc_number}: {title_base}"
    
    print(f"\nGenerated title: {full_title}")
    
    # Get description
    description = input("Description (optional): ").strip()
    description = clean_input(description)
    if not description:
        description = f"Verify that {title_base.lower()} functions correctly"
    
    # Get test steps
    print(f"\nEnter test steps (one per line, press Enter on empty line to finish):")
    steps_list = []
    step_num = 1
    
    while True:
        step = input(f"Step {step_num}: ").strip()
        step = clean_input(step)
        if not step:
            break
        steps_list.append(step)
        step_num += 1
    
    # Default steps if none provided
    if not steps_list:
        print("No steps provided, using defaults...")
        steps_list = [
            "Launch the application",
            "Navigate to the relevant feature",
            "Perform the test action",
            "Verify expected behavior",
            "Take screenshot if test fails"
        ]
    
    return {
        "function": function,
        "title": full_title,
        "description": description,
        "steps_list": steps_list,
        "tc_number": tc_number
    }


def preview_test_case(test_case):
    """Show a preview of the test case before creation"""
    print("\n" + "="*60)
    print("TEST CASE PREVIEW")
    print("="*60)
    print(f"Function:     {test_case['function']}")
    print(f"Title:        {test_case['title']}")
    print(f"Description:  {test_case['description']}")
    print(f"\nTest Steps:")
    for i, step in enumerate(test_case['steps_list'], 1):
        print(f"  {i}. {step}")
    print("="*60)


def add_test_cases_interactively():
    """Add new test cases one by one with proper Azure DevOps formatting"""
    if not AZURE_INTEGRATION_AVAILABLE:
        print("ERROR: Azure integration not available. Please install dependencies:")
        print("   pip install azure-devops python-dotenv")
        return None

    print("=" * 80)
    print("INTERACTIVE AZURE DEVOPS TEST CASE CREATOR")
    print("=" * 80)
    print("This tool creates Test Cases in Azure DevOps with proper XML formatting.")
    
    # Initialize Azure DevOps client
    try:
        azure = AzureDevOpsClient()
        print("SUCCESS: Azure DevOps client initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize Azure client: {e}")
        return None

    # Test connection
    print("INFO: Testing Azure DevOps connection...")
    if not test_azure_connection():
        print("ERROR: Cannot proceed without Azure DevOps connection")
        return None
    print("SUCCESS: Azure DevOps connection successful")

    mapper = TestCaseMapper()
    created_test_cases = []
    case_number = 1

    while True:
        print(f"\n{'-' * 20} TEST CASE #{case_number} {'-' * 20}")
        
        # Get test case details
        try:
            test_case = prompt_for_test_case()
            if not test_case:
                print("ERROR: Invalid input, try again...")
                continue
        except KeyboardInterrupt:
            print("\n\nSession cancelled by user")
            break

        # Show preview
        preview_test_case(test_case)
        
        # Confirm creation
        while True:
            confirm = input("\nCreate this test case? [Y/N/E(dit)]: ").strip().lower()
            if confirm in ['y', 'n', 'e']:
                break
            print("Please enter Y (yes), N (no), or E (edit)")
        
        if confirm == 'n':
            print("SKIPPED: Test case not created")
            continue
        elif confirm == 'e':
            print("INFO: Edit functionality not implemented yet. Skipping...")
            continue

        # Create in Azure DevOps
        try:
            print(f"\nINFO: Creating Azure Test Case: {test_case['title']}")
            
            # Format steps as proper XML
            steps_xml = format_test_steps_as_xml(test_case['steps_list'])
            
            # Create the test case (you'll need to update your azure_devops_client to handle XML steps)
            work_item_id = azure.create_test_case(
                title=test_case['title'],
                test_steps_xml=steps_xml,
                linked_story_id=None
            )

            print(f"   SUCCESS: Created Test Case {work_item_id}")

            # Optional mapping
            add_mapping = input(f"Add mapping '{test_case['function']}' -> {work_item_id} to test_mapping.json? [Y/N]: ").strip().lower()
            if add_mapping == "y":
                mapper.add_mapping(test_case['function'], work_item_id, "Test Case")
                print("   SUCCESS: Mapping saved to test_mapping.json")
            else:
                print("   SKIPPED: Mapping not added")

            created_test_cases.append({
                "sequence": case_number,
                "work_item_id": work_item_id,
                "function": test_case["function"],
                "title": test_case["title"],
                "tc_number": test_case["tc_number"]
            })

            case_number += 1
            
        except Exception as e:
            print(f"   ERROR: Failed to create test case: {e}")
            print(f"   Error details: {str(e)}")
            continue

        # Continue or exit
        print("\n" + "-" * 60)
        cont = input("Add another test case? [Y/N]: ").strip().lower()
        if cont != "y":
            break

    # Final summary
    print_summary(created_test_cases)
    return created_test_cases


def print_summary(created_test_cases):
    """Print a nice summary of created test cases"""
    if not created_test_cases:
        print(f"\n{'='*60}")
        print("SESSION COMPLETE - No test cases were created")
        print(f"{'='*60}")
        return

    print(f"\n{'='*80}")
    print("AZURE DEVOPS TEST CASE CREATION SUMMARY")
    print(f"{'='*80}")

    for tc in created_test_cases:
        azure_url = f"https://dev.azure.com/ttapani-solutions/test-automation-framework/_workitems/edit/{tc['work_item_id']}"
        print(f"#{tc['sequence']:2d}: {tc['tc_number']} | {tc['function']}")
        print(f"     Title: {tc['title']}")
        print(f"     Azure: {azure_url}")
        print()

    print(f"SUCCESS: Created {len(created_test_cases)} test cases")
    
    # Show decorator usage
    print(f"\n{'='*60}")
    print("DECORATOR USAGE FOR TEST FILES")
    print(f"{'='*60}")
    print("Add these decorators to your test functions:")
    print("-" * 40)
    for tc in created_test_cases:
        print(f"@azure_work_item({tc['work_item_id']})  # {tc['tc_number']}")
        print(f"def {tc['function']}(self):")
        print(f"    pass  # Your test implementation")
        print()


def main():
    """Main entry point"""
    try:
        print("Starting Interactive Azure Test Case Creator...")
        created_test_cases = add_test_cases_interactively()
        
        if created_test_cases:
            print(f"\nSession completed - {len(created_test_cases)} test cases added!")
        else:
            print(f"\nSession completed - no changes made.")
            
    except KeyboardInterrupt:
        print(f"\n\nSession interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()