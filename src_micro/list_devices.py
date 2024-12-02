import sounddevice as sd

# List all available audio devices
devices = sd.query_devices()

# Print device information
for i, device in enumerate(devices):
    print(f"Device {i}: {device['name']}")
    print(f"  Input Channels: {device['max_input_channels']}")
    print(f"  Output Channels: {device['max_output_channels']}")
    print(f"  Default Sample Rate: {device['default_samplerate']}")
    print("-" * 40)
