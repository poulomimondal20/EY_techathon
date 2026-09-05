import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import re


class MarketGapIdentifier:
    def __init__(self, data_path='../../Datasets/medicine_data_sampled.csv'):
        self.data = pd.read_csv(data_path)
        self.processed_data = None
        self._preprocess_data()
    
    def _preprocess_data(self):
        self.data['price_numeric'] = self.data['product_price'].str.replace('₹', '').str.replace(',', '').astype(float)
        self.processed_data = self.data[['sub_category', 'product_manufactured', 'price_numeric', 'product_name']].copy()
        self.processed_data = self.processed_data.dropna()
    
    def identify_market_gaps(self):

        category_counts = self.processed_data['sub_category'].value_counts()
        category_manufacturers = self.processed_data.groupby('sub_category')['product_manufactured'].nunique()
        category_avg_price = self.processed_data.groupby('sub_category')['price_numeric'].mean()
        category_price_std = self.processed_data.groupby('sub_category')['price_numeric'].std()
        
        gap_analysis = pd.DataFrame({
            'product_count': category_counts,
            'manufacturer_count': category_manufacturers,
            'avg_price': category_avg_price,
            'price_std': category_price_std
        })
        
        gap_analysis['opportunity_score'] = (
            (1 / gap_analysis['product_count']) * 100 + 
            (gap_analysis['price_std'] / gap_analysis['avg_price'] * 100)
        ).fillna(0)
        
        underserved = gap_analysis[
            (gap_analysis['product_count'] < gap_analysis['product_count'].median()) &
            (gap_analysis['manufacturer_count'] < gap_analysis['manufacturer_count'].median())
        ].sort_values('opportunity_score', ascending=False)
        
        return {
            'gap_analysis': gap_analysis,
            'underserved_categories': underserved,
            'high_opportunity_categories': gap_analysis.nlargest(10, 'opportunity_score')
        }
    
    def pricing_opportunity_analysis(self):

        pricing_analysis = {}
        
        for category in self.processed_data['sub_category'].unique():
            category_data = self.processed_data[self.processed_data['sub_category'] == category]
            price_stats = {
                'min_price': category_data['price_numeric'].min(),
                'max_price': category_data['price_numeric'].max(),
                'median_price': category_data['price_numeric'].median(),
                'mean_price': category_data['price_numeric'].mean(),
                'price_range': category_data['price_numeric'].max() - category_data['price_numeric'].min(),
                'coefficient_of_variation': category_data['price_numeric'].std() / category_data['price_numeric'].mean()
            }
            
            sorted_prices = sorted(category_data['price_numeric'].unique())
            price_gaps = []
            for i in range(1, len(sorted_prices)):
                gap = sorted_prices[i] - sorted_prices[i-1]
                if gap > price_stats['mean_price'] * 0.2:
                    price_gaps.append({
                        'lower_price': sorted_prices[i-1],
                        'upper_price': sorted_prices[i],
                        'gap_size': gap
                    })
            
            pricing_analysis[category] = {
                'stats': price_stats,
                'pricing_gaps': price_gaps,
                'competitor_count': len(category_data['product_manufactured'].unique())
            }
        
        return pricing_analysis
    
    def competitor_gap_analysis(self):

        market_share = self.processed_data.groupby(['sub_category', 'product_manufactured']).size().reset_index(name='product_count')
        total_per_category = market_share.groupby('sub_category')['product_count'].sum().reset_index(name='total_products')
        market_share = market_share.merge(total_per_category, on='sub_category')
        market_share['market_share_pct'] = (market_share['product_count'] / market_share['total_products']) * 100
        
        competition_analysis = market_share.groupby('sub_category').agg({
            'product_manufactured': 'count',
            'market_share_pct': ['max', 'mean', 'std']
        }).round(2)
        
        competition_analysis.columns = ['competitor_count', 'max_market_share', 'avg_market_share', 'market_share_std']
        
        hhi_data = []
        for category in self.processed_data['sub_category'].unique():
            category_shares = market_share[market_share['sub_category'] == category]['market_share_pct']
            hhi = sum(share**2 for share in category_shares)
            hhi_data.append({'sub_category': category, 'hhi': hhi})
        
        hhi_df = pd.DataFrame(hhi_data)
        competition_analysis = competition_analysis.merge(hhi_df.set_index('sub_category'), left_index=True, right_index=True)
        
        low_competition = competition_analysis[
            (competition_analysis['competitor_count'] <= 3) | 
            (competition_analysis['hhi'] < 1500)
        ].sort_values('hhi')
        
        return {
            'market_share_analysis': market_share,
            'competition_metrics': competition_analysis,
            'low_competition_categories': low_competition
        }
    
    def get_comprehensive_analysis(self):
        return {
            'market_gaps': self.identify_market_gaps(),
            'pricing_opportunities': self.pricing_opportunity_analysis(),
            'competitor_gaps': self.competitor_gap_analysis()
        }


if __name__ == "__main__":
    gap_identifier = MarketGapIdentifier()
    
    analysis_results = gap_identifier.get_comprehensive_analysis()
    
    print("=== MARKET GAP IDENTIFIER RESULTS ===")
    print("\n1. TOP UNDERSERVED THERAPEUTIC CATEGORIES:")
    underserved = analysis_results['market_gaps']['underserved_categories'].head(10)
    for idx, (category, data) in enumerate(underserved.iterrows(), 1):
        print(f"{idx}. {category}")
        print(f"   Products: {data['product_count']}, Manufacturers: {data['manufacturer_count']}")
        print(f"   Avg Price: ₹{data['avg_price']:.2f}, Opportunity Score: {data['opportunity_score']:.2f}")
    
    print("\n2. LOW COMPETITION CATEGORIES:")
    low_comp = analysis_results['competitor_gaps']['low_competition_categories'].head(5)
    for idx, (category, data) in enumerate(low_comp.iterrows(), 1):
        print(f"{idx}. {category}")
        print(f"   Competitors: {data['competitor_count']}, HHI: {data['hhi']:.2f}")