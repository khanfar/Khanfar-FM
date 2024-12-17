# Khanfar FM

<p align="center">
  <h2 align="center">🎵 Khanfar FM Radio Receiver 📻</h2>
  <p align="center">Listen to FM radio using RTL-SDR with a beautiful GUI interface</p>
</p>

## ✨ Features

- 📻 Real-time FM radio reception (88-108 MHz)
- 🎚️ Easy-to-use graphical interface
- 🎛️ Adjustable gain control for better reception
- 📊 Real-time signal strength monitoring
- 🔊 High-quality audio output
- ⚡ Optimized performance with 240kHz sampling
- 🎯 Precise frequency tuning

## 📋 Requirements

### 🔧 Hardware
- RTL-SDR USB dongle (RTL2832U chipset)
- Antenna for FM reception
- Computer with USB port

### 💻 Software
- Python 3.x
- Required Python packages:
  ```bash
  pip install numpy scipy sounddevice pyrtlsdr
  ```

### 📁 Required Files
Place these files in the same directory:

1. 📜 Python Files:
   - `rtl_fm_gui.py`

2. 🔌 DLL Files:
   - `librtlsdr.dll`
   - `libusb-1.0.dll`
   - `libwinpthread-1.dll`

## 🚀 Quick Start

1. 📥 Install Python packages:
   ```bash
   pip install numpy scipy sounddevice pyrtlsdr
   ```

2. 🔌 Connect your RTL-SDR device

3. ▶️ Run Khanfar FM:
   ```bash
   python rtl_fm_gui.py
   ```

## 📱 Using Khanfar FM

1. 🎯 Enter frequency (88-108 MHz)
2. 🎚️ Adjust gain if needed
3. ▶️ Click Start to begin reception
4. 🔊 Adjust your system volume
5. 📊 Monitor signal strength

## 🔧 Troubleshooting

### 🔇 No Sound?
- ✔️ Check RTL-SDR connection
- ✔️ Verify frequency input
- ✔️ Try adjusting gain
- ✔️ Check system audio

### ❌ DLL Errors?
- ✔️ Verify all DLLs are in the same folder
- ✔️ Check Python version (32/64 bit)
- ✔️ Try reinstalling drivers

### 📡 Device Not Found?
- ✔️ Check USB connection
- ✔️ Verify driver installation
- ✔️ Try different USB ports

## 🛠️ Technical Details

### Signal Processing
- 📡 Sample Rate: 240kHz
- 🎵 Audio Rate: 32kHz
- 📊 FM Demodulation with optimized algorithms
- 🔊 Real-time audio processing

### Performance
- 💻 Low CPU usage
- 🎯 Minimal latency
- 🔄 Efficient threading model

## 📝 Developer Notes

### Code Structure
```
rtl_fm_gui.py
├── RTLFMReceiver class
│   ├── GUI initialization
│   ├── SDR configuration
│   └── Audio processing
└── Signal processing functions
    ├── FM demodulation
    ├── Sample rate conversion
    └── Audio buffering
```

### Key Components
- 🎛️ RTL-SDR Interface
- 🔄 Sample Processing
- 🔊 Audio Output
- 📊 Signal Analysis

## 📜 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 👨‍💻 Author

Created by Khanfar

## 🙏 Acknowledgments

- RTL-SDR community
- PyRTLSDR developers
- Signal processing contributors

---

<p align="center">
  Made with ❤️ for radio enthusiasts
</p>
