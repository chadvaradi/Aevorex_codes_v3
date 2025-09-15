"""
Trading Hours Service
====================

Service for determining exchange trading hours and market status using EODHD API.
"""

from datetime import datetime, time, timedelta
from typing import Dict, Any, Optional, Tuple, List
import pytz
import httpx
import asyncio
from backend.utils.logger_config import get_logger
from backend.config.eodhd import settings as eodhd_settings

logger = get_logger(__name__)

# EODHD API configuration
EODHD_BASE_URL = "https://eodhd.com/api"
EODHD_API_KEY = eodhd_settings.API_KEY

# Fallback hardcoded data for when EODHD API is unavailable
FALLBACK_TRADING_HOURS = {
    "US": {
        "regular": {"open": "09:30", "close": "16:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "pre_market": {"open": "04:00", "close": "09:30", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "after_hours": {"open": "16:00", "close": "20:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    },
    "LSE": {
        "regular": {"open": "08:00", "close": "16:30", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "pre_market": {"open": "07:00", "close": "08:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "after_hours": {"open": "16:30", "close": "17:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    },
    "TO": {
        "regular": {"open": "09:30", "close": "16:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "pre_market": {"open": "07:00", "close": "09:30", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
        "after_hours": {"open": "16:00", "close": "17:00", "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    }
}

# Day name to weekday number mapping
DAY_TO_WEEKDAY = {
    "Monday": 0,
    "Tuesday": 1, 
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}


class TradingHoursService:
    """Service for determining exchange trading hours and market status using EODHD API."""
    
    @staticmethod
    async def fetch_exchange_details(exchange: str) -> Optional[Dict[str, Any]]:
        """
        Fetch exchange details from EODHD API.
        
        Args:
            exchange: Exchange code (e.g., 'US', 'LSE', 'TO')
            
        Returns:
            Dict containing exchange details or None if failed
        """
        try:
            url = f"{EODHD_BASE_URL}/exchange-details/{exchange.upper()}"
            params = {
                "api_token": EODHD_API_KEY,
                "fmt": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Successfully fetched exchange details for {exchange}")
                return data
                
        except Exception as e:
            logger.error(f"Failed to fetch exchange details for {exchange}: {e}")
            return None
    
    @staticmethod
    def parse_eodhd_trading_hours(eodhd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse EODHD exchange details into our trading hours format.
        
        Args:
            eodhd_data: Raw EODHD exchange details response
            
        Returns:
            Parsed trading hours data
        """
        try:
            trading_hours = eodhd_data.get("TradingHours", {})
            timezone = eodhd_data.get("Timezone", "UTC")
            
            # Parse working days
            working_days_str = trading_hours.get("WorkingDays", "Mon,Tue,Wed,Thu,Fri")
            working_days = []
            day_mapping = {
                "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
                "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
            }
            for day in working_days_str.split(","):
                if day.strip() in day_mapping:
                    working_days.append(day_mapping[day.strip()])
            
            # Parse trading hours
            open_time = trading_hours.get("Open", "09:30:00")
            close_time = trading_hours.get("Close", "16:00:00")
            
            # Convert to HH:MM format
            open_hhmm = open_time[:5] if len(open_time) >= 5 else open_time
            close_hhmm = close_time[:5] if len(close_time) >= 5 else close_time
            
            # Parse holidays
            holidays = []
            exchange_holidays = eodhd_data.get("ExchangeHolidays", {})
            for holiday_data in exchange_holidays.values():
                holidays.append({
                    "date": holiday_data.get("Date", ""),
                    "name": holiday_data.get("Holiday", ""),
                    "type": holiday_data.get("Type", "official")
                })
            
            return {
                "exchange": eodhd_data.get("Code", ""),
                "timezone": timezone,
                "trading_hours": {
                    "regular": {
                        "open": open_hhmm,
                        "close": close_hhmm,
                        "timezone": timezone,
                        "days": working_days
                    },
                    "pre_market": None,  # EODHD doesn't provide pre-market hours
                    "after_hours": None  # EODHD doesn't provide after-hours
                },
                "holidays": holidays,
                "is_open": eodhd_data.get("isOpen", False),
                "source": "eodhd_api"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse EODHD trading hours: {e}")
            return None
    
    @staticmethod
    def get_exchange_timezone(exchange: str) -> Optional[str]:
        """Get timezone for an exchange."""
        # This will be updated to use EODHD data
        timezone_mapping = {
            "US": "America/New_York",
            "LSE": "Europe/London", 
            "TO": "America/Toronto",
            "NASDAQ": "America/New_York",
            "NYSE": "America/New_York",
            "AMEX": "America/New_York"
        }
        return timezone_mapping.get(exchange.upper())
    
    @staticmethod
    def parse_time(time_str: str) -> time:
        """Parse time string in HH:MM format to time object."""
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)
    
    @staticmethod
    def is_trading_day(exchange: str, dt: datetime) -> bool:
        """Check if a given date is a trading day for the exchange."""
        exchange_upper = exchange.upper()
        if exchange_upper not in EXCHANGE_TRADING_HOURS:
            return False
            
        trading_hours = EXCHANGE_TRADING_HOURS[exchange_upper]
        regular_days = trading_hours["regular"]["days"]
        
        # Get weekday name
        weekday_name = dt.strftime("%A")
        return weekday_name in regular_days
    
    @staticmethod
    def is_market_open(exchange: str, dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if market is currently open for the given exchange.
        
        Returns:
            Tuple[bool, str]: (is_open, session_type)
            - is_open: True if market is open
            - session_type: "regular", "pre_market", "after_hours", or "closed"
        """
        if dt is None:
            dt = datetime.utcnow()
            
        exchange_upper = exchange.upper()
        if exchange_upper not in EXCHANGE_TRADING_HOURS:
            return False, "unknown"
        
        # Get exchange timezone
        timezone_str = TradingHoursService.get_exchange_timezone(exchange_upper)
        if not timezone_str:
            return False, "unknown"
            
        # Convert to exchange timezone
        exchange_tz = pytz.timezone(timezone_str)
        exchange_time = dt.astimezone(exchange_tz)
        
        # Check if it's a trading day
        if not TradingHoursService.is_trading_day(exchange_upper, exchange_time):
            return False, "closed"
        
        trading_hours = EXCHANGE_TRADING_HOURS[exchange_upper]
        current_time = exchange_time.time()
        
        # Check each session
        for session_name, session_info in trading_hours.items():
            if session_name == "regular" or session_name == "pre_market" or session_name == "after_hours":
                open_time = TradingHoursService.parse_time(session_info["open"])
                close_time = TradingHoursService.parse_time(session_info["close"])
                
                if open_time <= current_time <= close_time:
                    return True, session_name
        
        return False, "closed"
    
    @staticmethod
    async def get_market_status(exchange: str, dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get comprehensive market status for an exchange using EODHD API.
        
        Returns:
            Dict containing:
            - is_open: bool
            - session_type: str
            - next_open: str (next opening time)
            - next_close: str (next closing time)
            - timezone: str
            - current_time: str (current time in exchange timezone)
        """
        if dt is None:
            dt = datetime.utcnow()
            
        exchange_upper = exchange.upper()
        
        try:
            # Try to fetch from EODHD API first
            eodhd_data = await TradingHoursService.fetch_exchange_details(exchange_upper)
            
            if eodhd_data:
                # Use EODHD data
                parsed_data = TradingHoursService.parse_eodhd_trading_hours(eodhd_data)
                if parsed_data:
                    timezone_str = parsed_data["timezone"]
                    exchange_tz = pytz.timezone(timezone_str)
                    exchange_time = dt.astimezone(exchange_tz)
                    
                    # Get next open/close times
                    next_open, next_close = TradingHoursService.get_next_trading_times_from_eodhd(parsed_data, exchange_time)
                    
                    return {
                        "is_open": parsed_data.get("is_open", False),
                        "session_type": "regular" if parsed_data.get("is_open", False) else "closed",
                        "next_open": next_open,
                        "next_close": next_close,
                        "timezone": timezone_str,
                        "current_time": exchange_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                        "exchange": exchange_upper,
                        "source": "eodhd_api"
                    }
            
            # Fallback to hardcoded data
            logger.warning(f"Using fallback data for exchange {exchange_upper}")
            timezone_str = TradingHoursService.get_exchange_timezone(exchange_upper)
            
            if not timezone_str:
                return {
                    "is_open": False,
                    "session_type": "unknown",
                    "next_open": None,
                    "next_close": None,
                    "timezone": None,
                    "current_time": None,
                    "error": f"Unknown exchange: {exchange}",
                    "source": "fallback"
                }
            
            # Convert to exchange timezone
            exchange_tz = pytz.timezone(timezone_str)
            exchange_time = dt.astimezone(exchange_tz)
            
            is_open, session_type = TradingHoursService.is_market_open_fallback(exchange_upper, dt)
            
            # Get next open/close times
            next_open, next_close = TradingHoursService.get_next_trading_times_fallback(exchange_upper, exchange_time)
            
            return {
                "is_open": is_open,
                "session_type": session_type,
                "next_open": next_open,
                "next_close": next_close,
                "timezone": timezone_str,
                "current_time": exchange_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "exchange": exchange_upper,
                "source": "fallback"
            }
            
        except Exception as e:
            logger.error(f"Error getting market status for {exchange}: {e}")
            return {
                "is_open": False,
                "session_type": "error",
                "next_open": None,
                "next_close": None,
                "timezone": None,
                "current_time": None,
                "error": str(e),
                "source": "error"
            }
    
    @staticmethod
    def get_next_trading_times_from_eodhd(parsed_data: Dict[str, Any], dt: datetime) -> Tuple[Optional[str], Optional[str]]:
        """Get next trading open and close times from EODHD data."""
        try:
            trading_hours = parsed_data["trading_hours"]["regular"]
            holidays = parsed_data.get("holidays", [])
            
            # Find next trading day
            next_trading_day = dt
            while not TradingHoursService.is_trading_day_from_eodhd(next_trading_day, trading_hours, holidays):
                next_trading_day = next_trading_day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            # Get next open and close times
            next_open_time = TradingHoursService.parse_time(trading_hours["open"])
            next_close_time = TradingHoursService.parse_time(trading_hours["close"])
            
            next_open = next_trading_day.replace(hour=next_open_time.hour, minute=next_open_time.minute, second=0, microsecond=0)
            next_close = next_trading_day.replace(hour=next_close_time.hour, minute=next_close_time.minute, second=0, microsecond=0)
            
            return next_open.strftime("%Y-%m-%d %H:%M:%S"), next_close.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            logger.error(f"Error getting next trading times from EODHD: {e}")
            return None, None
    
    @staticmethod
    def is_trading_day_from_eodhd(dt: datetime, trading_hours: Dict[str, Any], holidays: List[Dict[str, Any]]) -> bool:
        """Check if a day is a trading day based on EODHD data."""
        try:
            # Check if it's a working day
            working_days = trading_hours.get("days", [])
            day_name = dt.strftime("%A")
            if day_name not in working_days:
                return False
            
            # Check if it's a holiday
            date_str = dt.strftime("%Y-%m-%d")
            for holiday in holidays:
                if holiday.get("date") == date_str:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking trading day from EODHD: {e}")
            return False
    
    @staticmethod
    def get_next_trading_times_fallback(exchange: str, dt: datetime) -> Tuple[Optional[str], Optional[str]]:
        """Get next trading open and close times using fallback data."""
        exchange_upper = exchange.upper()
        if exchange_upper not in FALLBACK_TRADING_HOURS:
            return None, None
            
        trading_hours = FALLBACK_TRADING_HOURS[exchange_upper]
        regular_hours = trading_hours["regular"]
        
        # Find next trading day
        next_trading_day = dt
        while not TradingHoursService.is_trading_day_fallback(exchange_upper, next_trading_day):
            next_trading_day = next_trading_day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Get next open and close times
        next_open_time = TradingHoursService.parse_time(regular_hours["open"])
        next_close_time = TradingHoursService.parse_time(regular_hours["close"])
        
        next_open = next_trading_day.replace(hour=next_open_time.hour, minute=next_open_time.minute, second=0, microsecond=0)
        next_close = next_trading_day.replace(hour=next_close_time.hour, minute=next_close_time.minute, second=0, microsecond=0)
        
        return next_open.strftime("%Y-%m-%d %H:%M:%S"), next_close.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def is_trading_day_fallback(exchange: str, dt: datetime) -> bool:
        """Check if a day is a trading day using fallback data."""
        exchange_upper = exchange.upper()
        if exchange_upper not in FALLBACK_TRADING_HOURS:
            return False
            
        trading_hours = FALLBACK_TRADING_HOURS[exchange_upper]
        regular_hours = trading_hours["regular"]
        
        # Check if it's a working day
        working_days = regular_hours["days"]
        day_name = dt.strftime("%A")
        return day_name in working_days
    
    @staticmethod
    def is_market_open_fallback(exchange: str, dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """Check if market is open using fallback data."""
        if dt is None:
            dt = datetime.utcnow()
            
        exchange_upper = exchange.upper()
        if exchange_upper not in FALLBACK_TRADING_HOURS:
            return False, "unknown"
            
        # Get exchange timezone
        timezone_str = TradingHoursService.get_exchange_timezone(exchange_upper)
        if not timezone_str:
            return False, "unknown"
            
        exchange_tz = pytz.timezone(timezone_str)
        exchange_time = dt.astimezone(exchange_tz)
        
        # Check if it's a trading day
        if not TradingHoursService.is_trading_day_fallback(exchange_upper, exchange_time):
            return False, "closed"
        
        # Check trading hours
        trading_hours = FALLBACK_TRADING_HOURS[exchange_upper]
        current_time = exchange_time.time()
        
        for session_name, session_hours in trading_hours.items():
            open_time = TradingHoursService.parse_time(session_hours["open"])
            close_time = TradingHoursService.parse_time(session_hours["close"])
            
            if open_time <= current_time <= close_time:
                return True, session_name
        
        return False, "closed"


# Import timedelta for the utility function
from datetime import timedelta
