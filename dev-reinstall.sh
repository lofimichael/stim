#!/bin/bash
set -e # Exit on error

echo "==> Uninstalling existing stim..."
brew uninstall stim 2>/dev/null || true # Don't fail if not installed

echo -e "\n==> Cleaning up Homebrew caches..."
brew cleanup stim 2>/dev/null || true
rm -rf "$(brew --cache)/stim--git" 2>/dev/null || true # Clean git clone cache

echo -e "\n==> Installing from local formula..."
STIM_DEV=1 brew install --HEAD --verbose Formula/stim.rb

echo -e "\n==> Testing installation:"
echo "Running 'stim help'..."
stim help

echo -e "\n==> Installation complete!"
echo "You can now use 'stim' commands."
