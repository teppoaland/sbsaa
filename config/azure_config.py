"""
Secure Azure DevOps Configuration Manager
Handles authentication and configuration without exposing secrets in public repos

File location: sbsaa/config/azure_config.py
"""

import os
import json
from typing import Optional, Dict
from pathlib import Path


class AzureConfig:
    """
    Secure configuration manager for Azure DevOps integration
    Supports multiple authentication methods without exposing secrets
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        
    def get_configuration(self) -> Dict[str, str]:
        """
        Get Azure DevOps configuration from multiple sources in priority order:
        1. Environment variables (CI/CD, local development)
        2. Local config file (development only, not committed)
        3. Public defaults (non-sensitive values only)
        """
        config = {}
        
        # Start with public defaults (safe to commit)
        config.update(self._get_public_defaults())
        
        # Override with local config file (gitignored)
        config.update(self._get_local_config())
        
        # Override with environment variables (highest priority)
        config.update(self._get_env_config())
        
        # Validate required fields
        self._validate_config(config)
        
        return config
    
    def _get_public_defaults(self) -> Dict[str, str]:
        """
        Public configuration that's safe to commit to repo
        Contains non-sensitive default values
        """
        return {
            "organization_url": "https://dev.azure.com/ttapani-solutions",
            "project": "test-automation-framework",
            "default_work_item_type": "Test Case",
            "default_bug_priority": "2",
            "default_bug_severity": "3 - Medium"
        }
    
    def _get_local_config(self) -> Dict[str, str]:
        """
        Load from local config file (gitignored)
        For development convenience - not committed to repo
        """
        local_config_file = self.config_dir / "azure_local.json"
        
        if local_config_file.exists():
            try:
                with open(local_config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load local config: {e}")
        
        return {}
    
    def _get_env_config(self) -> Dict[str, str]:
        """
        Load configuration from environment variables
        Primary method for CI/CD and production
        """
        env_mapping = {
            "AZURE_DEVOPS_ORG_URL": "organization_url",
            "AZURE_DEVOPS_PROJECT": "project", 
            "AZURE_DEVOPS_PAT": "personal_access_token",
            "AZURE_DEVOPS_DEFAULT_ASSIGNEE": "default_assignee"
        }
        
        config = {}
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                config[config_key] = value
        
        return config
    
    def _validate_config(self, config: Dict[str, str]):
        """
        Validate that required configuration is present
        Provides helpful error messages for missing values
        """
        required_fields = ["organization_url", "project", "personal_access_token"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(f"""
            Missing required Azure DevOps configuration: {', '.join(missing_fields)}
            
            Setup options:
            
            1. ENVIRONMENT VARIABLES (Recommended for CI/CD):
               export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/ttapani-solutions"
               export AZURE_DEVOPS_PROJECT="test-automation-framework"
               export AZURE_DEVOPS_PAT="your_pat_token_here"
            
            2. LOCAL CONFIG FILE (Development only):
               Create: {self.config_dir}/azure_local.json
               {{
                   "personal_access_token": "your_pat_token_here"
               }}
               
            3. GITHUB SECRETS (For GitHub Actions):
               Add repository secrets:
               - AZURE_DEVOPS_PAT
               
            Note: Never commit PAT tokens to public repositories!
            """)
    
    def create_local_config_template(self):
        """
        Create a template for local development configuration
        This file should be gitignored and manually updated
        """
        template = {
            "personal_access_token": "your_pat_token_here",
            "default_assignee": "your_email@example.com",
            "organization_url": "https://dev.azure.com/ttapani-solutions",
            "project": "test-automation-framework"
        }
        
        template_file = self.config_dir / "azure_local.json.template"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"""
        Created config template: {template_file}
        
        For local development:
        1. Copy to: {self.config_dir}/azure_local.json
        2. Update with your actual PAT token
        3. Verify azure_local.json is in .gitignore
        
        The azure_local.json file will be gitignored and safe for local development.
        """)


class SecureAzureDevOpsClient:
    """
    Azure DevOps client that uses secure configuration
    Drop-in replacement for the basic client with security built-in
    """
    
    def __init__(self):
        self.config_manager = AzureConfig()
        self.config = self.config_manager.get_configuration()
        
        # Import Azure DevOps dependencies only when needed
        try:
            from azure.devops.connection import Connection
            from msrest.authentication import BasicAuthentication
            
            # Initialize connection with secure config
            credentials = BasicAuthentication('', self.config['personal_access_token'])
            self.connection = Connection(
                base_url=self.config['organization_url'], 
                creds=credentials
            )
            self.work_item_client = self.connection.clients.get_work_item_tracking_client()
            
        except ImportError as e:
            raise ImportError(f"Azure DevOps SDK not installed: {e}\nRun: pip install azure-devops")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Azure DevOps: {e}")
    
    def test_connection(self) -> bool:
        """
        Test the Azure DevOps connection without exposing credentials
        Returns True if connection works, False otherwise
        """
        try:
            # Try to get project info as a connection test
            project_client = self.connection.clients.get_core_client()
            project = project_client.get_project(self.config['project'])
            print(f"✓ Successfully connected to Azure DevOps project: {project.name}")
            return True
            
        except Exception as e:
            print(f"✗ Azure DevOps connection failed: {e}")
            print("\nTroubleshooting:")
            print("1. Verify PAT token has correct permissions")
            print("2. Check organization URL and project name")
            print("3. Ensure PAT token hasn't expired")
            return False


# Utility functions for setup
def setup_secure_config():
    """
    Setup secure configuration for development
    Run this once per development environment
    """
    config_manager = AzureConfig()
    
    # Create template
    config_manager.create_local_config_template()
    
    # Update .gitignore if needed
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    
    required_ignores = [
        "# Azure DevOps local configuration",
        ".env",
        ".env.local", 
        "config/azure_local.json",
        "*.pat"
    ]
    
    # Read existing gitignore
    existing_ignores = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_ignores = f.read().splitlines()
    
    # Add missing ignores
    new_ignores = [ignore for ignore in required_ignores 
                   if ignore not in existing_ignores]
    
    if new_ignores:
        with open(gitignore_path, 'a') as f:
            f.write("\n")
            f.write("\n".join(new_ignores))
            f.write("\n")
        
        print(f"Updated .gitignore with {len(new_ignores)} new entries")
    else:
        print("✓ .gitignore already contains required entries")


if __name__ == "__main__":
    # Run setup
    setup_secure_config()
    
    # Test configuration (without exposing secrets)
    try:
        client = SecureAzureDevOpsClient()
        client.test_connection()
    except Exception as e:
        print(f"Setup incomplete: {e}")