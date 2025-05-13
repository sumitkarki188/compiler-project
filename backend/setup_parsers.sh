#!/bin/bash
# Clone Tree-sitter language parsers
mkdir -p vendor
cd vendor
git clone https://github.com/tree-sitter/tree-sitter-python
git clone https://github.com/tree-sitter/tree-sitter-java
git clone https://github.com/tree-sitter/tree-sitter-cpp
cd ..