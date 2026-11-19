import sys
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

N_ORDERS = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
SEED = 42
OUT = Path("data")
OUT.mkdir(exist_ok=True)

rng = np.random.default_rng(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

CITIES = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
CUISINES = ["North Indian", "South Indian", "Chinese", "Biryani", "Pizza", "Burgers",
            "Desserts", "Healthy", "Street Food", "Continental"]
START = pd.Timestamp("2025-11-01")
DAYS = 365

n_customers = max(N_ORDERS // 5, 1000)
n_restaurants = max(N_ORDERS // 200, 200)
n_partners = max(N_ORDERS // 100, 200)


def skewed_ids(n, upper):
    """Skewed IDs so some customers/restaurants are far more active (realistic repeat behavior)."""
    return (rng.beta(1, 3, n) * upper).astype(int) + 1


# ---------- customers ----------
print(f"Generating {n_customers:,} customers...")
signup = START - pd.to_timedelta(rng.integers(0, 730, n_customers), unit="D")
customers = pd.DataFrame({
    "customer_id": np.arange(1, n_customers + 1),
    "customer_name": [fake.name() for _ in range(n_customers)],
    "email": [fake.email() for _ in range(n_customers)],
    "phone": [fake.phone_number() for _ in range(n_customers)],
    "city": rng.choice(CITIES, n_customers),
    "signup_date": signup.date,
    "updated_at": signup,
})
# mess: some missing emails, some uppercase emails
customers.loc[rng.random(n_customers) < 0.02, "email"] = None
mask = rng.random(n_customers) < 0.03
customers.loc[mask, "email"] = customers.loc[mask, "email"].str.upper()

# ---------- restaurants ----------
print(f"Generating {n_restaurants:,} restaurants...")
rest_created = START - pd.to_timedelta(rng.integers(0, 900, n_restaurants), unit="D")
restaurants = pd.DataFrame({
    "restaurant_id": np.arange(1, n_restaurants + 1),
    "restaurant_name": [fake.company() + " Kitchen" for _ in range(n_restaurants)],
    "city": rng.choice(CITIES, n_restaurants),
    "cuisine": rng.choice(CUISINES, n_restaurants),
    "avg_rating": np.round(rng.uniform(2.8, 4.9, n_restaurants), 1),
    "is_active": rng.random(n_restaurants) > 0.05,
    "updated_at": rest_created,
})

# ---------- delivery partners ----------
print(f"Generating {n_partners:,} delivery partners...")
partners = pd.DataFrame({
    "partner_id": np.arange(1, n_partners + 1),
    "partner_name": [fake.name() for _ in range(n_partners)],
    "city": rng.choice(CITIES, n_partners),
    "vehicle_type": rng.choice(["bike", "scooter", "bicycle"], n_partners, p=[0.6, 0.35, 0.05]),
    "joined_date": (START - pd.to_timedelta(rng.integers(0, 1000, n_partners), unit="D")).date,
})

# ---------- orders ----------
print(f"Generating {N_ORDERS:,} orders...")
hour_w = np.array([1, 1, 0.5, 0.3, 0.3, 0.5, 1, 2, 3, 3, 4, 7, 10, 9, 5, 4, 4, 6, 9, 11, 11, 9, 5, 2], dtype=float)
hour_w /= hour_w.sum()

day = rng.integers(0, DAYS, N_ORDERS)
hour = rng.choice(24, N_ORDERS, p=hour_w)
order_ts = (START + pd.to_timedelta(day, unit="D") + pd.to_timedelta(hour, unit="h")
            + pd.to_timedelta(rng.integers(0, 3600, N_ORDERS), unit="s"))

subtotal = np.round(rng.gamma(4, 90, N_ORDERS) + 80, 2)
has_promo = rng.random(N_ORDERS) < 0.3
promo_code = np.where(has_promo, rng.choice(["WELCOME50", "FEAST20", "BIGSAVE", "FREEDEL"], N_ORDERS), None)
discount = np.where(has_promo, np.minimum(subtotal * rng.choice([0.1, 0.2, 0.3], N_ORDERS), 150), 0).round(2)
delivery_fee = rng.choice([0, 25, 40, 50], N_ORDERS, p=[0.2, 0.3, 0.3, 0.2])
tax = (subtotal * 0.05).round(2)

orders = pd.DataFrame({
    "order_id": np.arange(1, N_ORDERS + 1),
    "customer_id": skewed_ids(N_ORDERS, n_customers),
    "restaurant_id": skewed_ids(N_ORDERS, n_restaurants),
    "order_ts": order_ts,
    "order_status": rng.choice(["delivered", "cancelled", "refunded", "Delivered", "DELIVERED"],
                               N_ORDERS, p=[0.84, 0.07, 0.03, 0.04, 0.02]),
    "subtotal": subtotal,
    "discount": discount,
    "delivery_fee": delivery_fee,
    "tax": tax,
    "promo_code": promo_code,
})
orders["total_amount"] = (orders.subtotal - orders.discount + orders.delivery_fee + orders.tax).round(2)
orders["updated_at"] = orders.order_ts + pd.to_timedelta(rng.integers(30, 90, N_ORDERS), unit="m")

# mess: null customer ids, negative subtotals, orphan restaurant ids
orders.loc[rng.random(N_ORDERS) < 0.003, "customer_id"] = np.nan
orders.loc[rng.random(N_ORDERS) < 0.001, "subtotal"] *= -1
orders.loc[rng.random(N_ORDERS) < 0.0005, "restaurant_id"] = n_restaurants + 999

# mess: duplicate rows (re-delivered by the source with a later updated_at)
dupes = orders.sample(frac=0.005, random_state=SEED).copy()
dupes["updated_at"] += pd.Timedelta(minutes=15)
orders = pd.concat([orders, dupes], ignore_index=True)
orders["customer_id"] = orders["customer_id"].astype("Int64")

# ---------- deliveries (only for non-cancelled orders) ----------
print("Generating deliveries...")
valid = orders.drop_duplicates("order_id")
valid = valid[~valid.order_status.str.lower().isin(["cancelled"])].reset_index(drop=True)
n_del = len(valid)

distance = np.round(rng.gamma(2.5, 1.8, n_del).clip(0.3, 20), 1)
pickup = valid.order_ts + pd.to_timedelta(rng.integers(5, 20, n_del), unit="m")
travel_min = distance * rng.uniform(3, 6, n_del) + rng.integers(2, 15, n_del)
delivered = pickup + pd.to_timedelta(travel_min, unit="m")

deliveries = pd.DataFrame({
    "delivery_id": np.arange(1, n_del + 1),
    "order_id": valid.order_id.values,
    "partner_id": rng.integers(1, n_partners + 1, n_del),
    "pickup_ts": pickup.values,
    "delivered_ts": delivered.values,
    "distance_km": distance,
    "promised_minutes": rng.choice([30, 40, 45], n_del, p=[0.3, 0.5, 0.2]),
})
# mess: delivered before pickup (bad timestamps)
bad = rng.random(n_del) < 0.0005
deliveries.loc[bad, "delivered_ts"] = deliveries.loc[bad, "pickup_ts"] - pd.Timedelta(minutes=10)

# ---------- payments ----------
print("Generating payments...")
uniq = orders.drop_duplicates("order_id").reset_index(drop=True)
n_pay = len(uniq)
payments = pd.DataFrame({
    "payment_id": np.arange(1, n_pay + 1),
    "order_id": uniq.order_id.values,
    "payment_method": rng.choice(["upi", "card", "cod", "wallet"], n_pay, p=[0.6, 0.2, 0.15, 0.05]),
    "payment_status": rng.choice(["success", "failed"], n_pay, p=[0.97, 0.03]),
    "amount": uniq.total_amount.values,
    "paid_at": uniq.order_ts.values,
})

# ---------- write ----------
tables = {
    "customers": customers, "restaurants": restaurants, "delivery_partners": partners,
    "orders": orders, "deliveries": deliveries, "payments": payments,
}
for name, df in tables.items():
    df.to_parquet(OUT / f"{name}.parquet", index=False)
    print(f"  {name}: {len(df):,} rows")

print("Done. Files are in ./data")