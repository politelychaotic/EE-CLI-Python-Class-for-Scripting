import json
from typing import Dict, List, Any, Optional


class JSONAccountParser:
    """
    Parser for JSON files containing account data with sections and sublists.
    
    Expected structure:
    {
        "parent": "account_id",
        "sub_accounts": [...],
        "account_id": [
            {
                "section_name": [items...],
                "another_section": [items...]
            }
        ]
    }

    Methods:
    {
    get_parent_account() - Returns the parent account ID\n
    get_sub_accounts() - Returns list of sub-account IDs\n
    get_all_accounts() - Returns all account IDs in the file\n
    get_sections_for_account(account_id) - Lists all sections within an account\n
    get_items_by_section(account_id, section) - Gets all items in a specific section\n
    get_all_sections_by_account() - Returns a complete nested dictionary organized by account and section\n
    count_items_by_account() - Gets total item counts per account\n
    }
    """

    def __init__(self, file_path: str):
        """
        Initialize the parser with a JSON file.
        
        Args:
            file_path: Path to the JSON file to parse
        """
        self.file_path = file_path
        self.data = self._load_json()

    def _load_json(self) -> Dict[str, Any]:
        """Load and parse the JSON file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def get_parent_account(self) -> str:
        """Get the parent account ID."""
        return self.data.get('parent', '')

    def get_sub_accounts(self) -> List[str]:
        """Get list of sub-account IDs."""
        return self.data.get('sub_accounts', [])

    def get_all_accounts(self) -> List[str]:
        """Get all account IDs (excluding parent and sub_accounts keys)."""
        excluded_keys = {'parent', 'sub_accounts'}
        return [key for key in self.data.keys() if key not in excluded_keys]

    def get_sections_for_account(self, account_id: str) -> List[str]:
        """
        Get all section names for a specific account.
        
        Args:
            account_id: The account ID to query
            
        Returns:
            List of section names in the account
        """
        if account_id not in self.data:
            return []
        
        account_data = self.data[account_id]
        if not isinstance(account_data, list) or len(account_data) == 0:
            return []
        
        sections = set()
        for item in account_data:
            if isinstance(item, dict):
                sections.update(item.keys())
        
        return sorted(list(sections))

    def get_items_by_section(self, account_id: str, section: str) -> List[str]:
        """
        Get all items in a specific section of an account.
        
        Args:
            account_id: The account ID
            section: The section name (e.g., 'cameras', 'cloud-preview-only__unknown')
            
        Returns:
            List of items in the section
        """
        if account_id not in self.data:
            return []
        
        account_data = self.data[account_id]
        if not isinstance(account_data, list):
            return []
        
        items = []
        for item in account_data:
            if isinstance(item, dict) and section in item:
                section_items = item[section]
                if isinstance(section_items, list):
                    items.extend(section_items)
        
        return items

    def compare_sections(self, account_id: str, section1: str, section2: str) -> Dict[str, List[str]]:
        """
        Compare two sections within an account and return the differences.
        
        Args:
            account_id: The account ID
            section1: The first section name
            section2: The second section name
            
        Returns:
            Dictionary with keys 'only_in_section1', 'only_in_section2', and 'in_both'
        """
        items1 = set(self.get_items_by_section(account_id, section1))
        items2 = set(self.get_items_by_section(account_id, section2))
        
        return {
            'only_in_section1': list(items1 - items2),
            'only_in_section2': list(items2 - items1),
            'in_both': list(items1 & items2)
        }

    def get_all_sections_by_account(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get all sections and their items organized by account.
        
        Returns:
            Dictionary mapping account IDs to dictionaries of sections and items
            Example:
            {
                "00051488": {
                    "cameras": [id1, id2, ...],
                    "cloud-preview-only__unknown": [id3, id4, ...]
                },
                "00011936": {
                    "cameras": [id5, id6, ...]
                }
            }
        """
        result = {}
        
        for account_id in self.get_all_accounts():
            account_sections = {}
            sections = self.get_sections_for_account(account_id)
            
            for section in sections:
                items = self.get_items_by_section(account_id, section)
                account_sections[section] = items
            
            if account_sections:
                result[account_id] = account_sections
        
        return result

    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire file structure.
        
        Returns:
            Dictionary containing parent, sub_accounts, and all accounts with their sections
        """
        return {
            'parent': self.get_parent_account(),
            'sub_accounts': self.get_sub_accounts(),
            'accounts': self.get_all_sections_by_account()
        }

    def count_items_by_account(self) -> Dict[str, int]:
        """
        Get total count of items in each account.
        
        Returns:
            Dictionary mapping account IDs to total item counts
        """
        counts = {}
        all_sections = self.get_all_sections_by_account()
        
        for account_id, sections in all_sections.items():
            total = sum(len(items) for items in sections.values())
            counts[account_id] = total
        
        return counts
