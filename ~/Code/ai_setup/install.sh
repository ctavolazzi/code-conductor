#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing AI-Setup globally...${NC}"

# Uninstall any existing version
echo -e "Removing any existing installations..."
sudo pip3 uninstall -y ai_setup 2>/dev/null

# Install the package system-wide
echo -e "Installing package globally..."
cd "$(dirname "$0")"
sudo pip3 install -e .

# Create symlinks with dashes instead of underscores
echo -e "Creating command symlinks..."
if [ -f /usr/local/bin/ai-setup ]; then
    sudo rm /usr/local/bin/ai-setup
fi

if [ -f /usr/local/bin/ai-work-effort ]; then
    sudo rm /usr/local/bin/ai-work-effort
fi

# Create the symlinks
sudo ln -s "$(which python3)" /usr/local/bin/ai-setup
sudo ln -s "$(which python3)" /usr/local/bin/ai-work-effort

# Modify the symlinks to point to the entry points
sudo bash -c "cat > /usr/local/bin/ai-setup" << 'EOF'
#!/usr/bin/env python3
import sys
import cli

if __name__ == "__main__":
    sys.exit(cli.main_entry())
EOF

sudo bash -c "cat > /usr/local/bin/ai-work-effort" << 'EOF'
#!/usr/bin/env python3
import sys
import work_efforts.scripts.ai_work_effort_creator

if __name__ == "__main__":
    sys.exit(work_efforts.scripts.ai_work_effort_creator.main())
EOF

# Make the symlinks executable
sudo chmod +x /usr/local/bin/ai-setup
sudo chmod +x /usr/local/bin/ai-work-effort

echo -e "${GREEN}✅ Installation complete!${NC}"
echo -e "${YELLOW}You can now use:${NC}"
echo -e "  ${GREEN}ai-setup${NC} - Main command for AI setup and work effort management"
echo -e "  ${GREEN}ai-work-effort${NC} - Enhanced work effort creator with AI features"
echo ""
echo -e "${YELLOW}Try it out by running:${NC}"
echo -e "  ${GREEN}cd /path/to/your/project${NC}"
echo -e "  ${GREEN}ai-setup setup${NC}"