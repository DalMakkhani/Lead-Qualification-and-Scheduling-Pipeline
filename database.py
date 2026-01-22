"""
MongoDB Database Manager for SquadStack Sales Bot
Handles lead data storage, conversation logging, and call scheduling
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import gridfs
from dotenv import load_dotenv

load_dotenv()

class MongoDBManager:
    """Manages MongoDB Atlas connection and operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        # Connection string from environment or direct
        mongo_uri = os.getenv("MONGODB_URI", 
            "mongodb+srv://arjun_mirabballi:F22_raptor@salesbot.qmaynew.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")
        
        try:
            self.client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=5000,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            # Test connection
            self.client.admin.command('ping')
            print("[MongoDB Connected]")
            
            # Database and collections
            self.db = self.client["lead_qualification_db"]
            self.leads_collection = self.db["leads"]
            self.conversations_collection = self.db["conversations"]
            self.scheduled_calls_collection = self.db["scheduled_calls"]
            
            # GridFS for storing audio recordings
            self.fs = gridfs.GridFS(self.db)
            
            # Create indexes for better query performance
            self._create_indexes()
            
            # Initialize calendar manager (lazy import to avoid circular dependency)
            self.calendar_manager = None
            
        except (ConnectionFailure, OperationFailure) as e:
            print(f"[MongoDB Connection Failed: {e}]")
            raise
    
    def _init_calendar_manager(self):
        """Lazy initialization of calendar manager"""
        if self.calendar_manager is None:
            try:
                from calendar_manager import OutlookCalendarManager
                self.calendar_manager = OutlookCalendarManager()
                print("[Calendar manager initialized]")
            except Exception as e:
                print(f"[Calendar manager initialization failed: {e}]")
                # Continue without calendar integration
        return self.calendar_manager
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index on lead name for quick lookups
            self.leads_collection.create_index("lead_name")
            # Index on timestamp for chronological queries
            self.conversations_collection.create_index("timestamp")
            # Index on scheduled call time
            self.scheduled_calls_collection.create_index("scheduled_time")
        except Exception as e:
            print(f"[Index creation warning: {e}]")
    
    def store_lead(self, lead_data: Dict, conversation_history: List[Dict], 
                   audio_file_path: Optional[str] = None) -> str:
        """
        Store or update lead information with full conversation history and call recording
        
        Args:
            lead_data: Qualification data extracted from conversation (JSON)
            conversation_history: Full chat history (list of role/content dicts)
            audio_file_path: Path to WAV recording of the call (optional)
        
        Returns:
            MongoDB document ID
        """
        try:
            lead_name = lead_data.get("lead_name", "unknown_lead")
            
            # Store audio recording in GridFS if provided
            audio_file_id = None
            if audio_file_path and os.path.exists(audio_file_path):
                try:
                    with open(audio_file_path, "rb") as audio_file:
                        audio_file_id = self.fs.put(
                            audio_file,
                            filename=f"{lead_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.wav",
                            content_type="audio/wav",
                            metadata={
                                "lead_name": lead_name,
                                "timestamp": datetime.utcnow()
                            }
                        )
                    print(f"[Call recording stored: {audio_file_id}]")
                except Exception as e:
                    print(f"[Audio upload warning: {e}]")
            
            # Prepare document
            document = {
                "lead_name": lead_name,
                "company_name": lead_data.get("company_name", ""),
                "contact_info": {
                    "phone": lead_data.get("phone_number", ""),
                    "email": lead_data.get("email", ""),
                    "whatsapp": lead_data.get("whatsapp_number", "")
                },
                "requirement": {
                    "type": lead_data.get("requirement_type", ""),
                    "capacity": lead_data.get("capacity", ""),
                    "platform_length": lead_data.get("platform_length", ""),
                    "installation_type": lead_data.get("installation_type", ""),
                    "location": lead_data.get("location", ""),
                    "timeline": lead_data.get("timeline", "")
                },
                "qualification_data": lead_data,  # Full JSON
                "conversation_transcript": self._format_transcript(conversation_history),
                "conversation_history": conversation_history,  # Raw history
                "call_metadata": {
                    "timestamp": datetime.utcnow(),
                    "call_outcome": lead_data.get("call_outcome", "qualified"),
                    "duration_seconds": lead_data.get("call_duration", 0),
                    "audio_recording_id": str(audio_file_id) if audio_file_id else None
                },
                "scheduled_call": {
                    "preferred_day": lead_data.get("preferred_day", ""),
                    "preferred_time": lead_data.get("preferred_time_window", ""),
                    "alternate_time": lead_data.get("alternate_time_window", "")
                },
                "status": "new",
                "last_updated": datetime.utcnow()
            }
            
            # Upsert: update if exists, insert if new
            result = self.leads_collection.update_one(
                {"lead_name": lead_name},
                {"$set": document},
                upsert=True
            )
            
            doc_id = str(result.upserted_id) if result.upserted_id else "updated"
            print(f"[Lead stored in MongoDB: {lead_name}]")
            
            # Auto-schedule calendar event if lead wants a call
            self._auto_schedule_calendar(lead_name, lead_data, document)
            
            return doc_id
            
        except Exception as e:
            print(f"[MongoDB store error: {e}]")
            raise
    
    def _format_transcript(self, conversation_history: List[Dict]) -> str:
        """Convert conversation history to readable transcript"""
        transcript = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "system":
                continue  # Skip system prompt
            elif role == "assistant":
                transcript.append(f"Priya: {content}")
            elif role == "user":
                transcript.append(f"Lead: {content}")
        
        return "\n\n".join(transcript)
    
    def store_conversation(self, lead_name: str, conversation_history: List[Dict], 
                          call_outcome: str = "completed") -> str:
        """
        Store standalone conversation log
        
        Args:
            lead_name: Name of the lead
            conversation_history: Full chat history
            call_outcome: Result of call (completed, dropped, rescheduled, etc)
        
        Returns:
            MongoDB document ID
        """
        try:
            document = {
                "lead_name": lead_name,
                "timestamp": datetime.utcnow(),
                "conversation_history": conversation_history,
                "transcript": self._format_transcript(conversation_history),
                "call_outcome": call_outcome,
                "message_count": len([m for m in conversation_history if m["role"] != "system"])
            }
            
            result = self.conversations_collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"[Conversation storage error: {e}]")
            return ""
    
    def schedule_call(self, lead_name: str, scheduled_data: Dict) -> str:
        """
        Store scheduled sales executive call
        
        Args:
            lead_name: Name of the lead
            scheduled_data: Dict with preferred_day, preferred_time_window, etc
        
        Returns:
            MongoDB document ID
        """
        try:
            document = {
                "lead_name": lead_name,
                "scheduled_time": scheduled_data.get("preferred_time_window", ""),
                "scheduled_day": scheduled_data.get("preferred_day", ""),
                "alternate_time": scheduled_data.get("alternate_time_window", ""),
                "contact_mode": scheduled_data.get("contact_mode", "phone"),
                "created_at": datetime.utcnow(),
                "status": "pending"
            }
            
            result = self.scheduled_calls_collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"[Schedule storage error: {e}]")
            return ""
    
    def get_lead(self, lead_name: str) -> Optional[Dict]:
        """Retrieve lead by name"""
        try:
            return self.leads_collection.find_one({"lead_name": lead_name})
        except Exception as e:
            print(f"[Lead retrieval error: {e}]")
            return None
    
    def get_all_leads(self, limit: int = 100) -> List[Dict]:
        """Get all leads (most recent first)"""
        try:
            return list(self.leads_collection.find().sort("last_updated", -1).limit(limit))
        except Exception as e:
            print(f"[Leads retrieval error: {e}]")
            return []
    
    def get_pending_calls(self) -> List[Dict]:
        """Get all pending sales executive calls"""
        try:
            return list(self.scheduled_calls_collection.find({"status": "pending"}))
        except Exception as e:
            print(f"[Pending calls retrieval error: {e}]")
            return []
    
    def _auto_schedule_calendar(self, lead_name: str, lead_data: Dict, document: Dict):
        """
        Automatically schedule Outlook calendar event if lead wants a call
        
        Args:
            lead_name: Lead's name
            lead_data: Raw qualification data
            document: MongoDB document being stored
        """
        try:
            # Check if lead scheduled a call
            preferred_day = lead_data.get("preferred_day", "")
            preferred_time = lead_data.get("preferred_time_window", "")
            
            if not preferred_day or not preferred_time:
                return  # No scheduling needed
            
            # Initialize calendar manager
            calendar_mgr = self._init_calendar_manager()
            if not calendar_mgr:
                print("[Calendar integration unavailable, skipping auto-schedule]")
                return
            
            print(f"[Auto-scheduling calendar event for {lead_name}...]")
            
            # Schedule the call
            result = calendar_mgr.schedule_sales_call(
                lead_data,
                preferred_day,
                preferred_time
            )
            
            if result:
                print(f"[✅ Calendar event created]")
                print(f"   Executive: {result['executive_name']}")
                print(f"   Time: {result['scheduled_time']}")
                
                # Update lead document with assignment
                self.leads_collection.update_one(
                    {"lead_name": lead_name},
                    {"$set": {
                        "assigned_executive": {
                            "name": result['executive_name'],
                            "email": result['executive_email'],
                            "calendar_event_id": result['event_id'],
                            "assigned_at": datetime.utcnow()
                        }
                    }}
                )
                
                # Store in scheduled_calls collection
                self.scheduled_calls_collection.insert_one({
                    "lead_name": lead_name,
                    "executive_name": result['executive_name'],
                    "executive_email": result['executive_email'],
                    "calendar_event_id": result['event_id'],
                    "scheduled_time": result['scheduled_time'],
                    "preferred_day": preferred_day,
                    "preferred_time": preferred_time,
                    "created_at": datetime.utcnow(),
                    "status": "scheduled"
                })
                
                print(f"[📧 Meeting invite sent to {result['executive_email']}]")
            else:
                print("[⚠️ No executives available, call not auto-scheduled]")
        
        except Exception as e:
            print(f"[Auto-schedule error: {e}]")
            # Continue without crashing - calendar integration is optional
    
    def get_call_recording(self, audio_file_id: str, output_path: str) -> bool:
        """
        Download call recording from GridFS
        
        Args:
            audio_file_id: GridFS file ID
            output_path: Local path to save the audio file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from bson import ObjectId
            file_data = self.fs.get(ObjectId(audio_file_id))
            with open(output_path, "wb") as f:
                f.write(file_data.read())
            print(f"[Recording downloaded: {output_path}]")
            return True
        except Exception as e:
            print(f"[Recording download error: {e}]")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[MongoDB Connection Closed]")
