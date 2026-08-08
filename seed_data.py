import os
from datetime import datetime, date, time
from app import create_app
from models.models import db, User, Item, Match, Claim, Notification
from ai.matching_engine import run_matching_for_item

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing database tables...")
        db.drop_all()
        db.create_all()

        print("Creating Users...")
        admin = User(name="Admin Director", email="admin@lostfound.ai", phone="+1-800-555-0199", role="admin")
        admin.set_password("adminpassword")

        user1 = User(name="John Doe", email="john@gmail.com", phone="+1-555-0123", role="user")
        user1.set_password("password123")

        user2 = User(name="Sarah Jenkins", email="sarah@gmail.com", phone="+1-555-0456", role="user")
        user2.set_password("password123")

        user3 = User(name="Alex Rivera", email="alex@gmail.com", phone="+1-555-0789", role="user")
        user3.set_password("password123")

        user4 = User(name="Emily Wong", email="emily@gmail.com", phone="+1-555-0999", role="user")
        user4.set_password("password123")

        db.session.add_all([admin, user1, user2, user3, user4])
        db.session.commit()

        print("Seeding Lost & Found Reports...")

        # ----------------------------------------------------
        # DEMO TEST CASE (REQUIREMENT #20)
        # ----------------------------------------------------
        demo_lost = Item(
            user_id=user2.id, # Sarah
            type="lost",
            item_name="Samsung Galaxy Smartphone",
            category="Electronics",
            description="Black Samsung Galaxy smartphone with cracked screen, lost near college library on 5 August.",
            color="Black",
            brand="Samsung",
            location="College Library",
            date=date(2026, 8, 5),
            time=time(14, 30),
            status="active"
        )

        demo_found = Item(
            user_id=user3.id, # Alex
            type="found",
            item_name="Black Samsung Phone",
            category="Electronics",
            description="Black Samsung mobile phone, cracked display, found near college library on 5 August.",
            color="Black",
            brand="Samsung",
            location="College Library",
            date=date(2026, 8, 5),
            time=time(15, 15),
            status="active"
        )

        # ----------------------------------------------------
        # Additional 9 Lost Items (Total 10 Lost)
        # ----------------------------------------------------
        lost_items = [
            demo_lost,
            Item(
                user_id=user1.id,
                type="lost",
                item_name="Leather Wallet with Student ID",
                category="Wallets & Bags",
                description="Brown leather Tommy Hilfiger wallet containing driver license and college ID card.",
                color="Brown",
                brand="Tommy Hilfiger",
                location="Main Campus Cafeteria",
                date=date(2026, 8, 4),
                status="active"
            ),
            Item(
                user_id=user2.id,
                type="lost",
                item_name="Apple MacBook Pro 14 Inch",
                category="Electronics",
                description="Space gray MacBook Pro 14 inch in dark blue laptop sleeve with stickers.",
                color="Space Gray",
                brand="Apple",
                location="Computer Science Lab 3",
                date=date(2026, 8, 6),
                status="active"
            ),
            Item(
                user_id=user1.id,
                type="lost",
                item_name="Brass Keychain with 4 Keys",
                category="Keys",
                description="Set of 4 brass house keys attached to a red leather keychain strap.",
                color="Red",
                brand="Generic",
                location="North Parking Lot",
                date=date(2026, 8, 3),
                status="active"
            ),
            Item(
                user_id=user4.id,
                type="lost",
                item_name="Sony Noise Canceling Headphones",
                category="Electronics",
                description="Black Sony WH-1000XM4 wireless over-ear headphones in black zip case.",
                color="Black",
                brand="Sony",
                location="University Library 2nd Floor",
                date=date(2026, 8, 5),
                status="active"
            ),
            Item(
                user_id=user3.id,
                type="lost",
                item_name="Calculus & Physics Notebook",
                category="Books & Stationery",
                description="Spiral bound blue notebook labeled Advanced Engineering Mathematics.",
                color="Blue",
                brand="Mead",
                location="Lecture Hall B",
                date=date(2026, 8, 2),
                status="active"
            ),
            Item(
                user_id=user4.id,
                type="lost",
                item_name="Gold Plated Wristwatch",
                category="Jewelry & Watches",
                description="Fossil gold analog watch with stainless steel mesh strap.",
                color="Gold",
                brand="Fossil",
                location="Gym Locker Room",
                date=date(2026, 8, 1),
                status="active"
            ),
            Item(
                user_id=user2.id,
                type="lost",
                item_name="Passport and Travel Folder",
                category="Documents & ID",
                description="Navy blue leather document holder containing passport and visa papers.",
                color="Navy Blue",
                brand="Samsonite",
                location="Admin Building Auditorium",
                date=date(2026, 8, 4),
                status="active"
            ),
            Item(
                user_id=user1.id,
                type="lost",
                item_name="Denim Jacket with Pins",
                category="Clothing & Footwear",
                description="Blue Levi's denim jacket size Medium with enamel music pins on lapel.",
                color="Blue",
                brand="Levi's",
                location="Student Union Courtyard",
                date=date(2026, 8, 3),
                status="active"
            ),
            Item(
                user_id=user3.id,
                type="lost",
                item_name="Golden Retriever Puppy Tag",
                category="Pets",
                description="Golden Retriever named Max with blue collar and silver bone tag.",
                color="Golden",
                brand="N/A",
                location="East Campus Park",
                date=date(2026, 8, 6),
                status="active"
            ),
        ]

        # ----------------------------------------------------
        # Additional 9 Found Items (Total 10 Found)
        # ----------------------------------------------------
        found_items = [
            demo_found,
            Item(
                user_id=user3.id,
                type="found",
                item_name="Brown Men's Leather Wallet",
                category="Wallets & Bags",
                description="Found brown leather wallet with identity cards inside near cafeteria entrance.",
                color="Brown",
                brand="Tommy Hilfiger",
                location="Main Campus Cafeteria",
                date=date(2026, 8, 4),
                status="active"
            ),
            Item(
                user_id=user4.id,
                type="found",
                item_name="Apple Laptop in Blue Case",
                category="Electronics",
                description="Found laptop in blue protective sleeve on desk in computer lab.",
                color="Gray",
                brand="Apple",
                location="Computer Science Building",
                date=date(2026, 8, 6),
                status="active"
            ),
            Item(
                user_id=user2.id,
                type="found",
                item_name="Red Keychain with House Keys",
                category="Keys",
                description="Bunch of keys on red strap found near student parking area.",
                color="Red",
                brand="Unknown",
                location="North Parking Lot",
                date=date(2026, 8, 3),
                status="active"
            ),
            Item(
                user_id=user1.id,
                type="found",
                item_name="Black Wireless Headphones",
                category="Electronics",
                description="Black wireless headphones left behind on library study table.",
                color="Black",
                brand="Sony",
                location="University Library",
                date=date(2026, 8, 5),
                status="active"
            ),
            Item(
                user_id=user2.id,
                type="found",
                item_name="Engineering Math Notebook",
                category="Books & Stationery",
                description="Blue spiral notepad found in lecture room B desk slot.",
                color="Blue",
                brand="Generic",
                location="Lecture Hall B",
                date=date(2026, 8, 2),
                status="active"
            ),
            Item(
                user_id=user3.id,
                type="found",
                item_name="Gold Metallic Wrist Watch",
                category="Jewelry & Watches",
                description="Gold watch found near sports locker room benches.",
                color="Gold",
                brand="Fossil",
                location="Gymnasium",
                date=date(2026, 8, 1),
                status="active"
            ),
            Item(
                user_id=user1.id,
                type="found",
                item_name="Blue Travel Passport Folder",
                category="Documents & ID",
                description="Blue document holder found in auditorium row 4.",
                color="Blue",
                brand="Samsonite",
                location="Admin Building Auditorium",
                date=date(2026, 8, 4),
                status="active"
            ),
            Item(
                user_id=user4.id,
                type="found",
                item_name="Levi's Jean Jacket",
                category="Clothing & Footwear",
                description="Blue jean jacket found on courtyard bench.",
                color="Blue",
                brand="Levi's",
                location="Student Union Courtyard",
                date=date(2026, 8, 3),
                status="active"
            ),
            Item(
                user_id=user2.id,
                type="found",
                item_name="Lost Dog with Blue Collar",
                category="Pets",
                description="Friendly golden retriever found wandering near east gate park.",
                color="Golden",
                brand="N/A",
                location="East Campus Park",
                date=date(2026, 8, 6),
                status="active"
            ),
        ]

        db.session.add_all(lost_items)
        db.session.add_all(found_items)
        db.session.commit()

        print("Executing AI Matching Engine across all seeded records...")
        all_items = Item.query.all()
        for item in all_items:
            run_matching_for_item(item)

        print("\nSeed Data Population Completed Successfully!")
        print("--------------------------------------------------")
        print("Admin Account:     admin@lostfound.ai / adminpassword")
        print("User 1 Account:    john@gmail.com / password123")
        print("User 2 Account:    sarah@gmail.com / password123")
        print("User 3 Account:    alex@gmail.com / password123")
        print("--------------------------------------------------")
        print(f"Total Users:        {User.query.count()}")
        print(f"Total Lost Items:   {Item.query.filter_by(type='lost').count()}")
        print(f"Total Found Items:  {Item.query.filter_by(type='found').count()}")
        print(f"Total AI Matches:   {Match.query.count()}")
        print("--------------------------------------------------")

if __name__ == '__main__':
    seed_database()
