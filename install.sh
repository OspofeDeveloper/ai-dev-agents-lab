#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Installing SDD ecosystem to $CLAUDE_DIR..."
echo ""

# Install agents
mkdir -p "$CLAUDE_DIR/agents"
for agent in "$REPO_DIR/agents/"*.md; do
    name=$(basename "$agent")
    cp "$agent" "$CLAUDE_DIR/agents/$name"
    echo "  agents/$name"
done

# Install skills
mkdir -p "$CLAUDE_DIR/skills"
for skill_dir in "$REPO_DIR/skills/"*/; do
    name=$(basename "$skill_dir")
    mkdir -p "$CLAUDE_DIR/skills/$name"
    cp -r "$skill_dir/." "$CLAUDE_DIR/skills/$name/"
    echo "  skills/$name/"
done

echo ""
echo "Done. Restart Claude Code to activate the new skills and agents."
