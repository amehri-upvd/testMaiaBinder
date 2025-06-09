from IPython.core.magic import register_line_cell_magic, register_line_magic
from IPython import get_ipython
import subprocess
import time
import ipyparallel as ipp
import sys

def load_ipython_extension(ipython):
    # Register a custom magic to start the parallel environment
    @register_line_magic
    def start_parallel(line):
        """Start parallel environment with specified number of processes.
        Usage: %start_parallel [n_engines]
        Default: %start_parallel 4
        """
        try:
            n_engines = int(line.strip()) if line.strip() else 4
        except ValueError:
            print(f"Invalid number of engines: {line.strip()}")
            print("Using default: 4")
            n_engines = 4
            
        # Start by stopping any existing ipcluster
        print("Stopping any existing ipcluster...")
        subprocess.run(["ipcluster", "stop"], check=False)
        
        # Start ipcluster with MPI engines
        print(f"Starting ipcluster with {n_engines} MPI engines...")
        subprocess.run(["ipcluster", "start", "--engines=MPI", f"--n={n_engines}", "--daemonize"], check=True)
        
        # Wait for cluster to initialize
        print("Waiting for ipcluster to start...")
        #time.sleep(10)
        
        # Connect to the cluster
        print("Connecting to ipcluster...")
        try:
            client = ipp.Client(timeout=60)
            client.wait_for_engines(n=n_engines, timeout=120)
            ipython.user_ns['client'] = client
            ipython.user_ns['dview'] = client.direct_view()
            print(f"Connected to {len(client.ids)} engines")
            
            # Set up automatic px wrapping
            setup_px_wrapping(ipython)
            
        except Exception as e:
            print(f"Error connecting to ipcluster: {e}", file=sys.stderr)
            print("Parallel execution may not work.", file=sys.stderr)
    
    # Register a magic to stop the parallel environment
    @register_line_magic
    def stop_parallel(line):
        """Stop parallel environment and restore normal cell execution."""
        # Restore original run_cell if it was modified
        if hasattr(ipython, '_original_run_cell'):
            ipython.run_cell = ipython._original_run_cell
            
        # Stop ipcluster
        print("Stopping ipcluster...")
        subprocess.run(["ipcluster", "stop"], check=False)
    
    # Helper function to set up px wrapping
    def setup_px_wrapping(ipython):
        # Store original run_cell method
        ipython._original_run_cell = ipython.run_cell
        
        def parallel_run_cell(raw_cell, *args, **kwargs):
            # Skip if cell already has magic
            if raw_cell.lstrip().startswith('%') or raw_cell.lstrip().startswith('!'):
                return ipython._original_run_cell(raw_cell, *args, **kwargs)
            
            # Prepend px magic to regular cells
            px_cell = f"%%px\n{raw_cell}"
            return ipython._original_run_cell(px_cell, *args, **kwargs)
        
        # Replace run_cell with our parallel version
        ipython.run_cell = parallel_run_cell
    
    # Start with default 4 engines when extension is loaded
    print("Extension loaded. Use %start_parallel [n] to start with n engines.")
    print("Default behavior: %start_parallel 4")

def unload_ipython_extension(ipython):
    # Restore original run_cell when unloaded
    if hasattr(ipython, '_original_run_cell'):
        ipython.run_cell = ipython._original_run_cell
    
    # Stop ipcluster when extension is unloaded
    print("Stopping ipcluster...")
    subprocess.run(["ipcluster", "stop"], check=False)