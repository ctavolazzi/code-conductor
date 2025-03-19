#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for work node functionality.

This script tests the core features of the work node system:
1. Creating work nodes
2. Linking documents
3. Generating visualization data
4. Auto-discovery of related documents

Usage:
    python test_work_node.py
"""

import os
import sys
import yaml
import tempfile
import unittest
import shutil
import re
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the work node module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.code_conductor.work_efforts.create_work_node import WorkNode, WorkNodeManager

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestWorkNode(unittest.TestCase):
    """Test the WorkNode class functionality."""

    def test_work_node_creation(self):
        """Test creating a work node with various properties."""
        node = WorkNode(
            title="Test Node",
            category="test",
            description="Test description",
            documents=["doc1.md", "doc2.md"]
        )

        # Test basic properties
        self.assertEqual(node.title, "Test Node")
        self.assertEqual(node.category, "test")
        self.assertEqual(node.description, "Test description")
        self.assertEqual(len(node.documents), 2)
        self.assertIn("doc1.md", node.documents)
        self.assertIn("doc2.md", node.documents)

        # Test filename generation
        self.assertTrue(node.filename.endswith("_node_test_node.md"))

        # Test markdown generation
        markdown = node.to_markdown()
        self.assertIn("# Test Node", markdown)
        self.assertIn("## Connected Document", markdown)
        self.assertIn("- [[doc1.md]]", markdown)
        self.assertIn("- [[doc2.md]]", markdown)
        self.assertIn("## Connection Map", markdown)

        # Test dictionary conversion
        node_dict = node.to_dict()
        self.assertEqual(node_dict["title"], "Test Node")
        self.assertEqual(node_dict["category"], "test")
        self.assertEqual(node_dict["description"], "Test description")
        self.assertEqual(len(node_dict["connected_document"]), 2)


class TestWorkNodeManager(unittest.TestCase):
    """Test the WorkNodeManager class functionality."""

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.work_dir = os.path.join(self.temp_dir, '_AI-Setup', 'work_effort')
        os.makedirs(self.work_dir, exist_ok=True)

        # Create some test documents
        self.doc1_path = os.path.join(self.work_dir, 'doc1.md')
        self.doc2_path = os.path.join(self.work_dir, 'doc2.md')

        with open(self.doc1_path, 'w') as f:
            f.write("""---
title: "Document 1"
---

# Document 1

This is a test document with some content.
It contains references to certain topics like testing and Python.
""")

        with open(self.doc2_path, 'w') as f:
            f.write("""---
title: "Document 2"
---

# Document 2

This is another test document with similar content.
It also mentions testing and Python modules.
""")

        # Initialize the manager with dry run mode
        self.manager = WorkNodeManager(
            work_dir=self.work_dir,
            dry_run=True,
            verbose=True
        )

    def tearDown(self):
        """Clean up temporary files after testing."""
        shutil.rmtree(self.temp_dir)

    def test_find_all_documents(self):
        """Test finding all documents in the work directory."""
        documents = self.manager.find_all_documents()
        self.assertEqual(len(documents), 2)
        self.assertIn("doc1.md", documents)
        self.assertIn("doc2.md", documents)

    def test_extract_document_info(self):
        """Test extracting document information."""
        doc_info = self.manager.extract_document_info("doc1.md")
        self.assertEqual(doc_info["title"], "Document 1")
        self.assertIn("This is a test document", doc_info["content"])

    def test_discover_related_documents(self):
        """Test discovering related documents based on content similarity."""
        clusters = self.manager.discover_related_documents(min_similarity=0.3)
        self.assertEqual(len(clusters), 1)  # We should find one cluster
        self.assertEqual(len(clusters[0]), 2)  # With two documents

    def test_create_work_node(self):
        """Test creating a work node."""
        # Switch to actual execution mode (not dry run) for this test
        self.manager.dry_run = False

        node = self.manager.create_work_node(
            title="Test Connection",
            category="test",
            description="A test connection between documents",
            documents=["doc1.md", "doc2.md"]
        )

        # Verify the node was created
        node_path = os.path.join(self.manager.node_dir, node.filename)
        self.assertTrue(os.path.exists(node_path))

        # Verify document links were updated
        with open(self.doc1_path, 'r') as f:
            content = f.read()
            self.assertIn("connected_node:", content)
            self.assertIn(f"[[{node.filename}]]", content)

        with open(self.doc2_path, 'r') as f:
            content = f.read()
            self.assertIn("connected_node:", content)
            self.assertIn(f"[[{node.filename}]]", content)

    def test_generate_visualization(self):
        """Test generating visualization data."""
        # Create a node first
        self.manager.dry_run = False

        self.manager.create_work_node(
            title="Visualization Test",
            category="test",
            description="Testing visualization generation",
            documents=["doc1.md", "doc2.md"]
        )

        # Generate visualization
        output_file = os.path.join(self.temp_dir, "test_graph.json")
        graph_data = self.manager.generate_visualization(output_file=output_file)

        # Verify graph data
        self.assertTrue(os.path.exists(output_file))
        self.assertGreaterEqual(len(graph_data["nodes"]), 3)  # 1 node + 2 documents
        self.assertGreaterEqual(len(graph_data["edges"]), 2)  # 2 connections


def run_tests():
    """Run the test suite."""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    # Run the tests
    print("Running work node tests...")
    run_tests()
    print("Testing completed successfully!")