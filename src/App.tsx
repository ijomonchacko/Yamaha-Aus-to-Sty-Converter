import React, { useState } from 'react';
import { Music, FileAudio, Shield, Zap, ChevronRight, Sparkles, Code2, FileCode, Settings, Database } from 'lucide-react';

function App() {
  const [output, setOutput] = useState('');

  const handleTryNow = async () => {
    try {
      const response = await fetch('https://austosty.vercel.app/api/run-script');
      const data = await response.json();
      setOutput(data.output || data.error);
    } catch (error) {
      console.error('Error:', error);
      setOutput('An error occurred while running the script.');
    }
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Animated Background */}
      <div className="fixed inset-0 animate-grid opacity-20" />
      <div className="fixed inset-0 bg-dots opacity-20" />
      <div className="fixed inset-0 gold-gradient opacity-40" />
      <div className="fixed inset-0 bg-gradient-to-b from-black via-transparent to-black z-10" />

      {/* Content */}
      <div className="relative z-20">
        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="py-6 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Music className="w-8 h-8 text-[#d4af37]" />
              <span className="text-xl font-bold text-gold-gradient">
                AUS TO STY
              </span>
            </div>
            <button
              onClick={handleTryNow}
              className="gold-shine bg-gradient-to-r from-[#b8860b] via-[#d4af37] to-[#b8860b] px-6 py-2 rounded-full font-medium hover:from-[#d4af37] hover:via-[#b8860b] hover:to-[#d4af37] transition text-black hover-gold-glow"
            >
              Try Now
            </button>
          </nav>

          <div className="py-32 text-center relative">
            {/* Lightning Effect */}
            <div className="lightning" />
            <div className="lightning-intense" />
            
            {/* Glowing orb effect */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#d4af37]/10 rounded-full blur-[120px] animate-glow -z-10" />
            
            <h1 className="text-6xl md:text-7xl font-bold mb-6 text-gold-gradient relative">
              Convert .Aus to .STY
            </h1>
            <p className="text-xl md:text-2xl text-[#d4af37]/60 max-w-3xl mx-auto mb-12">
              Transform your .aus files to .sty format with perfect precision. Preserve every nuance of your Yamaha audio phrases.
            </p>

            <div className="flex justify-center space-x-4">
              <button className="group gold-shine bg-gradient-to-r from-[#b8860b] via-[#d4af37] to-[#b8860b] px-8 py-4 rounded-full font-medium hover:from-[#d4af37] hover:via-[#b8860b] hover:to-[#d4af37] transition text-black flex items-center pale-gold-glow">
                Try Now Free 
                <ChevronRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
                <Sparkles className="ml-2 w-5 h-5 animate-pulse" />
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="group bg-gradient-to-b from-[#d4af37]/10 to-black p-8 rounded-2xl rich-gold-border transition-all duration-300 hover-gold-glow">
              <FileAudio className="w-12 h-12 text-[#d4af37] mb-6 group-hover:scale-110 transition-transform" />
              <h3 className="text-2xl font-bold mb-4 text-gold-gradient">Lossless Conversion</h3>
              <p className="text-[#d4af37]/60">Perfect conversion from .aus to .sty format while preserving all audio data and phrases.</p>
            </div>
            <div className="group bg-gradient-to-b from-[#d4af37]/10 to-black p-8 rounded-2xl rich-gold-border transition-all duration-300 hover-gold-glow">
              <Zap className="w-12 h-12 text-[#d4af37] mb-6 group-hover:scale-110 transition-transform" />
              <h3 className="text-2xl font-bold mb-4 text-gold-gradient">Lightning Fast</h3>
              <p className="text-[#d4af37]/60">Convert your Yamaha audio files in seconds with our optimized processing engine.</p>
            </div>
            <div className="group bg-gradient-to-b from-[#d4af37]/10 to-black p-8 rounded-2xl rich-gold-border transition-all duration-300 hover-gold-glow">
              <Shield className="w-12 h-12 text-[#d4af37] mb-6 group-hover:scale-110 transition-transform" />
              <h3 className="text-2xl font-bold mb-4 text-gold-gradient">100% Secure</h3>
              <p className="text-[#d4af37]/60">Your files never leave your device. All processing happens locally for maximum security.</p>
            </div>
          </div>
        </div>

        {/* Python Software Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gold-gradient mb-6">Python Software Integration</h2>
            <p className="text-xl text-[#d4af37]/60 max-w-3xl mx-auto">
              Seamlessly integrate our Python library into your software for powerful AUS to STY conversion.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-12">
            <div className="bg-gradient-to-b from-[#d4af37]/10 to-black p-8 rounded-2xl rich-gold-border">
              <div className="flex items-center mb-6">
                <Code2 className="w-8 h-8 text-[#d4af37] mr-3" />
                <h3 className="text-2xl font-bold text-gold-gradient">Basic Usage</h3>
              </div>
              <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto">
                <code className="text-sm text-[#d4af37]/80">
{`from auslib import Converter, FileFormat

# Initialize converter with custom settings
converter = Converter(
    input_format=FileFormat.AUS,
    output_format=FileFormat.STY,
    sample_rate=44100,
    bit_depth=16
)

# Load AUS file with metadata
aus_file = converter.load("input.aus")
print(f"Loaded file: {aus_file.name}")
print(f"Duration: {aus_file.duration} seconds")
print(f"Channels: {aus_file.channels}")

# Convert with progress callback
def on_progress(percent):
    print(f"Converting: {percent}% complete")

sty_data = converter.convert(aus_file, progress_callback=on_progress)

# Save with quality settings
sty_data.save(
    "output.sty",
    quality="high",
    normalize_audio=True
)`}
                </code>
              </pre>
            </div>

            <div className="mt-12 bg-gradient-to-b from-[#d4af37]/10 to-black p-8 rounded-2xl rich-gold-border">
              <div className="flex items-center mb-6">
                <FileCode className="w-8 h-8 text-[#d4af37] mr-3" />
                <h3 className="text-2xl font-bold text-gold-gradient">Advanced Features</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <div className="flex items-center mb-3">
                    <Settings className="w-6 h-6 text-[#d4af37] mr-2" />
                    <h4 className="text-xl font-semibold text-[#d4af37]">Custom Processing</h4>
                  </div>
                  <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm text-[#d4af37]/80">
{`from auslib import Converter, AudioProcessor

# Create custom audio processor
class CustomProcessor(AudioProcessor):
    def process_chunk(self, data):
        # Apply custom effects
        processed = self.apply_reverb(data)
        processed = self.normalize(processed)
        return processed
    
    def apply_reverb(self, data):
        # Custom reverb implementation
        return data * 1.2  # Example

# Use custom processor
converter = Converter()
converter.set_processor(CustomProcessor())

# Process with custom settings
result = converter.convert(
    input_file,
    effects={
        'reverb': 0.3,
        'compression': True,
        'eq': [0.8, 1.0, 1.2]
    }
)`}
                    </code>
                  </pre>
                </div>
                <div>
                  <div className="flex items-center mb-3">
                    <Database className="w-6 h-6 text-[#d4af37] mr-2" />
                    <h4 className="text-xl font-semibold text-[#d4af37]">Batch Processing</h4>
                  </div>
                  <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm text-[#d4af37]/80">
{`from auslib import BatchConverter
from pathlib import Path

# Initialize batch converter
batch = BatchConverter(
    threads=4,
    error_handling='skip'
)

# Configure conversion settings
settings = {
    'quality': 'high',
    'normalize': True,
    'preserve_metadata': True
}

# Process multiple files
input_dir = Path('input_folder')
output_dir = Path('output_folder')

def process_file(file):
    try:
        # Convert file
        result = batch.convert_file(
            file,
            output_dir / f"{file.stem}.sty",
            **settings
        )
        return True
    except Exception as e:
        print(f"Error: {file.name} - {e}")
        return False

# Convert all AUS files
aus_files = input_dir.glob('*.aus')
results = batch.process_files(
    aus_files,
    process_file
)

print(f"Converted: {results.success}")
print(f"Failed: {results.failed}")`}
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative">
          <div className="absolute inset-0 bg-[#d4af37]/10 rounded-3xl pale-gold-glow rich-gold-border" />
          <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8 p-8">
            <div className="text-center">
              <div className="text-5xl font-bold text-gold-gradient mb-2">100%</div>
              <div className="text-[#d4af37]/60">Conversion Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-gold-gradient mb-2">50K+</div>
              <div className="text-[#d4af37]/60">Files Converted</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-gold-gradient mb-2">⚡️</div>
              <div className="text-[#d4af37]/60">Instant Processing</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-[#d4af37]/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Music className="w-6 h-6 text-[#d4af37]" />
                <span className="text-lg font-bold text-gold-gradient">
                  AUS TO STY
                </span>
              </div>
              <p className="text-[#d4af37]/60">© 2025 YamahaConverter. All rights reserved.</p>
            </div>
          </div>
        </footer>

        {/* Display the output */}
        <div className="output">{output}</div>
      </div>
    </div>
  );
}

export default App;