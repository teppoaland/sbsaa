"""
Setup Azure Integration - One-time Setup Script
File location: sbsaa/setup_azure_integration.py

Run this script once to create initial Azure DevOps work items for the Sää app
and establish the test case mappings.
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


def create_saa_app_work_items():
    """
    Create initial work items in Azure DevOps for the Sää app test automation
    This creates User Stories, Test Cases, and establishes mappings
    """
    if not AZURE_INTEGRATION_AVAILABLE:
        print("Azure integration not available. Please install dependencies:")
        print("pip install azure-devops python-dotenv")
        return None, None
    
    print("Creating Azure DevOps work items for Sää app...")
    
    try:
        # Initialize Azure DevOps client
        azure = AzureDevOpsClient()
        
        # Test connection first
        if not test_azure_connection():
            print("Cannot proceed without Azure DevOps connection")
            return None, None
        
        # Create Issue for Search Functionality (Basic process uses Issue instead of User Story)
        print("\n1. Creating Issue for Search Functionality...")
        story_id = azure.create_issue(
            title="Sää App - Weather Station Search Functionality",
            description="""
            <h3>User Story</h3>
            <p><strong>As a</strong> user of the Sää weather application</p>
            <p><strong>I want to</strong> search for weather stations by entering city names</p>
            <p><strong>So that</strong> I can quickly find weather information for my desired location</p>
            
            <h3>Background</h3>
            <p>The Sää app provides weather information from various weather stations across Finland. 
            Users should be able to easily find stations by searching with city names like "Oulu", 
            "Helsinki", "Tampere", etc.</p>
            
            <h3>Business Value</h3>
            <ul>
                <li>Improves user experience by enabling quick location discovery</li>
                <li>Reduces time needed to find specific weather stations</li>
                <li>Supports Finnish city name searches effectively</li>
                <li>Enhances app usability for location-based weather queries</li>
            </ul>
            
            <h3>Technical Context</h3>
            <p>This functionality is implemented in the main view of the mobile application, 
            accessible via a search field that accepts text input and displays matching weather stations.</p>
            """,
            acceptance_criteria="""
            <h4>Acceptance Criteria</h4>
            
            <h5>Scenario 1: Search Field Accessibility</h5>
            <ul>
                <li><strong>Given</strong> the user is on the main view of the Sää app</li>
                <li><strong>When</strong> they tap on the search field</li>
                <li><strong>Then</strong> the search field should become active and accept text input</li>
                <li><strong>And</strong> the device keyboard should appear</li>
            </ul>
            
            <h5>Scenario 2: City Name Search</h5>
            <ul>
                <li><strong>Given</strong> the user has tapped on the search field</li>
                <li><strong>When</strong> they enter a city name like "Oulu"</li>
                <li><strong>Then</strong> the text should appear in the search field</li>
                <li><strong>And</strong> the app should prepare to process the search query</li>
            </ul>
            
            <h5>Scenario 3: Search Results Display</h5>
            <ul>
                <li><strong>Given</strong> the user has entered a valid city name</li>
                <li><strong>When</strong> the search is executed</li>
                <li><strong>Then</strong> relevant weather stations for that city should be displayed</li>
                <li><strong>And</strong> each result should show weather station information</li>
            </ul>
            
            <h5>Definition of Done</h5>
            <ul>
                <li>Search field is accessible and functional on the main view</li>
                <li>Text input works correctly for Finnish city names</li>
                <li>Search results display relevant weather stations</li>
                <li>Automated tests verify the search functionality</li>
                <li>Manual testing confirms user experience is smooth</li>
            </ul>
            """
        )
        
        # Create Test Case for Oulu Search
        print("2. Creating Test Case for Oulu Search...")
        test_case_id = azure.create_test_case(
            title="Automated Test: Oulu Weather Station Search",
            test_steps="""
            <h3>Test Case: Oulu City Search Functionality</h3>
            
            <h4>Test Objective</h4>
            <p>Verify that the Sää app search functionality works correctly when searching for weather stations in Oulu.</p>
            
            <h4>Test Environment</h4>
            <ul>
                <li><strong>Platform:</strong> Android (real device)</li>
                <li><strong>App:</strong> Latest version of Sää weather application</li>
                <li><strong>Automation Tool:</strong> Appium with Python</li>
                <li><strong>Test Framework:</strong> pytest with Allure reporting</li>
            </ul>
            
            <h4>Test Prerequisites</h4>
            <ul>
                <li>Sää app is installed on the test device</li>
                <li>Device has internet connectivity</li>
                <li>App has necessary permissions</li>
                <li>Test device is connected and accessible via ADB</li>
            </ul>
            
            <h4>Detailed Test Steps</h4>
            <ol>
                <li>
                    <strong>Step 1 - App Launch and Verification</strong>
                    <ul>
                        <li>Launch the Sää application</li>
                        <li>Wait for main view to load completely</li>
                        <li>Verify that the main interface is displayed</li>
                    </ul>
                </li>
                <li>
                    <strong>Step 2 - Search Field Interaction</strong>
                    <ul>
                        <li>Locate the search field at coordinates (400, 780)</li>
                        <li>Tap on the search field</li>
                        <li>Wait 3 seconds for field activation and keyboard appearance</li>
                        <li>Verify search field is active and ready for input</li>
                    </ul>
                </li>
                <li>
                    <strong>Step 3 - Text Input Execution</strong>
                    <ul>
                        <li>Use mobile shell command to input text "Oulu"</li>
                        <li>Execute: mobile: shell with command 'input text Oulu'</li>
                        <li>Include error handling with 5-second timeout</li>
                        <li>Verify text appears correctly in the search field</li>
                    </ul>
                </li>
                <li>
                    <strong>Step 4 - Search Execution and Results</strong>
                    <ul>
                        <li>Execute the search (via enter key or search button)</li>
                        <li>Wait for search results to load</li>
                        <li>Verify that weather station results for Oulu are displayed</li>
                    </ul>
                </li>
                <li>
                    <strong>Step 5 - Results Verification and Documentation</strong>
                    <ul>
                        <li>Capture screenshot of the search results</li>
                        <li>Save screenshot as "Oulu_weather_stations_list"</li>
                        <li>Verify screenshot shows expected weather station list</li>
                    </ul>
                </li>
            </ol>
            
            <h4>Expected Results</h4>
            <ul>
                <li>Search field becomes active when tapped</li>
                <li>Text "Oulu" is successfully entered and visible</li>
                <li>Search executes without errors</li>
                <li>Weather stations relevant to Oulu are displayed</li>
                <li>Screenshot is captured showing the results</li>
                <li>No application crashes or freezes occur</li>
            </ul>
            
            <h4>Automation Implementation</h4>
            <p><strong>Test Function:</strong> test_oulu_search()</p>
            <p><strong>File Location:</strong> Test_features_automation_allure.py</p>
            <p><strong>Framework Integration:</strong> Uses Allure for reporting and screenshot capture</p>
            """,
            linked_story_id=story_id
        )
        
        # Create mapping for the test function
        print("3. Creating test function mapping...")
        mapper = TestCaseMapper()
        mapper.add_mapping("test_oulu_search", test_case_id, "Test Case")
        
        print(f"\n✓ Setup completed successfully!")
        print(f"  User Story ID: {story_id}")
        print(f"  Test Case ID: {test_case_id}")
        print(f"  Test mapping created for: test_oulu_search")
        
        return story_id, test_case_id
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your Azure DevOps PAT token is valid")
        print("2. Check that you have permission to create work items")
        print("3. Ensure the organization and project names are correct")
        print("4. Verify your network connection to Azure DevOps")
        return None, None


def create_additional_test_cases():
    """
    Create additional test cases for comprehensive coverage
    This can be expanded as more tests are added to the framework
    """
    print("\nCreating additional test cases...")
    
    try:
        azure = AzureDevOpsClient()
        mapper = TestCaseMapper()
        
        # Example: Create a test case for search error handling
        error_handling_id = azure.create_test_case(
            title="Test Case: Search Error Handling",
            test_steps="""
            <h3>Test Case: Search Error Handling and Edge Cases</h3>
            
            <h4>Test Objective</h4>
            <p>Verify that the search functionality handles invalid input and error conditions gracefully.</p>
            
            <h4>Test Scenarios</h4>
            <ol>
                <li>Search with empty string</li>
                <li>Search with special characters</li>
                <li>Search with very long city names</li>
                <li>Search with non-existent city names</li>
                <li>Network connectivity issues during search</li>
            </ol>
            
            <h4>Expected Behavior</h4>
            <ul>
                <li>App should handle invalid input without crashing</li>
                <li>Appropriate error messages should be displayed</li>
                <li>Search field should remain functional after errors</li>
            </ul>
            """
        )
        
        # Map to a hypothetical test function
        mapper.add_mapping("test_search_error_handling", error_handling_id, "Test Case")
        
        print(f"  Additional Test Case ID: {error_handling_id}")
        
        return [error_handling_id]
        
    except Exception as e:
        print(f"Could not create additional test cases: {e}")
        return []


def show_next_steps(story_id, test_case_id):
    """Display next steps for the user"""
    if story_id and test_case_id:
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                   SETUP COMPLETE!                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🎉 Azure DevOps Integration Successfully Configured

📋 Work Items Created:
   • User Story: {story_id} - "Sää App - Weather Station Search Functionality"
   • Test Case:  {test_case_id} - "Automated Test: Oulu Weather Station Search"

🔗 Azure DevOps Links:
   • User Story: https://dev.azure.com/ttapani-solutions/test-automation-framework/_workitems/edit/{story_id}
   • Test Case:  https://dev.azure.com/ttapani-solutions/test-automation-framework/_workitems/edit/{test_case_id}

📝 Next Steps:

1. UPDATE YOUR TEST FILE:
   Edit: Test_features_automation_allure.py
   Add this line above your test function:
   
   @azure_work_item({test_case_id})
   @allure.feature("Search Functionality")
   def test_oulu_search(driver, app_setup):
       # your existing test code

2. ADD THE IMPORT:
   Add this to the top of your test file:
   
   from azure_integration.azure_devops_client import azure_work_item

3. RUN YOUR TESTS:
   Your tests will now automatically:
   • Update Azure DevOps with test results
   • Create bugs when tests fail
   • Link test execution to work items

4. VIEW INTEGRATION:
   • Check Allure reports for Azure DevOps links
   • Monitor work item updates in Azure DevOps
   • Review automatically created bugs for failures

💡 Tips:
   • Test mappings are saved in: config/test_mapping.json
   • Run tests normally - Azure integration happens automatically
   • Check Azure DevOps work items to see test result updates

Happy testing! 🚀
        """)
    else:
        print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                 SETUP INCOMPLETE                                     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

❌ Setup encountered errors. Please check:

1. CONFIGURATION:
   • Verify .env file contains valid Azure DevOps PAT token
   • Check organization URL and project name
   • Ensure all required environment variables are set

2. PERMISSIONS:
   • Verify PAT token has "Work Items (Read & Write)" permissions
   • Check that you can access the Azure DevOps project
   • Ensure you have permission to create work items

3. DEPENDENCIES:
   Install required packages:
   pip install azure-devops python-dotenv

4. CONNECTION:
   • Test your network connection to Azure DevOps
   • Try accessing the web interface manually

Run the setup script again once issues are resolved.
        """)


def main():
    """Main setup function"""
    print("=== Sää App Azure DevOps Integration Setup ===\n")
    
    # Create work items
    story_id, test_case_id = create_saa_app_work_items()
    
    # Create additional test cases if main setup succeeded
    if story_id and test_case_id:
        additional_ids = create_additional_test_cases()
    
    # Show next steps
    show_next_steps(story_id, test_case_id)


if __name__ == "__main__":
    main()