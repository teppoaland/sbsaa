"""
Setup All Azure Test Cases - Complete Test Suite Creation
File location: sbsaa/setup_all_azure_test_cases.py

Creates all 10 Test Cases via API to match the test functions in Test_features_automation_allure.py
Uses proper "Test Case" work item type that supports automation status and correct state transitions
"""

import sys
from pathlib import Path

# Add azure_integration to path
sys.path.append(str(Path(__file__).parent / "azure_integration"))
sys.path.append(str(Path(__file__).parent / "config"))

try:
    from azure_integration.azure_devops_client import AzureDevOpsClient, TestCaseMapper, test_azure_connection
    AZURE_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Azure integration not available: {e}")
    AZURE_INTEGRATION_AVAILABLE = False


def create_all_saa_test_cases():
    """
    Create all 10 Test Cases for the Sää app test automation
    Maps each test function to a corresponding Azure DevOps Test Case
    """
    if not AZURE_INTEGRATION_AVAILABLE:
        print("Azure integration not available. Please install dependencies:")
        print("pip install azure-devops python-dotenv")
        return None
    
    print("Creating all Azure DevOps Test Cases for Sää app automation...")
    
    try:
        # Initialize Azure DevOps client
        azure = AzureDevOpsClient()
        
        # Test connection first
        if not test_azure_connection():
            print("Cannot proceed without Azure DevOps connection")
            return None
        
        # Define all test cases with their details (no ID field - Azure assigns work item IDs)
        test_cases = [
            {
                "function": "test_home_tab",
                "title": "TC-001: Sää App - Check Main View Visibility",
                "description": "Verify that the HOME tab button is visible and accessible on the main view after app launch.",
                "steps": "<h3>Test Steps:</h3><ol><li>Launch the Sää application</li><li>Wait for main view to load</li><li>Verify HOME tab button is visible</li><li>Capture screenshot for verification</li></ol>"
            },
            {
                "function": "test_oulu_search", 
                "title": "TC-002: Sää App - Oulu Weather Station Search",
                "description": "Verify that the search functionality works correctly for finding Oulu weather stations.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to search field on main view</li><li>Enter 'Oulu' as search term</li><li>Verify search results display Oulu weather stations</li><li>Capture screenshot of results</li></ol>"
            },
            {
                "function": "test_oulu_vihreasaari",
                "title": "TC-003: Sää App - Oulu Vihreasaari Weather Station", 
                "description": "Verify that Oulu Vihreasaari weather station data can be accessed and displayed correctly.",
                "steps": "<h3>Test Steps:</h3><ol><li>Search for Oulu weather stations</li><li>Select Vihreasaari station from results</li><li>Verify station-specific weather data is displayed</li><li>Validate data format and completeness</li></ol>"
            },
            {
                "function": "test_oulu_airport",
                "title": "TC-004: Sää App - Oulu Airport Weather Station",
                "description": "Verify that Oulu Airport weather station provides accurate and accessible weather data.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to Oulu Airport weather station</li><li>Verify airport weather data is displayed</li><li>Validate temperature, wind, and visibility data</li><li>Confirm data freshness and accuracy</li></ol>"
            },
            {
                "function": "test_warmest_view",
                "title": "TC-005: Sää App - Warmest Temperature View",
                "description": "Verify that the warmest temperature view displays correctly and shows accurate temperature rankings.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to warmest temperature view</li><li>Verify temperature data is displayed</li><li>Validate sorting by highest temperature</li><li>Confirm location names and temperature values</li></ol>"
            },
            {
                "function": "test_coldest_view",
                "title": "TC-006: Sää App - Coldest Temperature View",
                "description": "Verify that the coldest temperature view displays correctly and shows accurate temperature rankings.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to coldest temperature view</li><li>Verify temperature data is displayed</li><li>Validate sorting by lowest temperature</li><li>Confirm location names and temperature values</li></ol>"
            },
            {
                "function": "test_rainiest_view",
                "title": "TC-007: Sää App - Rainiest Location View",
                "description": "Verify that the rainiest location view displays precipitation data correctly.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to rainiest location view</li><li>Verify precipitation data is displayed</li><li>Validate sorting by rainfall amount</li><li>Confirm location names and precipitation values</li></ol>"
            },
            {
                "function": "test_windiest_view", 
                "title": "TC-008: Sää App - Windiest Location View",
                "description": "Verify that the windiest location view displays wind data correctly.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to windiest location view</li><li>Verify wind speed data is displayed</li><li>Validate sorting by wind speed</li><li>Confirm location names and wind speed values</li></ol>"
            },
            {
                "function": "test_records_tab",
                "title": "TC-009: Sää App - Weather Records Tab Access", 
                "description": "Verify that the records tab is accessible and displays historical weather data.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate to records tab</li><li>Verify tab is accessible and loads correctly</li><li>Validate historical data is displayed</li><li>Confirm data organization and format</li></ol>"
            },
            {
                "function": "test_final_home_check",
                "title": "TC-010: Sää App - Final Home Navigation Check",
                "description": "Verify that navigation back to home view works correctly after using other app features.",
                "steps": "<h3>Test Steps:</h3><ol><li>Navigate through various app sections</li><li>Return to home tab</li><li>Verify home view loads correctly</li><li>Confirm all home view elements are accessible</li></ol>"
            }
        ]
        
        created_test_cases = []
        mapper = TestCaseMapper()
        
        print(f"\nCreating {len(test_cases)} Test Cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i:2d}. Creating: {test_case['title']}")
            
            # Create the Test Case work item
            work_item_id = azure.create_test_case(
                title=test_case['title'],
                test_steps=test_case['steps'] + f"\n\n<p>{test_case['description']}</p>",
                linked_story_id=None  # No parent story needed
            )
            
            # Add mapping for the test function
            mapper.add_mapping(test_case['function'], work_item_id, "Test Case")
            
            created_test_cases.append({
                'sequence': i,
                'work_item_id': work_item_id,
                'function': test_case['function'],
                'title': test_case['title']
            })
            
            print(f"   ✓ Created Test Case {work_item_id} for {test_case['function']}")
        
        print(f"\n✓ Successfully created all {len(created_test_cases)} Test Cases!")
        
        # Display summary with actual Azure work item IDs
        print("\n" + "="*80)
        print("AZURE DEVOPS TEST CASE CREATION SUMMARY")
        print("="*80)
        
        for tc in created_test_cases:
            print(f"TC-{tc['sequence']:03d}: {tc['function']:25s} → Azure Work Item {tc['work_item_id']}")
        
        print("\n✓ All test function mappings saved to test_mapping.json")
        print("✓ Ready for automated test execution with Azure DevOps integration")
        print("\n" + "="*80)
        print("COPY THESE WORK ITEM IDs FOR MAPPING:")
        print("="*80)
        
        for tc in created_test_cases:
            print(f"{tc['function']}: {tc['work_item_id']}")
        
        return created_test_cases
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your Azure DevOps PAT token is valid and has Test Case creation permissions")
        print("2. Ensure you're using the correct organization and project names")
        print("3. Check network connectivity to Azure DevOps")
        return None


def show_next_steps(created_test_cases):
    """Display next steps after Test Case creation"""
    if created_test_cases:
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           ALL TEST CASES CREATED SUCCESSFULLY!                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🎉 Azure DevOps Integration Fully Configured

📋 Created Test Cases: {len(created_test_cases)}

🔗 Azure DevOps Project: https://dev.azure.com/ttapani-solutions/test-automation-framework

📝 Next Steps:

1. UPDATE TEST FILE DECORATORS:
   Edit: Test_features_automation_allure.py
   Update each test function with the correct work item ID from the mapping above

2. VERIFY MAPPINGS:
   Check: config/test_mapping.json
   Ensure all test functions are mapped to correct work item IDs

3. RUN AUTOMATED TESTS:
   All tests will now automatically update Azure DevOps Test Cases with execution results

Happy testing with full Azure DevOps traceability! 🚀
        """)
    else:
        print("Setup incomplete - check errors above")


def main():
    """Main setup function"""
    print("=== Sää App Complete Azure DevOps Test Case Setup ===\n")
    
    # Create all test cases
    created_test_cases = create_all_saa_test_cases()
    
    # Show next steps
    show_next_steps(created_test_cases)


if __name__ == "__main__":
    main()