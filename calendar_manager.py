"""
Microsoft Outlook Calendar Manager for SquadStack Sales Bot
Handles automatic scheduling, availability checking, and round-robin assignment
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv

load_dotenv()

class OutlookCalendarManager:
    """Manages Microsoft Outlook calendar integration for sales executive scheduling"""
    
    def __init__(self):
        """Initialize Microsoft Graph API client"""
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")
        self.bot_email = os.getenv("BOT_EMAIL")
        
        if not all([self.client_id, self.tenant_id, self.bot_email]):
            raise ValueError("Missing Microsoft credentials in .env file")
        
        # Token cache file
        self.cache_file = "msal_token_cache.json"
        self.cache = SerializableTokenCache()
        
        # Load existing cache if available
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                self.cache.deserialize(f.read())
        
        # MSAL public client for device code flow (delegated permissions)
        # Supports any Microsoft account, not just tenant users
        self.authority = "https://login.microsoftonline.com/common"
        self.app = PublicClientApplication(
            self.client_id,
            authority=self.authority,
            token_cache=self.cache
        )
        
        # Microsoft Graph API endpoint
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # Sales executive email addresses (configure these)
        self.sales_executives = self._load_executives()
        
        # Track last assigned executive for round-robin
        self.last_assigned_index = -1
        
        # Cached access token for bot account
        self._bot_token = None
    
    def _load_executives(self) -> List[Dict]:
        """
        Load sales executive details from environment or config
        
        Format:
        SALES_EXECUTIVES=email1@domain.com:Name1,email2@domain.com:Name2
        """
        execs_str = os.getenv("SALES_EXECUTIVES", "")
        if not execs_str:
            # Default fallback - replace with actual emails
            return [
                {"email": "exec1@yourdomain.com", "name": "Sales Executive 1"},
                {"email": "exec2@yourdomain.com", "name": "Sales Executive 2"},
            ]
        
        executives = []
        for exec_data in execs_str.split(","):
            email, name = exec_data.split(":")
            executives.append({"email": email.strip(), "name": name.strip()})
        
        return executives
    
    def get_access_token(self, user_email: str = None) -> Optional[str]:
        """
        Get access token for Microsoft Graph API
        Uses delegated permissions with device code flow (any Microsoft account)
        
        Args:
            user_email: Optional - if None, uses bot_email for authentication
        """
        # Use bot email if no specific user provided
        if user_email is None:
            user_email = self.bot_email
        
        # Return cached bot token if requesting bot email
        if user_email == self.bot_email and self._bot_token:
            return self._bot_token
        
        try:
            scopes = [
                "https://graph.microsoft.com/Calendars.ReadWrite",
                "https://graph.microsoft.com/User.Read"
            ]
            
            # Try to get cached token first
            accounts = self.app.get_accounts()
            if accounts:
                result = self.app.acquire_token_silent(scopes, account=accounts[0])
                if result and "access_token" in result:
                    token = result["access_token"]
                    # Cache bot token
                    if user_email == self.bot_email:
                        self._bot_token = token
                    # Save cache to file
                    self._save_cache()
                    return token
            
            # If no cached token, use device code flow (interactive)
            flow = self.app.initiate_device_flow(scopes=scopes)
            
            if "user_code" not in flow:
                print(f"[Calendar Auth Error: Failed to create device flow]")
                return None
            
            # Show auth instructions
            print(f"\n[Calendar Authentication Required]")
            print(f"[To authorize calendar access:]")
            print(f"[1. Go to: {flow['verification_uri']}")
            print(f"[2. Enter code: {flow['user_code']}")
            print(f"[3. Sign in with Microsoft account: {user_email}]")
            print(f"[Waiting for authentication...]")
            
            # Wait for user to complete authentication
            result = self.app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                print(f"[✅ Authentication successful for {user_email}]")
                token = result["access_token"]
                # Cache bot token
                if user_email == self.bot_email:
                    self._bot_token = token
                # Save cache to file
                self._save_cache()
                return token
            else:
                error = result.get("error_description", "Unknown error")
                print(f"[Calendar Auth Error: {error}]")
                return None
                
        except Exception as e:
            print(f"[Calendar Auth Exception: {e}]")
            return None
    
    def _save_cache(self):
        """Save token cache to file"""
        if self.cache.has_state_changed:
            with open(self.cache_file, "w") as f:
                f.write(self.cache.serialize())
    
    def check_availability(self, email: str, start_time: datetime, end_time: datetime) -> bool:
        """
        Check if a sales executive is available during the specified time
        Note: This checks the BOT's calendar for events with this executive
        
        Args:
            email: Sales executive's email
            start_time: Proposed meeting start time
            end_time: Proposed meeting end time
        
        Returns:
            True if available, False if busy
        """
        # Use bot's token to check bot's calendar
        token = self.get_access_token(self.bot_email)
        if not token:
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Use /me/calendar to check bot's calendar for conflicts
        url = f"{self.graph_url}/me/calendar/calendarView"
        params = {
            "startDateTime": start_time.isoformat(),
            "endDateTime": end_time.isoformat()
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                events = response.json().get("value", [])
                # Check if any events have this executive as attendee
                for event in events:
                    attendees = event.get("attendees", [])
                    for attendee in attendees:
                        if attendee.get("emailAddress", {}).get("address", "").lower() == email.lower():
                            return False  # Executive already has a meeting
                # No conflicts found
                return True
            else:
                print(f"[Calendar Check Error: {response.status_code}]")
                return False
        except Exception as e:
            print(f"[Calendar Check Exception: {e}]")
            return False
    
    def find_available_executive(self, start_time: datetime, end_time: datetime) -> Optional[Dict]:
        """
        Find the next available sales executive using round-robin
        
        Args:
            start_time: Proposed meeting start time
            end_time: Proposed meeting end time
        
        Returns:
            Executive dict with email and name, or None if none available
        """
        num_execs = len(self.sales_executives)
        
        # Try each executive starting from the next in rotation
        for i in range(num_execs):
            index = (self.last_assigned_index + 1 + i) % num_execs
            exec_info = self.sales_executives[index]
            
            if self.check_availability(exec_info["email"], start_time, end_time):
                self.last_assigned_index = index
                return exec_info
        
        # No one available
        return None
    
    def create_calendar_event(
        self,
        executive_email: str,
        lead_name: str,
        company_name: str,
        phone: str,
        requirements: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[str]:
        """
        Create a calendar event and send email reminder (not meeting invite)
        
        Args:
            executive_email: Sales executive's email (receives reminder)
            lead_name: Name of the lead
            company_name: Lead's company
            phone: Lead's phone number
            requirements: Brief requirements summary
            start_time: Call start time
            end_time: Call end time
        
        Returns:
            Event ID if successful, None otherwise
        """
        # Use bot's token to create event in bot's calendar
        token = self.get_access_token(self.bot_email)
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create calendar event (without attendees - just marks calendar)
        event_body = {
            "subject": f"Call: {lead_name} - {phone}",
            "body": {
                "contentType": "HTML",
                "content": f"""
                <h3>📞 Telephonic Sales Call Scheduled</h3>
                <p><strong>Lead Name:</strong> {lead_name}</p>
                <p><strong>Phone Number:</strong> {phone}</p>
                <p><strong>Company:</strong> {company_name}</p>
                <hr>
                <p>📊 <strong>View full lead details on the dashboard</strong></p>
                <p><em>This is a telephonic call - check dashboard for complete requirements and notes</em></p>
                """
            },
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "location": {
                "displayName": f"Telephonic Call: {phone}"
            },
            "isReminderOn": True,
            "reminderMinutesBeforeStart": 15,
            "categories": ["Sales Call", "Lead Qualification Bot"]
        }
        
        # Create event in bot's calendar
        url = f"{self.graph_url}/me/calendar/events"
        
        try:
            response = requests.post(url, headers=headers, json=event_body)
            if response.status_code == 201:
                event = response.json()
                event_id = event.get("id")
                print(f"[Calendar event created: {event_id}]")
                
                # Send email reminder (not meeting invite)
                self._send_email_reminder(executive_email, lead_name, phone, company_name, start_time, token)
                
                return event_id
            else:
                print(f"[Calendar Event Error: {response.status_code} - {response.text}]")
                return None
        except Exception as e:
            print(f"[Calendar Event Exception: {e}]")
            return None
    
    def _send_email_reminder(self, executive_email: str, lead_name: str, phone: str, 
                            company_name: str, scheduled_time: datetime, token: str):
        """Send email reminder about calendar event (not meeting invitation)"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            email_body = {
                "message": {
                    "subject": f"📅 Call Scheduled: {lead_name} - {phone}",
                    "body": {
                        "contentType": "HTML",
                        "content": f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                            <h2 style="color: #2c5aa0;">📞 New Telephonic Call Scheduled</h2>
                            
                            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p style="margin: 5px 0;"><strong>Lead Name:</strong> {lead_name}</p>
                                <p style="margin: 5px 0;"><strong>Phone Number:</strong> <a href="tel:{phone}">{phone}</a></p>
                                <p style="margin: 5px 0;"><strong>Company:</strong> {company_name}</p>
                                <p style="margin: 5px 0;"><strong>Scheduled Time:</strong> {scheduled_time.strftime('%B %d, %Y at %I:%M %p IST')}</p>
                            </div>
                            
                            <p><strong>✅ Event marked on your calendar</strong></p>
                            
                            <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0;">
                                <p style="margin: 0;"><strong>📊 For complete lead details:</strong></p>
                                <p style="margin: 5px 0;">Visit the <strong>Lead Qualification Dashboard</strong> to view full requirements, conversation history, and call recording.</p>
                            </div>
                            
                            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                                <em>This is an automated reminder from Lead Qualification Bot. This is not a meeting invitation - it's a reminder for a telephonic call.</em>
                            </p>
                        </body>
                        </html>
                        """
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": executive_email
                            }
                        }
                    ]
                },
                "saveToSentItems": False
            }
            
            url = f"{self.graph_url}/me/sendMail"
            response = requests.post(url, headers=headers, json=email_body)
            
            if response.status_code == 202:
                print(f"[✅ Email reminder sent to {executive_email}]")
            else:
                print(f"[⚠️ Email send status: {response.status_code}]")
                
        except Exception as e:
            print(f"[Email reminder error: {e}]")
    
    def schedule_sales_call(
        self,
        lead_data: Dict,
        preferred_day: str,
        preferred_time: str
    ) -> Optional[Dict]:
        """
        Automatically schedule a sales call with round-robin assignment
        
        Args:
            lead_data: Lead information dict
            preferred_day: Day preference (e.g., "tomorrow", "Monday")
            preferred_time: Time window (e.g., "11AM-12PM")
        
        Returns:
            Dict with executive_email, executive_name, event_id if successful
        """
        # Parse time preference
        start_time, end_time = self._parse_time_preference(preferred_day, preferred_time)
        if not start_time or not end_time:
            print(f"[Could not parse time: {preferred_day} {preferred_time}]")
            return None
        
        # Find available executive
        executive = self.find_available_executive(start_time, end_time)
        if not executive:
            print("[No executives available at this time]")
            return None
        
        # Prepare requirements summary
        requirements = f"""
        Capacity: {lead_data.get('capacity_tons', 'N/A')}
        Vehicle Type: {lead_data.get('vehicle_type', 'N/A')}
        Location: {lead_data.get('site_city', 'N/A')}
        Timeline: {lead_data.get('timeline', 'N/A')}
        """
        
        # Create calendar event
        event_id = self.create_calendar_event(
            executive["email"],
            lead_data.get("lead_name", "Unknown"),
            lead_data.get("company_name", ""),
            lead_data.get("phone_number", ""),
            requirements,
            start_time,
            end_time
        )
        
        if event_id:
            return {
                "executive_email": executive["email"],
                "executive_name": executive["name"],
                "event_id": event_id,
                "scheduled_time": start_time.isoformat()
            }
        
        return None
    
    def _parse_time_preference(self, day: str, time_window: str) -> tuple:
        """
        Parse natural language time preference into datetime objects with current date context
        
        Args:
            day: "today", "tomorrow", "23rd January", "next Monday", etc.
            time_window: "11AM-12PM", "11 AM to 12 PM", "2PM-3PM", etc.
        
        Returns:
            (start_time, end_time) tuple of datetime objects in IST
        
        Examples:
            - "tomorrow" with "11AM-12PM" on Jan 22, 2026 → Jan 23, 2026 11:00-12:00 IST
            - "today" with "2PM-3PM" → Same day 14:00-15:00 IST
        """
        try:
            # Current date context (IST)
            from datetime import timezone, timedelta as td
            ist = timezone(td(hours=5, minutes=30))
            now = datetime.now(ist)
            
            day_lower = day.lower().strip()
            
            # Parse day relative to current date
            if "today" in day_lower or "now" in day_lower:
                target_date = now.date()
                print(f"[Parsed 'today' as {target_date}]")
            elif "tomorrow" in day_lower:
                target_date = (now + timedelta(days=1)).date()
                print(f"[Parsed 'tomorrow' as {target_date}]")
            elif "day after" in day_lower or "overmorrow" in day_lower:
                target_date = (now + timedelta(days=2)).date()
                print(f"[Parsed 'day after tomorrow' as {target_date}]")
            else:
                # Default to next day if unclear
                target_date = (now + timedelta(days=1)).date()
                print(f"[Defaulted to tomorrow: {target_date}]")
            
            # Parse time window - support multiple formats
            time_window = time_window.upper().replace(" ", "").replace("TO", "-")
            time_parts = time_window.split("-")
            
            if len(time_parts) != 2:
                print(f"[Invalid time format: {time_window}]")
                return None, None
            
            start_hour = self._parse_time_string(time_parts[0])
            end_hour = self._parse_time_string(time_parts[1])
            
            if start_hour is None or end_hour is None:
                print(f"[Could not parse hours: {time_parts}]")
                return None, None
            
            # Create datetime objects in IST
            start_time = datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour, tzinfo=ist)
            end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=end_hour, tzinfo=ist)
            
            print(f"[Scheduled: {start_time.strftime('%d %b %Y %I:%M %p')} - {end_time.strftime('%I:%M %p')} IST]")
            return start_time, end_time
        
        except Exception as e:
            print(f"[Time parsing error: {e}]")
            return None, None
    
    def _parse_time_string(self, time_str: str) -> Optional[int]:
        """Parse time string like '11AM' or '2PM' to hour (24-hour format)"""
        try:
            time_str = time_str.upper().strip()
            if "AM" in time_str:
                hour = int(time_str.replace("AM", ""))
                return hour if hour != 12 else 0
            elif "PM" in time_str:
                hour = int(time_str.replace("PM", ""))
                return hour + 12 if hour != 12 else 12
            else:
                return int(time_str)
        except:
            return None
