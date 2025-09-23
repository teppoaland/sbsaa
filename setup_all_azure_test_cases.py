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
        
        # Define all test cases with their details
        test_cases = [
            {
                "id": 1,
                "function": "test_home_tab",
                "title": "Sää App - Check Main View Visibility",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> the main view to be visible when the app is opened</p>
                <p><strong>So that</strong> I can navigate to the home tab and access the app's features</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the HOME tab button is visible and accessible on the main view after app launch.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Launch the Sää application</li>
                    <li>Wait for main view to load</li>
                    <li>Verify HOME tab button is visible with accessibility ID "KOTI\\nTab 1 of 3"</li>
                    <li>Capture screenshot for verification</li>
                </ol>
                """
            },
            {
                "id": 2,
                "function": "test_oulu_search",
                "title": "Sää App - Oulu Weather Station Search",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to search for weather stations by city name</p>
                <p><strong>So that</strong> I can find weather information for Oulu specifically</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the search functionality works correctly for finding Oulu weather stations.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to search field on main view</li>
                    <li>Tap search field to activate input</li>
                    <li>Enter "Oulu" as search term</li>
                    <li>Verify search results display Oulu weather stations</li>
                    <li>Capture screenshot of results</li>
                </ol>
                """
            },
            {
                "id": 3,
                "function": "test_oulu_vihreasaari",
                "title": "Sää App - Oulu Vihreasaari Weather Station",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to access specific weather station data</p>
                <p><strong>So that</strong> I can view detailed weather information for Oulu Vihreasaari station</p>
                
                <h3>Test Objective</h3>
                <p>Verify that Oulu Vihreasaari weather station data can be accessed and displayed correctly.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Search for Oulu weather stations</li>
                    <li>Select Vihreasaari station from results</li>
                    <li>Verify station-specific weather data is displayed</li>
                    <li>Validate data format and completeness</li>
                </ol>
                """
            },
            {
                "id": 4,
                "function": "test_oulu_airport",
                "title": "Sää App - Oulu Airport Weather Station",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to access airport weather data</p>
                <p><strong>So that</strong> I can view current weather conditions at Oulu Airport</p>
                
                <h3>Test Objective</h3>
                <p>Verify that Oulu Airport weather station provides accurate and accessible weather data.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to Oulu Airport weather station</li>
                    <li>Verify airport weather data is displayed</li>
                    <li>Validate temperature, wind, and visibility data</li>
                    <li>Confirm data freshness and accuracy</li>
                </ol>
                """
            },
            {
                "id": 5,
                "function": "test_warmest_view",
                "title": "Sää App - Warmest Temperature View",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to view the warmest temperatures</p>
                <p><strong>So that</strong> I can see which locations have the highest temperatures</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the warmest temperature view displays correctly and shows accurate temperature rankings.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to warmest temperature view</li>
                    <li>Verify temperature data is displayed</li>
                    <li>Validate sorting by highest temperature</li>
                    <li>Confirm location names and temperature values</li>
                </ol>
                """
            },
            {
                "id": 6,
                "function": "test_coldest_view",
                "title": "Sää App - Coldest Temperature View",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to view the coldest temperatures</p>
                <p><strong>So that</strong> I can see which locations have the lowest temperatures</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the coldest temperature view displays correctly and shows accurate temperature rankings.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to coldest temperature view</li>
                    <li>Verify temperature data is displayed</li>
                    <li>Validate sorting by lowest temperature</li>
                    <li>Confirm location names and temperature values</li>
                </ol>
                """
            },
            {
                "id": 7,
                "function": "test_rainiest_view",
                "title": "Sää App - Rainiest Location View",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to view locations with highest rainfall</p>
                <p><strong>So that</strong> I can see which areas are experiencing the most precipitation</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the rainiest location view displays precipitation data correctly.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to rainiest location view</li>
                    <li>Verify precipitation data is displayed</li>
                    <li>Validate sorting by rainfall amount</li>
                    <li>Confirm location names and precipitation values</li>
                </ol>
                """
            },
            {
                "id": 8,
                "function": "test_windiest_view",
                "title": "Sää App - Windiest Location View",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to view locations with strongest winds</p>
                <p><strong>So that</strong> I can see which areas have the highest wind speeds</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the windiest location view displays wind data correctly.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to windiest location view</li>
                    <li>Verify wind speed data is displayed</li>
                    <li>Validate sorting by wind speed</li>
                    <li>Confirm location names and wind speed values</li>
                </ol>
                """
            },
            {
                "id": 9,
                "function": "test_records_tab",
                "title": "Sää App - Weather Records Tab Access",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to access historical weather records</p>
                <p><strong>So that</strong> I can view past weather data and trends</p>
                
                <h3>Test Objective</h3>
                <p>Verify that the records tab is accessible and displays historical weather data.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate to records tab</li>
                    <li>Verify tab is accessible and loads correctly</li>
                    <li>Validate historical data is displayed</li>
                    <li>Confirm data organization and format</li>
                </ol>
                """
            },
            {
                "id": 10,
                "function": "test_final_home_check",
                "title": "Sää App - Final Home Navigation Check",
                "description": """
                <h3>User Story</h3>
                <p><strong>As a</strong> user of the Sää weather application</p>
                <p><strong>I want</strong> to return to the home view after navigation</p>
                <p><strong>So that</strong> I can ensure consistent navigation behavior throughout the app</p>
                
                <h3>Test Objective</h3>
                <p>Verify that navigation back to home view works correctly after using other app features.</p>
                """,
                "steps": """
                <h3>Test Steps:</h3>
                <ol>
                    <li>Navigate through various app sections</li>
                    <li>Return to home tab</li>
                    <li>Verify home view loads correctly</li>
                    <li>Confirm all home view elements are accessible</li>
                </ol>
                """
            }
        ]
        
        created_test_cases = []
        mapper = TestCaseMapper()
        
        print(f"\nCreating {len(test_cases)} Test Cases...")
        
        for test_case in test_cases:
            print(f"\n{test_case['id']}. Creating: {test_case['title']}")
            
            # Create the Test Case work item
            work_item_id = azure.create_test_case(
                title=test_case['title'],
                test_steps=test_case['steps'] + f"\n\n{test_case['description']}",
                linked_story_id=None  # No parent story needed
            )
            
            # Add mapping for the test function
            mapper.add_mapping(test_case['function'], work_item_id, "Test Case")
            
            created_test_cases.append({
                'id': test_case['id'],
                'work_item_id': work_item_id,
                'function': test_case['function'],
                'title': test_case['title']
            })
            
            print(f"   ✓ Created Test Case {work_item_id} for {test_case['function']}")
        
        print(f"\n✓ Successfully created all {len(created_test_cases)} Test Cases!")
        
        # Display summary
        print("\n" + "="*80)
        print("AZURE DEVOPS TEST CASE CREATION SUMMARY")
        print("="*80)
        
        for tc in created_test_cases:
            print(f"Test {tc['id']:2d}: {tc['function']:25s} → Work Item {tc['work_item_id']}")
        
        print("\n✓ All test function mappings saved to test_mapping.json")
        print("✓ Ready for automated test execution with Azure DevOps integration")
        
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
   Update each test function with the correct work item ID:
   
   @azure_work_item(1)
   def test_home_tab(driver, app_setup):
   
   @azure_work_item(2) 
   def test_oulu_search(driver, app_setup):
   
   ... and so on for all 10 tests

2. VERIFY MAPPINGS:
   Check: config/test_mapping.json
   Ensure all test functions are mapped to correct work item IDs

3. RUN AUTOMATED TESTS:
   All tests will now automatically:
   • Update Azure DevOps Test Cases with execution results
   • Transition work item states (Design → Closed for passing tests)
   • Create detailed execution logs in Azure DevOps history

4. MONITOR RESULTS:
   • Check Azure DevOps for real-time test result updates
   • Review work item history for execution details
   • Monitor automation status changes

💡 Pro Tips:
   • Test Cases are now properly configured for automation status tracking
   • Work items will show "Automated" status after first test execution
   • Failed tests will provide detailed error information in work item history

Happy testing with full Azure DevOps traceability! 🚀
        """)
    else:
        print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                 SETUP INCOMPLETE                                     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

❌ Test Case creation encountered errors. Please check:

1. Azure DevOps PAT token permissions for Test Case creation
2. Network connectivity and organization/project access
3. API rate limits or temporary service issues

Retry the setup after resolving configuration issues.
        """)


def main():
    """Main setup function"""
    print("=== Sää App Complete Azure DevOps Test Case Setup ===\n")
    
    # Create all test cases
    created_test_cases = create_all_saa_test_cases()
    
    # Show next steps
    show_next_steps(created_test_cases)


if __name__ == "__main__":
    main()