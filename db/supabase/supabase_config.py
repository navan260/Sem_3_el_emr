"""
Supabase Configuration
======================
Configuration for connecting to Supabase database
"""

import os
from supabase import create_client, Client

# =============================================================================
# SUPABASE CONFIGURATION
# =============================================================================

SUPABASE_URL = "https://qzevvnkvwzbvbiqzajns.supabase.co"  # Replace with your URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6ZXZ2bmt2d3pidmJpcXpham5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NTcyOTksImV4cCI6MjA3ODMzMzI5OX0.82I14IcKC62adArAYnEzY1vIkgnS__zekVba3b1689U"  # Replace with your anon key

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase


if __name__ == "__main__":
    print("✅ Supabase configuration loaded")
    print(f"URL: {SUPABASE_URL}")
