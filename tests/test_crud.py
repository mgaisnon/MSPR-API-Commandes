import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import schemas, crud
from app.database import Base

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_customer(db):
    customer = schemas.CustomerCreate(name="Test", username="test", first_name="T", last_name="U", address_postal_code="123", address_city="City", profile_first_name="P", profile_last_name="U", company_name="C")
    created = crud.create_customer(db, customer)
    assert created.id == 1
    assert created.name == "Test"

def test_get_customer(db):
    customer = schemas.CustomerCreate(name="Test", username="test", first_name="T", last_name="U", address_postal_code="123", address_city="City", profile_first_name="P", profile_last_name="U", company_name="C")
    created = crud.create_customer(db, customer)
    retrieved = crud.get_customer(db, created.id)
    assert retrieved.id == created.id

def test_get_customers(db):
    for i in range(3):
        customer = schemas.CustomerCreate(name=f"Test{i}", username=f"test{i}", first_name="T", last_name="U", address_postal_code="123", address_city="City", profile_first_name="P", profile_last_name="U", company_name="C")
        crud.create_customer(db, customer)
    customers = crud.get_customers(db)
    assert len(customers) == 3

def test_update_customer(db):
    customer = schemas.CustomerCreate(name="Test", username="test", first_name="T", last_name="U", address_postal_code="123", address_city="City", profile_first_name="P", profile_last_name="U", company_name="C")
    created = crud.create_customer(db, customer)
    update_data = schemas.CustomerCreate(name="Updated", username="updated", first_name="U", last_name="D", address_postal_code="456", address_city="Town", profile_first_name="Up", profile_last_name="Da", company_name="UpC")
    updated = crud.update_customer(db, created.id, update_data)
    assert updated.name == "Updated"

def test_delete_customer(db):
    customer = schemas.CustomerCreate(name="Test", username="test", first_name="T", last_name="U", address_postal_code="123", address_city="City", profile_first_name="P", profile_last_name="U", company_name="C")
    created = crud.create_customer(db, customer)
    deleted = crud.delete_customer(db, created.id)
    assert deleted is not None
    assert crud.get_customer(db, created.id) is None