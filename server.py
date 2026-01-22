"""
Combined Flask Server for Lead Qualification and Scheduling Bot
Serves both API endpoints and frontend dashboard
"""

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from database import MongoDBManager
import os
from bson import ObjectId

app = Flask(__name__, static_folder='dashboard/dist', static_url_path='')
CORS(app)

# Initialize MongoDB
try:
    db_manager = MongoDBManager()
    print("[MongoDB Connected - Server Ready]")
except Exception as e:
    print(f"[MongoDB Connection Failed: {e}]")
    db_manager = None

# ============================================================
# API ENDPOINTS
# ============================================================

def normalize_lead(lead):
    """
    Ensure all expected fields exist with default values
    Prevents dashboard crashes from missing data
    """
    # Convert MongoDB _id to string id
    lead['id'] = str(lead.pop('_id', lead.get('id', 'unknown')))
    
    # Ensure basic fields
    lead.setdefault('lead_name', 'N/A')
    lead.setdefault('company_name', 'N/A')
    lead.setdefault('status', 'new')
    lead.setdefault('conversation_transcript', '')
    
    # Ensure contact_info with all subfields
    if 'contact_info' not in lead:
        lead['contact_info'] = {}
    lead['contact_info'].setdefault('phone', 'N/A')
    lead['contact_info'].setdefault('email', 'N/A')
    lead['contact_info'].setdefault('whatsapp', 'N/A')
    
    # Ensure call_metadata with all subfields
    if 'call_metadata' not in lead:
        lead['call_metadata'] = {}
    
    # Convert timestamp to ISO string if it's a datetime
    if 'timestamp' in lead['call_metadata']:
        if isinstance(lead['call_metadata']['timestamp'], datetime):
            lead['call_metadata']['timestamp'] = lead['call_metadata']['timestamp'].isoformat()
    else:
        lead['call_metadata']['timestamp'] = datetime.now().isoformat()
    
    lead['call_metadata'].setdefault('call_outcome', 'not_interested')
    lead['call_metadata'].setdefault('duration_seconds', 0)
    
    # Always add audio_recording_url (empty if no recording)
    recording_id = lead['call_metadata'].get('audio_recording_id')
    if recording_id:
        lead['call_metadata']['audio_recording_url'] = f'/api/audio/{recording_id}'
    else:
        lead['call_metadata']['audio_recording_url'] = ''
    
    # Ensure requirement with all subfields
    if 'requirement' not in lead:
        lead['requirement'] = {}
    lead['requirement'].setdefault('type', 'unknown')
    lead['requirement'].setdefault('capacity', 'N/A')
    lead['requirement'].setdefault('platform_length', 'N/A')
    lead['requirement'].setdefault('installation_type', 'N/A')
    lead['requirement'].setdefault('location', 'N/A')
    lead['requirement'].setdefault('timeline', 'N/A')
    lead['requirement'].setdefault('decision_maker', 'N/A')
    
    # Ensure scheduled_call with all subfields
    if 'scheduled_call' not in lead:
        lead['scheduled_call'] = {}
    lead['scheduled_call'].setdefault('preferred_day', 'N/A')
    lead['scheduled_call'].setdefault('preferred_time', 'N/A')
    lead['scheduled_call'].setdefault('alternate_time', 'N/A')
    lead['scheduled_call'].setdefault('contact_mode', 'phone')
    
    return lead

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db_manager else "disconnected"
    })

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads with optional filters"""
    if not db_manager:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        # Get query parameters
        date_range = request.args.get('date_range', 'all')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        sort = request.args.get('sort', 'newest')
        
        # Build query
        query = {}
        
        # Date range filter
        if date_range != 'all':
            days = 7 if date_range == '7days' else 30
            cutoff_date = datetime.now() - timedelta(days=days)
            query['call_metadata.timestamp'] = {'$gte': cutoff_date}
        
        # Status filter
        if status:
            query['call_metadata.call_outcome'] = status
        
        # Search filter
        if search:
            query['$or'] = [
                {'lead_name': {'$regex': search, '$options': 'i'}},
                {'company_name': {'$regex': search, '$options': 'i'}}
            ]
        
        # Sort order
        sort_order = -1 if sort == 'newest' else 1 if sort == 'oldest' else None
        sort_field = 'call_metadata.timestamp' if sort_order else 'lead_name'
        
        # Fetch leads
        leads_cursor = db_manager.leads_collection.find(query)
        if sort_order:
            leads_cursor = leads_cursor.sort(sort_field, sort_order)
        else:
            leads_cursor = leads_cursor.sort(sort_field, 1)
        
        leads = []
        for lead in leads_cursor:
            normalized_lead = normalize_lead(lead)
            leads.append(normalized_lead)
        
        return jsonify(leads)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leads/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Get a specific lead by ID"""
    if not db_manager:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        lead = db_manager.leads_collection.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return jsonify({"error": "Lead not found"}), 404
        
        normalized_lead = normalize_lead(lead)
        return jsonify(normalized_lead)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics"""
    if not db_manager:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        total_calls = db_manager.leads_collection.count_documents({})
        qualified_calls = db_manager.leads_collection.count_documents({
            'call_metadata.call_outcome': 'qualified'
        })
        
        success_rate = round((qualified_calls / total_calls * 100)) if total_calls > 0 else 0
        
        # Today's calls
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        todays_calls = db_manager.leads_collection.count_documents({
            'call_metadata.timestamp': {'$gte': today_start}
        })
        
        return jsonify({
            "totalCalls": total_calls,
            "successRate": success_rate,
            "todaysCalls": todays_calls
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audio/<recording_id>', methods=['GET'])
def get_audio(recording_id):
    """Stream audio recording"""
    if not db_manager:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        audio_file = db_manager.fs.get(ObjectId(recording_id))
        return send_file(
            audio_file,
            mimetype='audio/wav',
            as_attachment=False,
            download_name=f'recording_{recording_id}.wav'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/export/transcript/<lead_id>', methods=['GET'])
def export_transcript(lead_id):
    """Export conversation transcript"""
    if not db_manager:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        lead = db_manager.leads_collection.find_one({'_id': ObjectId(lead_id)})
        if not lead:
            return jsonify({"error": "Lead not found"}), 404
        
        transcript = lead.get('conversation_transcript', 'No transcript available')
        
        return jsonify({
            "lead_name": lead.get('lead_name'),
            "company_name": lead.get('company_name'),
            "transcript": transcript,
            "timestamp": lead.get('call_metadata', {}).get('timestamp')
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For React Router - serve index.html for all routes
        return send_from_directory(app.static_folder, 'index.html')

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Lead Qualification Combined Server Starting...")
    print("="*60)
    print("API Endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/leads")
    print("  - GET  /api/leads/:id")
    print("  - GET  /api/metrics")
    print("  - GET  /api/audio/:recording_id")
    print("  - GET  /api/export/transcript/:lead_id")
    print("\nFrontend:")
    print("  - Dashboard at http://localhost:5000")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
