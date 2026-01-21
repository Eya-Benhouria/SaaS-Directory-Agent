"""
Seed script to populate the database with default directories.
Run this after the initial migration.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Directory, SaaSProduct
from app.config import settings


# Default directories for SaaS submissions
# Fields match the Directory model: name, url, submission_url, category, 
# requires_account, requires_approval, requires_payment, notes, form_schema
DEFAULT_DIRECTORIES = [
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com",
        "submission_url": "https://www.producthunt.com/posts/new",
        "category": "General",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 91,
        "notes": "The place to launch and discover new tech products",
        "form_schema": {
            "fields": [
                {"name": "name", "selector": "input[name='name']", "type": "text"},
                {"name": "tagline", "selector": "input[name='tagline']", "type": "text"},
                {"name": "description", "selector": "textarea[name='description']", "type": "textarea"},
                {"name": "website_url", "selector": "input[name='url']", "type": "url"}
            ]
        }
    },
    {
        "name": "BetaList",
        "url": "https://betalist.com",
        "submission_url": "https://betalist.com/submit",
        "category": "Startups",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 65,
        "notes": "Discover and get early access to tomorrow's startups",
        "form_schema": {
            "fields": [
                {"name": "startup_name", "selector": "input[name='startup_name']", "type": "text"},
                {"name": "tagline", "selector": "input[name='tagline']", "type": "text"},
                {"name": "description", "selector": "textarea[name='description']", "type": "textarea"},
                {"name": "url", "selector": "input[name='url']", "type": "url"}
            ]
        }
    },
    {
        "name": "SaaSHub",
        "url": "https://www.saashub.com",
        "submission_url": "https://www.saashub.com/submit",
        "category": "SaaS",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 58,
        "notes": "Independent software marketplace",
        "form_schema": {
            "fields": [
                {"name": "name", "selector": "input[name='name']", "type": "text"},
                {"name": "description", "selector": "textarea[name='description']", "type": "textarea"},
                {"name": "website", "selector": "input[name='website']", "type": "url"}
            ]
        }
    },
    {
        "name": "AlternativeTo",
        "url": "https://alternativeto.net",
        "submission_url": "https://alternativeto.net/add-app/",
        "category": "General",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 75,
        "notes": "Crowdsourced software recommendations"
    },
    {
        "name": "Capterra",
        "url": "https://www.capterra.com",
        "submission_url": "https://www.capterra.com/vendors/sign-up",
        "category": "B2B",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 85,
        "notes": "Business software reviews and comparisons"
    },
    {
        "name": "G2",
        "url": "https://www.g2.com",
        "submission_url": "https://www.g2.com/products/new",
        "category": "B2B",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 88,
        "notes": "Business software and services reviews"
    },
    {
        "name": "GetApp",
        "url": "https://www.getapp.com",
        "submission_url": "https://www.getapp.com/submit",
        "category": "B2B",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 70,
        "notes": "Business app discovery platform"
    },
    {
        "name": "Indie Hackers",
        "url": "https://www.indiehackers.com",
        "submission_url": "https://www.indiehackers.com/products/new",
        "category": "Startups",
        "requires_account": True,
        "requires_approval": False,
        "domain_authority": 68,
        "notes": "Community for indie makers and founders"
    },
    {
        "name": "Startup Stash",
        "url": "https://startupstash.com",
        "submission_url": "https://startupstash.com/submit/",
        "category": "Startups",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 52,
        "notes": "Curated directory of resources and tools for startups"
    },
    {
        "name": "SideProjectors",
        "url": "https://www.sideprojectors.com",
        "submission_url": "https://www.sideprojectors.com/project/new",
        "category": "Side Projects",
        "requires_account": True,
        "requires_approval": False,
        "domain_authority": 45,
        "notes": "Marketplace for side projects"
    },
    {
        "name": "StackShare",
        "url": "https://stackshare.io",
        "submission_url": "https://stackshare.io/submit",
        "category": "Developer Tools",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 72,
        "notes": "Tech stack intelligence"
    },
    {
        "name": "Slant",
        "url": "https://www.slant.co",
        "submission_url": "https://www.slant.co/suggest",
        "category": "General",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 55,
        "notes": "Product recommendation community"
    },
    {
        "name": "AppSumo",
        "url": "https://appsumo.com",
        "submission_url": "https://sell.appsumo.com",
        "category": "Deals",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 78,
        "notes": "Software deals for entrepreneurs"
    },
    {
        "name": "Crunchbase",
        "url": "https://www.crunchbase.com",
        "submission_url": "https://www.crunchbase.com/add-new",
        "category": "Business",
        "requires_account": True,
        "requires_approval": True,
        "domain_authority": 91,
        "notes": "Business information platform"
    },
    {
        "name": "F6S",
        "url": "https://www.f6s.com",
        "submission_url": "https://www.f6s.com/company/create",
        "category": "Startups",
        "requires_account": True,
        "requires_approval": False,
        "domain_authority": 62,
        "notes": "Startup network and funding platform"
    },
    {
        "name": "StartupBuffer",
        "url": "https://startupbuffer.com",
        "submission_url": "https://startupbuffer.com/submit-startup",
        "category": "Startups",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 40,
        "notes": "Promote your startup for free"
    },
    {
        "name": "TechPluto",
        "url": "https://www.techpluto.com",
        "submission_url": "https://www.techpluto.com/submit-startup/",
        "category": "Tech",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 38,
        "notes": "Tech and startup news"
    },
    {
        "name": "Launching Next",
        "url": "https://www.launchingnext.com",
        "submission_url": "https://www.launchingnext.com/submit/",
        "category": "Startups",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 42,
        "notes": "Discover the next big startup"
    },
    {
        "name": "Land-book",
        "url": "https://land-book.com",
        "submission_url": "https://land-book.com/submit",
        "category": "Design",
        "requires_account": False,
        "requires_approval": True,
        "domain_authority": 55,
        "notes": "Website design gallery"
    },
    {
        "name": "MicroConf Connect",
        "url": "https://microconfconnect.com",
        "submission_url": "https://microconfconnect.com/submit",
        "category": "Bootstrapped",
        "requires_account": True,
        "requires_approval": False,
        "domain_authority": 35,
        "notes": "Community for bootstrapped founders"
    }
]

# Sample SaaS product (genie-ops.com)
# Fields match the SaaSProduct model
SAMPLE_PRODUCT = {
    "name": "Genie-Ops",
    "website_url": "https://www.genie-ops.com",
    "tagline": "AI-Powered Operations Management for Modern Teams",
    "short_description": "Intelligent operations management platform for teams",
    "long_description": """Genie-Ops is an intelligent operations management platform that helps teams streamline their workflows, automate repetitive tasks, and gain actionable insights through AI-powered analytics.

Key Features:
- Intelligent workflow automation
- Real-time collaboration tools
- AI-powered insights and recommendations
- Seamless integrations with popular tools
- Custom dashboards and reporting

Perfect for startups and growing teams looking to optimize their operations without the complexity of traditional enterprise tools.""",
    "category": "Operations",
    "subcategory": "Workflow Automation",
    "tags": ["AI", "Operations", "Automation", "Productivity", "SaaS"],
    "contact_email": "hello@genie-ops.com",
    "contact_name": "Genie-Ops Team",
    "twitter_url": "https://twitter.com/genieops",
    "linkedin_url": "https://linkedin.com/company/genie-ops",
    "pricing_model": "freemium",
    "pricing_details": "Free tier available. Pro plans start at $29/month.",
    "is_active": True
}


async def seed_database():
    """Seed the database with default data."""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if data already exists
            from sqlalchemy import select
            
            existing_dirs = await session.execute(select(Directory).limit(1))
            if existing_dirs.scalar():
                print("⚠️ Data already exists. Skipping seed.")
                return
            
            # Add directories
            print("Seeding directories...")
            for dir_data in DEFAULT_DIRECTORIES:
                directory = Directory(**dir_data)
                session.add(directory)
            
            # Add sample product
            print("Seeding sample product (Genie-Ops)...")
            product = SaaSProduct(**SAMPLE_PRODUCT)
            session.add(product)
            
            await session.commit()
            print(f"✅ Successfully seeded {len(DEFAULT_DIRECTORIES)} directories and 1 sample product!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
