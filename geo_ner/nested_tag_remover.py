#!/usr/bin/env python3
"""
Nested Tag Remover Module

This module provides functionality to detect and remove nested geo-XML tags
from text that has been processed by multiple NER systems.
"""

import re
from typing import List, Tuple, Dict, Optional
from .logging_config import get_logger

logger = get_logger(__name__)


class TagNode:
    """Represents a tag node in the XML tree structure."""
    
    def __init__(self, tag_name: str, start_pos: int, end_pos: int, content_start: int, content_end: int):
        self.tag_name = tag_name
        self.start_pos = start_pos  # Position of opening tag
        self.end_pos = end_pos      # Position of closing tag
        self.content_start = content_start  # Start of content (after opening tag)
        self.content_end = content_end      # End of content (before closing tag)
        self.children = []  # Child tag nodes
        self.parent = None  # Parent tag node
        
    def add_child(self, child_node):
        """Add a child node to this tag."""
        child_node.parent = self
        self.children.append(child_node)
        
    def is_geo_tag(self) -> bool:
        """Check if this is a geo-related tag."""
        return self.tag_name in {"GPE", "LOC", "address"}
        
    def get_full_text(self, text: str) -> str:
        """Get the full text including tags."""
        return text[self.start_pos:self.end_pos]
        
    def get_content_text(self, text: str) -> str:
        """Get just the content text (without tags)."""
        return text[self.content_start:self.content_end]


class NestedTagRemover:
    """
    A class to detect and remove nested geo-XML tags from processed text.
    
    This class uses a tree-based approach to parse XML tags and remove nesting.
    """
    
    def __init__(self):
        """Initialize the nested tag remover."""
        self.logger = get_logger(__name__)
        
        # Define the geo entity tag types we care about
        self.geo_tags = {"GPE", "LOC", "address"}
        
        # Pattern to find opening and closing tags
        self.opening_tag_pattern = re.compile(r'<(\w+)(?:\s[^>]*)?>')
        self.closing_tag_pattern = re.compile(r'</(\w+)>')
        
    def remove_nested_tags(self, text: str) -> str:
        """
        Remove nested geo-XML tags from the text.
        
        Args:
            text (str): Text that may contain nested XML tags
            
        Returns:
            str: Text with nested tags removed
        """
        if not text or not text.strip():
            return text
            
        self.logger.debug(f"Processing text of length {len(text)} for nested tag removal")
        
        # Parse the text and build tag tree
        tag_tree = self._build_tag_tree(text)
        
        if not tag_tree:
            self.logger.debug("No tags found in text")
            return text
            
        # Remove nested tags, keeping only top-level ones
        cleaned_text = self._remove_nested_tags_from_tree(text, tag_tree)
        
        self.logger.debug("Nested tag removal complete")
        return cleaned_text
        
    def _build_tag_tree(self, text: str) -> List[TagNode]:
        """
        Build a tree structure of XML tags from the text.
        
        Args:
            text (str): Text to parse
            
        Returns:
            List[TagNode]: List of top-level tag nodes
        """
        # Find all opening and closing tags with their positions
        opening_tags = []
        for match in self.opening_tag_pattern.finditer(text):
            tag_name = match.group(1)
            if tag_name in self.geo_tags:
                opening_tags.append({
                    'tag': tag_name,
                    'pos': match.start(),
                    'end': match.end()
                })
                
        closing_tags = []
        for match in self.closing_tag_pattern.finditer(text):
            tag_name = match.group(1)
            if tag_name in self.geo_tags:
                closing_tags.append({
                    'tag': tag_name,
                    'pos': match.start(),
                    'end': match.end()
                })
        
        if not opening_tags or not closing_tags:
            return []
            
        # Build the tag tree
        root_nodes = []
        tag_stack = []
        
        # Process tags in order of appearance
        all_tags = []
        for tag in opening_tags:
            all_tags.append(('open', tag))
        for tag in closing_tags:
            all_tags.append(('close', tag))
            
        # Sort by position
        all_tags.sort(key=lambda x: x[1]['pos'])
        
        for tag_type, tag_info in all_tags:
            if tag_type == 'open':
                # Create new tag node
                node = TagNode(
                    tag_name=tag_info['tag'],
                    start_pos=tag_info['pos'],
                    end_pos=-1,  # Will be set when we find closing tag
                    content_start=tag_info['end'],
                    content_end=-1  # Will be set when we find closing tag
                )
                
                if tag_stack:
                    # Add as child of current parent
                    tag_stack[-1].add_child(node)
                else:
                    # Top-level tag
                    root_nodes.append(node)
                    
                tag_stack.append(node)
                
            elif tag_type == 'close':
                # Find matching opening tag on stack
                for i in range(len(tag_stack) - 1, -1, -1):
                    if tag_stack[i].tag_name == tag_info['tag']:
                        # Found matching opening tag
                        node = tag_stack[i]
                        node.end_pos = tag_info['end']
                        node.content_end = tag_info['pos']
                        
                        # Remove this tag and all its children from stack
                        tag_stack = tag_stack[:i]
                        break
                        
        # Return only top-level nodes
        return root_nodes
        
    def _remove_nested_tags_from_tree(self, text: str, root_nodes: List[TagNode]) -> str:
        """
        Remove nested tags from the text based on the tag tree.
        
        Args:
            text (str): Original text
            root_nodes (List[TagNode]): Top-level tag nodes
            
        Returns:
            str: Text with nested tags removed
        """
        if not root_nodes:
            return text
            
        # Start with the original text
        result = text
        
        # Process each top-level tag
        for root_node in root_nodes:
            result = self._process_tag_node(result, root_node)
            
        return result
        
    def _process_tag_node(self, text: str, node: TagNode) -> str:
        """
        Process a single tag node, removing its nested children.
        
        Args:
            text (str): Text to process
            node (TagNode): Tag node to process
            
        Returns:
            str: Processed text
        """
        if not node.children:
            # No children, keep as is
            return text
            
        # Get the original content
        original_content = text[node.content_start:node.content_end]
        
        # Remove all nested tags from content, keeping only text
        cleaned_content = self._remove_all_tags_from_text(original_content)
        
        # Create new tag with cleaned content
        new_tag = f"<{node.tag_name}>{cleaned_content}</{node.tag_name}>"
        
        # Replace the entire original tag with the new one
        original_tag = text[node.start_pos:node.end_pos]
        result = text.replace(original_tag, new_tag)
        
        return result
        
    def _remove_all_tags_from_text(self, text: str) -> str:
        """
        Remove all XML tags from text, keeping only the content.
        
        Args:
            text (str): Text that may contain XML tags
            
        Returns:
            str: Text with all tags removed
        """
        # Remove all opening tags
        text = re.sub(r'<\w+(?:\s[^>]*)?>', '', text)
        
        # Remove all closing tags
        text = re.sub(r'</\w+>', '', text)
        
        return text
        
    def _find_nested_tags(self, text: str) -> List[Dict]:
        """
        Find all instances of nested tags in the text.
        This method is kept for backward compatibility with tests.
        
        Args:
            text (str): Text to search for nested tags
            
        Returns:
            List[Dict]: List of nested tag information dictionaries
        """
        # Build tag tree
        root_nodes = self._build_tag_tree(text)
        
        nested_instances = []
        
        # Check each root node for nested children
        for root_node in root_nodes:
            if root_node.children:
                nested_instances.append({
                    'outer_tag': root_node.tag_name,
                    'inner_tag': root_node.children[0].tag_name,
                    'full_match': root_node.get_full_text(text),
                    'start_pos': root_node.start_pos,
                    'end_pos': root_node.end_pos,
                    'match_text': root_node.get_full_text(text)
                })
                
        return nested_instances


def remove_nested_geo_tags(text: str) -> str:
    """
    Convenience function to remove nested geo-XML tags from text.
    
    Args:
        text (str): Text that may contain nested XML tags
        
    Returns:
        str: Text with nested tags removed
    """
    remover = NestedTagRemover()
    return remover.remove_nested_tags(text)


if __name__ == "__main__":
    # Example usage and testing
    test_cases = [
        # Address containing GPE tags
        "<address>248 Sophia Way, <GPE>Oceanside</GPE>, <GPE>CA</GPE> 92057</address>",
        
        # GPE containing GPE tags
        "<GPE><GPE>San Diego</GPE> County</GPE>",
        
        # GPE containing LOC tags
        "<GPE><LOC>Mount Baldy</LOC> Regional Park</GPE>",
        
        # Complex nested case
        "<address>123 Main St, <GPE><LOC>Downtown</LOC> District</GPE>, <GPE>Los Angeles</GPE>, CA</address>"
    ]
    
    remover = NestedTagRemover()
    
    print("Nested Tag Removal Examples")
    print("=" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input:  {test_case}")
        cleaned = remover.remove_nested_tags(test_case)
        print(f"Output: {cleaned}")
        print("-" * 40)
