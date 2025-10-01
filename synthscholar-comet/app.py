from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import logging
from datetime import datetime
from comet_automation import CometAutomation, MockCometAutomation
from utils.content_synthesizer import ContentSynthesizer
from utils.audio_generator import AudioGenerator
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
comet_automation = MockCometAutomation()  # Using mock for reliable demo
content_synthesizer = ContentSynthesizer()
audio_generator = AudioGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "mode": "demo" if Config.DEMO_MODE else "production"
    })

@app.route('/api/initialize-comet', methods=['POST'])
def initialize_comet():
    """Initialize COMET browser session"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        logger.info("🔄 Initializing COMET browser...")
        
        # For demo, we'll simulate initialization
        if Config.DEMO_MODE:
            return jsonify({
                "success": True,
                "message": "COMET browser initialized in demo mode",
                "demo_mode": True
            })
        
        # Real initialization (commented for demo)
        # if not comet_automation.initialize_browser():
        #     return jsonify({"error": "Failed to initialize browser"}), 500
        
        # if not comet_automation.login_to_comet(email, password):
        #     return jsonify({"error": "COMET login failed"}), 500
        
        return jsonify({
            "success": True,
            "message": "COMET browser initialized successfully"
        })
        
    except Exception as e:
        logger.error(f"❌ COMET initialization error: {str(e)}")
        return jsonify({"error": "COMET initialization failed"}), 500

@app.route('/api/research', methods=['POST'])
def create_research_podcast():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        if len(topic) < 3:
            return jsonify({"error": "Topic too short"}), 400
        
        logger.info(f"🎯 Processing research topic: {topic}")
        
        # Step 1: Research with COMET Browser
        logger.info("🔍 Starting COMET research...")
        research_data = comet_automation.research_topic(topic)
        
        if not research_data:
            return jsonify({"error": "Research failed. Please try a different topic."}), 500
        
        # Step 2: Synthesize content
        logger.info("✍️ Synthesizing podcast script...")
        podcast_script = content_synthesizer.create_podcast_script(topic, research_data)
        
        if not podcast_script:
            return jsonify({"error": "Content synthesis failed."}), 500
        
        # Step 3: Generate audio
        logger.info("🔊 Generating audio podcast...")
        audio_file_path = audio_generator.text_to_speech(podcast_script, topic)
        
        if not audio_file_path:
            return jsonify({"error": "Audio generation failed."}), 500
        
        # Return success response
        return jsonify({
            "success": True,
            "audio_url": f"/api/download/{os.path.basename(audio_file_path)}",
            "script_preview": podcast_script[:400] + "..." if len(podcast_script) > 400 else podcast_script,
            "topic": topic,
            "research_summary": f"Researched {len(research_data)} key aspects",
            "script_length": len(podcast_script),
            "demo_mode": True
        })
        
    except Exception as e:
        logger.error(f"❌ Research podcast error: {str(e)}")
        return jsonify({"error": "Internal server error. Please try again."}), 500

@app.route('/api/download/<filename>')
def download_audio(filename):
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            safe_topic = "research_podcast"
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"synthscholar_{safe_topic}.mp3",
                mimetype="audio/mpeg"
            )
        else:
            return jsonify({"error": "Audio file not found"}), 404
            
    except Exception as e:
        logger.error(f"❌ Download error: {str(e)}")
        return jsonify({"error": "Download failed"}), 500

@app.route('/api/demo-topics')
def get_demo_topics():
    """Get list of demo topics"""
    return jsonify({
        "topics": [
            {"id": "ai", "name": "Artificial Intelligence", "description": "AI benefits and challenges"},
            {"id": "climate", "name": "Climate Change Solutions", "description": "Renewable energy and sustainability"},
            {"id": "quantum", "name": "Quantum Computing", "description": "Next-gen computing revolution"},
            {"id": "biotech", "name": "Biotechnology", "description": "Medical and agricultural advances"}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting SynthScholar Server...")
    print("📍 Access at: http://localhost:5000")
    print("🎭 Running in DEMO MODE - Using pre-researched data")
    app.run(debug=True, host='0.0.0.0', port=5000)