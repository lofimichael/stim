#!/usr/bin/env python3
import json
import sys
import time
from datetime import datetime, timedelta
import os
from pathlib import Path
import plotext as plt

# Constants ⚙️
HALF_LIFE_HOURS = 6
DATA_DIR = Path.home() / '.stim'  # Store data in user's home directory 📁
DATA_FILE = DATA_DIR / 'caffeine_data.json'
CACHE_FILE = DATA_DIR / 'caffeine_cache.json'
TIMESERIES_FILE = DATA_DIR / 'caffeine_timeseries.json'
VERSION = "1.0.0"  # Added version number 🔢

# Create data directory if it doesn't exist 📂
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load caffeine tracking data"""
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        return {
            'doses': [],
            'undone_doses': [],
            'next_id': 1
        }
    with open(DATA_FILE) as f:
        data = json.load(f)
        # Ensure all required fields exist
        if 'undone_doses' not in data:
            data['undone_doses'] = []
        if 'next_id' not in data:
            # Initialize IDs for existing doses if needed
            data['next_id'] = 1
            for dose in data['doses']:
                if 'id' not in dose:
                    dose['id'] = data['next_id']
                    data['next_id'] += 1
        return data

def save_data(data):
    """Save caffeine tracking data"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_current_level(doses, specific_time=None):
    """Calculate current caffeine level"""
    current_time = specific_time or time.time()
    total = 0
    # Sort doses by timestamp to ensure proper calculation
    sorted_doses = sorted(doses, key=lambda x: x['timestamp'])
    # Only consider doses before the calculation time
    valid_doses = [d for d in sorted_doses if d['timestamp'] <= current_time]
    
    for dose in valid_doses:
        hours_passed = (current_time - dose['timestamp']) / 3600
        remaining = dose['amount'] * (0.5 ** (hours_passed / HALF_LIFE_HOURS))
        total += remaining
    return round(total, 2)

def cache_current_level():
    """Cache the current caffeine level with timestamp"""
    data = load_data()
    current_time = time.time()
    current_level = calculate_current_level(data['doses'])
    
    cache = {
        'timestamp': current_time,
        'level': current_level,
        'datetime': datetime.fromtimestamp(current_time).strftime('%d/%m/%Y %H:%M:%S')
    }
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    
    return cache

def get_cached_level():
    """Get the most recent cached measurement"""
    try:
        # Always recalculate immediately
        return cache_current_level()
    except Exception:
        return cache_current_level()

def add_dose(amount, minutes_offset=0):
    """Add a new caffeine dose"""
    if amount <= 0:
        raise ValueError("Dose amount must be greater than 0")
    if amount > 1000:
        raise ValueError("Amount must be less than 1000! That's seriously a -lot- of caffeine! ⚠️")
        
    data = load_data()
    # For positive offsets (hours/minutes ago), we subtract from current time
    timestamp = time.time() - abs(minutes_offset * 60)
    # Verify the timestamp isn't in the future
    if timestamp > time.time():
        timestamp = time.time()
    
    # Create the dose with all necessary fields
    dose = {
        'id': data['next_id'],
        'timestamp': timestamp,
        'amount': amount,
        'datetime': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
    }
    data['next_id'] += 1
    
    data['doses'].append(dose)
    save_data(data)
    
    # Invalidate cache after adding a dose
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    
    return calculate_current_level(data['doses'])

def show_history(limit=5):
    """Show recent dose history"""
    data = load_data()
    if not data['doses']:
        return []
    
    now = time.time()
    history = []
    
    # Get the last N doses
    for dose in sorted(data['doses'], key=lambda x: x['timestamp'])[-limit:]:
        hours_ago = round((now - dose['timestamp']) / 3600, 1)
        remaining = dose['amount'] * (0.5 ** (hours_ago / HALF_LIFE_HOURS))
        history.append({
            'timestamp': dose['timestamp'],
            'datetime': dose['datetime'],
            'amount': dose['amount'],
            'hours_ago': hours_ago,
            'remaining': round(remaining, 2)
        })
    
    return history

def undo_last():
    """Undo the last dose"""
    data = load_data()
    if data['doses']:
        removed = data['doses'].pop()
        save_data(data)
        return removed
    return None

def clean_old_doses():
    """Remove doses that are effectively 0 (less than 1mg remaining)"""
    data = load_data()
    current_time = time.time()
    data['doses'] = [
        dose for dose in data['doses']
        if (current_time - dose['timestamp']) / 3600 < HALF_LIFE_HOURS * 10
    ]
    save_data(data)

def generate_timeseries(start_time=None, end_time=None, interval_minutes=15):
    """Generate 15-minute interval data points from doses"""
    data = load_data()
    current_time = time.time()
    
    # Set end_time if not provided
    end_time = end_time or current_time
    
    # If no start time specified, use earliest dose
    if not start_time:
        if data['doses']:
            start_time = min(dose['timestamp'] for dose in data['doses'])
        else:
            start_time = end_time - (24 * 3600)  # Default to 24h if no doses
    
    # Calculate number of points needed
    interval_seconds = interval_minutes * 60
    num_points = int((end_time - start_time) / interval_seconds) + 1
    
    # Safety check for very large ranges
    if num_points > 10000:
        print(f"Warning: Large time range ({num_points} points) ⚠️")
    
    timeseries = []
    for i in range(num_points):
        point_time = start_time + (i * interval_seconds)
        level = calculate_current_level(data['doses'], point_time)
        timeseries.append({
            'timestamp': point_time,
            'datetime': datetime.fromtimestamp(point_time).strftime('%d/%m/%Y %H:%M:%S'),
            'level': level
        })
    
    return timeseries

def generate_graph(hours_back=24, points=48):
    """Generate a terminal graph of caffeine levels over time"""
    current_time = time.time()
    # Use all available data for graphing
    data = load_data()
    if data['doses']:
        start_time = min(dose['timestamp'] for dose in data['doses'])
        hours_back = (current_time - start_time) / 3600
    else:
        start_time = current_time - (24 * 3600)
    
    # Get 15-minute interval data
    timeseries = generate_timeseries(start_time, current_time, 15)
    
    times = [point['datetime'][11:16] for point in timeseries]  # Extract HH:MM
    levels = [point['level'] for point in timeseries]
    
    # Clear any existing plots
    plt.clear_figure()
    
    plt.date_form('H:M')
    
    # Use simpler ASCII style
    plt.plot(times, levels, color="white")
    plt.title(f"Caffeine Levels Over Past {hours_back}h")
    
    plt.plotsize(50, 15)  # Slightly smaller plot
    plt.theme('clear')    # Cleaner theme
    plt.grid(True)
    plt.frame(True)       # Add frame around plot
    
    # Set y-axis to start at 0
    if max(levels) > 0:
        plt.ylim(0, max(levels) * 1.1)
    
    return plt.show()

def update_timeseries():
    """Update and store timeseries data"""
    timeseries = generate_timeseries()
    with open(TIMESERIES_FILE, 'w') as f:
        json.dump(timeseries, f, indent=2)
    return timeseries

def get_next_time(hour, minute=0):
    """Get the next occurrence of a specific time"""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if target <= now:
        # If the time has passed today, get tomorrow's occurrence
        target += timedelta(days=1)
    
    return target.timestamp()

def check_future_dose(amount, minutes_offset=0):
    """Check impact of a potential dose"""
    # First calculate what would happen if we add this dose
    data = load_data()
    timestamp = time.time() - abs(minutes_offset * 60)
    current_level = calculate_current_level(data['doses'])
    
    # Create a temporary dose
    temp_dose = {
        'timestamp': timestamp,
        'amount': amount,
    }
    
    # Add to a copy of current doses
    test_doses = data['doses'] + [temp_dose]
    
    # Get next 6 PM, 8 AM, and 10 PM times
    next_evening = get_next_time(18, 0)  # 6 PM
    next_night = get_next_time(22, 0)    # 10 PM
    next_morning = get_next_time(8, 0)   # 8 AM
    
    evening_level = calculate_current_level(test_doses, next_evening)
    night_level = calculate_current_level(test_doses, next_night)
    morning_level = calculate_current_level(test_doses, next_morning)
    
    return {
        'current': {
            'time': datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M'),
            'level': current_level,
            'added_level': calculate_current_level(test_doses)
        },
        'evening': {
            'time': datetime.fromtimestamp(next_evening).strftime('%d/%m/%Y %H:%M'),
            'level': evening_level
        },
        'night': {
            'time': datetime.fromtimestamp(next_night).strftime('%d/%m/%Y %H:%M'),
            'level': night_level
        },
        'morning': {
            'time': datetime.fromtimestamp(next_morning).strftime('%d/%m/%Y %H:%M'),
            'level': morning_level
        }
    }

def plot_graph(hours=24, project_hours=72):  # Default to 3 days projection
    """Plot detailed caffeine level graph"""
    data = load_data()
    now = time.time()
    
    # Generate time points for past and future with 5-minute intervals
    start_time = now - (hours * 3600)
    end_time = now + (project_hours * 3600)
    time_points = list(range(int(start_time), int(end_time), 300))  # 5-minute intervals
    
    # Split points into historical and projected
    historical_points = [t for t in time_points if t <= now]
    projected_points = [t for t in time_points if t > now]
    
    # Calculate levels for both sets
    historical_levels = [calculate_current_level(data['doses'], t) for t in historical_points]
    projected_levels = [calculate_current_level(data['doses'], t) for t in projected_points]
    
    # Format times for display - only show every 30 minutes for readability
    all_times = []
    for i, t in enumerate(time_points):
        dt = datetime.fromtimestamp(t)
        if i % 6 == 0:  # Every 30 minutes (6 * 5 minutes)
            if t <= now:
                all_times.append(dt.strftime('%H:%M '))
            else:
                all_times.append(f"*{dt.strftime('%H:%M')} ")
        else:
            all_times.append("")  # Empty label for other times
    
    # Calculate reasonable y-axis limits
    all_levels = historical_levels + projected_levels
    max_level = max(all_levels) if all_levels else 0
    y_max = max(max_level * 1.1, 50)  # At least show up to 50mg
    
    # Calculate appropriate step size
    if y_max > 500:
        y_step = 100
    elif y_max > 200:
        y_step = 50
    elif y_max > 100:
        y_step = 25
    else:
        y_step = 10
        
    # Round y_max up to nearest step
    y_max = ((int(y_max) + y_step - 1) // y_step) * y_step
    
    # Clear any existing plots
    plt.clear_data()
    plt.clear_figure()
    plt.clear_color()
    
    # Create indices for x-axis
    x_indices = list(range(len(time_points)))
    
    # Set up the plot
    plt.plotsize(120, 30)  # Even larger plot for better readability
    plt.title(f"Caffeine Levels (Past {hours}h + Next {project_hours}h)\nGreen = Historical, White Dots = Projected, Red Stars = Target Times")
    plt.xlabel("Time (* = Projected)")
    plt.ylabel("Caffeine (mg) ")  # Add space after label
    
    # Plot historical data in green
    if historical_levels:
        historical_indices = x_indices[:len(historical_points)]
        plt.plot(historical_indices, historical_levels, color="green")
        
        # Add vertical line at current time, but only up to current level if it's non-zero
        current_idx = len(historical_points) - 1
        current_level = historical_levels[-1]
        
        # Only draw vertical line if we have a non-zero current level
        if current_level > 0:
            # Draw vertical line segments from 0 to current level
            plt.plot([current_idx, current_idx], [0, current_level], color="green")
    
    # Plot projected data with white dots - use fewer dots for cleaner look
    if projected_levels:
        projected_indices = x_indices[len(historical_points):]
        # Only plot every 15 minutes for dots
        dot_indices = projected_indices[::15]
        dot_levels = projected_levels[::15]
        plt.scatter(dot_indices, dot_levels, color="white", marker="dot")
    
    # Add markers for important times (6 PM and 8 AM)
    next_6pm = get_next_time(18, 0)
    next_8am = get_next_time(8, 0)
    
    for target_time in [next_6pm, next_8am]:
        if start_time <= target_time <= end_time:
            # Find the closest time point
            closest_idx = min(range(len(time_points)), 
                            key=lambda i: abs(time_points[i] - target_time))
            level = calculate_current_level(data['doses'], target_time)
            time_str = datetime.fromtimestamp(target_time).strftime('%H:%M')
            # Add marker
            plt.scatter([closest_idx], [level], color="red", marker="star")
    
    # Set up axes
    plt.ylim(0, y_max)
    y_ticks = list(range(0, int(y_max) + y_step, y_step))
    # Add spaces to y-axis labels
    y_tick_labels = [f"{y} " for y in y_ticks]  # Add space after each number
    plt.yticks(y_ticks, y_tick_labels)
    
    # Set x-axis ticks with time labels - show fewer labels for readability
    tick_spacing = max(1, len(time_points) // 15)  # Show ~15 time labels
    tick_indices = list(range(0, len(time_points), tick_spacing))
    tick_labels = [all_times[i] if i < len(all_times) else "" for i in tick_indices]
    plt.xticks(tick_indices, tick_labels)
    
    plt.grid(True)
    plt.theme('clear')
    plt.show()

def main():
    """Main program entry point"""
    if len(sys.argv) == 1:
        level = get_cached_level()['level']
        print(f"Current caffeine level: {level}mg ☕")
        return

    cmd = sys.argv[1].lower()

    # Handle all non-numeric commands first
    if cmd == 'help':
        print_help()
        return
        
    if cmd == 'about':
        print_about()
        return

    if cmd in ['redo', 'undo', 'history', 'graph', 'check']:
        if cmd == 'redo':
            handle_redo()
        elif cmd == 'undo':
            handle_undo()
        elif cmd == 'history':
            handle_history()
        elif cmd == 'graph':
            handle_graph()
        elif cmd == 'check':
            handle_check()
        return

    # Try to parse as a dose amount
    try:
        amount = float(cmd)
        time_offset = 0
        if len(sys.argv) > 2:
            if sys.argv[2] == '-h' and len(sys.argv) > 3:
                # Convert hours to minutes
                hours = float(sys.argv[3])  # The sign of the number determines past/future
                # Convert hours to minutes
                time_offset = hours * 60
            else:
                # Treat as minutes
                time_offset = float(sys.argv[2])
        
        try:
            current = add_dose(amount, time_offset)
            if time_offset:
                hours = time_offset / 60
                if abs(hours) >= 1:
                    direction = "ago" if hours < 0 else "ahead"
                    print(f"Added {amount}mg ({abs(hours):.1f}h {direction}). Current level: {current}mg ☕")
                else:
                    direction = "ago" if time_offset < 0 else "ahead"
                    print(f"Added {amount}mg ({abs(time_offset):.0f}min {direction}). Current level: {current}mg ☕")
            else:
                print(f"Added {amount}mg. Current level: {current}mg ☕")
        except ValueError as e:
            print(str(e))
    except ValueError:
        print("Invalid input. Use 'stim help' to see usage instructions")

def handle_redo():
    """Handle redo command"""
    data = load_data()
    if not data or not data.get('undone_doses'):
        print("No doses to redo")
        return
        
    last_undone = data['undone_doses'].pop()
    data['doses'].append(last_undone)
    save_data(data)
    
    # Invalidate cache after redo
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    
    # Only show last 5 doses if there are any
    if data['doses']:
        print("\nLast 5 doses: 📜")
        for dose in data['doses'][-5:]:
            print(f"{dose['datetime']}: {dose['amount']}mg ☕")
    
    print(f"\nRestored dose: {last_undone['amount']}mg from {last_undone['datetime']} ↩️")
    current = calculate_current_level(data['doses'])
    print(f"Current level: {current}mg ☕")

def handle_undo():
    """Handle undo command"""
    data = load_data()
    if not data or not data.get('doses'):
        print("No doses to undo")
        return
        
    removed = data['doses'].pop()
    data['undone_doses'].append(removed)
    save_data(data)
    
    # Invalidate cache after undo
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    
    # Only show last 5 doses if there are any remaining
    if data['doses']:
        print("\nLast 5 doses: 📜")
        for dose in data['doses'][-5:]:
            print(f"{dose['datetime']}: {dose['amount']}mg ☕")
    
    print(f"\nRemoved dose: {removed['amount']}mg from {removed['datetime']} ↩️")
    current = calculate_current_level(data['doses'])
    print(f"Current level: {current}mg ☕")

def handle_history():
    """Handle history command"""
    history = show_history(5)
    print("\nRecent doses: 📜")
    for dose in history:
        print(f"{dose['datetime']} ({dose['hours_ago']}h ago): {dose['amount']}mg -> {dose['remaining']}mg remaining ☕")
    current = calculate_current_level(load_data()['doses'])
    print(f"\nCurrent total: {current}mg ☕")

def handle_graph():
    """Handle graph command"""
    hours = 24
    project_hours = 72
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
            if len(sys.argv) > 3:
                project_hours = int(sys.argv[3])
        except ValueError:
            print("Invalid hours value")
            return
    plot_graph(hours, project_hours)

def handle_check():
    """Handle check command"""
    if len(sys.argv) <= 2:
        print("Please provide an amount to check")
        return
        
    try:
        amount = float(sys.argv[2])
        projection = check_future_dose(amount)
        print(f"\nCurrent level: {projection['current']['level']:.1f}mg ☕")
        print(f"After {amount}mg dose: {projection['current']['added_level']:.1f}mg ⬆️")
        
        # Calculate time until evening, night, and morning
        now = time.time()
        evening_hours = (get_next_time(18, 0) - now) / 3600
        night_hours = (get_next_time(22, 0) - now) / 3600
        morning_hours = (get_next_time(8, 0) - now) / 3600
        
        print(f"\nProjected levels: 🔮")
        print(f"  At {projection['evening']['time']} (6 PM, in {evening_hours:.1f}h): {projection['evening']['level']:.1f}mg 🌅")
        if projection['evening']['level'] > 30:
            print("  ⚠️  Warning: Evening level above 30mg may affect sleep")
            
        print(f"  At {projection['night']['time']} (10 PM, in {night_hours:.1f}h): {projection['night']['level']:.1f}mg 🌙")
        if projection['night']['level'] > 15:
            print("  ⚠️  Warning: Night level above 15mg may affect sleep")
            
        print(f"  At {projection['morning']['time']} (8 AM, in {morning_hours:.1f}h): {projection['morning']['level']:.1f}mg 🌅")
        
        # Show half-life progression
        print("\nHalf-life progression: ⏳")
        initial = projection['current']['added_level']
        print(f"  t=0 (now): {initial:.1f}mg")
        for i in range(1, 4):
            hours = i * HALF_LIFE_HOURS
            level = initial * (0.5 ** i)
            print(f"  t={hours}h: {level:.1f}mg")
    except ValueError:
        print("Invalid amount. Please provide a number")

def print_disclaimer():
    """Print disclaimer message"""
    print("\nDISCLAIMER:")
    print("This software is for informational purposes only and is not intended")
    print("to be a substitute for professional medical advice, diagnosis, or")
    print("treatment. The calculations and tracking features are approximations")
    print("based on general well-studied caffeine half-life data and should not")
    print("be used in isolation for medical decisions. Always seek the advice of")
    print("your physician or other qualified health provider with any questions")
    print("you may have regarding caffeine consumption or a medical condition.")
    
def print_about():
    """Print about message"""
    print(f"\nCaffeine Tracker v{VERSION}")
    print("Created by Michael Kirsanov")
    print("https://github.com/lofimichael/stim")
    print("\nA command-line tool for tracking caffeine intake and projecting")
    print("levels over time based on the scientifically established half-life")
    print("of caffeine in the human body.")
    print("\nLicensed under dual license - free for personal use.")
    print("Commercial use requires a license. Contact michael@lofilabs.xyz")
    print_disclaimer()


def print_help():
    """Print help message"""
    print(f"Caffeine Tracker v{VERSION} Usage:")
    print("  stim                    Show current caffeine level")
    print("  stim <amount>           Add caffeine dose in mg")
    print("  stim <amount> -h <hours> Add dose with hours offset (negative = past)")
    print("  stim <amount> <minutes>  Add dose with minutes offset (negative for past)")
    print("  stim check <amount>      Check projected levels of potential caffeinedose")
    print("  stim undo               Show last 5 doses and remove most recent")
    print("  stim redo               Restore the last undone dose")
    print("  stim history            Show last 5 doses with remaining amounts")
    print("  stim graph [hours] [projection_hours]  Show caffeine levels over time")
    print("  stim help               Show this help message")
    print("  stim about              Show about message")

if __name__ == '__main__':
    main()