#!/bin/bash
set -e # Exit on error

echo "==> Cleaning up previous installations..."
pip uninstall -y stim 2>/dev/null || true
rm -rf build/ dist/ *.egg-info/

echo "==> Reinstalling in development mode..."
pip install --no-deps -e .

echo "==> Refreshing Homebrew tap..."
brew untap lofimichael/stim 2>/dev/null || true
brew tap lofimichael/stim https://github.com/lofimichael/stim

echo "==> Reinstalling via Homebrew..."
brew reinstall stim || brew install stim

echo "==> Done! 🎉"
