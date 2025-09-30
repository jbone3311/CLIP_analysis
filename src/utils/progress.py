"""
Progress Tracking Utilities

Reusable progress tracking for batch operations.
"""

import time
from typing import Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ProgressState:
    """State container for progress tracking"""
    total_items: int
    completed: int = 0
    failed: int = 0
    start_time: float = field(default_factory=time.time)
    current_item: str = ""
    current_step: str = ""
    current_mode: str = ""


class ProgressTracker:
    """
    Tracks and displays progress for batch processing with detailed status.
    
    Example:
        tracker = ProgressTracker(total=100, callback=print)
        for item in items:
            tracker.update_status(item_name="item1", step="Processing")
            # ... do work ...
            tracker.update(success=True)
        tracker.finish()
    """
    
    def __init__(
        self, 
        total: int, 
        callback: Optional[Callable[[str], None]] = None,
        show_rate: bool = True,
        show_eta: bool = True
    ):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            callback: Optional callback function for progress messages
            show_rate: Show processing rate in messages
            show_eta: Show estimated time to completion
        """
        self.state = ProgressState(total_items=total)
        self.callback = callback or self._default_callback
        self.show_rate = show_rate
        self.show_eta = show_eta
        
    def _default_callback(self, message: str) -> None:
        """Default callback that prints to stdout"""
        print(message, end='', flush=True)
    
    def update(
        self, 
        success: bool = True, 
        item_name: str = "", 
        step: str = "", 
        mode: str = ""
    ) -> None:
        """
        Update progress counter and display.
        
        Args:
            success: Whether the operation succeeded
            item_name: Name of current item
            step: Current processing step
            mode: Current processing mode
        """
        self.state.completed += 1
        if not success:
            self.state.failed += 1
        
        if item_name:
            self.state.current_item = item_name
        if step:
            self.state.current_step = step
        if mode:
            self.state.current_mode = mode
            
        self._display_progress()
    
    def update_status(
        self, 
        item_name: str = "", 
        step: str = "", 
        mode: str = ""
    ) -> None:
        """
        Update status without incrementing progress counter.
        
        Args:
            item_name: Name of current item
            step: Current processing step
            mode: Current processing mode
        """
        if item_name:
            self.state.current_item = item_name
        if step:
            self.state.current_step = step
        if mode:
            self.state.current_mode = mode
        self._display_progress()
    
    def _display_progress(self) -> None:
        """Display current progress"""
        elapsed = time.time() - self.state.start_time
        rate = self.state.completed / elapsed if elapsed > 0 else 0
        remaining = self.state.total_items - self.state.completed
        eta = remaining / rate if rate > 0 else 0
        
        progress_bar = self._create_progress_bar()
        
        # Create status line
        status_parts = []
        status_parts.append(f"Item {self.state.completed}/{self.state.total_items}")
        
        if self.state.current_item:
            import os
            item_display = os.path.basename(self.state.current_item)
            if len(item_display) > 30:
                item_display = item_display[:27] + "..."
            status_parts.append(f"'{item_display}'")
        
        if self.state.current_step:
            status_parts.append(f"[{self.state.current_step}]")
            
        if self.state.current_mode:
            status_parts.append(f"Mode: {self.state.current_mode}")
        
        status_line = " | ".join(status_parts)
        
        # Build message
        message = f"\r{progress_bar} {status_line} "
        message += f"({self.state.completed/self.state.total_items*100:.1f}%) "
        message += f"| Failed: {self.state.failed}"
        
        if self.show_rate:
            message += f" | Rate: {rate:.1f}/s"
        
        if self.show_eta:
            message += f" | ETA: {eta:.0f}s"
        
        self.callback(message)
    
    def _create_progress_bar(self, width: int = 30) -> str:
        """
        Create visual progress bar.
        
        Args:
            width: Width of progress bar in characters
            
        Returns:
            Progress bar string
        """
        filled = int(width * self.state.completed / self.state.total_items)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def finish(self, message: Optional[str] = None) -> None:
        """
        Complete progress tracking and display summary.
        
        Args:
            message: Optional custom completion message
        """
        elapsed = time.time() - self.state.start_time
        rate = self.state.completed / elapsed if elapsed > 0 else 0
        
        if message:
            final_message = f"\n{message}\n"
        else:
            final_message = f"\n[SUCCESS] Processing complete! "
            final_message += f"Processed {self.state.completed} items in {elapsed:.1f}s "
            final_message += f"({rate:.1f} items/s)\n"
        
        if self.state.failed > 0:
            final_message += f"[ERROR] {self.state.failed} items failed to process\n"
        
        self.callback(final_message)
    
    def get_stats(self) -> dict:
        """
        Get current progress statistics.
        
        Returns:
            Dictionary with progress statistics
        """
        elapsed = time.time() - self.state.start_time
        rate = self.state.completed / elapsed if elapsed > 0 else 0
        
        return {
            'total': self.state.total_items,
            'completed': self.state.completed,
            'failed': self.state.failed,
            'elapsed_seconds': elapsed,
            'rate_per_second': rate,
            'percent_complete': (self.state.completed / self.state.total_items * 100) if self.state.total_items > 0 else 0
        }
