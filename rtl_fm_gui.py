import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import sounddevice as sd
from scipy import signal
import queue
import numpy as np
from threading import Thread
import time
import ctypes
from ctypes import util
from ctypes import windll, c_wchar_p

# Add the current directory to DLL search path using Windows API
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.name == 'nt':
    # Add DLL directory to the search path
    os.add_dll_directory(current_dir)
    # Also set it using Windows API
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.SetDllDirectoryW(c_wchar_p(current_dir))

os.environ['PATH'] = current_dir + os.pathsep + os.environ['PATH']

def load_dll(dll_name):
    try:
        dll_path = os.path.join(current_dir, dll_name)
        if not os.path.exists(dll_path):
            print(f"DLL not found: {dll_path}")
            return None
        print(f"Loading DLL from: {dll_path}")
        return ctypes.CDLL(dll_path)
    except Exception as e:
        print(f"Error loading {dll_name}: {e}")
        return None

# Try to load DLLs manually
if os.name == 'nt':  # Windows
    # Load required DLLs in order
    print("Current directory:", current_dir)
    print("PATH:", os.environ['PATH'])
    
    libusb = load_dll('libusb-1.0.dll')
    if not libusb:
        print("Failed to load libusb-1.0.dll")
    else:
        print("Successfully loaded libusb-1.0.dll")
    
    libwinpthread = load_dll('libwinpthread-1.dll')
    if not libwinpthread:
        print("Failed to load libwinpthread-1.dll")
    else:
        print("Successfully loaded libwinpthread-1.dll")
    
    rtlsdr = load_dll('librtlsdr.dll')
    if not rtlsdr:
        print("Failed to load librtlsdr.dll")
    else:
        print("Successfully loaded librtlsdr.dll")

# Try to set up RTL-SDR
try:
    from rtlsdr import RtlSdr
    RTLSDR_AVAILABLE = True
    print("Successfully imported RtlSdr")
except ImportError as e:
    RTLSDR_AVAILABLE = False
    ERROR_MESSAGE = str(e)
    print(f"RTL-SDR Error: {e}")

class RTLFMReceiver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Khanfar FM")
        
        # Audio settings
        self.sample_rate = 32000
        self.chunk_size = 1024 * 8  # Large buffer for stability
        self.audio_queue = queue.Queue(maxsize=16)
        
        try:
            if not RTLSDR_AVAILABLE:
                raise ImportError("RTL-SDR library not available")
            
            self.sdr = RtlSdr()
            self.sdr.sample_rate = 240000  # Standard rate for FM
            self.sdr.center_freq = 100e6
            self.sdr.gain = 'auto'
            
            # Start audio stream
            self.audio_stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=self.chunk_size,
                dtype=np.float32)
            self.audio_stream.start()
            
            # Create GUI elements
            self.create_widgets()
            
            # Start RTL-SDR reading thread
            self.running = True
            self.monitor_thread = Thread(target=self.read_rtl_data)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not initialize RTL-SDR device:\n{str(e)}\n\nMake sure:\n1. The device is plugged in\n2. Correct drivers are installed\n3. No other application is using it")
            return
    
    def audio_callback(self, outdata, frames, time, status):
        try:
            data = self.audio_queue.get_nowait()
            if len(data) == len(outdata):
                outdata[:] = data.reshape(-1, 1)
            else:
                outdata[:] = np.zeros((frames, 1), dtype=np.float32)
        except queue.Empty:
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)
    
    def demodulate_fm(self, samples):
        try:
            # Convert to complex samples
            iq = samples.astype(np.complex64)
            
            # FM demodulation
            angles = np.angle(iq[1:] * np.conj(iq[:-1]))
            
            # De-emphasis filter
            alpha = np.exp(-1.0/(self.sample_rate * 75e-6))
            y_emp = np.zeros_like(angles)
            y_emp[0] = angles[0]
            for i in range(1, len(angles)):
                y_emp[i] = angles[i] * (1-alpha) + y_emp[i-1] * alpha
            
            # Decimate to audio rate
            decimation = int(self.sdr.sample_rate / self.sample_rate)
            audio = y_emp[::decimation]
            
            # Normalize
            audio = audio - np.mean(audio)
            peak = np.max(np.abs(audio))
            if peak > 0:
                audio = audio / peak * 0.7
            
            return audio.astype(np.float32)
            
        except Exception as e:
            print(f"FM demodulation error: {e}")
            return np.zeros(self.chunk_size, dtype=np.float32)
    
    def read_rtl_data(self):
        """Read and process RTL-SDR data"""
        samples_to_read = 128 * 1024
        
        while self.running:
            try:
                # Read samples
                samples = self.sdr.read_samples(samples_to_read)
                
                if len(samples) > 0:
                    # Demodulate
                    audio = self.demodulate_fm(samples)
                    
                    # Process audio in chunks
                    chunk_size = self.chunk_size
                    for i in range(0, len(audio), chunk_size):
                        chunk = audio[i:i + chunk_size]
                        if len(chunk) == chunk_size:
                            try:
                                self.audio_queue.put(chunk, timeout=0.1)
                            except queue.Full:
                                continue
                    
                    # Update signal level
                    power = 10 * np.log10(np.mean(np.abs(samples)**2))
                    self.root.after(100, self.update_level_display, power)
                
                # Small delay
                time.sleep(0.001)
                            
            except Exception as e:
                print(f"Error reading RTL-SDR: {e}")
                time.sleep(0.1)
    
    def create_widgets(self):
        # Frequency control
        freq_frame = ttk.LabelFrame(self.root, text="Frequency Control")
        freq_frame.pack(padx=5, pady=5, fill="x")
        
        ttk.Label(freq_frame, text="Frequency (MHz):").pack(side="left", padx=5)
        self.freq_var = tk.StringVar(value="100.0")
        freq_entry = ttk.Entry(freq_frame, textvariable=self.freq_var, width=10)
        freq_entry.pack(side="left", padx=5)
        
        ttk.Button(freq_frame, text="Tune", command=self.tune_frequency).pack(side="left", padx=5)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="Demodulation Mode")
        mode_frame.pack(padx=5, pady=5, fill="x")
        
        self.mode_var = tk.StringVar(value="FM")
        modes = [("Wide FM", "FM"), ("AM", "AM")]
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, value=mode, 
                          variable=self.mode_var, command=self.change_mode).pack(side="left", padx=5)
        
        # Gain control
        gain_frame = ttk.LabelFrame(self.root, text="Gain Control")
        gain_frame.pack(padx=5, pady=5, fill="x")
        
        self.auto_gain_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gain_frame, text="Auto Gain", variable=self.auto_gain_var,
                       command=self.toggle_auto_gain).pack(side="left", padx=5)
        
        self.gain_scale = ttk.Scale(gain_frame, from_=0, to=50, orient="horizontal")
        self.gain_scale.pack(side="left", padx=5, fill="x", expand=True)
        self.gain_scale.bind("<ButtonRelease-1>", self.change_gain)
        
        # Signal level meter
        level_frame = ttk.LabelFrame(self.root, text="Signal Level")
        level_frame.pack(padx=5, pady=5, fill="x")
        
        self.level_var = tk.StringVar(value="0 dB")
        ttk.Label(level_frame, textvariable=self.level_var).pack(padx=5)
        
        self.level_bar = ttk.Progressbar(level_frame, length=200, mode='determinate')
        self.level_bar.pack(padx=5, pady=5)
    
    def tune_frequency(self):
        try:
            freq = float(self.freq_var.get()) * 1e6
            self.sdr.center_freq = freq
        except ValueError:
            messagebox.showerror("Error", "Invalid frequency")
    
    def change_mode(self):
        # Clear audio queue when changing modes
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def toggle_auto_gain(self):
        if self.auto_gain_var.get():
            self.sdr.gain = 'auto'
        else:
            self.change_gain(None)
    
    def change_gain(self, event):
        if not self.auto_gain_var.get():
            gain = int(self.gain_scale.get())
            self.sdr.gain = gain
    
    def update_level_display(self, power):
        # Update signal level display and progress bar
        normalized = min(max((power + 50) * 2, 0), 100)
        self.level_var.set(f"{power:.1f} dB")
        self.level_bar['value'] = normalized
    
    def run(self):
        self.root.mainloop()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop()
            self.audio_stream.close()
        if hasattr(self, 'sdr'):
            self.sdr.close()
        self.root.destroy()

def main():
    app = RTLFMReceiver()
    try:
        app.run()
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()
