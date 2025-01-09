# Stim - Caffeine Intake Tracker

A command-line tool for tracking caffeine intake with half-life calculations and visualization.

> **Medical Disclaimer**: This software is for informational purposes only and is not intended to be a substitute for professional medical advice, diagnosis, or treatment. The calculations and tracking features are approximations based on general well-studied caffeine half-life data and should not be used in isolation for medical decisions. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding caffeine consumption or a medical condition.

## Features

- Track caffeine doses with precise timing
- Calculate current caffeine levels based on 6 hour half-life
- Visualize caffeine levels over time with ASCII graphs
- Project future caffeine levels
- Undo/redo functionality
- Historical dose tracking

## Installation

### Using Homebrew (recommended for macOS)

```bash
brew tap lofimichael/stim https://github.com/lofimichael/stim && brew install stim
```
*Note: This package is not in Homebrew Core as it uses a dual license model - This model helps fund custom implementations for organizations concerned with [quantified self](https://en.wikipedia.org/wiki/Quantified_self) while keeping the tool free for individuals.*

## Usage

```bash
stim                     # Show current caffeine level
stim <amount>           # Add caffeine dose in mg
stim <amount> -h <hours> # Add dose with hours offset (negative = past)
stim <amount> <minutes>  # Add dose with minutes offset (negative for past)
stim check <amount>      # Check impact of potential dose
stim undo               # Show last 5 doses and remove most recent
stim redo               # Restore the last undone dose
stim history            # Show last 5 doses with remaining amounts
stim graph [hours] [projection_hours]  # Show caffeine levels over time
stim help               # Show this help message
```

## Common Caffeine Amounts

- Espresso Shot: ~63mg
- Coffee Cup (8 oz): ~95mg
- Cold Brew (12 oz): ~155mg
- Green Tea (8 oz): ~28mg
- Energy Drink (8.4 oz): ~80mg

## Development

To install for development:

```bash
git clone https://github.com/lofimichael/stim.git
cd stim
./dev-reinstall.sh
```

## License

This software is available under a dual license:

### Personal Use
Free for individual, non-commercial use. See [LICENSE.md](./LICENSE.md) for details.

### Commercial Use
For company/organizational use, a commercial license is required. 
See [LICENSE.md](./LICENSE.md) for licensing and custom implementation information.
