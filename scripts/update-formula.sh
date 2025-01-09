#!/bin/bash

# Get SHA256 of current v1.0.0 tarball
SHA256=$(curl -sL "https://github.com/lofimichael/stim/archive/refs/tags/v1.0.0.tar.gz" | shasum -a 256 | cut -d ' ' -f 1)

# Update the formula (only the main package SHA256, not resources)
sed -i '' "/url \".*stim.*tar\.gz\"/{n;s/sha256 \".*\"/sha256 \"$SHA256\"/;}" Formula/stim.rb

# Stage the changes
git add Formula/stim.rb
