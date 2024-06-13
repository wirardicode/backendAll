# model.py
import tensorflow as tf
import pickle
import numpy as np

# Memuat model dan tokenizer
model = tf.keras.models.load_model('newModel.keras')

with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

def categorize_transaction(category, amount):
    primary_keywords = ['food', 'family', 'household', 'health', 'self-development', 'education', 'rent']
    secondary_keywords = ['transportation', 'funding', 'life insurance', 'beauty', 'maid', 'money transfer', 'recurring deposit', 'tourism', 'investment']
    tertiary_keywords = ['subscription', 'festivals', 'apparel', 'gift', 'culture', 'other']

    category = category.lower()
    if any(keyword in category for keyword in primary_keywords):
        return 'Primary'
    elif any(keyword in category for keyword in secondary_keywords):
        return 'Secondary'
    elif any(keyword in category for keyword in tertiary_keywords):
        return 'Tertiary'
    else:
        return 'Secondary' if amount < 100 else 'Tertiary'

def predict_budget(categories, income):
    sequences = tokenizer.texts_to_sequences(categories)
    padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=100)
    
    predictions = model.predict(padded_sequences)
    predicted_labels = np.argmax(predictions, axis=1)
    
    category_types = ['Primary', 'Secondary', 'Tertiary']
    result = [category_types[label] for label in predicted_labels]
    
    return result
