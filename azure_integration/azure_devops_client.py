"""
Azure DevOps Client - Core Integration Module
File location: sbsaa/azure_integration/azure_devops_client.py

Handles work item creation, updates, and test result linking for the Sää app test automation
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import allure

# Add the config directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "config"))

try:
    from azure.devops.connection import Connection
    from azure.devops.v7_1.work_item_tracking.models import Wiql, WorkItem
    from msrest.authentication import BasicAuthentication
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Azure DevOps SDK not installed. Run: pip install azure-devops")


class AzureDevOpsClient:
    """Main client for Azure DevOps integration with Sää app tests"""
    
    def __init__(self):
        if not AZURE_AVAILABLE:
            raise ImportError("Azure DevOps SDK not available. Install with: pip install azure-devops")
        
        # Import secure config
        try:
            from azure_config import AzureConfig
            config_manager = AzureConfig()
            self.config = config_manager.get_configuration()
        except ImportError:
            # Fallback to environment variables
            self.config = {
                'organization_url': os.getenv('AZURE_DEVOPS_ORG_URL'),
                'project': os.getenv('AZURE_DEVOPS_PROJECT'),
                'personal_access_token': os.getenv('AZURE_DEVOPS_PAT')
            }
            
        # Validate configuration
        if not all([self.config.get('organization_url'), 
                   self.config.get('project'), 
                   self.config.get('personal_access_token')]):
            raise ValueError("Azure DevOps configuration incomplete. Check environment variables or config files.")
        
        # Initialize Azure DevOps connection
        credentials = BasicAuthentication('', self.config['personal_access_token'])
        self.connection = Connection(base_url=self.config['organization_url'], creds=credentials)
        self.work_item_client = self.connection.clients.get_work_item_tracking_client()
        
        # Initialize test case mapper
        self.mapper = TestCaseMapper()
    
    def create_issue(self, title: str, description: str, acceptance_criteria: str = None) -> int:
        """Create an Issue work item (Basic process template)"""
        fields = {
            'System.Title': title,
            'System.Description': description,
            'System.WorkItemType': 'Issue',
            'System.State': 'To Do'
        }
        
        # For Basic template, acceptance criteria goes in description
        if acceptance_criteria:
            fields['System.Description'] = f"{description}<br/><br/><h3>Acceptance Criteria</h3>{acceptance_criteria}"
        
        work_item = self.work_item_client.create_work_item(
            document=[{"op": "add", "path": f"/fields/{field}", "value": value} 
                     for field, value in fields.items()],
            project=self.config['project'],
            type='Issue'
        )
        
        print(f"Created Issue: {work_item.id} - {title}")
        return work_item.id
    
    def create_user_story(self, title: str, description: str, acceptance_criteria: str = None) -> int:
        """Create a User Story work item"""
        fields = {
            'System.Title': title,
            'System.Description': description,
            'System.WorkItemType': 'User Story',
            'System.State': 'New'
        }
        
        if acceptance_criteria:
            fields['Microsoft.VSTS.Common.AcceptanceCriteria'] = acceptance_criteria
        
        work_item = self.work_item_client.create_work_item(
            document=[{"op": "add", "path": f"/fields/{field}", "value": value} 
                     for field, value in fields.items()],
            project=self.config['project'],
            type='User Story'
        )
        
        print(f"Created User Story: {work_item.id} - {title}")
        return work_item.id
    
    def create_test_case(self, title: str, description: str = "", test_steps_xml: str = "", linked_story_id: int = None) -> int:
        """Create a Test Case work item with proper XML steps"""
        fields = {
            'System.Title': title,
            'System.WorkItemType': 'Test Case',
            'System.State': 'Design',
            'System.Description': description,
            'Microsoft.VSTS.TCM.Steps': test_steps_xml  # Proper XML format
        }
        
        if linked_story_id:
            fields['System.Parent'] = linked_story_id
        
        # Create work item
        work_item = self.work_item_client.create_work_item(
            document=[{"op": "add", "path": f"/fields/{field}", "value": value} 
                    for field, value in fields.items() if value],
            project=self.config['project'],
            type='Test Case'
        )
    
        return work_item.id
    
    def create_bug_from_test_failure(self, test_name: str, error_details: str, 
                                   test_file: str, linked_test_case_id: int = None) -> int:
        """Create a Bug work item from test failure"""
        title = f"Test Failure: {test_name}"
        
        description = f"""
        <h3>Automated Test Failure</h3>
        <p><strong>Test Function:</strong> {test_name}</p>
        <p><strong>Test File:</strong> {test_file}</p>
        
        <h4>Error Details:</h4>
        <pre>{error_details}</pre>
        
        <h4>Investigation Steps:</h4>
        <ul>
            <li>Verify if this is a test issue or application bug</li>
            <li>Check recent code changes that might affect this functionality</li>
            <li>Review test environment and device configuration</li>
            <li>Validate test data and assumptions</li>
        </ul>
        """
        
        fields = {
            'System.Title': title,
            'System.Description': description,
            'System.WorkItemType': 'Bug',
            'System.State': 'New',
            'Microsoft.VSTS.Common.Priority': 2,
            'Microsoft.VSTS.Common.Severity': '3 - Medium'
        }
        
        work_item = self.work_item_client.create_work_item(
            document=[{"op": "add", "path": f"/fields/{field}", "value": value} 
                     for field, value in fields.items()],
            project=self.config['project'],
            type='Bug'
        )
        
        if linked_test_case_id:
            self.link_work_items(work_item.id, linked_test_case_id, 'Tested By')
        
        print(f"Created Bug: {work_item.id} - {title}")
        return work_item.id
    
    def link_work_items(self, source_id: int, target_id: int, link_type: str = 'Related'):
        """Create a link between two work items"""
        # Basic process template uses simpler link types
        if link_type == 'Tests':
            rel_type = "System.LinkTypes.Related"
        else:
            rel_type = "System.LinkTypes.Related"
            
        link_data = [{
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": rel_type,
                "url": f"{self.config['organization_url']}/{self.config['project']}/_workitems/edit/{target_id}",
                "attributes": {
                    "comment": f"Linked by Sää app test automation ({link_type})"
                }
            }
        }]
        
        self.work_item_client.update_work_item(
            document=link_data,
            id=source_id,
            project=self.config['project']
        )
    
    def update_test_result(self, work_item_id: int, test_status: str, execution_details: str = None):
        """Update work item with test execution results"""
        updates = []
        
        if test_status == "PASSED":
            updates.append({"op": "add", "path": "/fields/System.State", "value": "Closed"})
        elif test_status == "FAILED":
            updates.append({"op": "add", "path": "/fields/System.State", "value": "Ready"})
        
        if execution_details:
            updates.append({
                "op": "add", 
                "path": "/fields/System.History", 
                "value": f"<strong>Automated Test Result:</strong><br/>{execution_details}"
            })
        
        if updates:
            self.work_item_client.update_work_item(
                document=updates,
                id=work_item_id,
                project=self.config['project']
            )
            print(f"Updated work item {work_item_id} with test result: {test_status}")


class TestCaseMapper:
    """Maps test functions to Azure DevOps work items"""
    
    def __init__(self, mapping_file: str = None):
        if mapping_file is None:
            # Default to config directory
            config_dir = Path(__file__).parent.parent / "config"
            mapping_file = config_dir / "test_mapping.json"
        
        self.mapping_file = Path(mapping_file)
        self.mappings = self._load_mappings()
    
    def _load_mappings(self) -> Dict:
        """Load test mappings from JSON file"""
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load test mappings: {e}")
        return {}
    
    def _save_mappings(self):
        """Save mappings to JSON file"""
        # Ensure directory exists
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mappings, f, indent=2)
    
    def add_mapping(self, test_function: str, work_item_id: int, work_item_type: str = "Test Case"):
        """Add mapping between test function and work item"""
        self.mappings[test_function] = {
            "work_item_id": work_item_id,
            "work_item_type": work_item_type,
            "azure_url": f"https://dev.azure.com/ttapani-solutions/test-automation-framework/_workitems/edit/{work_item_id}"
        }
        self._save_mappings()
        print(f"Mapped {test_function} -> Work Item {work_item_id}")
    
    def get_work_item_id(self, test_function: str) -> Optional[int]:
        """Get work item ID for test function"""
        mapping = self.mappings.get(test_function)
        return mapping["work_item_id"] if mapping else None
    
    def get_all_mappings(self) -> Dict:
        """Get all current mappings"""
        return self.mappings


def azure_work_item(work_item_id: int):
    """
    Decorator to link test function with Azure DevOps work item
    
    Usage:
        @azure_work_item(12345)
        @allure.feature("Search Functionality")
        def test_oulu_search(driver, app_setup):
            # test implementation
    """
    def decorator(func):
        # Store work item ID as function attribute
        func.azure_work_item_id = work_item_id
        
        # Add to Allure report
        azure_url = f"https://dev.azure.com/ttapani-solutions/test-automation-framework/_workitems/edit/{work_item_id}"
        allure.dynamic.link(azure_url, name=f"Azure Work Item {work_item_id}")
        
        return func
    return decorator


# Test connection utility
def test_azure_connection():
    """Test Azure DevOps connection"""
    try:
        client = AzureDevOpsClient()
        
        # Try to get project info
        core_client = client.connection.clients.get_core_client()
        project = core_client.get_project(client.config['project'])
        
        print(f"✓ Successfully connected to Azure DevOps")
        print(f"  Organization: {client.config['organization_url']}")
        print(f"  Project: {project.name}")
        return True
        
    except Exception as e:
        print(f"✗ Azure DevOps connection failed: {e}")
        return False