import xgboost as xgb
import sys
import os

def inspect_model(token: str):
    model_path = f"model/latest_model_{token.lower()}.xgb"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return

    print(f"🔍 Loading model: {model_path}")
    model = xgb.XGBClassifier()
    model.load_model(model_path)

    booster = model.get_booster()
    feature_names = booster.feature_names

    print(f"🔢 Feature count: {len(feature_names)}")
    print("🧠 Feature names:")
    for i, f in enumerate(feature_names):
        print(f"{i + 1:>2}. {f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_model.py <TOKEN>")
    else:
        token = sys.argv[1]
        inspect_model(token)
