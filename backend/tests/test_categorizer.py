from app.services.categorizer import categorize_channel

def test_categorize_marketing():
    assert categorize_channel("Маркетинг и SMM", "Канал про digital маркетинг") == "marketing"

def test_categorize_it():
    assert categorize_channel("Python Dev", "Programming tutorials") == "it"

def test_categorize_unknown():
    assert categorize_channel("Random stuff", "Just random things") == "other"
