#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Installing SDD ecosystem to $CLAUDE_DIR..."
echo ""

# Install agents and skills organized by feature under sdd/
for feature_dir in "$REPO_DIR/sdd/"*/; do
    feature=$(basename "$feature_dir")

    # Install agents
    if [ -d "$feature_dir/agents" ]; then
        for agent in "$feature_dir/agents/"*.md; do
            [ -f "$agent" ] || continue
            mkdir -p "$CLAUDE_DIR/agents"
            name=$(basename "$agent")
            cp "$agent" "$CLAUDE_DIR/agents/$name"
            echo "  agents/$name  ($feature)"
        done
    fi

    # Install skills
    if [ -d "$feature_dir/skills" ]; then
        for skill_dir in "$feature_dir/skills/"*/; do
            [ -d "$skill_dir" ] || continue
            name=$(basename "$skill_dir")
            mkdir -p "$CLAUDE_DIR/skills/$name"
            cp -r "$skill_dir/." "$CLAUDE_DIR/skills/$name/"
            echo "  skills/$name/  ($feature)"
        done
    fi
done

echo ""
echo "Done. Restart Claude Code to activate the new skills and agents."
