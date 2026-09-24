import pandas as pd
import numpy as np

def generate_synthetic_dataset(num_samples=1000):
    np.random.seed(42)
    
    # Generate labels (approx 50% fake, 50% genuine)
    is_fake = np.random.choice([0, 1], size=num_samples)
    
    # Feature 1: Profile picture exists (1.0 = yes, 0.0 = no)
    # Genuine accounts usually have one, fake accounts often don't
    profile_pic = np.where(is_fake == 1, np.random.choice([0.0, 1.0], p=[0.7, 0.3], size=num_samples), 
                                         np.random.choice([0.0, 1.0], p=[0.1, 0.9], size=num_samples))
    
    # Feature 2: Ratio of numbers in username length (e.g. user12345 = 5/9 = 0.55)
    # Fake accounts tend to have lots of numbers
    nums_in_username = np.where(is_fake == 1, np.random.uniform(0.3, 0.9, num_samples), 
                                              np.random.uniform(0.0, 0.2, num_samples))
    
    # Feature 3: Follower count
    # Genuine accounts have varied followers, fakes usually have very few
    followers = np.where(is_fake == 1, np.random.exponential(scale=50, size=num_samples), 
                                       np.random.exponential(scale=500, size=num_samples))
    
    # Feature 4: Following count
    # Fake accounts follow a massive amount of people compared to their followers
    following = np.where(is_fake == 1, np.random.normal(loc=800, scale=200, size=num_samples), 
                                       np.random.normal(loc=300, scale=150, size=num_samples))
    
    # Feature 5: Account Age (Days)
    # Fake accounts are often newly created
    account_age = np.where(is_fake == 1, np.random.uniform(1, 30, num_samples), 
                                         np.random.uniform(100, 1500, num_samples))
    
    # Clip negative values
    followers = np.clip(followers, 0, None)
    following = np.clip(following, 0, None)
    
    df = pd.DataFrame({
        'profile_pic': profile_pic,
        'nums_in_username': nums_in_username,
        'followers': followers,
        'following': following,
        'account_age_days': account_age,
        'is_fake': is_fake
    })
    
    # Add a bit of random noise to make it realistic
    noise = np.random.normal(0, 0.05, df.shape)
    # Exclude profile_pic and is_fake from noise
    df.iloc[:, 1:5] = np.maximum(0, df.iloc[:, 1:5] + noise[:, 1:5])
    
    df.to_csv('social_media_profiles.csv', index=False)
    print("✅ Created synthetic dataset: social_media_profiles.csv with 1000 records")

if __name__ == "__main__":
    generate_synthetic_dataset()
